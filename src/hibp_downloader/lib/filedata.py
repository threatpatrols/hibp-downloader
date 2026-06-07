import gzip
import json
import os
from datetime import datetime
from pathlib import Path

import aiofiles
import aiofiles.os

from hibp_downloader import LOGGER_NAME
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import PrefixMetadata

logger = logger_get(name=LOGGER_NAME)


def generate_filepath(
    base_path: Path,
    hash_type: str,
    prefix: str,
    filename_suffix: str,
) -> Path:
    return Path(
        os.path.join(
            os.path.expanduser(base_path),
            hash_type.lower(),
            prefix[0:2].lower(),
            prefix[2:4].lower(),
            f"{prefix}.{filename_suffix}".lower(),
        )
    )


async def append_stringfile(filepath: Path, content: str) -> None:
    try:
        if not await aiofiles.os.path.isfile(filepath):
            return await save_bytesfile(filepath=filepath, content=content.encode("utf8"))
        async with aiofiles.open(filepath, mode="a") as f:
            await f.write(content)
    except OSError as e:
        logger.error(f"Failed to append string to file {filepath}: {e}")
        raise HibpDownloaderException(f"Failed to append string file: {e}") from e


async def save_bytesfile(filepath: Path, content: bytes, timestamp: datetime | None = None) -> None:
    full_path = os.path.realpath(os.path.expanduser(filepath))
    try:
        await aiofiles.os.makedirs(os.path.dirname(full_path), exist_ok=True)
        async with aiofiles.open(full_path, mode="wb") as f:
            await f.write(content)
        if timestamp:
            os.utime(full_path, times=(timestamp.timestamp(), timestamp.timestamp()))
    except OSError as e:
        logger.error(f"Failed to save bytes to file {filepath}: {e}")
        raise HibpDownloaderException(f"Failed to save bytes file: {e}") from e


async def save_datafile(
    data_path: Path,
    hash_type: str,
    prefix: str,
    filename_suffix: str,
    content: bytes,
    timestamp: str | datetime | None = None,
) -> None:
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    await save_bytesfile(
        filepath=generate_filepath(data_path, hash_type, prefix, filename_suffix),
        content=content,
        timestamp=timestamp,
    )


async def save_metadatafile(
    metadata_path: Path, hash_type: str, prefix: str, metadata: PrefixMetadata
) -> PrefixMetadata:
    def json_serial(data):
        if isinstance(data, datetime):
            return data.isoformat()
        raise HibpDownloaderException(f"Type {type(data)!r} not serializable")

    await save_bytesfile(
        filepath=generate_filepath(metadata_path, hash_type, prefix, filename_suffix="meta"),
        content=json.dumps(metadata.as_dict(), default=json_serial, separators=(",", ":")).encode("utf8"),
    )

    return metadata


async def load_bytesfile(filepath: Path) -> bytes:
    if not await aiofiles.os.path.isfile(filepath):
        raise HibpDownloaderException(f"File not found {filepath}")
    try:
        async with aiofiles.open(filepath, mode="rb") as f:
            return await f.read()
    except OSError as e:
        logger.error(f"Failed to read bytes from file {filepath}: {e}")
        raise HibpDownloaderException(f"Failed to read bytes file: {e}") from e


async def load_datafile(
    data_path: Path, hash_type: str, prefix: str, datafile_suffix: str, decompression_type=None, prepend_prefix=False
) -> tuple[str, Path]:
    data_filepath = generate_filepath(data_path, hash_type, prefix, datafile_suffix)
    data: bytes = await load_bytesfile(filepath=data_filepath)

    if decompression_type is None:
        pass
    elif decompression_type in ("gz", "gzip"):
        data = gzip.decompress(data)
    else:
        raise HibpDownloaderException(f"Unsupported decompression_type {decompression_type}")

    if prepend_prefix is False:
        return data.decode("utf8"), data_filepath

    data_lines = [f"{prefix.upper()}{x.upper()}" for x in data.decode("utf8").replace("\r", "").split("\n")]
    return "\n".join(data_lines), data_filepath


async def load_metadata(
    metadata_path: Path, data_path: Path, hash_type: str, prefix: str, datafile_suffix="gz"
) -> PrefixMetadata:
    metadata_filepath = generate_filepath(metadata_path, hash_type, prefix, filename_suffix="meta")

    content = None
    try:
        if await aiofiles.os.path.isfile(metadata_filepath):
            async with aiofiles.open(metadata_filepath, "r") as f:
                content = await f.read()
    except OSError as e:
        logger.error(f"Failed to read metadata file {metadata_filepath}: {e}")
        raise HibpDownloaderException(f"Failed to read metadata file: {e}") from e

    if not content:
        logger.debug(
            f"No existing metadata file {str(metadata_filepath)!r} using an empty entry",
        )
        return PrefixMetadata(prefix=prefix)

    try:
        prefix_metadata = PrefixMetadata(**json.loads(content))
    except ValueError:
        logger.warning(
            f"Unable to parse metadata file {metadata_filepath!r} using an empty entry",
        )
        return PrefixMetadata(prefix=prefix)

    if isinstance(prefix_metadata.server_timestamp, str):
        prefix_metadata.server_timestamp = datetime.fromisoformat(prefix_metadata.server_timestamp)
    if isinstance(prefix_metadata.last_modified, str):
        prefix_metadata.last_modified = datetime.fromisoformat(prefix_metadata.last_modified)

    # If the data file is missing despite metadata existing, force a re-download
    # by returning empty metadata (clears etag and server_timestamp so we don't skip)
    data_file = generate_filepath(data_path, hash_type, prefix, datafile_suffix)
    if not data_file.is_file():
        logger.debug(
            f"Data file {str(data_file)!r} missing despite metadata existing for {prefix!r}, forcing re-download"
        )
        return PrefixMetadata(prefix=prefix)

    if not prefix_metadata.bytes or prefix_metadata.bytes < 1:
        data_file = generate_filepath(data_path, hash_type, prefix, datafile_suffix)
        if data_file.is_file():
            prefix_metadata.bytes = data_file.stat().st_size

    return prefix_metadata


def encoding_type_file_suffix(encoding_type: str) -> str:
    if encoding_type is None or encoding_type.lower() == "identity":
        return "txt"
    elif encoding_type.lower() == "gzip" or encoding_type.lower() == "gz":
        return "gz"  # extension makes shell command completion for zcat, zgrep and others work nicely

    # the encoding type becomes a naive 1:1 mapping at this point
    return encoding_type.lower()


def is_valid_gzip(data: bytes) -> bool:
    """Verify that the content is a valid gzip file.

    Fully acknowledging github.com/matrix for the original implementation in branch fix-issue-10.
    - https://github.com/matrix/hibp-downloader/tree/issue_10
    - https://github.com/threatpatrols/hibp-downloader/pull/14/changes/8516fb21e48a312dcdb9cfdbf429e5c2594885c5

    """
    if not data or len(data) < 2:
        return False
    if not data.startswith(b"\x1f\x8b"):
        return False
    try:
        gzip.decompress(data)
        return True
    except Exception:
        return False


def is_valid_identity(data: bytes) -> bool:
    """Verify that the content is valid plain-text HIBP range response data."""
    if not data:
        return False
    try:
        text = data.decode("utf-8")
        if not text:
            return False
        first_line = text.splitlines()[0]
        if ":" not in first_line:
            return False
        parts = first_line.split(":")
        if len(parts) != 2:
            return False
        hex_part, count_part = parts
        int(hex_part, 16)
        int(count_part)
        return True
    except Exception:
        return False


def verify_binary_encoding(data: bytes, encoding_type: str | None) -> bool:
    """Verify that the binary blob matches the expected ENCODING_TYPE."""
    if not data:
        return False
    encoding_lower = (encoding_type or "identity").lower()
    if encoding_lower in ("gzip", "gz"):
        return is_valid_gzip(data)
    elif encoding_lower == "identity":
        return is_valid_identity(data)
    return True
