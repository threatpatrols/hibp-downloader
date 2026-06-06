import asyncio
import os
import time
from pathlib import Path
import typer
from typing import Annotated
import aiofiles

from hibp_downloader import ENCODING_TYPE, HELP_EPILOG_FOOTER, LOGGER_NAME, LOGGING_INFO_EVENT_MODULUS, app_context
from hibp_downloader.lib.filedata import encoding_type_file_suffix, generate_filepath, verify_binary_encoding
from hibp_downloader.lib.generators import hex_sequence, iterable_chunker
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import HashType

logger = logger_get(name=LOGGER_NAME)

command = typer.Typer(no_args_is_help=False, epilog=HELP_EPILOG_FOOTER)
command_name = "validate"
command_section = "Commands"


class ValidationStats:
    def __init__(self):
        self.checked = 0
        self.valid = 0
        self.missing_data = 0
        self.corrupted = 0
        self.start_time = time.time()

    @property
    def run_time(self) -> float:
        return time.time() - self.start_time


@command.callback(invoke_without_command=True)
def main(
    hash_type: Annotated[
        HashType,
        typer.Option(
            "--hash-type",
            help="Hash type to validate from the --data-path",
            case_sensitive=False,
        ),
    ] = HashType.sha1,
    first_hash: Annotated[
        str,
        typer.Option(help="Start the validator from a specific hash prefix; trimmed to the first 5 characters"),
    ] = "00000",
    last_hash: Annotated[
        str,
        typer.Option(help="Stop the validator at a hash prefix; trimmed to the first 5 characters"),
    ] = "fffff",
):
    """
    Validate local pwned password data files and clean up corrupted data or orphaned metadata; [bold cyan]validate --help[/bold cyan] for more.
    """

    logger.debug(f"Starting command {app_context.command!r} from {os.path.basename(__file__)!r}")

    if app_context.data_path and not os.path.isdir(app_context.data_path):
        logger.error(f"Data path {app_context.data_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    if app_context.metadata_path and not os.path.isdir(app_context.metadata_path):
        logger.warning(f"Metadata path {app_context.metadata_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    logger.info(f"data-path {app_context.data_path!r}")
    logger.info(f"metadata-path {app_context.metadata_path!r}")

    stats = ValidationStats()
    asyncio.run(pwnedpasswords_validate_gather(stats, hash_type, first_hash[0:5], last_hash[0:5]))

    logger.info("Validation completed:")
    logger.info(f"  Checked prefixes:   {stats.checked}")
    logger.info(f"  Valid datafiles:    {stats.valid}")
    logger.info(f"  Missing datafiles:  {stats.missing_data}")
    logger.info(f"  Corrupted/deleted:  {stats.corrupted}")


async def pwnedpasswords_validate_gather(
    stats: ValidationStats,
    hash_type: HashType,
    first_hash: str,
    last_hash: str,
    chunk_size: int = 64,
) -> None:
    prefixes = list(hex_sequence(hex_first=first_hash, hex_last=last_hash))
    total_prefixes = len(prefixes)
    logger.info(f"Validating {total_prefixes} prefixes...")
    logger.info("Legend: vd = valid, ms = missing, cr = corrupted")

    iteration_count = 0
    for chunk in iterable_chunker(iterable=prefixes, size=chunk_size):
        results = await asyncio.gather(
            *[
                verify_local_datafile(
                    prefix=prefix,
                    hash_type=hash_type,
                    data_path=Path(app_context.data_path),  # type: ignore[arg-type]
                    metadata_path=Path(app_context.metadata_path),  # type: ignore[arg-type]
                    encoding_type=ENCODING_TYPE,
                )
                for prefix in chunk
            ],
        )

        for res in results:
            stats.checked += 1
            if res == "valid":
                stats.valid += 1
            elif res == "missing":
                stats.missing_data += 1
            elif res == "corrupted":
                stats.corrupted += 1

        iteration_count += len(chunk)
        if (iteration_count // chunk_size) % LOGGING_INFO_EVENT_MODULUS == 0 or iteration_count == total_prefixes:
            elapsed = stats.run_time
            rate = int(stats.checked / elapsed) if elapsed > 0 else 0
            logger.info(
                f"prefix={chunk[-1]} "
                f"checked={stats.checked} "
                f"stats=[vd:{stats.valid} ms:{stats.missing_data} cr:{stats.corrupted}] "
                f"rate={rate}files/sec "
                f"runtime={round(elapsed / 60, 1)}min"
            )


async def verify_local_datafile(
    prefix: str,
    hash_type: HashType,
    data_path: Path,
    metadata_path: Path,
    encoding_type: str,
) -> str:
    """Checks that the local file exists and is valid.

    If datafile is missing, deletes metadata file.
    If datafile is corrupted, deletes both datafile and metadata file.
    Returns:
      "valid" if the datafile exists and is valid.
      "missing" if datafile was missing (and metadata was deleted if it existed).
      "corrupted" if datafile was corrupted and deleted.
    """
    logger_ = logger_get(name=LOGGER_NAME)
    hash_type_str = hash_type.value.lower()
    datafile_suffix = encoding_type_file_suffix(encoding_type)

    data_file_path = generate_filepath(data_path, hash_type_str, prefix, datafile_suffix)
    metadata_file_path = generate_filepath(metadata_path, hash_type_str, prefix, "meta")

    if not data_file_path.exists():
        if metadata_file_path.exists():
            logger_.warning(f"Prefix {prefix}: Metadata file exists but data file is missing. Deleting metadata.")
            try:
                metadata_file_path.unlink()
            except OSError as e:
                logger_.error(f"Prefix {prefix}: Error deleting metadata file: {e}")
        return "missing"

    # verify contents
    try:
        async with aiofiles.open(data_file_path, "rb") as f:
            data = await f.read()

        if verify_binary_encoding(data, encoding_type):
            return "valid"

        logger_.warning(
            f"Prefix {prefix}: Corrupted data file (invalid encoding '{encoding_type}'). Deleting data and metadata."
        )
    except Exception as e:
        logger_.warning(f"Prefix {prefix}: Error reading data file ({e}). Deleting data and metadata.")

    # delete corrupted file
    if data_file_path.exists():
        try:
            data_file_path.unlink()
        except OSError as e:
            logger_.error(f"Prefix {prefix}: Error deleting corrupted data file: {e}")

    # delete metadata
    if metadata_file_path.exists():
        try:
            metadata_file_path.unlink()
        except OSError as e:
            logger_.error(f"Prefix {prefix}: Error deleting metadata file: {e}")

    return "corrupted"
