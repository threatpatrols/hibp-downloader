import importlib
import os
import sys
import textwrap

import typer
from typing_extensions import Annotated

from .. import __help_epilog_footer__, __logger_name__, __title__, __version__, app_context
from ..exceptions import HibpDownloaderException
from ..lib.logger import logger_get

logger = logger_get(name=__logger_name__)
app = typer.Typer(
    add_completion=app_context.add_completion,
    no_args_is_help=app_context.no_args_is_help,
    rich_markup_mode="rich",
    epilog=textwrap.dedent(
        """
        Environment variables prefixed with HIBPDL_ that match their command-line equivalent may be used; for
        example use [bold]HIBPDL_DATA_PATH[/bold] to set the --data-path command option.
           
           
           
    """
        + __help_epilog_footer__,
    ),
)


def invoke_app():
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
        ),
    ] = "",
    profiler: Annotated[
        bool,
        typer.Option(
            hidden=True, help="Enable the application performance profiler", envvar="HIBPDL_PROFILER", show_envvar=False
        ),
    ] = False,
    debug: Annotated[
        bool, typer.Option(help="Enable debug logging to stderr", envvar="HIBPDL_DEBUG", show_envvar=False)
    ] = False,
):
    """
    [bold]hibp-downloader[/bold] - Efficiently download new data for a local-copy of the pwned password hashes from https://api.pwnedpasswords.com
    """

    # return early if --help is all we need
    if "--help" in sys.argv:
        return

    # debug is captured at __init__; referenced here for happy linters
    if debug:
        ...

    # profiler is captured at __init__; referenced here for happy linters
    if profiler:
        ...

    # command context
    app_context.command = ctx.invoked_subcommand
    app_context.data_path = data_path
    app_context.metadata_path = metadata_path if metadata_path else data_path

    # start
    logger.info(f"{__title__} [v{__version__}]")


def load_commands():
    loader_paths = [os.path.join(os.path.dirname(__file__), "..", "commands")]

    for loader_path in loader_paths:
        loader_path = os.path.realpath(loader_path)
        logger.debug(f"Loading command modules from {loader_path!r}")

        if loader_path not in sys.path:
            sys.path.append(loader_path)

        for filename in [f for f in os.listdir(loader_path) if os.path.isfile(os.path.join(loader_path, f))]:
            if filename.startswith("_"):
                continue
            module_name = filename.split(".")[0]

            try:
                module = importlib.import_module(module_name)
            except Exception as e:
                raise HibpDownloaderException(f"Failed importing command-module {module_name}", detail=e)

            logger.debug(f"Loaded command module {module_name!r} from {os.path.realpath(module.__file__)!r}")
            if loader_path not in module.__file__:
                logger.warning(
                    f"Command module {module_name!r} NOT loaded from {loader_path!r}; "
                    f"check for command-module filename collisions and consider renaming files."
                )

            for registered_group in app.registered_groups:
                if registered_group.name == module.command_name:
                    raise HibpDownloaderException(
                        f"Command {module.command_name!r} from {os.path.realpath(module.__file__)!r}"
                        "overrides already loaded command; consider changing the 'command_name' value."
                    )

            app.add_typer(module.command, name=module.command_name, rich_help_panel=module.command_section)
