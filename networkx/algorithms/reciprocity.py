# reciprocity.py - global reciprocity measures for graphs
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing reciprocity measures of a graph."""
from __future__ import division

from itertools import permutations

from networkx import density
from networkx.utils import not_implemented_for

__all__ = ['reciprocity', 'correlation_reciprocity']


@not_implemented_for('undirected')
def reciprocity(G):
    # For simple digraphs, each entry in the sum will be one if and only
    # if there is an edge from u to v and from v to u. For
    # multidigraphs, the minimum gives the number of pairs of reciprocal
    # edges joining u and v.
    bidirectional = sum(min(G.number_of_edges(u, v), G.number_of_edges(v, u))
                        for u, v in permutations(G, 2))
    return bidirectional / G.number_of_edges()


@not_implemented_for('undirected')
def correlation_reciprocity(G):
    r = reciprocity(G)
    d = density(G)
    return (r - d) / (1 - d)
