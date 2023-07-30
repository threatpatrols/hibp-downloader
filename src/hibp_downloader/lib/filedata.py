import gzip
import json
import os
from datetime import datetime
from typing import Union

import aiofiles
import aiofiles.os

from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.models import PrefixMetadata


async def append_stringfile(filename: str, content: str) -> None:
    if not await aiofiles.os.path.isfile(filename):
        return await save_bytesfile(os.path.dirname(filename), os.path.basename(filename), content.encode("utf8"))
    async with aiofiles.open(filename, mode="a") as f:
        await f.write(content)


async def save_bytesfile(pathname: str, filename: str, content: bytes, timestamp: Union[datetime, None] = None) -> None:
    await aiofiles.os.makedirs(pathname, exist_ok=True)
    async with aiofiles.open(os.path.join(pathname, filename), mode="wb") as f:
        await f.write(content)

    if timestamp:
        os.utime(os.path.join(pathname, filename), times=(timestamp.timestamp(), timestamp.timestamp()))


async def save_datafile(
    data_path: str, prefix: str, content: bytes, filename_suffix: str, timestamp: Union[datetime, None] = None
) -> None:
    await save_bytesfile(
        pathname=os.path.join(data_path, prefix[0:2], prefix[2:4]),
        filename=f"{prefix}.{filename_suffix}",
        content=content,
        timestamp=timestamp,
    )


async def save_metadatafile(metadata_path: str, prefix: str, metadata: PrefixMetadata) -> PrefixMetadata:
    def json_serial(data):
        if isinstance(data, datetime):
            return data.isoformat()
        raise HibpDownloaderException(f"Type {type(data)!r} not serializable")

    await save_bytesfile(
        pathname=os.path.join(metadata_path, prefix[0:2], prefix[2:4]),
        filename=f"{prefix}.meta",
        content=json.dumps(metadata.as_dict(), default=json_serial, separators=(",", ":")).encode("utf8"),
    )

    return metadata


async def load_bytesfile(pathname: str, filename: str) -> bytes:
    filename = os.path.join(pathname, filename)
    if not await aiofiles.os.path.isfile(filename):
        raise HibpDownloaderException(f"File not found {filename}")
    async with aiofiles.open(filename, mode="rb") as f:
        return await f.read()


async def load_datafile(
    data_path: str, prefix: str, filename_suffix: str, decompression_type=None, prepend_prefix=False
) -> str:
    data: bytes = await load_bytesfile(
        pathname=os.path.join(data_path, prefix[0:2], prefix[2:4]),
        filename=f"{prefix}.{filename_suffix}",
    )
    if decompression_type is None:
        pass
    elif decompression_type in ("gz", "gzip"):
        data = gzip.decompress(data)
    else:
        raise HibpDownloaderException(f"Unsupported decompression_type {decompression_type}")

    if prepend_prefix is False:
        return data.decode("utf8")

    data_lines = [f"{prefix.lower()}{x.lower()}" for x in data.decode("utf8").replace("\r", "").split("\n")]
    return "\n".join(data_lines)


async def load_metadata(metadata_path: str, prefix: str) -> PrefixMetadata:
    filename = os.path.join(metadata_path, prefix[0:2], prefix[2:4], f"{prefix}.meta")

    content = None
    if await aiofiles.os.path.isfile(filename):
        async with aiofiles.open(filename, "r") as f:
            content = await f.read()

    if content is None:
        return PrefixMetadata(prefix=prefix)

    prefix_metadata = PrefixMetadata(**json.loads(content))

    if isinstance(prefix_metadata.server_timestamp, str):
        prefix_metadata.server_timestamp = datetime.fromisoformat(prefix_metadata.server_timestamp)
    if isinstance(prefix_metadata.last_modified, str):
        prefix_metadata.last_modified = datetime.fromisoformat(prefix_metadata.last_modified)

    return prefix_metadata
