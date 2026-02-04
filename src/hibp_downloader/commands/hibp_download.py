import asyncio
import hashlib
import os
from datetime import datetime
from multiprocessing import Manager, Process, Queue
from pathlib import Path
from typing import Any, List, Union

import gzip

GZIP_MAGIC_BYTES = b'\x1f\x8b'

import typer
from typing_extensions import Annotated

from hibp_downloader import (
    APPROX_GZIP_BYTES_PER_HASH,
    ENCODING_TYPE,
    HELP_EPILOG_FOOTER,
    HTTP_MAX_RETRIES_DEFAULT,
    HTTP_TIMEOUT_DEFAULT,
    LOCAL_CACHE_TTL_DEFAULT,
    LOGGER_NAME,
    LOGGING_INFO_EVENT_MODULUS,
    MULTIPROCESSING_PREFIXES_CHUNK_SIZE_DEFAULT,
    MULTIPROCESSING_PROCESSES_DEFAULT,
    PWNEDPASSWORDS_API_URL,
    app_context,
)
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.filedata import encoding_type_file_suffix, load_metadata, save_datafile, save_metadatafile
from hibp_downloader.lib.generators import hex_sequence, iterable_chunker
from hibp_downloader.lib.http import httpx_binary_response
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import (
    HashType,
    PrefixMetadata,
    PrefixMetadataDataSource,
    QueueItemStatsCompute,
    QueueRunningStats,
    WorkerArgs,
)

def is_valid_gzip(data: bytes) -> bool:
    """Verify that the content is a valid gzip file."""
    if not data or len(data) < 2:
        return False
    if not data.startswith(GZIP_MAGIC_BYTES):
        return False
    try:
        gzip.decompress(data)
        return True
    except Exception:
        return False

logger = logger_get(name=LOGGER_NAME)

command = typer.Typer(no_args_is_help=False, epilog=HELP_EPILOG_FOOTER)
command_name = "download"
command_section = "Commands"


QUEUE_WORKER_EXIT_SENTINEL = "__queue_exit_sentinel__"


@command.callback(invoke_without_command=True)
def main(
    hash_type: Annotated[
        HashType,
        typer.Option(help="Hash type to download from HIBP to the --data-path", case_sensitive=False),
    ] = HashType.sha1,
    first_hash: Annotated[
        str,
        typer.Option(help="Start the downloader from a specific hash prefix; trimmed to the first 5 characters"),
    ] = "00000",
    last_hash: Annotated[
        str,
        typer.Option(help="Stop the downloader at a hash prefix; trimmed to the first 5 characters"),
    ] = "fffff",
    number_of_workers: Annotated[
        int,
        typer.Option(
            "--processes", help="Number of parallel processes to use; default value based on host CPU core count", min=1
        ),
    ] = MULTIPROCESSING_PROCESSES_DEFAULT,
    chunk_size: Annotated[
        int,
        typer.Option(
            help="Number of hash-prefixes to consume (asynchronously) per iteration per process",
        ),
    ] = MULTIPROCESSING_PREFIXES_CHUNK_SIZE_DEFAULT,
    force: Annotated[
        bool, typer.Option("--force", help="Same as setting --local-cache-ttl=0 and --ignore-etag")
    ] = False,
    ignore_etag: Annotated[
        bool, typer.Option("--ignore-etag", help="Do not use request etag headers to manage local/remote cached data")
    ] = False,
    local_cache_ttl: Annotated[
        int,
        typer.Option(
            help="Time-to-live (seconds) on local metadata cache items; "
            "prevents requesting the same data twice in this period"
        ),
    ] = LOCAL_CACHE_TTL_DEFAULT,
    http_timeout: Annotated[
        int,
        typer.Option(help="HTTP timeout (seconds) per request"),
    ] = HTTP_TIMEOUT_DEFAULT,
    http_max_retries: Annotated[
        int,
        typer.Option(help="Maximum number of HTTP request retries on request failure"),
    ] = HTTP_MAX_RETRIES_DEFAULT,
    http_proxy: Annotated[
        str,
        typer.Option(help="HTTP proxy"),
    ] = "",
    http_certificates: Annotated[
        str,
        typer.Option(help="Path to cert file to verify SSL connection"),
    ] = "",
):
    """
    Download new pwned password hash data from HIBP and update the local --data-path data storage path; use [bold cyan]download --help[/bold cyan] for more.
    """

    logger.debug(f"Starting command {app_context.command!r} from {os.path.basename(__file__)!r}")

    if app_context.data_path and not os.path.isdir(app_context.data_path):
        logger.warning(f"Data path {app_context.data_path!r} does not exist, creating it now...")
        os.makedirs(app_context.data_path, exist_ok=True)

    if app_context.metadata_path and not os.path.isdir(app_context.metadata_path):
        logger.warning(f"Metadata path {app_context.metadata_path!r} does not exist, creating it now...")
        os.makedirs(app_context.metadata_path, exist_ok=True)

    logger.info(f"data-path {app_context.data_path!r}")
    logger.info(f"metadata-path {app_context.metadata_path!r}")

    if force:
        ignore_etag = True
        local_cache_ttl = 0

    result_queue = Manager().Queue()
    results_queue_process = Process(target=results_queue_processor, args=(result_queue,))
    results_queue_process.daemon = True
    results_queue_process.start()

    work_queue: Queue = Queue()
    worker_args = WorkerArgs(
        hash_type=hash_type,
        data_path=app_context.data_path,  # type: ignore[arg-type]
        metadata_path=app_context.metadata_path,  # type: ignore[arg-type]
        encoding_type=ENCODING_TYPE,
        ignore_etag=ignore_etag,
        local_cache_ttl=local_cache_ttl,
        http_timeout=http_timeout,
        http_max_retries=http_max_retries,
        http_proxy=http_proxy,
        http_certificates=http_certificates,
        http_debug=False,
    )

    worker_processes = []

    try:
        worker_processes = start_worker_processes(
            work_queue=work_queue, result_queue=result_queue, worker_count=number_of_workers, worker_args=worker_args
        )
        enqueue_worker_tasks(
            first_hash, last_hash, worker_count=len(worker_processes), queue=work_queue, chunk_size=chunk_size
        )

        logger.info(f"Created {len(worker_processes)} worker processes to consume a queue of prefix-hash values.")

        for i, worker_process in enumerate(worker_processes):
            worker_process.join()
            logger.debug(f"Queue worker process {i} finished.")

        result_queue.put(QUEUE_WORKER_EXIT_SENTINEL)
        results_queue_process.join()
        logger.info("Done")

    except KeyboardInterrupt:
        logger.warning("Download process interrupted by user. Stopping workers...")
        for p in worker_processes:
            if p.is_alive():
                p.terminate()
        if results_queue_process.is_alive():
            results_queue_process.terminate()

        work_queue.close()
        work_queue.cancel_join_thread()

        logger.warning("Workers stopped.")


def enqueue_worker_tasks(
    first_hash: str, last_hash: str, worker_count: int, queue: Queue, chunk_size: int = 10
) -> None:
    prefix_chunks = iterable_chunker(
        iterable=hex_sequence(hex_first=first_hash[0:5], hex_last=last_hash[0:5]), size=chunk_size
    )

    for prefix_chunk in prefix_chunks:
        queue.put(prefix_chunk)

    for _ in range(0, worker_count):
        queue.put(QUEUE_WORKER_EXIT_SENTINEL)


def start_worker_processes(
    work_queue: Queue, result_queue: Any, worker_count: int, worker_args: WorkerArgs
) -> List[Process]:
    worker_processes = []
    for worker_index in range(0, worker_count):
        worker_process = Process(
            target=queue_worker_process, args=(work_queue, result_queue, worker_index, worker_args)
        )
        worker_process.daemon = True
        worker_process.start()
        worker_processes.append(worker_process)

    return worker_processes


def queue_worker_process(work_queue: Queue, result_queue: Queue, worker_index: int, worker_args: WorkerArgs):
    while True:
        hash_prefixes = work_queue.get()
        if hash_prefixes == QUEUE_WORKER_EXIT_SENTINEL:
            break
        worker_args.worker_index = worker_index
        asyncio.run(pwnedpasswords_get_store_gather(result_queue, hash_prefixes, worker_args))


async def pwnedpasswords_get_store_gather(result_queue: Queue, hash_prefixes: tuple, worker_args: WorkerArgs) -> None:
    metadata_results = await asyncio.gather(
        *[pwnedpasswords_get_and_store_async(hash_prefix, **worker_args.as_dict()) for hash_prefix in hash_prefixes],
    )
    result_queue.put(metadata_results)


async def pwnedpasswords_get_and_store_async(
    prefix: str,
    hash_type: HashType,
    data_path: Path,
    metadata_path: Path,
    encoding_type: str,
    http_timeout: int,
    http_max_retries: int,
    http_proxy: str,
    http_certificates: str,
    http_debug: bool,
    ignore_etag: bool,
    local_cache_ttl: int,
    worker_index: int,
) -> PrefixMetadata:
    logger_ = logger_get(name=LOGGER_NAME)
    start_timestamp = datetime.now().astimezone()

    logger_.debug(
        f"{worker_index=} {prefix=} hash_type='{hash_type.value}' {encoding_type=} "
        f"{http_timeout=} {http_max_retries=} {http_proxy=} {http_certificates=} {http_debug=}"
        f"{ignore_etag=} {local_cache_ttl=} start_timestamp={str(start_timestamp)}"
    )

    datafile_suffix = encoding_type_file_suffix(encoding_type)

    force_redownload = False
    local_file_valid = await verify_local_datafile(
        data_path=data_path,
        metadata_path=metadata_path,
        hash_type=hash_type,
        prefix=prefix,
        datafile_suffix=datafile_suffix,
    )
    if not local_file_valid:
        logger_.warning(
            f"Prefix {prefix}: Local file corrupted or missing, forcing re-download"
        )
        force_redownload = True

    metadata_existing = PrefixMetadata(prefix=prefix, hash_type=hash_type)
    if not force_redownload:
        # get existing metadata if available
        metadata_existing = await load_metadata(
            metadata_path=metadata_path,
            data_path=data_path,
            prefix=prefix,
            hash_type=hash_type.value,
            datafile_suffix=datafile_suffix,
        )

        if not metadata_existing:
            logger_.debug(f"No existing metadata, will generate new metadata for {prefix!r}")

    etag = None
    if metadata_existing.data_source and not force_redownload:
        if metadata_existing.server_timestamp:
            local_ttl = (
                local_cache_ttl - (datetime.now().astimezone() - metadata_existing.server_timestamp).total_seconds()
            )
            if local_ttl > 0:
                logger_.debug(f"Skipping {prefix}; local-cache has {local_ttl} time-to-live")
                metadata_existing.data_source = PrefixMetadataDataSource.local_source_ttl_cache
                metadata_existing.start_timestamp = start_timestamp
                return metadata_existing
        if not ignore_etag:
            etag = metadata_existing.etag

    # download
    binary, metadata_latest = await pwnedpasswords_get(
        prefix,
        hash_type=hash_type,
        etag=etag,
        encoding=encoding_type,
        http_timeout=http_timeout,
        http_max_retires=http_max_retries,
        http_proxy=http_proxy,
        http_certificates=http_certificates,
        http_debug=http_debug,
    )
    metadata_latest.start_timestamp = start_timestamp

    metadata = metadata_existing if not force_redownload else PrefixMetadata(prefix=prefix, hash_type=hash_type)
    for attr_name in dir(metadata_latest):
        if not callable(getattr(metadata_latest, attr_name)) and not str(attr_name).startswith("_"):
            value = getattr(metadata_latest, attr_name)
            if value:
                setattr(metadata, attr_name, value)

    # save only if content is valid
    if binary:
        if is_valid_gzip(binary):
            await save_datafile(
                data_path=data_path,
                hash_type=hash_type,
                prefix=prefix,
                content=binary,
                filename_suffix=datafile_suffix,
                timestamp=metadata.last_modified,
            )
        else:
            logger_.error(f"Prefix {prefix}: Download failed, invalid non-gzip binary")
            metadata.data_source = PrefixMetadataDataSource.unknown_source_status

    if metadata.data_source not in (
        PrefixMetadataDataSource.local_source_ttl_cache,
        PrefixMetadataDataSource.unknown_source_status,
    ):
        await save_metadatafile(metadata_path=metadata_path, hash_type=hash_type, prefix=prefix, metadata=metadata)

    return metadata


async def pwnedpasswords_get(
    prefix: str,
    hash_type: HashType,
    etag: Union[str, None],
    encoding: str,
    http_timeout: int,
    http_max_retires: int,
    http_proxy: str,
    http_certificates: str,
    http_debug: bool,
):
    logger_ = logger_get(name=LOGGER_NAME)

    url = f"{PWNEDPASSWORDS_API_URL}/range/{prefix}"
    if hash_type == HashType.ntlm:
        url += "?mode=ntlm"

    max_attempts = max(http_max_retires, 3)  # at least 3 attempts
    current_etag = etag  # use etag only on the first attempt

    for attempt in range(1, max_attempts + 1):
        try:
            response = await httpx_binary_response(
                url=url,
                etag=current_etag,
                encoding=encoding,
                debug=http_debug,
                timeout=http_timeout,
                max_retries=http_max_retires,
                proxy=http_proxy,
                verify=http_certificates,
            )
        except HibpDownloaderException as e:
            logger_.warning(
                f"Prefix {prefix}: HTTP error (attempt {attempt}/{max_attempts}): {e}"
            )
            if attempt < max_attempts:
                await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff: 1s, 2s, 4s...
                current_etag = None  # disable etag for retries
                continue
            return None, PrefixMetadata(
                prefix=prefix,
                hash_type=hash_type,
                data_source=PrefixMetadataDataSource.unknown_source_status
            )

        # HTTP 304 Not Modified - the local file is already up to date.
        if response.status_code == 304:
            metadata = PrefixMetadata(
                prefix=prefix,
                hash_type=hash_type,
                etag=response.headers.get("etag"),
                bytes=0,
                server_timestamp=response.headers.get("date"),
                last_modified=response.headers.get("last-modified"),
                content_encoding=response.headers.get("content-encoding"),
                content_checksum=None,
                data_source=PrefixMetadataDataSource.local_source_etag_match,
            )
            return None, metadata

        # HTTP 200 OK - verify that the content is valid
        elif response.status_code == 200:
            if response.binary and is_valid_gzip(response.binary):
                # valid content
                metadata = PrefixMetadata(
                    prefix=prefix,
                    hash_type=hash_type,
                    etag=response.headers.get("etag"),
                    bytes=len(response.binary),
                    server_timestamp=response.headers.get("date"),
                    last_modified=response.headers.get("last-modified"),
                    content_encoding=response.headers.get("content-encoding"),
                    content_checksum=hashlib.sha256(response.binary).hexdigest(),
                )
                cf_cache_status = response.headers.get("cf-cache-status", "")
                if cf_cache_status.upper() == "HIT":
                    metadata.data_source = PrefixMetadataDataSource.remote_source_remote_cache
                else:
                    metadata.data_source = PrefixMetadataDataSource.remote_source_origin_source
                return response.binary, metadata

            else:
                # HTTP 200 but corrupted content - try again
                content_preview = response.binary[:50] if response.binary else b''
                logger_.warning(
                    f"Prefix {prefix}: HTTP 200 but invalid gzip content "
                    f"(attempt {attempt}/{max_attempts}, preview: {content_preview!r})"
                )
                if attempt < max_attempts:
                    await asyncio.sleep(2 ** (attempt - 1))
                    current_etag = None  # force complete re-download
                    continue

        # other status codes (4xx, 5xx) - try again
        else:
            logger_.warning(
                f"Prefix {prefix}: HTTP {response.status_code} "
                f"(attempt {attempt}/{max_attempts})"
            )
            if attempt < max_attempts:
                await asyncio.sleep(2 ** (attempt - 1))
                current_etag = None
                continue

    # all attempts exhausted
    logger_.error(
        f"Prefix {prefix}: download failed after {max_attempts} attempts"
    )
    return None, PrefixMetadata(
        prefix=prefix,
        hash_type=hash_type,
        data_source=PrefixMetadataDataSource.unknown_source_status
    )


async def verify_local_datafile(
    data_path: Path,
    metadata_path: Path,
    hash_type: HashType,
    prefix: str,
    datafile_suffix: str,
) -> bool:
    """
    Checks that the local file exists and is a valid gzip file.
    If corrupted, deletes both the file and the metadata.
    Returns True if the file is valid, False otherwise.
    """
    logger_ = logger_get(name=LOGGER_NAME)

    hash_type_str = hash_type.value if isinstance(hash_type, HashType) else hash_type

    data_file_path = (
        Path(data_path) / hash_type_str / prefix[0:2] / prefix[2:4] / f"{prefix}.{datafile_suffix}"
    )

    metadata_file_path = (
        Path(metadata_path) / hash_type_str / prefix[0:2] / prefix[2:4] / f"{prefix}.json"
    )

    if not data_file_path.exists():
        if metadata_file_path.exists():
            try:
                metadata_file_path.unlink()
            except OSError:
                pass
        return False

    # verify contents
    try:
        with open(data_file_path, 'rb') as f:
            data = f.read()

        if is_valid_gzip(data):
            return True

        logger_.warning(f"Prefix {prefix}: Corrupted file, removing ...")

    except Exception as e:
        logger_.warning(f"Prefix {prefix}: Error reading ({e}), removing ...")

    # delete corrupted file
    try:
        data_file_path.unlink()
    except OSError:
        pass

    # delete metadata
    if metadata_file_path.exists():
        try:
            metadata_file_path.unlink()
        except OSError:
            pass

    return False

def results_queue_processor(q: Queue):
    running_stats = QueueRunningStats()

    while True:
        metadata_items = q.get()
        if metadata_items == QUEUE_WORKER_EXIT_SENTINEL:
            running_stats.end_trigger()
            logger.info(f"Finished in {round(running_stats.run_time / 60, 1)}min")
            break

        if metadata_items:
            running_stats.add_item_stats(item=QueueItemStatsCompute(metadata_items).stats)

        if running_stats.queue_item_count % LOGGING_INFO_EVENT_MODULUS == 0:
            logger.info(
                f"prefix={running_stats.prefix_latest} "
                f"source=[lc:{running_stats.local_source_ttl_cache_count_sum} "
                f"et:{running_stats.local_source_etag_match_count_sum} "
                f"rc:{running_stats.remote_source_remote_cache_count_sum} "
                f"ro:{running_stats.remote_source_origin_source_count_sum} "
                f"xx:{running_stats.unknown_source_status_count_sum}] "
                f"processed=[{to_mbytes(running_stats.bytes_processed_sum, 1)}MB "
                f"~{int(running_stats.bytes_processed_rate_total / APPROX_GZIP_BYTES_PER_HASH)}H/s] "
                f"api=[{int(running_stats.request_rate_total)}req/s "
                f"{to_mbytes(running_stats.bytes_received_sum, 1)}MB] "
                f"runtime={round(running_stats.run_time / 60, 1)}min"
            )


def to_mbytes(value, rounding=None):
    if value is not None:
        return round(value / 1024 / 1024, rounding) if rounding else value / 1024 / 1024
