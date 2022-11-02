"""
This module manages nodes and node funtions. Conections are
managed via simplex connections called ports.
These are not to be confused with the TCP ip
ports that support them.
"""
from netdevice import SLEEP_TIME, NetDevice
from time import sleep

class Switch(NetDevice):
    """
    Represents a switch as defined in the project.
    """
    def __init__(self, ports_in: list,
                 ports_out: list) -> None:
        super().__init__(ports_in, ports_out)

        # Setus up the Switching table(s)
        # Twos tables are actualy used since
        # the connecions are simplex

        self.in_st = dict()
        self.out_st = dict()
        self.ito = dict()
        self.oti = dict()
        for i, o in zip(ports_in, ports_out):
            self.in_st[i] = list()
            self.out_st[o] = list()
            self.ito[i] = o
            self.oti[o] = i
        print(f"SWITCH CREATED: \n {self} \n")

    def process_loop(self):

        # Get a message from the recieved queue

        while(True):
            if (self.rcv_q.empty()):
                sleep(SLEEP_TIME)
                continue
            in_port, in_msg = self.rcv_q.get()

            # Add inbound connection to the switching
            # tables

            tmp_in = self.in_st[in_port]
            tmp_out = self.out_st[self.ito[in_port]]
            tmp_in.append(in_msg.src)
            tmp_out.append(in_msg.src)

            # Find port to forward frame to the requested HAC

            dest = in_msg.dest
            send_port = None
            for k, o in self.out_st.items():
                if (dest in o):
                    send_port = k
                    break

            # If there is no known route, flood

            if (send_port is None):
                print("~~ FLOODING")
                for port in self.ports_out:
                    self.send_q.put((port, in_msg))


            # otherwise forward single frame

            else:
                print("@@ DIRECT")
                self.send_q.put((send_port, in_msg))
