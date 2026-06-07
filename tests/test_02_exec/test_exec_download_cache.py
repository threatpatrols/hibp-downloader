"""
Regression tests for cache correctness: local TTL, ETag (304 Not Modified), and missing-data-file recovery.

These tests guard against the bugs fixed in:
  - http.py:    ETag not passed per-request when using a shared httpx.AsyncClient
  - filedata.py: load_metadata() not checking whether the data file actually exists on disk
  - hibp_download.py: metadata file overwritten even on 304 (resetting server_timestamp / TTL clock)

Each test downloads a small prefix range, then performs a second operation and inspects the
debug log output and filesystem state for the expected cache-source behaviour:

  lc = local-cache TTL hit     (no API request made; "Skipping" debug line emitted)
  et = ETag match / 304        (API request made, no data transferred; data file mtime unchanged)
  rc = remote CDN cache hit    (API request + data from CDN; data file rewritten)
  ro = remote origin source    (API request + data from origin; data file rewritten)

Note: the periodic stats log line (source=[lc:N et:N ...]) only fires every 25 queue items,
so these tests use per-prefix debug messages and file-system state instead of that summary line.
"""

import os
from uuid import uuid4

from ..helpers.content_inspect import is_match_error_warn
from ..helpers.exec_helpers import exec_command


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_args(prefix: str, data_path: str, first_suffix: str = "0", last_suffix: str = "3") -> list[str]:
    """Return a standard set of CLI args for a small download range."""
    return [
        "--debug",
        "--data-path",
        data_path,
        "download",
        "--first-hash",
        f"{prefix}{first_suffix}",
        "--last-hash",
        f"{prefix}{last_suffix}",
    ]


def _run(args: list[str], timeout: int = 60) -> tuple[bytes, bytes, int]:
    return exec_command("hibp-downloader", args=args, timeout=timeout)


def _assert_clean_run(stderr: str, *, allow_creating: bool = True) -> None:
    """Assert no unexpected errors/warnings in a download run."""
    excludes = ["does not exist, creating it now"] if allow_creating else []
    if is_match_error_warn(content=stderr, match_excludes=excludes):
        raise AssertionError(f"Unexpected ERROR/WARN in output:\n{stderr}")
    assert "hibp-downloader | Done" in stderr


def _data_file_path(data_path: str, hash_type: str, prefix: str) -> str:
    """Reconstruct the on-disk path for a prefix data file."""
    return os.path.join(
        data_path,
        hash_type.lower(),
        prefix[0:2].lower(),
        prefix[2:4].lower(),
        f"{prefix}.gz".lower(),
    )


def _meta_file_path(data_path: str, hash_type: str, prefix: str) -> str:
    """Reconstruct the on-disk path for a prefix metadata file."""
    return os.path.join(
        data_path,
        hash_type.lower(),
        prefix[0:2].lower(),
        prefix[2:4].lower(),
        f"{prefix}.meta".lower(),
    )


def _mtimes(paths: list[str]) -> dict[str, float]:
    """Return a {path: mtime} dict for all given paths that exist."""
    return {p: os.path.getmtime(p) for p in paths if os.path.isfile(p)}


# ---------------------------------------------------------------------------
# Test: ETag / 304 Not Modified
# ---------------------------------------------------------------------------


def test_exec_download_etag_respected():
    """
    Second download with --local-cache-ttl=0 must use ETags (304) rather than
    re-fetching full data.  Confirms Bug 1 fix: per-request If-None-Match header.

    Observable evidence:
    - "Skipping" debug lines must NOT appear (TTL is bypassed, so ETag requests go out)
    - Data file mtimes must be unchanged (304 means no new content written)
    - The run must complete cleanly (no errors)
    """
    prefix = str(uuid4().hex)[0:4]
    data_path = f"/tmp/hibp-test/{prefix}"
    test_prefixes = [f"{prefix}{s}" for s in ("0", "1", "2", "3")]

    # First download — populates data files and .meta files
    _, stderr, rc = _run(_base_args(prefix, data_path))
    assert rc == 0
    _assert_clean_run(stderr.decode())

    # Record data-file mtimes after the first download
    data_paths = [_data_file_path(data_path, "sha1", p) for p in test_prefixes]
    for path in data_paths:
        assert os.path.isfile(path), f"Expected data file to exist after first download: {path}"
    mtimes_before = _mtimes(data_paths)

    # Second download — TTL bypassed via --local-cache-ttl=0, so ETag conditional
    # requests must be sent.  Server should return 304 (ETags match) → no file rewrite.
    args = _base_args(prefix, data_path) + ["--local-cache-ttl", "0"]
    _, stderr2, rc2 = _run(args)
    assert rc2 == 0
    _assert_clean_run(stderr2.decode(), allow_creating=False)

    stderr2_str = stderr2.decode()

    # "Skipping" must NOT appear — TTL is 0 so we go to the network (with ETags)
    for p in test_prefixes:
        assert f"Skipping {p}; local-cache has" not in stderr2_str, (
            f"Prefix {p} was incorrectly served from local TTL cache despite --local-cache-ttl=0. "
            f"The TTL bypass is not working."
        )

    # Data files must NOT have been rewritten (304 = no new content)
    mtimes_after = _mtimes(data_paths)
    for path in data_paths:
        assert mtimes_after[path] == mtimes_before[path], (
            f"Data file {path} was rewritten on the second run despite TTL=0. "
            f"This means a full download occurred instead of a 304 ETag match — "
            f"the If-None-Match header is not being sent correctly on the second request."
        )


# ---------------------------------------------------------------------------
# Test: local TTL cache skips the API entirely
# ---------------------------------------------------------------------------


def test_exec_download_local_ttl_skips_api():
    """
    Second download within the default TTL must serve all previously-downloaded
    prefixes from the local cache without making any API requests for them.
    Confirms the TTL-skip path sets data_source = local_source_ttl_cache.

    Observable evidence:
    - "Skipping {prefix}; local-cache has" debug line for every cached prefix
    - Data file mtimes unchanged (no rewrite when served from TTL cache)
    """
    prefix = str(uuid4().hex)[0:4]
    data_path = f"/tmp/hibp-test/{prefix}"
    test_prefixes = [f"{prefix}{s}" for s in ("0", "1", "2", "3")]

    # First download — 4 prefixes (0–3)
    _, stderr, rc = _run(_base_args(prefix, data_path, first_suffix="0", last_suffix="3"))
    assert rc == 0
    _assert_clean_run(stderr.decode())

    # Record data-file mtimes
    data_paths = [_data_file_path(data_path, "sha1", p) for p in test_prefixes]
    for path in data_paths:
        assert os.path.isfile(path), f"Expected data file to exist after first download: {path}"
    mtimes_before = _mtimes(data_paths)

    # Second download — same 4 prefixes; default TTL is 12h so all should be lc hits
    _, stderr2, rc2 = _run(_base_args(prefix, data_path, first_suffix="0", last_suffix="3"))
    assert rc2 == 0
    _assert_clean_run(stderr2.decode(), allow_creating=False)

    stderr2_str = stderr2.decode()

    # Every prefix must show the TTL-skip debug message
    for p in test_prefixes:
        assert f"Skipping {p}; local-cache has" in stderr2_str, (
            f"Expected 'Skipping {p}; local-cache has' in debug output — "
            f"prefix was not served from the local TTL cache."
        )

    # Data files must be untouched
    mtimes_after = _mtimes(data_paths)
    for path in data_paths:
        assert mtimes_after[path] == mtimes_before[path], (
            f"Data file {path} was rewritten during a TTL-cache hit — "
            f"the local cache skip is not preventing file writes."
        )


# ---------------------------------------------------------------------------
# Test: metadata file NOT overwritten on 304 (TTL clock preserved)
# ---------------------------------------------------------------------------


def test_exec_download_metadata_not_overwritten_on_etag_match():
    """
    When a 304 Not Modified is received, the .meta file must NOT be rewritten.
    Overwriting it would reset server_timestamp, which defeats the TTL cache on
    the next run.  Confirms Bug 2 fix: etag-match excluded from metadata save.

    Observable evidence:
    - .meta file mtime is unchanged after a TTL=0 second run (304 path)
    - A third run within default TTL correctly serves from the local TTL cache
    """
    prefix = str(uuid4().hex)[0:4]
    data_path = f"/tmp/hibp-test/{prefix}"
    test_prefixes = [f"{prefix}{s}" for s in ("0", "1", "2", "3")]

    # First download — write data + metadata
    _, stderr, rc = _run(_base_args(prefix, data_path))
    assert rc == 0
    _assert_clean_run(stderr.decode())

    # Collect .meta mtimes and verify they exist
    meta_paths = [_meta_file_path(data_path, "sha1", p) for p in test_prefixes]
    for path in meta_paths:
        assert os.path.isfile(path), f"Expected metadata file to exist after first download: {path}"
    meta_mtimes_before = _mtimes(meta_paths)

    # Second download with TTL=0 — should trigger ETag requests → 304 responses
    args = _base_args(prefix, data_path) + ["--local-cache-ttl", "0"]
    _, stderr2, rc2 = _run(args)
    assert rc2 == 0
    _assert_clean_run(stderr2.decode(), allow_creating=False)

    # .meta files must NOT have been rewritten on 304
    meta_mtimes_after = _mtimes(meta_paths)
    for path in meta_paths:
        assert meta_mtimes_after[path] == meta_mtimes_before[path], (
            f"Metadata file {path} was rewritten after a 304 ETag match. "
            f"This resets server_timestamp and breaks the TTL cache on subsequent runs."
        )

    # Third download — must be served from TTL cache (server_timestamp was preserved)
    _, stderr3, rc3 = _run(_base_args(prefix, data_path, first_suffix="0", last_suffix="3"))
    assert rc3 == 0
    _assert_clean_run(stderr3.decode(), allow_creating=False)

    stderr3_str = stderr3.decode()
    for p in test_prefixes:
        assert f"Skipping {p}; local-cache has" in stderr3_str, (
            f"Prefix {p} was NOT served from TTL cache on the third run. "
            f"This suggests the .meta file's server_timestamp was reset by the 304 response "
            f"on the second run, causing the TTL clock to restart."
        )


# ---------------------------------------------------------------------------
# Test: deleted data file triggers re-download (not silently skipped)
# ---------------------------------------------------------------------------


def test_exec_download_missing_datafile_triggers_redownload():
    """
    If a .gz data file is deleted, the next download must re-fetch it even if
    the corresponding .meta file still exists (and is within TTL).
    Confirms Bug 3 fix: load_metadata() returns empty PrefixMetadata when
    the data file is absent, forcing a full re-download without using cached ETags.

    Observable evidence:
    - Deleted prefixes must NOT show "Skipping" (they are re-downloaded)
    - Intact prefixes MUST show "Skipping" (TTL still valid, files present)
    - Deleted data files are recreated on disk after the second run
    """
    prefix = str(uuid4().hex)[0:4]
    data_path = f"/tmp/hibp-test/{prefix}"

    deleted_prefixes = [f"{prefix}0", f"{prefix}2"]
    intact_prefixes = [f"{prefix}1", f"{prefix}3"]

    # First download — 4 prefixes
    _, stderr, rc = _run(_base_args(prefix, data_path, first_suffix="0", last_suffix="3"))
    assert rc == 0
    _assert_clean_run(stderr.decode())

    # Verify data files exist, then delete two of them
    for p in deleted_prefixes:
        path = _data_file_path(data_path, "sha1", p)
        assert os.path.isfile(path), f"Expected data file at {path} after first download"
        os.remove(path)
        assert not os.path.isfile(path), f"Failed to delete data file {path}"

    # Second download over the same range — within default TTL but missing files
    _, stderr2, rc2 = _run(_base_args(prefix, data_path, first_suffix="0", last_suffix="3"))
    assert rc2 == 0
    _assert_clean_run(stderr2.decode(), allow_creating=False)

    stderr2_str = stderr2.decode()

    # Deleted prefixes must NOT be skipped (they must be re-downloaded)
    for p in deleted_prefixes:
        assert f"Skipping {p}; local-cache has" not in stderr2_str, (
            f"Prefix {p} was incorrectly served from the local TTL cache despite its data file "
            f"being deleted. The missing-file detection in load_metadata() is not working."
        )

    # Intact prefixes MUST be served from TTL cache (files are present and TTL is valid)
    for p in intact_prefixes:
        assert f"Skipping {p}; local-cache has" in stderr2_str, (
            f"Prefix {p} should have been served from the local TTL cache (data file intact, "
            f"within TTL), but it was re-downloaded."
        )

    # Deleted files must have been recreated
    for p in deleted_prefixes:
        path = _data_file_path(data_path, "sha1", p)
        assert os.path.isfile(path), (
            f"Data file {path} was not recreated after being deleted — the re-download did not produce a file."
        )
        assert os.path.getsize(path) > 0, f"Data file {path} was recreated but is empty."
