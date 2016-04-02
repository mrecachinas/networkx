# -*- coding: utf-8 -*-
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
"""Functions for finding an approximate maximum independent set.

An `independent set`_ (or *stable set*) is a set of nodes in a graph, no
two of which are adjacent.

The problem of finding an independent set of maximum cardinality is
called the maximum independent set problem and is an NP-hard
optimization problem.  As such, it is unlikely that there exists an
efficient algorithm for finding a maximum independent set of a graph.

.. _independent set: https://en.wikipedia.org/wiki/Independent_set_(graph_theory)

"""
from networkx.algorithms.approximation import clique_removal
__all__ = ["maximum_independent_set"]
__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""


def maximum_independent_set(G):
    r"""Return an approximate maximum independent set.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    iset : Set
        The apx-maximum independent set

    Notes
    -----
    This approximation algorithm from [1]_ guarantees a
    :math:`O(n / \log^2 n)`-approximation of the maximum independent set
    in the worst case, where *n* is the number of nodes in the graph.

    References
    ----------
    .. [1] Boppana, R., & Halldórsson, M. M. (1992).
       "Approximating maximum independent sets by excluding subgraphs."
       *BIT Numerical Mathematics*, 32(2), 180–196. Springer.
       <https://dx.doi.org/10.1007/BF01994876>

    """
    iset, _ = clique_removal(G)
    return iset
