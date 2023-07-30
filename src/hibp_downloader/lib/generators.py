from itertools import islice


def hex_sequence(hex_first: str = "00000", hex_last: str = "fffff", __string_length=5):
    if hex_first.startswith("0x"):
        hex_first = hex_first[2:]

    if hex_last.startswith("0x"):
        hex_last = hex_last[2:]

    hex_first = hex_first.lower()
    hex_last = hex_last.lower()

    value = int(hex_first, 16)
    while value <= int(str(hex_last), 16):
        yield str(hex(value))[2:].zfill(__string_length)
        value += 1


def iterable_chunker(iterable, size=10):
    iterable = iter(iterable)
    while True:
        x = tuple(islice(iterable, size))
        if not x:
            return
        yield x
