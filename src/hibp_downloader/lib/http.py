import httpx

from hibp_downloader import __logger_name__, __title__, __version__
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.logger import logger_get

logger = logger_get(__logger_name__)


async def httpx_debug_request(request):
    logger.debug(f"request: {request.method} {request.url}")
    if "_content" in vars(request) and request._content:  # noqa
        logger.debug(f"request-data: {request._content}")  # noqa


async def httpx_debug_response(response):
    logger.debug(
        f"response: {response.request.method} {response.request.url} "
        f"{response.status_code=} {response.http_version=} {response.headers=}"
    )


async def httpx_binary_response(url, etag=None, method="GET", encoding="gzip", debug=False):
    event_hooks = {}
    if debug:
        event_hooks["request"] = [httpx_debug_request]
        event_hooks["response"] = [httpx_debug_response]

    headers = {"User-Agent": f"{__title__}/{__version__}"}

    if encoding:
        headers["Accept-Encoding"] = encoding
    else:
        headers["Accept-Encoding"] = "identity"

    if etag:
        headers["If-None-Match"] = etag

    httpx_client = {
        "headers": headers,
        "http2": True,
        "timeout": 5,
        "follow_redirects": False,
        "trust_env": False,
    }

    if event_hooks:
        httpx_client["event_hooks"] = event_hooks

    async with httpx.AsyncClient(**httpx_client) as client:
        request = client.build_request(method=method, url=url)
        try:
            response = await client.send(request=request, stream=True)
        except (httpx.ConnectError, httpx.RemoteProtocolError):
            raise HibpDownloaderException(f"Unable to establish connection {url}")

        response.binary = b"".join([part async for part in response.aiter_raw()])

    return response
