from ..helpers.exec_helpers import exec_command


def test_exec_help_output01():
    # fmt: off
    args = [
        "--help"
    ]
    # fmt: on

    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "--data-path" in stdout.decode()
    assert "--metadata-path" not in stdout.decode()


def test_exec_help_output02():
    # fmt: off
    args = [
        "--debug",
        "--help"
    ]
    # fmt: on

    stdout, stderr, rc = exec_command("hibp-downloader", args=args)

    assert "--data-path" in stdout.decode()
    assert "--metadata-path" in stdout.decode()
