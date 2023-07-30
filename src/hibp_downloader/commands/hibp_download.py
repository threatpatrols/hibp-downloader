import asyncio
import hashlib
import os
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool, Process, Queue

import typer
from typing_extensions import Annotated

from hibp_downloader import (
    __approx_gzip_bytes_per_hash__,
    __encoding_type__,
    __help_epilog_footer__,
    __local_cache_ttl_default__,
    __logger_name__,
    __logging_info_event_modulus__,
    __multiprocessing_prefixes_chunk_size__,
    __multiprocessing_processes_default__,
    __pwnedpasswords_api_url__,
    app_context,
)
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.filedata import load_metadata, save_datafile, save_metadatafile
from hibp_downloader.lib.generators import hex_sequence, iterable_chunker
from hibp_downloader.lib.http import httpx_binary_response
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import (
    HashType,
    PrefixMetadata,
    PrefixMetadataDataSource,
    QueueItemStatsCompute,
    QueueRunningStats,
)

logger = logger_get(name=__logger_name__)

command = typer.Typer(no_args_is_help=False, epilog=__help_epilog_footer__)
command_name = "download"
command_section = "Commands"


results_queue = Queue()
results_queue_exit_sentinel = "__results_queue_exit_sentinel__"


@command.callback(invoke_without_command=True)
def main(
    hash_type: Annotated[
        HashType,
        typer.Option(help="Hash type to download from HIBP to the --data-path", case_sensitive=False),
    ] = HashType.sha1.value,
    first_hash: Annotated[
        str,
        typer.Option(help="Start the downloader from a specific hash prefix; trimmed to the first 5 characters"),
    ] = "00000",
    last_hash: Annotated[
        str,
        typer.Option(help="Stop the downloader at a hash prefix; trimmed to the first 5 characters"),
    ] = "fffff",
    processes: Annotated[
        int,
        typer.Option(
            help="Number of parallel processes to use; default value based on host CPU core count",
        ),
    ] = __multiprocessing_processes_default__,
    chunk_size: Annotated[
        int,
        typer.Option(
            help="Number of hash-prefixes to consume (asynchronously) per iteration per process",
        ),
    ] = __multiprocessing_prefixes_chunk_size__,
    force: Annotated[bool, typer.Option(help="Same as setting --local_cache_ttl=0 and --ignore-etag")] = False,
    ignore_etag: Annotated[
        bool, typer.Option(help="Do not use request etag headers to manage local/remote cached data")
    ] = False,
    local_cache_ttl: Annotated[
        int,
        typer.Option(
            help="Time-to-live (seconds) on local metadata cache items; "
            "prevents requesting the same data twice in this period"
        ),
    ] = __local_cache_ttl_default__,
):
    """
    Download new pwned password hash data from HIBP and update the local --data-path data storage path; use [bold cyan]download --help[/bold cyan] for more.
    """

    logger.debug(f"Starting command {app_context.command!r} from {os.path.basename(__file__)!r}")

    if not os.path.isdir(app_context.data_path):
        logger.warning(f"Data path {app_context.data_path!r} does not exist, creating it now...")
        os.makedirs(app_context.data_path, exist_ok=True)

    if not os.path.isdir(app_context.metadata_path):
        logger.warning(f"Metadata path {app_context.metadata_path!r} does not exist, creating it now...")
        os.makedirs(app_context.metadata_path, exist_ok=True)

    logger.info(f"data-path {app_context.data_path!r}")
    logger.info(f"metadata-path {app_context.metadata_path!r}")

    if force:
        ignore_etag = True
        local_cache_ttl = 0

    encoding_type = __encoding_type__
    prefix_chunks = iterable_chunker(
        iterable=hex_sequence(hex_first=first_hash[0:5], hex_last=last_hash[0:5]), size=chunk_size
    )

    results_queue_process = Process(target=results_queue_processor, args=(results_queue,))
    results_queue_process.start()

    with Pool(
        processes=processes, initializer=results_queue_initialize, initargs=(results_queue,)
    ) as multiprocessing_pool:
        multiprocessing_pool.starmap(
            pwnedpasswords_get_and_store_asyncio_run,
            zip(
                prefix_chunks,
                repeat(hash_type),
                repeat(os.path.join(app_context.data_path, hash_type.value)),  # data_path
                repeat(os.path.join(app_context.metadata_path, hash_type.value)),  # metadata_path
                repeat(encoding_type),
                repeat(ignore_etag),
                repeat(local_cache_ttl),
                repeat(logger),
            ),
        )
        multiprocessing_pool.close()
        multiprocessing_pool.join()
        results_queue.put(results_queue_exit_sentinel)

    results_queue_process.join()


def pwnedpasswords_get_and_store_asyncio_run(*args):
    asyncio.run(pwnedpasswords_get_and_store_gather(*args))


async def pwnedpasswords_get_and_store_gather(*args) -> None:
    """
    Gather the async tasks to get pwnedpasswords per prefix-chunk item
     - First arg is the list of prefixes in this chunk
     - Last arg is the results_queue
    """
    prefixes = args[0]
    metadata_results = await asyncio.gather(
        *[pwnedpasswords_get_and_store_async(prefix, *args[1:-1]) for prefix in prefixes],
    )
    results_queue.put(metadata_results)


async def pwnedpasswords_get_and_store_async(
    prefix: str,
    hash_type: HashType,
    data_path: str,
    metadata_path: str,
    encoding_type: str,
    ignore_etag: bool,
    local_cache_ttl: int,
    logger_: logger = None,
):
    start_timestamp = datetime.now().astimezone()

    if not logger_:
        logger_ = logger_get(name=None)

    logger_.debug(
        f"{prefix=} hash_type='{hash_type.value}' {encoding_type=} {ignore_etag=} {local_cache_ttl=} {start_timestamp=}"
    )

    # get existing metadata if available
    metadata = await load_metadata(metadata_path=metadata_path, prefix=prefix)

    etag = None
    if metadata.data_source:
        if metadata.server_timestamp:
            local_ttl = local_cache_ttl - (datetime.now().astimezone() - metadata.server_timestamp).seconds
            if local_ttl > 0:
                logger_.debug(f"Skipping {prefix}; local-cache has {local_ttl} time-to-live")
                return PrefixMetadata(
                    prefix=prefix,
                    data_source=PrefixMetadataDataSource.local_source_ttl_cache,
                    start_timestamp=start_timestamp,
                )
        if not ignore_etag:
            etag = metadata.etag

    # download with etag setting
    binary, metadata = await pwnedpasswords_get(prefix, hash_type=hash_type, etag=etag, encoding=encoding_type)
    metadata.start_timestamp = start_timestamp

    # filename suffix based on encoding
    if encoding_type is None or encoding_type.lower() == "identity":
        filename_suffix = "txt"
    elif encoding_type.lower() == "gzip" or encoding_type.lower() == "gz":
        filename_suffix = "gz"  # extension makes shell command completion for zcat, zgrep and others work nicely
    else:
        filename_suffix = encoding_type.lower()

    # save
    if binary:
        await save_datafile(
            data_path=data_path,
            prefix=prefix,
            content=binary,
            filename_suffix=filename_suffix,
            timestamp=metadata.last_modified,
        )

    if metadata.data_source not in (
        PrefixMetadataDataSource.local_source_ttl_cache,
        PrefixMetadataDataSource.unknown_source_status,
    ):
        await save_metadatafile(metadata_path=metadata_path, prefix=prefix, metadata=metadata)

    return metadata


async def pwnedpasswords_get(prefix: str, hash_type: HashType, etag: str, encoding: str, httpx_debug: bool = False):
    url = f"{__pwnedpasswords_api_url__}/range/{prefix}"
    if hash_type == HashType.ntlm:
        url += "?mode=ntlm"

    try:
        response = await httpx_binary_response(url=url, etag=etag, encoding=encoding, debug=httpx_debug)
    except HibpDownloaderException:
        return None, PrefixMetadata(prefix=prefix, data_source=PrefixMetadataDataSource.unknown_source_status)

    metadata = PrefixMetadata(
        prefix=prefix,
        hash_type=hash_type,
        etag=response.headers.get("etag"),
        bytes=len(response.binary),
        server_timestamp=response.headers.get("date"),
        last_modified=response.headers.get("last-modified"),
        content_encoding=response.headers.get("content-encoding"),
        content_checksum=hashlib.sha256(response.binary).hexdigest() if response.binary else None,
    )

    if response.status_code == 304:  # HTTP 304 Not Modified status
        metadata.data_source = PrefixMetadataDataSource.local_source_etag_match
    elif response.status_code == 200:
        if response.headers.get("cf-cache-status").upper() == "HIT":
            metadata.data_source = PrefixMetadataDataSource.remote_source_remote_cache
        else:
            metadata.data_source = PrefixMetadataDataSource.remote_source_origin_source
    else:
        metadata.data_source = PrefixMetadataDataSource.unknown_source_status

    return response.binary, metadata


def results_queue_initialize(q):
    global results_queue
    results_queue = q


def results_queue_processor(q: Queue):
    running_stats = QueueRunningStats()

    while True:
        metadata_items = q.get()
        if metadata_items == results_queue_exit_sentinel:
            break

        if metadata_items:
            running_stats.add_item_stats(item=QueueItemStatsCompute(metadata_items).stats)

        if running_stats.queue_item_count % __logging_info_event_modulus__ == 0:
            logger.info(
                f"prefix={running_stats.prefix_latest} "
                f"source=[lc:{running_stats.local_source_ttl_cache_count_sum} "
                f"et:{running_stats.local_source_etag_match_count_sum} "
                f"rc:{running_stats.remote_source_remote_cache_count_sum} "
                f"ro:{running_stats.remote_source_origin_source_count_sum} "
                f"xx:{running_stats.unknown_source_status_count_sum}] "
                f"runtime_rate=[{to_mbytes(running_stats.bytes_received_rate_total * 8, 1)}MBit/s "
                f"{int(running_stats.request_rate_total)}req/s "
                f"~{int(running_stats.bytes_received_rate_total / __approx_gzip_bytes_per_hash__)}H/s] "
                f"runtime={round(running_stats.run_time/3600,2)}hr "
                f"download={to_mbytes(running_stats.bytes_received_sum, 1)}MB"
            )


def to_mbytes(value, rounding=None):
    if value is not None:
        return round(value / 1024 / 1024, rounding) if rounding else value / 1024 / 1024
