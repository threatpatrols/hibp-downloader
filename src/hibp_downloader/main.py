#
# Copyright [2022-2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from signal import SIGINT, SIGTERM, signal

from . import LOGGER_NAME
from .lib.app import invoke_app
from .lib.logger import logger_get

logger = logger_get(LOGGER_NAME)


def entrypoint():
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)
    invoke_app()


def signal_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    exit()
