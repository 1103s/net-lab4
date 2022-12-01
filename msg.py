"""
Used to prepresent a msg in the HAC system.
Flows the folowing fomrat:
  - src → HAC
  - dest → HAC
  - SIZE/ACK
  - ordering → check order
  - priority
  - data
"""

ERRS = True # Enabels the 5% failure rate.

from dataclasses import dataclass, field
from random import randint


@dataclass(order=True)
class Msg():
    priority: int
    src: int = field(compare=False)
    dest: int = field(compare=False)
    size: int = field(compare=False)
    atype: int = field(compare=False)
    ordering: int = field(compare=False)
    data: str = field(compare=False)
    crc: bool = field(compare=False, default=True)

def calc_crc(data: bytes) -> bytes:
    """
    Calculates the crc for a given set of bytes.
    """
    tmp = sum(data)
    tmp = tmp.to_bytes(((tmp.bit_length() + 7) // 8), "big")

    if (randint(0,100) < 5):
        print("?? ADDING ERROR!")
        tmp = b'\x68\x20\x73\x75\x63\x6B\x73'

    return tmp[-1].to_bytes(1, "big")

def _dump_empty(msg: Msg) -> bytes:
    """
    Used internaly for crc calculation.
    """
    ret = msg.src.to_bytes(1, "big")
    ret += msg.dest.to_bytes(1, "big")
    ret += b'\x00'
    ret += msg.size.to_bytes(1, "big")
    ret += msg.ordering.to_bytes(1, "big")
    ret += msg.priority.to_bytes(1, "big")
    ret += msg.atype.to_bytes(1, "big")
    ret += msg.data.encode("utf-8")

    return ret

def dumps(msg: Msg) -> bytes:
    """
    Turns a Msg to bytes to be sent.
    """

    ret = _dump_empty(msg)

    crc = calc_crc(ret)

    ret = msg.src.to_bytes(1, "big")
    ret += msg.dest.to_bytes(1, "big")
    ret += crc
    ret += msg.size.to_bytes(1, "big")
    ret += msg.ordering.to_bytes(1, "big")
    ret += msg.priority.to_bytes(1, "big")
    ret += msg.atype.to_bytes(1, "big")
    ret += msg.data.encode("utf-8")

    return ret


def loads(msg: bytes) -> Msg:
    """
    Turns a bytes to Msg.
    """
    src = msg[0]
    dest = msg[1]
    crc = msg[2]
    size = msg[3]
    ordering = msg[4]
    priority = msg[5]
    atype = msg[6]
    data = msg[7:].decode("utf-8")

    ret = Msg(priority, src, dest, size, atype, ordering, data)

    tmp = _dump_empty(ret)
    tmp = calc_crc(tmp)
    ret.crc = (int.from_bytes(tmp, "big") == crc)

    return ret


def unit_test():
    """
    The functionality of this module.
    """
    tmp = Msg(1,2,4,1,0,0,"test")
    print(f"input: {tmp}")
    b = dumps(tmp)
    print(f"bytes: {b}")
    tmp2 = loads(b)
    print(f"output: {tmp2}")
    assert tmp == tmp2
