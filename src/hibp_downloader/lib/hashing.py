import hashlib

from .md4 import MD4


def hashed_sha1(value: str) -> str:
    # usedforsecurity=False: hash is used for HIBP prefix lookup, not cryptography.
    # Prevents errors on FIPS-enabled builds (parameter available from Python 3.9+,
    # which is below our current minimum of 3.10).
    return hashlib.sha1(value.encode(), usedforsecurity=False).hexdigest().lower()


def hashed_ntlm(value: str) -> str:
    return MD4(value.encode("utf-16le")).hexdigest().lower()


def hashed_sha256(data: bytes) -> str:
    """Return SHA-256 hex digest of raw bytes.

    usedforsecurity=False: hash is used for content-change detection only.
    """
    return hashlib.sha256(data, usedforsecurity=False).hexdigest()
