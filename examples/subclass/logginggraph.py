#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Author: Aric Hagberg (hagberg@lanl.gov)
"""
Example subclass of the Graph class that logs changes.
"""
from copy import deepcopy
import logging

import networkx as nx


class LoggingGraph(nx.Graph):
    """A graph that logs activity using Python's built-in :mod:`logging`
    module.

    """

    def add_node(self, n, *args, **kw):
        super(LoggingGraph, self).add_node(n, *args, **kw)
        logging.debug('Add node: {}'.format(n))

    def add_nodes_from(self, nodes, *args, **kw):
        for n in nodes:
            self.add_node(n, *args, **kw)

    def remove_node(self, n):
        super(LoggingGraph, self).remove_node(n)
        logging.debug('Remove node: {}'.format(n))

    def remove_nodes_from(self, nodes):
        nodes = list(nodes)
        for n in nodes:
            self.remove_node(n)

    def add_edge(self, u, v, *args, **kw):
        super(LoggingGraph, self).add_edge(u, v, *args, **kw)
        logging.debug('Add edge: {}-{}'.format(u, v))

    def add_edges_from(self, ebunch, *args, **kw):
        for u, v in ebunch:
            self.add_edge(u, v, *args, **kw)

    def remove_edge(self, u, v):
        super(LoggingGraph, self).remove_edge(u, v)
        logging.debug('Remove edge: {}-{}'.format(u, v))

    def remove_edges_from(self, ebunch):
        for u, v in ebunch:
            self.remove_edge(u, v)

    def clear(self):
        super(LoggingGraph, self).clear()
        logging.debug('Clear graph')

    def subgraph(self, nbunch, copy=True):
        # subgraph is needed here since it can destroy edges in the
        # graph (copy=False) and we want to keep track of all changes.
        #
        # Also for copy=True Graph() uses dictionary assignment for speed
        # Here we use H.add_edge()
        bunch = set(self.nbunch_iter(nbunch))

        if not copy:
            # remove all nodes (and attached edges) not in nbunch
            self.remove_nodes_from(n for n in self if n not in bunch)
            self.name = "Subgraph of (%s)" % (self.name)
            return self
        else:
            # create new graph and copy subgraph into it
            H = self.__class__()
            H.name = "Subgraph of (%s)" % (self.name)
            # add nodes
            H.add_nodes_from(bunch)
            # add edges
            seen = set()
            for u, nbrs in self.adjacency_iter():
                if u in bunch:
                    for v, datadict in nbrs.items():
                        if v in bunch and v not in seen:
                            dd = deepcopy(datadict)
                            H.add_edge(u, v, dd)
                    seen.add(u)
            # copy node and graph attr dicts
            H.node = {n: deepcopy(d) for n, d in self.node.items() if n in H}
            H.graph = deepcopy(self.graph)
            return H


if __name__ == '__main__':
    # Configure your logging here.
    logging.basicConfig(level=logging.DEBUG)

    G = LoggingGraph()
    G.add_node('foo')
    G.add_nodes_from('bar', weight=8)
    G.remove_node('b')
    G.remove_nodes_from('ar')
    print(list(G.nodes(data=True)))
    G.add_edge(0, 1, weight=10)
    print(list(G.edges(data=True)))
    G.remove_edge(0, 1)
    G.add_edges_from(nx.utils.pairwise(range(4)), weight=10)
    print(list(G.edges(data=True)))
    G.remove_edges_from(nx.utils.pairwise(range(4)))
    print(list(G.edges(data=True)))

    G = LoggingGraph()
    nx.add_path(G, range(10))
    print("subgraph")
    H1 = G.subgraph(range(4), copy=False)
    H2 = G.subgraph(range(4), copy=False)
    print(list(H1.edges()))
    print(list(H2.edges()))
