import gzip
from hibp_downloader.lib.filedata import is_valid_gzip, is_valid_identity, verify_binary_encoding


def test_is_valid_gzip():
    # Valid gzip data
    valid_data = gzip.compress(b"some test password range data")
    assert is_valid_gzip(valid_data) is True

    # Invalid: empty
    assert is_valid_gzip(b"") is False

    # Invalid: too short
    assert is_valid_gzip(b"\x1f") is False

    # Invalid: wrong magic bytes
    assert is_valid_gzip(b"\x1f\x8c" + valid_data[2:]) is False

    # Invalid: correct magic but truncated/corrupt body
    assert is_valid_gzip(b"\x1f\x8b\x08\x00") is False


def test_is_valid_identity():
    # Valid identity data (plain text password list)
    valid_text = b"00180800000000000000000000000000:3\n00180800000000000000000000000001:5"
    assert is_valid_identity(valid_text) is True

    # Invalid: empty
    assert is_valid_identity(b"") is False

    # Invalid: non-ASCII/UTF-8
    assert is_valid_identity(b"\xff\xfe\x00\x00") is False

    # Invalid: wrong format (no colon)
    assert is_valid_identity(b"001808000000000000000000000000003") is False

    # Invalid: wrong format (non-integer count)
    assert is_valid_identity(b"00180800000000000000000000000000:abc") is False

    # Invalid: wrong format (non-hex prefix/suffix)
    assert is_valid_identity(b"xyzxyzxyzxyzxyzxyzxyzxyzxyzxyzxyz:3") is False


def test_verify_binary_encoding():
    valid_gzip = gzip.compress(b"some test password range data")
    valid_text = b"00180800000000000000000000000000:3"

    assert verify_binary_encoding(valid_gzip, "gzip") is True
    assert verify_binary_encoding(valid_gzip, "gz") is True
    assert verify_binary_encoding(b"corrupted", "gzip") is False

    assert verify_binary_encoding(valid_text, "identity") is True
    assert verify_binary_encoding(valid_text, None) is True
    assert verify_binary_encoding(b"corrupted", "identity") is False

    # Unknown encodings fall back to True
    assert verify_binary_encoding(b"anything", "deflate") is True
