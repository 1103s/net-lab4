"""
A program that simulates a switched network.

The program can be run without any extra -- flags and
will operate as specified in the assignment, with all required functionality.

There are 3 -- flags that you can add to have the program
run in compliance with the various extra credit modes
specified in the assignment.

For further details, see the rest of the documentation.
"""

from random import shuffle
import threading as t
from time import sleep
from netdevice import SLEEP_TIME
import switch as s
import node as n
import argparse

class Main():
    """
    The primary test object as described in the asignment.
    """

    def __init__(self, num_nodes: int) -> None:

        # Setup ports for conections

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        # Setup nodes

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        # Connect nodes via switch

        tmp_out = [x[0] for x in self.node_ports]
        tmp_in = [x[1] for x in self.node_ports]
        self.switches = []
        tmp = s.Switch(tmp_in, tmp_out)
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

class ExtraCredit1(Main):
    """
    The extra-credit backbone network sim.
    """
    def __init__(self, num_nodes: int) -> None:

        # Check that the number of nodes can be devided

        if (num_nodes % 2):
            raise Exception("Number of nodes must be even.")

        # set up ports

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        # set up nodes

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        # set backbone conections

        tmp_out = [x[0] for x in self.node_ports]
        tmp_in = [x[1] for x in self.node_ports]
        backbone_in = num_nodes * 2
        backbone_out = (num_nodes * 2) + 1

        # set up switches

        self.switches = []
        tmp = s.Switch([*tmp_in[:num_nodes//2], backbone_in],
                       [*tmp_out[:num_nodes//2], backbone_out])
        self.switches.append(tmp)
        tmp = s.Switch([*tmp_in[num_nodes//2:], backbone_out],
                       [*tmp_out[num_nodes//2:], backbone_in])
        self.switches.append(tmp)


class ExtraCredit2(Main):
    """
    The extra-credit star of star network sim.
    """
    def __init__(self, num_nodes: int) -> None:

        # Check that the number of nodes can be devided

        if (num_nodes % 2):
            raise Exception("Number of nodes must be even.")

        # Set up ports

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

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
                [backbone_in_right, backbone_in_left])
        self.switches.append(tmp)


class ExtraCredit3(Main):
    """
    The extra-credit network sim with priority packets.
    """
    def __init__(self, num_nodes: int) -> None:

        # Set up ports

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))


        # Set up nodes with priority enabled

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i, priority=True)
            self.nodes.append(tmp)


        # set up swithces

        tmp_out = [x[0] for x in self.node_ports]
        tmp_in = [x[1] for x in self.node_ports]
        self.switches = []
        tmp = s.Switch(tmp_in, tmp_out)
        self.switches.append(tmp)


if __name__ == '__main__':

    # Parse cmd line args

    import argparse
    parser = argparse.ArgumentParser(
            description=__doc__)
    parser.add_argument('nodes',
                        metavar='N',
                        type=int,
                        help='Number of nodes (max 255) used.')
    parser.add_argument('--backbone',
                        action='store_true',
                        help='Use backbone switching.')
    parser.add_argument('--star',
                        action='store_true',
                        help='Use star of star switching.')
    parser.add_argument('--priority',
                        action='store_true',
                        help='Use priority messages.')
    args = parser.parse_args()
    if ((args.nodes > 255) or (args.nodes <= 0)):
        raise Exception("N out of range!")

    # set up sim env

    print(f"STARTING SIM")
    tmp = None
    if (args.backbone):
        tmp = ExtraCredit1(args.nodes)
    elif (args.star):
        tmp = ExtraCredit2(args.nodes)
    elif (args.priority):
        tmp = ExtraCredit3(args.nodes)
    else:
        tmp = Main(args.nodes)

    # run sim

    tmp.run_sim()
    print(f"SIM FINISHED")


