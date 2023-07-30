#
# Copyright [2022-2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

import atexit
from os import getenv
from signal import SIGINT, signal
from sys import argv

from typer import Exit as TyperExit

from . import __logger_name__, app_context
from .lib.app import invoke_app
from .lib.logger import logger_get

logger = logger_get(__logger_name__)
profiler = None  # type: ignore


def entrypoint():
    if "--profiler" in argv or getenv("HIBPDL_PROFILER", "").lower().startswith(("true", "yes", "enable")):
        logger.warning("pyinstrument.Profiler enabled")
        from pyinstrument import Profiler

        global profiler
        profiler = Profiler()
        profiler.start()
        app_context.profiler = True

    invoke_app()


def sigint_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    raise TyperExit(code=1)


def exit_handler():
    if app_context.profiler:
        global profiler
        profiler.stop()
        output_filename = "profiler.html"
        output_html = profiler.output_html()
        with open(output_filename, "w") as f:
            f.write(output_html)
        logger.warning(f"pyinstrument.Profiler report written to {output_filename!r}")


signal(SIGINT, sigint_handler)
atexit.register(exit_handler)
