import os
from uuid import uuid4

from ..helpers.content_inspect import is_match_error_warn
from ..helpers.exec_helpers import exec_command


def test_exec_generate():
    prefix = str(uuid4().hex)[0:4]
    filename = f"/tmp/hibp-test/{prefix}.output"

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
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
        "generate",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
        "--filename", filename,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    if not os.path.isfile(filename):
        raise FileExistsError(f"Unable to locate outout file {filename}")

    stdout, stderr, rc = exec_command("cat", args=[filename])
    assert stderr == b""

    lines = stdout.decode().split("\n")
    assert len(lines) > 500


def test_exec_generate_sha1():
    prefix = str(uuid4().hex)[0:4]
    filename = f"/tmp/hibp-test/{prefix}.output"
    hash_type = "sha1"

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
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
        "generate",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
        "--hash-type", hash_type,
        "--filename", filename,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    if not os.path.isfile(filename):
        raise FileExistsError(f"Unable to locate outout file {filename}")

    stdout, stderr, rc = exec_command("cat", args=[filename])
    assert stderr == b""

    lines = stdout.decode().split("\n")
    assert len(lines) > 500


def test_exec_generate_ntlm():
    prefix = str(uuid4().hex)[0:4]
    filename = f"/tmp/hibp-test/{prefix}.output"
    hash_type = "ntlm"

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
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
        "generate",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
        "--hash-type", hash_type,
        "--filename", filename,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    if not os.path.isfile(filename):
        raise FileExistsError(f"Unable to locate outout file {filename}")

    stdout, stderr, rc = exec_command("cat", args=[filename])
    assert stderr == b""

    lines = stdout.decode().split("\n")
    assert len(lines) > 500


def test_exec_generate_w_metadata_path():
    prefix = str(uuid4().hex)[0:4]
    filename = f"/tmp/hibp-test/{prefix}.output"

    # fmt: off
    args = [
        "--data-path", f"/tmp/hibp-test/{prefix}",
        "--metadata-path", f"/tmp/hibp-test-metadata/{prefix}",
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
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
        "generate",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}4",
        "--filename", filename,
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "hibp-downloader | HIBP Downloader" in stderr.decode()
    if is_match_error_warn(content=stderr.decode(), match_excludes=[]):
        raise AssertionError("ERROR/WARN detected in hibp response")

    if not os.path.isfile(filename):
        raise FileExistsError(f"Unable to locate outout file {filename}")

    stdout, stderr, rc = exec_command("cat", args=[filename])
    assert stderr == b""

    lines = stdout.decode().split("\n")
    assert len(lines) > 500
