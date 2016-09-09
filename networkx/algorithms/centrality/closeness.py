#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:
#   Aric Hagberg <aric.hagberg@gmail.com>
#   Pieter Swart <swart@lanl.gov>
#   Sasha Gutfraind <ag362@cornell.edu>
#
"""
Closeness centrality measures.
"""
import networkx as nx

__all__ = ['closeness_centrality']


def closeness_centrality(G, u=None, distance=None, normalized=True):
    r"""Compute closeness centrality for nodes.

    Closeness centrality [1]_ of a node `u` is the reciprocal of the
    sum of the shortest path distances from `u` to all `n-1` other nodes.
    Since the sum of distances depends on the number of nodes in the
    graph, closeness is normalized by the sum of minimum possible
    distances `n-1`.

    .. math::

        C(u) = \frac{n - 1}{\sum_{v=1}^{n-1} d(v, u)},

    where `d(v, u)` is the shortest-path distance between `v` and `u`,
    and `n` is the number of nodes in the graph.

    Notice that higher values of closeness indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph
    u : node, optional
      Return only the value for node u
    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations
    normalized : bool, optional
      If True (default) normalize by the number of nodes in the connected
      part of the graph.

    Returns
    -------
    nodes : dictionary or number
      Dictionary of nodes with closeness centrality as the value, or a
      single number if `u` was specified.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality

    Notes
    -----
    The closeness centrality is normalized to `(n-1)/(|G|-1)` where
    `n` is the number of nodes in the connected part of graph
    containing the node.  If the graph is not completely connected,
    this algorithm computes the closeness centrality for each
    connected part separately.

    If the 'distance' keyword is set to an edge attribute key then the
    shortest-path length will be computed using Dijkstra's algorithm with
    that edge attribute as the edge weight.

    References
    ----------
    .. [1] Freeman, Linton C. "Centrality in social networks
       conceptual clarification." *Social networks* 1.3 (1978):
       215--239. <http://dx.doi.org/10.1016/0378-8733(78)90021-7>

    """
    if G.is_directed():
        G = G.reverse()
    if u is None:
        sp = nx.shortest_path_length(G, weight=distance)
        if normalized:
            return {v: (len(dd) - 1) / sum(dd.values()) for v, dd in sp}
        else:
            return {v: (len(G) - 1) / sum(dd.values()) for v, dd in sp}
    else:
        sp = nx.shortest_path_length(G, source=u, weight=distance)
        if normalized:
            return (len(sp) - 1) / sum(d for v, d in sp)
        else:
            return (len(G) - 1) / sum(d for v, d in sp)
