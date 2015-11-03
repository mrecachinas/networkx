# reachability.py - functions for deciding whether nodes are reachable
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for deciding whether nodes are reachable from other nodes.

"""
from __future__ import division

import math

__all__ = ['is_reachable']


# TODO This is appropriate for directed graphs. For undirected graphs
# there is actually a more space-efficient algorithm. For regular
# directed graphs, there is a more space-efficient algorithm.
def is_reachable(G, s, t, path_length=None):
    r"""Returns ``True`` if and only if there is a path from ``s`` to
    ``t`` in the graph ``G``.

    Parameters
    ----------
    G : NetworkX graph

    s, t: nodes
        Nodes in the graph ``G``.

    path_length: int
        If specified, this function will only look for paths of length
        at most ``path_length``. If not specified, paths of any length
        (that is, up to ``len(G) - 1``) will be considered.

    Returns
    -------
    bool
        ``True`` if and only if there is a path from node ``s`` to node
        ``t`` in ``G``.

    See also
    --------
    shortest_path

    Notes
    -----
    This function is more space-efficient than using, for example, the
    :func:`~networkx.shortest_path` function. Other than the memory
    required to store the graph, this function requires only `O(\log n)`
    additional memory, where *n* is the number of nodes in the graph. In
    contrast, the :func:`~networkx.shortest_path` function requires `O(n
    \log n)` additional memory.

    Examples
    --------
    To check if each node in a set is reachable from some node in
    another set::

        >>> from networkx import DiGraph
        >>> from networkx import is_reachable
        >>> from networkx.utils import pairwise
        >>> G = DiGraph(pairwise(range(10)))
        >>> sources = {2 * i for i in range(5)}
        >>> targets = {2 * i + 1 for i in range(5)}
        >>> all(any(is_reachable(G, u, v) for u in sources) for v in targets)
        True

    """
    if path_length is None:
        return is_reachable(G, s, t, path_length=len(G) - 1)
    if path_length == 0:
        return s == t
    if path_length == 1:
        return s == t or t in G[s]
    # TODO This `any` expression is parallelizable.
    return any(is_reachable(G, s, v, path_length // 2)
               and is_reachable(G, v, t, math.ceil(path_length / 2))
               for v in G)
