import os
import shutil
from pathlib import Path
from uuid import uuid4

from ..helpers.content_inspect import is_match_error_warn
from ..helpers.exec_helpers import exec_command


def test_exec_validate():
    prefix = str(uuid4().hex)[0:4]
    data_path = f"/tmp/hibp-test/{prefix}"

    # 1. Download a small range of hashes (6 prefixes: e.g. e5b90 to e5b95)
    # fmt: off
    args_download = [
        "--debug",
        "--data-path", data_path,
        "download",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}5"
    ]
    # fmt: on
    stdout, stderr, rc = exec_command("hibp-downloader", args=args_download)
    assert rc == 0
    assert "hibp-downloader | Done" in stderr.decode()

    # Verify that files were created
    path_obj = Path(data_path)
    hash_dir = path_obj / "sha1" / prefix[0:2] / prefix[2:4]
    assert hash_dir.is_dir()

    datafiles = list(hash_dir.glob(f"{prefix}*.gz"))
    metafiles = list(hash_dir.glob(f"{prefix}*.meta"))
    assert len(datafiles) == 6
    assert len(metafiles) == 6

    # 2. Run validate command on the valid data
    # fmt: off
    args_validate_1 = [
        "--debug",
        "--data-path", data_path,
        "validate",
        "--first-hash", f"{prefix}0",
        "--last-hash", f"{prefix}5"
    ]
    # fmt: on
    stdout_val1, stderr_val1, rc_val1 = exec_command("hibp-downloader", args=args_validate_1)
    assert rc_val1 == 0
    assert "Checked prefixes:   6" in stderr_val1.decode()
    assert "Valid datafiles:    6" in stderr_val1.decode()
    assert "Missing datafiles:  0" in stderr_val1.decode()
    assert "Corrupted/deleted:  0" in stderr_val1.decode()

    # 3. Corrupt one datafile manually
    corrupt_prefix = f"{prefix}2"
    corrupt_data_path = hash_dir / f"{corrupt_prefix}.gz"
    corrupt_meta_path = hash_dir / f"{corrupt_prefix}.meta"
    assert corrupt_data_path.exists()
    assert corrupt_meta_path.exists()

    with open(corrupt_data_path, "wb") as f:
        f.write(b"NOT A VALID GZIP FILE CONTENT")

    # 4. Make an orphaned metadata file manually by deleting its datafile
    orphan_prefix = f"{prefix}4"
    orphan_data_path = hash_dir / f"{orphan_prefix}.gz"
    orphan_meta_path = hash_dir / f"{orphan_prefix}.meta"
    assert orphan_data_path.exists()
    assert orphan_meta_path.exists()
    orphan_data_path.unlink()  # delete datafile only

    # 5. Run validate command to detect and clean up
    stdout_val2, stderr_val2, rc_val2 = exec_command("hibp-downloader", args=args_validate_1)
    assert rc_val2 == 0

    stderr_output = stderr_val2.decode()
    assert "Checked prefixes:   6" in stderr_output
    assert "Valid datafiles:    4" in stderr_output
    assert "Missing datafiles:  1" in stderr_output
    assert "Corrupted/deleted:  1" in stderr_output

    # Check that cleanup actually occurred
    assert not corrupt_data_path.exists()
    assert not corrupt_meta_path.exists()
    assert not orphan_meta_path.exists()

    # 6. Run validate command again - should now report 4 valid, 2 missing, 0 corrupted
    stdout_val3, stderr_val3, rc_val3 = exec_command("hibp-downloader", args=args_validate_1)
    assert rc_val3 == 0

    stderr_output3 = stderr_val3.decode()
    assert "Checked prefixes:   6" in stderr_output3
    assert "Valid datafiles:    4" in stderr_output3
    assert "Missing datafiles:  2" in stderr_output3
    assert "Corrupted/deleted:  0" in stderr_output3

    # Clean up the test directory
    shutil.rmtree(data_path, ignore_errors=True)
