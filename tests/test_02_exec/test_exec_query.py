import json

from ..helpers.content_inspect import is_match_error_warn
from ..helpers.exec_helpers import exec_command


def test_exec_query_w_metadata():
    password = "foobar"
    password_hash = "8843D7F92416211DE9EBB963FF4CE28125932878"
    prefix = password_hash[0:5]

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "--metadata-path", f"/tmp/hibp-test-metadata/{prefix}",
        "download",
        "--first-hash", prefix,
        "--last-hash", prefix,
    ]
    # fmt: on

    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "--metadata-path", f"/tmp/hibp-test-metadata/{prefix}",
        "query",
        "--password", password,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    data = json.loads(stdout)
    assert data.get("status") == "Found"


def test_exec_query_sha1():
    password = "foobar"
    password_hash = "8843D7F92416211DE9EBB963FF4CE28125932878"
    hash_type = "sha1"
    prefix = password_hash[0:5]

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", prefix,
        "--last-hash", prefix,
        "--hash-type", hash_type,
    ]
    # fmt: on

    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "query",
        "--password", password,
        "--hash-type", hash_type,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    data = json.loads(stdout)
    assert data.get("status") == "Found"


def test_exec_query_ntlm():
    password = "foobar"
    password_hash = "BAAC3929FABC9E6DCD32421BA94A84D4"
    hash_type = "ntlm"
    prefix = password_hash[0:5]

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", prefix,
        "--last-hash", prefix,
        "--hash-type", hash_type,
    ]
    # fmt: on

    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=["does not exist, creating it now"]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    assert "hibp-downloader | Finished in " in stderr.decode()
    assert "hibp-downloader | Done" in stderr.decode()

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "query",
        "--password", password,
        "--hash-type", hash_type,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    data = json.loads(stdout)
    assert data.get("status") == "Found"
