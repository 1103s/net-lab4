"""
Contains all the features shared by the nodes and the switches.
This includes send / recieve functionality, which is built
on top of TCP/IP, although the statefull nature of TCP is
intenionaly ignored as this would not be an accurate
simulation of network switching communication.
"""

import itertools as it
from dataclasses import field, dataclass
from queue import PriorityQueue
from random import randint
from time import time, sleep
import socket
from msg import Msg, dumps, loads
import threading as t

SLEEP_TIME = 0.001 # How long to wait in sec between loops
TCP_PORT_PREFIX = 3000 + randint(0,100)

# How long to wait on a conections

socket.setdefaulttimeout(1)

@dataclass
class NetDevice():
    """
    Represents a device that can send and recieve messages.

    A NetDevice has three threads that are activated when
    it is run. One for sending, one for reciving, and
    one thread that is overwriten by nodes and switches to do
    their respective processing.

    Messages put on the send_q in a tuple of the format:
        (port to send on, Msg object)
    Will be placed on the rcv_q on the other end of the
    specified port.

    Msg objects with the priority flag set will
    automatically be placed at the front fo th queue.

    See msg.py for more info on that.
    """
    ports_in: list
    ports_out: list
    global_blocks: list = field(default_factory=list, repr=False)
    local_blocks: list = field(default_factory=list, repr=False)
    do_firewall: bool = False
    send_q: PriorityQueue = field(
            default_factory=PriorityQueue,
            repr=False)
    rcv_q: PriorityQueue = field(
            default_factory=PriorityQueue,
            repr=False)
    node_id: int = -1

    def to_hac(self, s: str) -> int:
        """
        Takes a string of the format <number>_<number> and converts it to the
        hack format where the first 4 bytes are the first number and the last 4
        are the second mumber.
        """
        net, dev = s.split("_")
        netb = (int(net) << 4).to_bytes(1, "big")
        devb = (int(dev)).to_bytes(1, "big")
        ret = int.from_bytes(netb, "big") | int.from_bytes(devb, "big")
        return ret

    def from_hack(self, i: int) -> str:
        """
        Inverse of the to_hac function.
        """
        net = (i & 0b11110000) >> 4
        dev = i & 0b00001111
        ret = f"{int(net)}_{int(dev)}"
        return ret

    def is_blocked(self, msg: Msg) -> bool:
        """
        Checks to see if a message should be blocked by the firewall.
        """
        src_net = msg.src & 0b11110000
        dest_net = msg.dest & 0b11110000
        src_node = msg.src & 0b00001111
        dest_node = msg.dest & 0b00001111

        is_local = (src_net == dest_net)
        is_blocked = ((dest_net in self.global_blocks) or \
                        (dest_node in self.local_blocks))

        if (is_blocked):
            if (is_local):
                return True
            else:
                return False
        else:
            return True

    def __repr__(self) -> str:
        """
        Prettry printing function.
        """
        hac = self.node_id if (self.node_id >= 0) else "N/A"
        r = [hex(x) for x in self.ports_in]
        w = [hex(x) for x in self.ports_out]
        t = (f"\tHAC ADRESS: {hac}\n\tREAD PORTS: {r}"
             f"\n\tWRITE PORTS: {w}")
        return t

    def send_loop(self):
        """
        This function will be run as a background thread
        sending any messages added to send_q.
        """

        # Pull a message of the queue

        while (True):
            sleep(SLEEP_TIME)
            if(self.send_q.empty()):
                continue
            next_hop, msg  = self.send_q.get()


            # Check to see if the message is firewalled

            if(self.is_blocked(msg)):
                print("|| FIREWALL BLOCKED MSG")

                # Send NACK

                msg.size = 0
                msg.atype = 0b00000010
                tmp = msg.dest
                msg.dest = msg.src
                msg.src = tmp
                self.rcv_q.put((-1, msg))
                continue


            # Can not send on a port that is not attached

            if(next_hop not in self.ports_out):
                raise Exception(
                        f"Can not send to port {next_hop:x}")


            # Create TCP/IP socket and send

            next_sock = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
            next_port = next_hop + TCP_PORT_PREFIX
            tmp = msg.data if (msg.size) else \
                    f"ACK:{msg.data}"
            try:
                next_sock.connect(("", next_port))
                tmp2 = dumps(msg)
                next_sock.sendall(tmp2)
                # print(f"-> SENT {tmp}:{next_port}")
            except Exception as e:

                # If sending fails, put msg back on queue

                print(f"-- MSG '{tmp}'"
                      f" TO {msg.dest}"
                      f" VIA PORT {hex(next_hop)} IS DELAYED")
                next_sock.close()
                self.send_q.put((next_hop, msg))
                continue

            print(f">> {msg.src} SENDS '{tmp}' TO {msg.dest}"
                  f" VIA PORT {hex(next_hop)}")


            next_sock.close()

    def listen(self):
        """
        Start Listening ports for incoming messages.

        NOTE: must be closed latter.
        """
        self.sockets_in = []
        for port in self.ports_in:
            tmp = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
            self.sockets_in.append((port, tmp))
            my_tcp = TCP_PORT_PREFIX + port
            try:
                tmp.bind(("", my_tcp))
            except Exception as e:
                raise Exception(f'The ports that are required'
                                f' for this program are in'
                                f' in use. If you recently'
                                f' ran this program, please'
                                f' wait a couple seconds'
                                f' while the OS marks them'
                                f' as available.')
            tmp.listen()

    def recieve_loop(self):
        """
        On an indepenednt thread, recieve messages via TCP/IP
        and add them to the rcv_q for processing by another
        thread.
        """
        while(True):
            for port, socket in self.sockets_in:
                tmp = tuple()
                try:
                    tmp = socket.accept()
                except Exception as e:
                    continue
                clientsocket = tmp[0]
                data = clientsocket.recv(255)
                if (not data):
                    continue
                # print(f'<- {data}')
                clientsocket.close()
                new_msg = loads(data)

                # Add firewall rules

                if (new_msg.atype == 0b11111111):
                    if (self.do_firewall):
                        self.local_blocks.append(self.to_hac(new_msg.data))
                    print(f"\\ RECIEVED FIREWALL RULE AT {self}")

                # Check to see if its CRC is bad

                elif (not new_msg.crc):

                    # Make send a NACK

                    new_msg.size = 0
                    new_msg.atype = 0b00000001
                    tmp = new_msg.dest
                    new_msg.dest = new_msg.src
                    new_msg.src = tmp
                    self.rcv_q.put((-1, new_msg))

                    print("~~ CRC FAIL. NACK SENT.")

                else:
                    self.rcv_q.put((port, new_msg))
                    tmp = new_msg.data if (new_msg.size) \
                            else f"ACK:{new_msg.data}"
                    print(f"<< DELIVERED '{tmp}'"
                          f" VIA PORT {hex(port)}")
                    if (new_msg.priority):
                        print(f"!! PRIORITY PACKET FOUND"
                               " MOVING TO FRONT!")
                sleep(SLEEP_TIME)

    def process_loop(self):
        """
        The third thread to process frames on rcv_q.
        To be implemented in children.
        """
        ...

    def start_device(self):
        """
        Start the above defined functions as threads.
        """
        self.listen()
        self.jobs = [
                t.Thread(target=self.recieve_loop,
                         daemon=True),
                t.Thread(target=self.send_loop,
                         daemon=True),
                t.Thread(target=self.process_loop,
                         daemon=True)
                ]
        for job in self.jobs:
            job.start()

def unit_test():
    """
    Tests this unit.
    """
    tmp = NetDevice([10,20], [11, 21])
    tmp2 = NetDevice([10,20], [11, 21])
    print(f"device: {tmp}")
    print(f"device: {tmp2}")

if __name__ == "__main__":
    unit_test()

