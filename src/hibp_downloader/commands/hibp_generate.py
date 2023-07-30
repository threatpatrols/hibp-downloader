import asyncio
import os

import typer
from typing_extensions import Annotated

from hibp_downloader import (
    __encoding_type__,
    __help_epilog_footer__,
    __logger_name__,
    __logging_info_event_modulus__,
    app_context,
)
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.filedata import append_stringfile, load_datafile
from hibp_downloader.lib.generators import hex_sequence, iterable_chunker
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import HashType

logger = logger_get(name=__logger_name__)

command = typer.Typer(no_args_is_help=False, epilog=__help_epilog_footer__)
command_name = "generate"
command_section = "Commands"


@command.callback(invoke_without_command=True)
def main(
    filename: Annotated[
        str,
        typer.Option(help="Filename to write the pwned password hash data as a single text file."),
    ],
    hash_type: Annotated[
        HashType,
        typer.Option(help="Hash type to use from the --data-path", case_sensitive=False),
    ] = HashType.sha1.value,
    first_hash: Annotated[
        str,
        typer.Option(help="Start the generator from a specific hash prefix; trimmed to the first 5 characters"),
    ] = "00000",
    last_hash: Annotated[
        str,
        typer.Option(help="Stop the generator at a hash prefix; trimmed to the first 5 characters"),
    ] = "fffff",
):
    """
    Generate a single text file with the pwned password hash values in-order from the --data-path location; [bold cyan]generate --help[/bold cyan] for more.
    """

    logger.debug(f"Starting command {app_context.command!r} from {os.path.basename(__file__)!r}")

    if not os.path.isdir(app_context.data_path):
        logger.error(f"Data path {app_context.data_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    if not os.path.isdir(app_context.metadata_path):
        logger.warning(f"Metadata path {app_context.metadata_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    logger.info(f"data-path {app_context.data_path!r}")

    if os.path.isfile(filename):
        logger.error(f"Output file already exists {filename!r}")
        raise typer.Exit(1)

    asyncio.run(pwnedpasswords_datastore_sorted_gather(filename, hash_type, first_hash[0:5], last_hash[0:5]))


async def pwnedpasswords_datastore_sorted_gather(filename, hash_type, first_hash, last_hash, chunk_size=16):
    iteration_count = 0
    for prefixes in iterable_chunker(iterable=hex_sequence(hex_first=first_hash, hex_last=last_hash), size=chunk_size):
        results = await asyncio.gather(
            *[pwnedpasswords_datastore_sorted_async(prefix, hash_type) for prefix in prefixes],
        )

        if (
            iteration_count == 0
            or iteration_count % (__logging_info_event_modulus__ * __logging_info_event_modulus__) == 0
        ):
            logger.info(f"Prefix position {prefixes[0]!r} appending to {filename!r}")
        iteration_count += 1

        output = ""
        for k, v in dict(sorted({k: v for d in results for k, v in d.items()}.items())).items():
            output = f"{output}\n{v}"
        await append_stringfile(filename=filename, content=output)


async def pwnedpasswords_datastore_sorted_async(prefix, hash_type):
    if __encoding_type__ in ("gz", "gzip"):
        filename_suffix = "gz"
        decompression_mode = "gzip"
    else:
        raise HibpDownloaderException(f"Unsupported __encoding_type__ {__encoding_type__}")

    source_data = await load_datafile(
        data_path=os.path.join(app_context.data_path, hash_type),
        prefix=prefix,
        filename_suffix=filename_suffix,
        decompression_type=decompression_mode,
        prepend_prefix=True,
    )

    return {prefix: source_data}
