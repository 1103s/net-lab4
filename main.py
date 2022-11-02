"""
The main module as requested by the instructions.
"""

import threading as t
import switch as s
import node as n

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
        




