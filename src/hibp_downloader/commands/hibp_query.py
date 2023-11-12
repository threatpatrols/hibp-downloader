import asyncio
import json
import os

import typer
from typing_extensions import Annotated

from hibp_downloader import ENCODING_TYPE, HELP_EPILOG_FOOTER, LOGGER_NAME, app_context
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.filedata import load_datafile
from hibp_downloader.lib.hashing import hashed_ntlm, hashed_sha1
from hibp_downloader.lib.logger import logger_get
from hibp_downloader.models import HashType

logger = logger_get(name=LOGGER_NAME)

command = typer.Typer(no_args_is_help=False, epilog=HELP_EPILOG_FOOTER)
command_name = "query"
command_section = "Commands"


@command.callback(invoke_without_command=True)
def main(
    password: Annotated[
        str,
        typer.Option(
            prompt=True,
            hide_input=True,
            help="Cleartext password string to query the local data store",
            envvar="HIBPDL_PASSWORD",
        ),
    ],
    hash_type: Annotated[
        HashType,
        typer.Option(
            "--hash-type",
            help="Hash type to use from the --data-path",
            case_sensitive=False,
        ),
    ] = HashType.sha1,
):
    """
    Query the local --data-path and return any data that may exist; [bold cyan]query --help[/bold cyan] for more.
    """

    logger.debug(f"Starting command {app_context.command!r} from {os.path.basename(__file__)!r}")

    if app_context.data_path and not os.path.isdir(app_context.data_path):
        logger.error(f"Data path {app_context.data_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    if app_context.metadata_path and not os.path.isdir(app_context.metadata_path):
        logger.warning(f"Metadata path {app_context.metadata_path!r} does not exist, unable to continue")
        raise typer.Exit(1)

    logger.info(f"data-path {app_context.data_path!r}")

    if hash_type == HashType.sha1:
        password_hashed = hashed_sha1(password)
    elif hash_type == HashType.ntlm:
        password_hashed = hashed_ntlm(password)
    else:
        raise HibpDownloaderException(f"Unsupported hash_type {hash_type!r}")

    logger.debug(f"Password {hash_type.value!r} hashed {password_hashed!r}")

    asyncio.run(pwnedpasswords_query_datastore(password_hashed=password_hashed, hash_type=hash_type))


async def pwnedpasswords_query_datastore(password_hashed: str, hash_type: HashType):
    if ENCODING_TYPE in ("gz", "gzip"):
        filename_suffix = "gz"
        decompression_mode = "gzip"
    else:
        raise HibpDownloaderException(f"Unsupported ENCODING_TYPE {ENCODING_TYPE}")

    prefix = password_hashed[0:5]

    result = {
        "hash": password_hashed.upper(),
        "hash_type": hash_type,
        "data_path": app_context.data_path,
        "hibp_count": None,
    }

    try:
        source_data = await load_datafile(
            data_path=os.path.join(app_context.data_path, hash_type),  # type: ignore[arg-type]
            prefix=prefix,
            filename_suffix=filename_suffix,
            decompression_type=decompression_mode,
            prepend_prefix=True,
        )
    except HibpDownloaderException as e:
        result["status"] = str(e)
        return stdout_json(result)

    for line in source_data.split("\n"):
        if password_hashed.upper() in line:
            line_parts = line.split(":")
            if len(line_parts) >= 2:
                result["hibp_count"] = int(line_parts[1])  # type: ignore[assignment]
            result["status"] = "Found"
            return stdout_json(result)

    result["status"] = "Not Found"
    return stdout_json(result)


def stdout_json(data, indent="  "):
    as_string = json.dumps(data, indent=indent, sort_keys=True)
    print(as_string)
    return as_string
