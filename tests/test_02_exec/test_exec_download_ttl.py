from uuid import uuid4

from ..helpers.exec_helpers import exec_command
from ..helpers.content_inspect import is_match_error_warn


def test_exec_download_within_local_ttl():
    prefix = str(uuid4().hex)[0:4]

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}3"
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Queue worker process 0 finished" in stderr.decode()
    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}7"
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert f"Skipping {prefix}0; local-cache has" in stderr.decode()
    assert f"Skipping {prefix}1; local-cache has" in stderr.decode()
    assert f"Skipping {prefix}2; local-cache has" in stderr.decode()
    assert f"Skipping {prefix}3; local-cache has" in stderr.decode()

    assert f"Skipping {prefix}4; local-cache has" not in stderr.decode()
    assert f"Skipping {prefix}5; local-cache has" not in stderr.decode()
    assert f"Skipping {prefix}6; local-cache has" not in stderr.decode()
    assert f"Skipping {prefix}7; local-cache has" not in stderr.decode()
