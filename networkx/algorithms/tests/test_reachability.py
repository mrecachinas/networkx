# test_reachability.py - unit tests for the reachability module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.reachability` module."""
from nose.tools import assert_false
from nose.tools import assert_true

from networkx import DiGraph
from networkx import empty_graph
from networkx import is_reachable
from networkx import path_graph


class TestReachability(object):
    """Unit tests for the
    :func:`~networkx.algorithms.reachability.is_reachable` function.

    """

    def test_undirected_disconnected(self):
        G = empty_graph(2)
        assert_false(is_reachable(G, 0, 1))

    def test_undirected_connected(self):
        G = path_graph(2)
        assert_true(is_reachable(G, 0, 1))

    def test_directed_disconnected(self):
        G = DiGraph(empty_graph(2))
        assert_false(is_reachable(G, 0, 1))

    def test_directed_not_reachable(self):
        G = DiGraph([(0, 1), (1, 2)])
        assert_false(is_reachable(G, 2, 0))

    def test_directed_reachable(self):
        G = DiGraph([(0, 1), (1, 2)])
        assert_true(is_reachable(G, 0, 2))

    def test_path_length(self):
        G = path_graph(4)
        assert_true(is_reachable(G, 0, 2, path_length=2))

    def test_path_length_too_short(self):
        G = path_graph(4)
        assert_false(is_reachable(G, 0, 3, path_length=2))
