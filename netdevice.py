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
from time import time, sleep
import socket
from msg import dumps, loads
import threading as t

SLEEP_TIME = 1 # How long to wait in sec between loops
TCP_PORT_PREFIX = 550

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
    send_q: PriorityQueue = field(
            default_factory=PriorityQueue,
            repr=False)
    rcv_q: PriorityQueue = field(
            default_factory=PriorityQueue,
            repr=False)

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

            # Can not send on a port that is not attached

            if(next_hop not in self.ports_out):
                raise Exception(
                        f"Can not send to port {next_hop}")


            # Create TCP/IP socket and send

            next_sock = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
            next_port = next_hop + TCP_PORT_PREFIX
            tmp = msg.data if (msg.size) else \
                    f"ACK:{msg.data}"
            try:
                next_sock.connect(("", next_port))
                next_sock.sendall(dumps(msg))
            except Exception as e:

                # If sending fails, put msg back on queue

                print(f"-- MSG '{tmp}'"
                      f" TO {msg.dest}"
                      f" VIA {next_hop} IS DELAYED")
                self.send_q.put((next_hop, msg))
                continue

            print(f">> {msg.src} SENDS '{tmp}' TO {msg.dest}"
                  f" VIA {next_hop}")


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
                raise Exception(f'BAD PORT {my_tcp}! {e}')
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
                new_msg = loads(data)
                self.rcv_q.put((port, new_msg))
                clientsocket.close()
                tmp = new_msg.data if (new_msg.size) \
                        else f"ACK:{new_msg.data}"
                print(f"<< DELIVERED '{tmp}'"
                      f" VIA {port}")
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










