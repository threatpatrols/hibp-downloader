import sys

import typer
from typing import Annotated

from .. import HELP_EPILOG_FOOTER, LOGGER_NAME, __title__, __version__, app_context
from ..commands import hibp_download, hibp_generate, hibp_query, hibp_validate
from ..exceptions import HibpDownloaderException
from ..lib.logger import logger_get

logger = logger_get(name=LOGGER_NAME)
app = typer.Typer(
    add_completion=app_context.add_completion,
    no_args_is_help=app_context.no_args_is_help,
    rich_markup_mode="rich",
    epilog=(
        "Environment variables prefixed with HIBPDL_ that match their command-line equivalent may be used; for "
        "example use [bold]HIBPDL_DATA_PATH[/bold] to set the --data-path command option."
        "\n\n---\n"
        f"{HELP_EPILOG_FOOTER}"
    ),
)


def invoke_app() -> None:
    try:
        load_commands()
        app()
    except HibpDownloaderException:
        exit(1)


@app.callback()
def main(
    ctx: typer.Context,
    data_path: Annotated[
        str,
        typer.Option(
            help="Path where a local-copy of the per-prefix HIBP pwned password data fragments are saved.",
            envvar="HIBPDL_DATA_PATH",
            show_envvar=False,
        ),
    ],
    metadata_path: Annotated[
        str,
        typer.Option(
            help="Path where metadata is saved; by default both data and metadata are saved in the same --data-path",
            envvar="HIBPDL_METADATA_PATH",
            show_envvar=False,
            hidden=False if app_context.debug else True,
        ),
    ] = "",
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Set logging to debug-level messages", envvar="HIBPDL_DEBUG", show_envvar=False),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Set logging to fatal-level messages; overrides --debug option",
            envvar="HIBPDL_QUIET",
            show_envvar=False,
        ),
    ] = False,
) -> None:
    """
    [bold]hibp-downloader[/bold] - Efficiently download new pwned password hashes from api.pwnedpasswords.com fast.
    """

    # return early if --help is all we need
    if "--help" in sys.argv:
        return

    # debug is captured at __init__; referenced here for happy linters
    if debug:
        ...

    # quiet is captured at __init__; referenced here for happy linters
    if quiet:
        ...

    # command context
    app_context.command = ctx.invoked_subcommand
    app_context.data_path = data_path
    app_context.metadata_path = metadata_path if metadata_path else data_path

    # start
    logger.info(f"{__title__}: v{__version__}")


def load_commands() -> None:
    app.add_typer(hibp_download.command, name=hibp_download.command_name, rich_help_panel=hibp_download.command_section)
    app.add_typer(hibp_generate.command, name=hibp_generate.command_name, rich_help_panel=hibp_generate.command_section)
    app.add_typer(hibp_query.command, name=hibp_query.command_name, rich_help_panel=hibp_query.command_section)
    app.add_typer(hibp_validate.command, name=hibp_validate.command_name, rich_help_panel=hibp_validate.command_section)
