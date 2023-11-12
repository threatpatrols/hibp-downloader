import hashlib

from .md4 import MD4


def hashed_sha1(value: str):
    return hashlib.sha1(value.encode()).hexdigest().lower()


def hashed_ntlm(value: str):
    return MD4(value.encode("utf-16le")).hexdigest().lower()
