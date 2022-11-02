"""
The main module as requested by the instructions.
"""

import threading as t
from time import sleep
from netdevice import SLEEP_TIME
import switch as s
import node as n
import argparse

class Main():
    def __init__(self, num_nodes: int) -> None:
        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        tmp_in = [x[0] for x in self.node_ports]
        tmp_out = [x[1] for x in self.node_ports]
        self.switches = []
        tmp = s.Switch(tmp_in, tmp_out)
        self.switches.append(tmp)



    def run_sim(self):
        for dev in [*self.nodes, *self.switches]:
            dev.start_device()
        running = True
        while (running):
            sleep(SLEEP_TIME)
            tmp = [x for x in self.nodes
                   if (not x.exit)]
            running = bool(tmp)
        for dev in [*self.nodes, *self.switches]:
            dev.listen_socket.close()

class ExtraCredit1(Main):
    def __init__(self, num_nodes: int) -> None:
        
        if (num_nodes % 2):
            exit(5)

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        tmp_in = [x[0] for x in self.node_ports]
        tmp_out = [x[1] for x in self.node_ports]

        backbone_in = num_nodes * 2
        backbone_out = (num_nodes * 2) + 1
        self.switches = []
        tmp = s.Switch([*tmp_in[:num_nodes/2], backbone_in],
                       [*tmp_out[:num_nodes/2], backbone_out])
        self.switches.append(tmp)
        tmp = s.Switch([*tmp_in[num_nodes/2:], backbone_in],
                       [*tmp_out[num_nodes/2:], backbone_out])
        self.switches.append(tmp)


class ExtraCredit2(Main):
    def __init__(self, num_nodes: int) -> None:
        
        if (num_nodes % 2):
            exit(5)

        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i)
            self.nodes.append(tmp)

        tmp_in = [x[0] for x in self.node_ports]
        tmp_out = [x[1] for x in self.node_ports]

        backbone_in_left = num_nodes * 2
        backbone_out_left = (num_nodes * 2) + 1
        backbone_in_right = (num_nodes * 2) + 2
        backbone_out_right = (num_nodes * 2) + 3
        self.switches = []
        tmp = s.Switch([*tmp_in[:num_nodes/2],
                        backbone_in_left],
                       [*tmp_out[:num_nodes/2],
                        backbone_out_left])
        self.switches.append(tmp)
        tmp = s.Switch([*tmp_in[num_nodes/2:],
                        backbone_in_right],
                       [*tmp_out[num_nodes/2:],
                        backbone_out_right])
        self.switches.append(tmp)
        tmp = s.Switch([backbone_in_right, backbone_in_left],
                [backbone_out_right, backbone_out_left])
        self.switches.append(tmp)


class ExtraCredit3(Main):
    def __init__(self, num_nodes: int) -> None:
        self.node_ports = []
        for i in range(num_nodes):
            self.node_ports.append((i, i + num_nodes))

        self.nodes = []
        for i in self.node_ports:
            tmp = n.Node(*i, priority=True)
            self.nodes.append(tmp)

        tmp_in = [x[0] for x in self.node_ports]
        tmp_out = [x[1] for x in self.node_ports]
        self.switches = []
        tmp = s.Switch(tmp_in, tmp_out)
        self.switches.append(tmp)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
            description=__doc__)
    parser.add_argument('Nodes',
                        metavar='N',
                        type=int,
                        nargs='+',
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
        exit(6)
    tmp = None
    if (args.backbone):
        tmp = ExtraCredit1(args.nodes)
    elif (args.star):
        tmp = ExtraCredit2(args.nodes)
    elif (args.priority):
        tmp = ExtraCredit3(args.nodes)
    else:
        tmp = Main(args.nodes)

    tmp.run_sim()



