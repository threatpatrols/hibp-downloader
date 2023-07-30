from os import cpu_count, getenv
from sys import argv

from .lib.logger import logger_get
from .models import AppContext

__title__ = "HIBP Downloader"
__version__ = "0.1.2"
__logger_name__ = "hibp-downloader"
__pwnedpasswords_api_url__ = "https://api.pwnedpasswords.com"
__local_cache_ttl_default__ = 86400
__multiprocessing_processes_default__ = cpu_count()
__multiprocessing_prefixes_chunk_size__ = cpu_count() * 2
__approx_gzip_bytes_per_hash__ = 20.674
__logging_info_event_modulus__ = 5

# encoding_type
# The encoded response-content is stored as-is without trying to decode (ie decompress) it into a new encoding type
# for local storage; Because this content is stored as-is, it is more useful to use "gzip" because the command-line
# tools (eg zcat, zgrep) are more readily available than brotli enabled tools when examining the data-store files
__encoding_type__ = "gzip"  # values: [ gzip | br | None ]

__logger_level__ = "info"
if "--debug" in argv or getenv("HIBPDL_DEBUG", "").lower().startswith(("true", "yes", "enable")):
    __logger_level__ = "debug"

__app_profiler__ = False
if "--profiler" in argv or getenv("HIBPDL_PROFILER", "").lower().startswith(("true", "yes", "enable")):
    __app_profiler__ = True

__help_epilog_footer__ = """
        Project: [https://github.com/threatpatrols/hibp-downloader](https://github.com/threatpatrols/hibp-downloader)
"""

logger_get(name=__logger_name__, loglevel=__logger_level__)
app_context = AppContext(debug=True if __logger_level__ == "debug" else False, profiler=__app_profiler__)
