
import random
from typing import Any, Callable

import httpx

from hibp_downloader import LOGGER_NAME, __title__, __version__
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.logger import logger_get

logger = logger_get(LOGGER_NAME)

__TESTING_RANDOM_ERROR_INJECT_RATE = 0  # manual development testing only


async def httpx_debug_request(request: httpx.Request) -> None:
    logger.debug(f"request: {request.method} {request.url}")
    if "_content" in vars(request) and request._content:  # noqa
        logger.debug(f"request-data: {request._content!r}")  # noqa


async def httpx_debug_response(response: httpx.Response) -> None:
    logger.debug(
        f"response: {response.request.method} {response.request.url} "
        f"{response.status_code=} {response.http_version=} {response.headers=}"
    )


async def httpx_binary_response(
    url: str,
    etag: str | None = None,
    method: str = "GET",
    encoding: str | None = "gzip",
    timeout: int | float = 10,
    max_retries: int = 3,
    proxy: str = "",
    verify: str | bool = "",
    debug: bool = False,
) -> Any:
    event_hooks: dict[str, list[Callable[..., Any]]] = {}
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

    httpx_client: dict[str, Any] = {
        "headers": headers,
        "http2": True,
        "timeout": timeout,
        "follow_redirects": False,
        "trust_env": False,
    }

    if not proxy == "":
        httpx_client["proxy"] = proxy

    if not verify == "":
        httpx_client["verify"] = verify

    if event_hooks:
        httpx_client["event_hooks"] = event_hooks

    if __TESTING_RANDOM_ERROR_INJECT_RATE and __TESTING_RANDOM_ERROR_INJECT_RATE > random.random():
        url = url.replace("http", "BR0KEN")
        logger.warning(f"Testing, creating broken URL {url}")

    async with httpx.AsyncClient(**httpx_client) as client:
        for attempt in range(1, max_retries + 1):
            logger.debug(f"Request attempt {attempt} of {max_retries} for {url!r}")
            request = client.build_request(method=method, url=url)
            try:
                response = await client.send(request=request, stream=True)
                try:
                    response.binary = b"".join([part async for part in response.aiter_raw()])  # type: ignore[attr-defined]
                    return response
                finally:
                    await response.aclose()
            except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPError):
                logger.warning(f"Request [{attempt} of {max_retries}] failed for {request.method!r} {url!r}")
                if attempt >= max_retries:
                    raise HibpDownloaderException(f"Request failed after {attempt} retries: {url!r}")
                if "BR0KEN" in url:
                    url = url.replace("BR0KEN", "http")

    raise HibpDownloaderException(f"Request failed after {max_retries} retries: {url!r}")
