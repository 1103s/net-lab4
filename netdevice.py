"""
Represents a device that can send messages.

"""
import itertools as it
from dataclasses import field, dataclass
from queue import PriorityQueue
from time import time, sleep
import socket
from msg import dumps, loads
import threading as t

SLEEP_TIME = 2
TCP_PORT_PREFIX = 1000

@dataclass
class NetDevice():
    ports_in: list
    ports_out: list
    send_q: PriorityQueue = field(
            default_factory=PriorityQueue)
    rcv_q: PriorityQueue = field(
            default_factory=PriorityQueue)

    def send_loop(self):
        while (True):
            sleep(SLEEP_TIME)
            if(self.send_q.empty()):
                continue

            next_hop, msg  = self.send_q.get()

            if(next_hop not in self.ports_out):
                exit(4)

            next_sock = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
            next_port = next_hop + TCP_PORT_PREFIX

            try:
                next_sock.connect(("", next_port))
                next_sock.sendall(dumps(msg))
            except Exception as e:
                self.send_q.put((next_hop, msg))
            else:
                break
            next_sock.close()

    def listen(self):
        self.sockets_in = []
        for port in self.ports_in:
            tmp = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
            self.sockets_in.append((port, tmp))
            my_tcp = TCP_PORT_PREFIX + port
            try:
                tmp.bind(("", my_tcp))
            except Exception as e:
                exit(2)
            tmp.listen()

    def recieve_loop(self):
        while(True):
            for port, socket in self.sockets_in:
                tmp = socket.accept()
                clientsocket = tmp[1]
                data = clientsocket.recv(255).decode("utf-8")
                new_msg = loads(data)
                self.rcv_q.put((port, new_msg))
                clientsocket.close()
                sleep(SLEEP_TIME)

    def process_loop(self):
        ...

    def start_device(self):
        self.listen()
        self.jobs = [
                t.Thread(target=self.recieve_loop,
                              args=(self,)),
                t.Thread(target=self.send_loop,
                              args=(self,)),
                t.Thread(target=self.process_loop,
                              args=(self,))
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










