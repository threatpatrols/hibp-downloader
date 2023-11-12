#
# Copyright [2022-2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from signal import SIGINT, signal

from . import LOGGER_NAME
from .lib.app import invoke_app
from .lib.logger import logger_get

logger = logger_get(LOGGER_NAME)


def entrypoint():
    invoke_app()


def sigint_handler(__signal_received, __frame):
    print("SIGINT received, exiting.")
    exit()


signal(SIGINT, sigint_handler)
