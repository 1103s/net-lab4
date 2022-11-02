"""
Used to prepresent a msg in the HAC system.
Flows the folowing fomrat:
  - src → HAC
  - dest → HAC
  - SIZE/ACK
  - ordering → reassembly order (NOT USED)
  - priority
  - data
"""

from dataclasses import dataclass, field


@dataclass(order=True)
class Msg():
    priority: int
    src: int = field(compare=False)
    dest: int = field(compare=False)
    size: int = field(compare=False)
    ordering: int = field(compare=False)
    data: str = field(compare=False)

def dumps(msg: Msg) -> bytes:
    """
    Turns a Msg to bytes to be sent.
    """
    ret = msg.src.to_bytes(1, "big")
    ret += msg.dest.to_bytes(1, "big")
    ret += msg.size.to_bytes(1, "big")
    ret += msg.ordering.to_bytes(1, "big")
    ret += msg.priority.to_bytes(1, "big")
    ret += msg.data.encode("utf-8")
    return ret


def loads(msg: bytes) -> Msg:
    """
    Turns a bytes to Msg.
    """
    src = msg[0]
    dest = msg[1]
    size = msg[2]
    ordering = msg[3]
    priority = msg[4]
    data = msg[5:].decode("utf-8")
    ret = Msg(src, dest, size, ordering, priority, data)
    return ret


def unit_test():
    """
    The functionality of this module.
    """
    tmp = Msg(1,2,4,1,0,"test")
    print(f"input: {tmp}")
    b = dumps(tmp)
    print(f"bytes: {b}")
    tmp2 = loads(b)
    print(f"output: {tmp2}")
    assert tmp == tmp2


