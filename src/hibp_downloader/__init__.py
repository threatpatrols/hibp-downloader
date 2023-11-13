#
# Copyright [2023] Threat Patrols Pty Ltd (https://www.threatpatrols.com)
#

from os import cpu_count, getenv
from sys import argv

from .lib.logger import logger_get
from .models import AppContext

__title__ = "HIBP Downloader"
__version__ = "0.2.1"

LOGGER_NAME = "hibp-downloader"
PWNEDPASSWORDS_API_URL = "https://api.pwnedpasswords.com"
LOCAL_CACHE_TTL_DEFAULT = 12 * 3600
MULTIPROCESSING_PROCESSES_DEFAULT = int(cpu_count() if cpu_count() else 4)  # type: ignore[arg-type]
MULTIPROCESSING_PREFIXES_CHUNK_SIZE = 10
APPROX_GZIP_BYTES_PER_HASH = 20.674
LOGGING_INFO_EVENT_MODULUS = 25

# encoding_type
# The encoded response-content is stored as-is without trying to decode (ie decompress) it into a new encoding type
# for local storage; Because this content is stored as-is, it is more useful to use "gzip" because the command-line
# tools (eg zcat, zgrep) are more readily available than brotli enabled tools when examining the data-store files
ENCODING_TYPE = "gzip"  # values: [ gzip | br | None ]

LOGGER_LEVEL = "info"
if "--debug" in argv or getenv("HIBPDL_DEBUG", "").lower().startswith(("true", "yes", "enable")):
    LOGGER_LEVEL = "debug"

if "--quiet" in argv or getenv("HIBPDL_QUIET", "").lower().startswith(("true", "yes", "enable")):
    LOGGER_LEVEL = "fatal"

HELP_EPILOG_FOOTER = f"""
{__title__} v{__version__}

Docs: [hibp-downloader.readthedocs.io](https://hibp-downloader.readthedocs.io)

Project: [github.com/threatpatrols/hibp-downloader](https://github.com/threatpatrols/hibp-downloader)
"""

logger_get(name=LOGGER_NAME, loglevel=LOGGER_LEVEL)
app_context = AppContext(debug=True if LOGGER_LEVEL == "debug" else False)
