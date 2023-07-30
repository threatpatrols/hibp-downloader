from enum import Enum


class HashType(str, Enum):
    sha1 = "sha1"
    ntlm = "ntlm"
