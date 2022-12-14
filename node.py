"""
This module manages nodes and node funtions. Nodes are tracked
via HACs (Hamdy Access Codes). These are my versions of MACs.
"""
from time import sleep
from netdevice import SLEEP_TIME, NetDevice
from itertools import count
from msg import Msg
import re
import random as r

class Node(NetDevice):
    """
    Represents a node as described in the directions.
    """
    def __init__(self, switch_in: int,
                 switch_out: int,
                 shac: str,
                 priority=False) -> None:
        super().__init__([switch_in], [switch_out])

        # Setup node variables

        self.shac = shac
        self.node_id = self.to_hac(shac)
        self.gateway_switch = switch_out
        send_dat = []
        m_count = count()
        self.send_dat = {}
        self.exit = False
        self.rcv_counts = {}

        # Setup node files

        with open(f"node{self.shac}.txt") as f:
            send_dat = f.readlines()
        with open(f"node{self.shac}output.txt",
                  "w") as f:
            f.write("")

        # Extract data that needs to tbe sent from node file

        if (not send_dat):
            self.exit = True
        for x in send_dat:
            m = re.match(r"(.*): (.*)", x)
            if (m is None):
                raise Exception("Malformed Node File!")

            # Convert m to a hac
            hac = self.to_hac(m[1])

            # If priority is enabled, randomly
            # give frames priority

            pri = 0
            if (priority):
                pri = r.randint(0,1)

            # Add messages to send queue

            tmp = Msg(pri, self.node_id, hac,
                      len(m[2]), 0, next(m_count),
                      m[2])
            self.send_dat[tmp.ordering] = tmp
            self.send_q.put((switch_out, tmp))

        print(f"NODE #{self.node_id} CREATED: \n {self} \n")

    def process_loop(self):
        while(True):

            # Check to see if all messages are sent

            self.send_dat_old = self.send_dat
            self.send_dat = {k:v for k,v in
                             self.send_dat.items()
                             if not(v is None)}
            if ((not self.send_dat) and (not self.exit)):
                self.exit = True
                print(f"-- NODE {self.node_id} FINISHED")
            elif ((not self.exit)
                  and (self.send_dat_old != self.send_dat)):
                print(f"## NODE {self.node_id}"
                      f" WATING FOR"
                      f" {len(self.send_dat)} ACKs.")

            # Pull a message from a queue

            if (self.rcv_q.empty()):
                sleep(SLEEP_TIME)
                continue
            in_port, in_msg = self.rcv_q.get()

            # Reject messages that are not for me

            if (in_msg.dest != self.node_id):
                continue

            # Check to see if the packet is an ack

            if (in_msg.size <= 0):

                # Remove message from send buffer

                print(f"|< ACK FOR '{in_msg.data}' NOTED")
                tmp = self.send_dat.get(in_msg.ordering, None)
                if (tmp is None):
                    continue
                if (in_msg.data == tmp.data):
                    self.send_dat[in_msg.ordering] = None
                else:
                    raise Exception("Invalid ACK!")
            else:


                # Message is a normal message

                sender = in_msg.src
                order = in_msg.ordering
                data = in_msg.data

                # Make sure message is in order
                # Curently unu used

                m_count = self.rcv_counts.get(sender, 0)
                #if (order > m_count):
                #    self.rcv_q.appendleft(in_msg)
                #elif (order == m_count):

                self.rcv_counts[sender] = (m_count + 1)
                with open(f"node{self.node_id}output.txt",
                          "a") as f:
                    tmp = f"{sender}: {data}"
                    print(f">| DATA '{tmp}' RECORDED AT"
                          f" {self.node_id}")
                    f.write(tmp + '\n')

                # Make ack

                in_msg.src = in_msg.dest
                in_msg.dest = sender
                in_msg.size = 0
                self.send_q.put(
                        (self.gateway_switch, in_msg))

            sleep(SLEEP_TIME)


