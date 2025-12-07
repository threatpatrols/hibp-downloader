#
# Copyright [2022-2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from . import LOGGER_NAME
from .lib.app import invoke_app
from .lib.logger import logger_get

logger = logger_get(LOGGER_NAME)


def entrypoint():
    invoke_app()
