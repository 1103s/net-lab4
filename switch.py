"""
Represents a switch as defined in the project.
"""

from netdevice import SLEEP_TIME, NetDevice
from time import sleep

class Switch(NetDevice):
    def __init__(self, ports_in: list,
                 ports_out: list) -> None:
        super().__init__(ports_in, ports_out)
        for i, o in zip(ports_in, ports_out):
            self.in_st[i] = list()
            self.out_st[o] = list()
            self.ito[i] = o
            self.oti[o] = i

    def process_loop(self):
        while(True):
            if (self.rcv_q.empty()):
                sleep(SLEEP_TIME)
                continue
            in_port, in_msg = self.rcv_q.get()
            tmp_in = self.in_st[in_port]
            tmp_out = self.out_st[self.ito[in_port]]
            tmp_in.append(in_msg.src)
            tmp_out.append(in_msg.src)
            for i, o in zip(self.tmp_in.values(),
                             self.tmp_out.values()):
                if (i != tmp_in):
                    i.remove(in_msg.src)
                if (o != tmp_out):
                    o.remove(in_msg.src)

            dest = in_msg.dest
            send_port = None
            for k, o in self.tmp_out.items():
                if (dest in o):
                    send_port = k
                    break

            if (send_port is None):
                for port in self.ports_out:
                    self.send_q.put((port, in_msg))
            else:
                self.send_q.put((send_port, in_msg))



