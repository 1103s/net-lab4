"""
A program that simulates a switched network.

The program can be run without any extra -- flags and
will operate as specified in the assignment, with all required functionality.

There are 3 -- flags that you can add to have the program
run in compliance with the various extra credit modes
specified in the assignment.

For further details, see the rest of the documentation.
"""

from itertools import cycle
from random import shuffle
import threading as t
from time import sleep
from netdevice import SLEEP_TIME
import switch as s
import node as n
import argparse
import re

class Main():
    """
    The primary test object as described in the asignment.
    """

    def __init__(self, num_nodes: int) -> None:

        # Check that the number of nodes can be devided

        if (num_nodes % 2):
            raise Exception("Number of nodes must be even.")

        # Read firewall
        global_blocks = list()
        local_blocks = list()
        with open("firewall.txt") as f:
            rules = f.readlines()
            for x in rules:
                m = re.match(r"(.*): (.*)", x)
                if (m is None):
                    raise Exception("Malformed Node File!")
                if ("#" in m[1]):
                    shac = m[1].replace("#", "0")
                    global_blocks.append(shac)
                else:
                    local_blocks.append(m[1])

        # Set up ports
        nets = cycle([1,2])

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes,
                                    f'{next(nets)}_{i}'))
        print(self.node_ports)

        # Set up nodes

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        # set up backbone ports

        tmp_out = [x[0] for x in self.node_ports]
        tmp_in = [x[1] for x in self.node_ports]
        backbone_in_left = num_nodes * 2
        backbone_out_left = (num_nodes * 2) + 1
        backbone_in_right = (num_nodes * 2) + 2
        backbone_out_right = (num_nodes * 2) + 3

        # Set up switches

        self.switches = []
        tmp = s.Switch([*tmp_in[:num_nodes//2],
                        backbone_in_left],
                       [*tmp_out[:num_nodes//2],
                        backbone_out_left])
        self.switches.append(tmp)
        tmp = s.Switch([*tmp_in[num_nodes//2:],
                        backbone_in_right],
                       [*tmp_out[num_nodes//2:],
                        backbone_out_right])
        self.switches.append(tmp)
        tmp = s.Switch([backbone_out_right, backbone_out_left],
                [backbone_in_right, backbone_in_left], global_blocks,
                       local_blocks)
        self.switches.append(tmp)

    def run_sim(self):
        """
        Runs the simulation of the programed network.
        """

        # Start devices in random order

        devices = [*self.nodes, *self.switches]
        shuffle(devices)

        # For each netdevice object start its threads

        for dev in devices:
            dev.start_device()

        # Periodicly check to see if the threads are done

        running = True
        while (running):
            sleep(SLEEP_TIME)
            tmp = [x for x in self.nodes
                   if (not x.exit)]
            running = bool(tmp)

        # Shutdown threads and ports

        print(f"SHUTING DOWN THREADS")
        for dev in [*self.nodes, *self.switches]:
            for soc in dev.sockets_in:
                soc[1].close()

if __name__ == '__main__':

    # Parse cmd line args

    import argparse
    parser = argparse.ArgumentParser(
            description=__doc__)
    parser.add_argument('nodes',
                        metavar='N',
                        type=int,
                        help='Number of nodes (max 255) used.')
    args = parser.parse_args()
    if ((args.nodes > 255) or (args.nodes <= 0)):
        raise Exception("N out of range!")

    # set up sim env

    print(f"STARTING SIM")
    tmp = None
    tmp = Main(args.nodes)

    # run sim

    tmp.run_sim()
    print(f"SIM FINISHED")


