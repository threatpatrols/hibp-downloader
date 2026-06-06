from pathlib import Path
from hibp_downloader.lib.hashing import hashed_sha1, hashed_ntlm, hashed_sha256
from hibp_downloader.lib.generators import hex_sequence, iterable_chunker
from hibp_downloader.lib.filedata import generate_filepath, encoding_type_file_suffix


def test_hashing_sha1():
    # Verify standard SHA1 hashing output (lowercase hex)
    assert hashed_sha1("password") == "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8"
    assert hashed_sha1("") == "da39a3ee5e6b4b0d3255bfef95601890afd80709"


def test_hashing_ntlm():
    # Verify standard NTLM hashing output (lowercase hex)
    # "password" NTLM hash: 8846f7eaee8fb117ad06bdd830b7586c
    assert hashed_ntlm("password") == "8846f7eaee8fb117ad06bdd830b7586c"
    assert hashed_ntlm("") == "31d6cfe0d16ae931b73c59d7e0c089c0"


def test_hashing_sha256():
    # Verify standard SHA-256 hashing output
    assert hashed_sha256(b"password") == "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"


def test_hex_sequence():
    # Test hex sequence generator
    seq = list(hex_sequence("00000", "00005"))
    assert seq == ["00000", "00001", "00002", "00003", "00004", "00005"]

    # Test handling of 0x prefixes
    seq_0x = list(hex_sequence("0x0000a", "0x0000f"))
    assert seq_0x == ["0000a", "0000b", "0000c", "0000d", "0000e", "0000f"]

    # Test single item sequence
    seq_single = list(hex_sequence("abcde", "abcde"))
    assert seq_single == ["abcde"]


def test_iterable_chunker():
    # Test chunking list into fixed size chunks
    items = list(range(10))
    chunks = list(iterable_chunker(items, size=3))
    assert chunks == [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

    # Empty iterable returns empty list of chunks
    assert list(iterable_chunker([], size=5)) == []


def test_generate_filepath():
    # Test path generation structure
    path = generate_filepath(Path("/tmp/data"), "sha1", "0018a", "gz")
    assert path == Path("/tmp/data/sha1/00/18/0018a.gz")

    # Test path generation case sensitivity (should be lowercased)
    path_caps = generate_filepath(Path("/tmp/DATA"), "SHA1", "0018A", "GZ")
    assert path_caps == Path("/tmp/DATA/sha1/00/18/0018a.gz")


def test_encoding_type_file_suffix():
    assert encoding_type_file_suffix("gzip") == "gz"
    assert encoding_type_file_suffix("GZ") == "gz"
    assert encoding_type_file_suffix("identity") == "txt"
    assert encoding_type_file_suffix(None) == "txt"
    assert encoding_type_file_suffix("br") == "br"
