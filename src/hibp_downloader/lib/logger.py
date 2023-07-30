import logging
from typing import Union

__logging_format__ = "%(asctime)s | %(levelname)s | __name__ | %(message)s"
__logging_date_format__ = "%Y-%m-%dT%H:%M:%S%z"


class LoggerNone:
    def __getattr__(self, _):
        def empty(*_):
            pass

        return empty


def logger_get(name: Union[str, None], loglevel="warning", logfile=None) -> Union[logging.Logger, LoggerNone]:
    if name is None:
        return LoggerNone()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logging_level = __logger_level_int(loglevel)
    logger.setLevel(logging_level)

    logging_formatter = LoggingFormatterWrapper(
        fmt=__logging_format__, datefmt=__logging_date_format__, name=name, colorize_levelname=True
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging_level)
    console_handler.setFormatter(logging_formatter)

    logger.addHandler(console_handler)

    try:
        if logfile:
            file_handler = logging.FileHandler(filename=logfile)
            file_handler.setLevel(logging_level)
            file_handler.setFormatter(logging_formatter)
            logger.addHandler(file_handler)
    except (FileNotFoundError, PermissionError):
        raise PermissionError(f"Unable to write to logfile at: {logfile}")

    return logger


def logger_setlevel(name: str, loglevel: str) -> None:
    logger = logging.getLogger(name)
    logging_level = __logger_level_int(loglevel)

    logger.setLevel(logging_level)
    for handler in logger.handlers:
        handler.setLevel(logging_level)

    return None


def __logger_level_int(loglevel) -> int:
    logging_level = logging.getLevelName(loglevel.upper())
    try:
        int(logging_level)
    except ValueError:
        raise ValueError(f"Unknown loglevel requested: {loglevel}")

    return int(logging_level)


class LoggingFormatterWrapper(logging.Formatter):
    colorize_levelname: bool = False

    def __init__(self, **kwargs):
        if "name" in kwargs:
            kwargs["fmt"] = kwargs.get("fmt", "").replace("__name__", kwargs["name"])
            del kwargs["name"]
        if "colorize_levelname" in kwargs:
            self.colorize_levelname = True
            del kwargs["colorize_levelname"]
        logging.Formatter.__init__(self, **kwargs)

    def format(self, record):
        if self.colorize_levelname:
            return self.colorized_levelname_format(record)
        return logging.Formatter.format(self, record)

    def colorized_levelname_format(self, record):
        levelname = record.levelname.upper()

        if levelname == "CRITICAL":
            color_code = "\x1b[1;41m"  # white-on-red
        elif levelname == "ERROR":
            color_code = "\x1b[1;31m"  # red
        elif levelname in ("WARNING", "WARN"):
            color_code = "\x1b[1;33m"  # yellow
        elif levelname == "INFO":
            color_code = "\x1b[1;36m"  # cyan
        elif levelname == "DEBUG":
            color_code = "\x1b[1;37m"  # white
        else:
            color_code = None

        if color_code:
            color_reset = "\x1b[0m"  # reset
            record.levelname = "{}{}{}".format(color_code, record.levelname, color_reset)

        return logging.Formatter.format(self, record)
