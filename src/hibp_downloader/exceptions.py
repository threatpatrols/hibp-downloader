#
# Copyright [2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from . import LOGGER_NAME, logger_get

logger = logger_get(LOGGER_NAME)


class HibpDownloaderBaseException(Exception):
    def __init__(self, *args, **kwargs):
        log_message = " ".join([str(x) for x in args]).strip()
        if log_message:
            logger.error(f"{log_message}")
        if "detail" in kwargs:
            logger.error(f"{kwargs['detail']}".strip())
        super().__init__(*args)


class HibpDownloaderException(HibpDownloaderBaseException):
    pass
