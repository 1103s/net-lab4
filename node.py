"""
Represents a node as described in the directions.
"""
from time import sleep
from netdevice import SLEEP_TIME, NetDevice
from itertools import count
from msg import Msg
import re
import random as r

TOP_NODE = count(1)

class Node(NetDevice):
    def __init__(self, switch_in: int,
                 switch_out: int,
                 priority=False) -> None:
        super().__init__([switch_in], [switch_out])
        self.node_id = next(TOP_NODE)
        self.router = switch_in
        send_dat = []
        m_count = count()
        self.send_dat = {}
        self.exit = False
        self.rcv_counts = {}
        with open(f"node{self.node_id}.txt") as f:
            send_dat = f.readlines()
        with open(f"node{self.node_id}output.txt",
                  "w") as f:
            f.write("")
        for x in send_dat:
            m = re.match(r"(.*): (.*)", x)
            if (m is None):
                exit(3)
            pri = 0
            if (priority):
                pri = r.randint(0,1)

            tmp = Msg(m[1], self.node_id,
                      len(m[2]), next(m_count),
                      pri, m[2])
            self.send_dat[tmp.ordering] = tmp
            self.send_q.put((switch_in, tmp))

    def process_loop(self):
        while(True):
            if (self.rcv_q.empty()):
                sleep(SLEEP_TIME)
                continue
            in_port, in_msg = self.rcv_q.get()
            if (in_msg.size <= 0):
                tmp = self.send_dat[in_msg.ordering]
                if (in_msg.data == tmp.data):
                    self.send_dat[in_msg.ordering] = None
                else:
                    ...
                    ## TODO
            else:
                sender = in_msg.src
                order = in_msg.ordering
                data = in_msg.data
                m_count = self.rcv_counts.get(sender, 0)
                if (order > m_count):
                    self.rcv_q.appendleft(in_msg)
                elif (order == m_count):
                    self.rcv_counts[sender] = (m_count + 1)
                    with open(f"node{self.node_id}output.txt",
                              "a") as f:
                        tmp = f"{sender}: {data}"
                        f.writelines([tmp])
                    in_msg.src = in_msg.dest
                    in_msg.dest = sender
                    in_msg.size = 0
                    self.send_q.put(
                            (self.router, in_msg))
                else:
                    ...
                    ## TODO
            self.send_dat = {k:v for k,v in
                             self.send_dat.items()
                             if not(v is None)}
            if (not self.send_dat):
                self.exit = True
            sleep(SLEEP_TIME)

## No unit test?



