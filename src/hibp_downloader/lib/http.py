import random
from typing import Any, Dict, Optional

import httpx

from hibp_downloader import LOGGER_NAME, __title__, __version__
from hibp_downloader.exceptions import HibpDownloaderException
from hibp_downloader.lib.logger import logger_get

"""
2026-04-05 Fixes and improvements from JimTheFrog and AI: Reused HTTP client instead of creating one per request
- Added a reusable client factory and shared request path in http.py:66, http.py:86, and http.py:129.
- Updated the main response function to accept an optional injected client in http.py:28.
- Retry handling is now iterative in one client context rather than recursive client recreation.
- Reused one event loop per worker process
- Worker now creates one event loop and one HTTP client once, then processes queue chunks on that same loop in hibp_download.py:229.
- The loop/client lifecycle is closed in a finally path for cleanup in hibp_download.py:251.
"""


logger = logger_get(LOGGER_NAME)

__TESTING_RANDOM_ERROR_INJECT_RATE = 0  # manual development testing only


async def httpx_debug_request(request):
    logger.debug(f"request: {request.method} {request.url}")
    if "_content" in vars(request) and request._content:  # noqa
        logger.debug(f"request-data: {request._content}")  # noqa


async def httpx_debug_response(response):
    logger.debug(
        f"response: {response.request.method} {response.request.url} "
        f"{response.status_code=} {response.http_version=} {response.headers=}"
    )


async def httpx_binary_response(
    url,
    etag=None,
    method="GET",
    encoding="gzip",
    timeout=10,
    max_retries=3,
    proxy="",
    verify="",
    debug=False,
    client: Optional[httpx.AsyncClient] = None,
):
    httpx_client = httpx_client_options(
        etag=etag,
        encoding=encoding,
        timeout=timeout,
        proxy=proxy,
        verify=verify,
        debug=debug,
    )

    if client:
        return await _httpx_binary_response_with_client(
            client=client,
            url=url,
            method=method,
            max_retries=max_retries,
        )

    async with httpx.AsyncClient(**httpx_client) as http_client:
        return await _httpx_binary_response_with_client(
            client=http_client,
            url=url,
            method=method,
            max_retries=max_retries,
        )


def httpx_async_client(
    etag=None,
    encoding="gzip",
    timeout=10,
    proxy="",
    verify="",
    debug=False,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        **httpx_client_options(
            etag=etag,
            encoding=encoding,
            timeout=timeout,
            proxy=proxy,
            verify=verify,
            debug=debug,
        )
    )


def httpx_client_options(
    etag=None,
    encoding="gzip",
    timeout=10,
    proxy="",
    verify="",
    debug=False,
) -> Dict[str, Any]:
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

    client_options: Dict[str, Any] = {
        "headers": headers,
        "http2": True,
        "timeout": timeout,
        "follow_redirects": False,
        "trust_env": False,
    }

    if not proxy == "":
        client_options["proxy"] = proxy

    if not verify == "":
        client_options["verify"] = verify

    if event_hooks:
        client_options["event_hooks"] = event_hooks

    return client_options


async def _httpx_binary_response_with_client(
    client: httpx.AsyncClient,
    url,
    method="GET",
    max_retries=3,
):
    original_url = url
    attempt = 0

    if __TESTING_RANDOM_ERROR_INJECT_RATE and __TESTING_RANDOM_ERROR_INJECT_RATE > random.random():
        url = url.replace("http", "BR0KEN")
        logger.warning(f"Testing, creating broken URL {url}")

    while attempt < max_retries:
        attempt += 1
        logger.debug(f"Request attempt {attempt} of {max_retries} for {url!r}")
        request = client.build_request(method=method, url=url)
        response = None
        try:
            response = await client.send(request=request, stream=True)
            setattr(response, "binary", b"".join([part async for part in response.aiter_raw()]))
            await response.aclose()
            return response
        except httpx.HTTPError:
            if response is not None:
                await response.aclose()
            logger.warning(f"Request [{attempt} of {max_retries}] failed for {request.method!r} {url!r}")
            url = original_url
            continue

    raise HibpDownloaderException(f"Request failed after {attempt} retries: {original_url!r}")
