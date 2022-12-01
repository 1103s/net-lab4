"""
This module manages nodes and node funtions. Conections are
managed via simplex connections called ports.
These are not to be confused with the TCP ip
ports that support them.
"""
from msg import Msg
from netdevice import SLEEP_TIME, NetDevice
from time import sleep, time

# The amount of time to wait before clearing the ST

ST_TIME = 8

class Switch(NetDevice):
    """
    Represents a switch as defined in the project.
    """
    def __init__(self, ports_in: list,
                 ports_out: list, global_blocks: list = [],
                 local_blocks: list = []) -> None:
        self.do_firewall = True # Enable firewall
        super().__init__(ports_in, ports_out, global_blocks)

        # Setus up the Switching table(s)
        # Twos tables are actualy used since
        # the connecions are simplex

        self.in_st = dict()
        self.out_st = dict()
        self.ito = dict()
        self.oti = dict()
        self.cach_time = time() + (ST_TIME)
        self.init_switching_table()

        # Forward firewall rules to other switches.

        for rule in local_blocks:
            tmp = Msg(0, 0, 0, 0, 0b11111111, 0, rule)
            self.send_q.put((-1, rule))
            print(f"FORWARDING RULE: \n {rule} \n")

        print(f"SWITCH CREATED: \n {self} \n")


    def init_switching_table(self):
        """
        Creates a blank switching table
        """
        for i, o in zip(self.ports_in, self.ports_out):
            self.in_st[i] = list()
            self.out_st[o] = list()
            self.ito[i] = o
            self.oti[o] = i

    def process_loop(self):

        # Get a message from the recieved queue

        while(True):
            if (self.rcv_q.empty()):
                sleep(SLEEP_TIME)
                continue
            in_port, in_msg = self.rcv_q.get()

            # Check to see if the message is a self send
            if (in_port == -1):
                self.cach_time = 0

            # Check to see if we have seen this message before

            if (time() >= self.cach_time):
                print("%% ST HAS EXPIRED"
                      ", CLEARING ST")

                # Wipe ST if time is up

                self.cach_time = time() + (ST_TIME)
                self.init_switching_table()

            else:

                # Calculate inbound tables

                tmp_in = self.in_st[in_port]
                tmp_out = self.out_st[self.ito[in_port]]

                # Add inbound connection to the switching
                # tables

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
                print("~~ SWITCH IS FLOODING")
                for port in self.ports_out:

                    # Dont send on input port

                    if (port == in_port):
                        continue
                    self.send_q.put((port, in_msg))


            # otherwise forward single frame

            else:
                print("@@ SWITCH IS SENDING DIRECT")
                self.send_q.put((send_port, in_msg))
