from uuid import uuid4

from ..helpers.exec_helpers import exec_command
from ..helpers.content_inspect import is_match_error_warn


def test_exec_download():
    prefix = str(uuid4().hex)[0:4]

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}8"
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Queue worker process 0 finished" in stderr.decode()
    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()


def test_exec_download_sha1():
    prefix = str(uuid4().hex)[0:4]
    hash_type = "sha1"

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}8",
        "--hash-type", hash_type,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Queue worker process 0 finished" in stderr.decode()
    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()


def test_exec_download_ntlm():
    prefix = str(uuid4().hex)[0:4]
    hash_type = "ntlm"

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}8",
        "--hash-type", hash_type,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Queue worker process 0 finished" in stderr.decode()
    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()


def test_exec_download_w_metadata_path():
    prefix = str(uuid4().hex)[0:4]

    # fmt: off
    args = [
        "--debug",
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "--metadata-path", f"/tmp/hibp-test-metadata/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}8"
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Queue worker process 0 finished" in stderr.decode()
    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()
