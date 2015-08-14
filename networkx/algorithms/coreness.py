# coreness.py - functions for computing coreness of a node in a graph
#
# Copyright 2010 Reya Group <http://www.reyagroup.com>.
# Copyright 2010 Alex Levenson <alex@isnotinvain.com>.
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing the coreness value of a node."""
try:
    import numpy as np
    from scipy import optimize
    from scipy.stats.stats import pearsonr
except ImportError:
    is_scipy_available = False
else:
    is_scipy_available = True

import networkx as nx

__all__ = ['coreness']


def coreness(G, return_correlation=False):
    """Returns a dictionary mapping each node in the graph to its
    coreness value.

    This function requires SciPy.

    The *coreness* of a node is a measure of to what degree a node is a
    member of the core of the graph [1].

    Parameters
    ----------
    G : NetworkX graph

    return_correlation : bool
        Whether to return the correlation between the computed coreness
        and the ideal core/periphery structure of the graph.

    Returns
    -------
    dictionary or tuple
        If `return_correlation` is False, this function returns a
        dictionary that maps each node in `G` to its coreness value. If
        `return_correlation` is True, this function returns a pair, the
        first element of which is that dictionary and the second element
        of which is a number representing the correlation between the
        computed coreness and the ideal core/periphery structure of the
        graph. The correlation is a number between -1 and +1.

    Raises
    ------
    NetworkXError
        If SciPy is not available.

    References
    ----------
    .. [1] Borgatti, Stephen P., and Martin G. Everett.
           "Models of Core/Periphery Structures."
           *Social Networks* 21.4 (2000): 375--395.
           <http://dx.doi.org/10.1016/S0378-8733(99)00019-2>

    """
    if not is_scipy_available:
        raise NetworkXError('coreness requires SciPy: https://scipy.org/')

    def core_fitness(C, *args):
        """Returns the negative correlation betwen ``C`` and the first
        positional argument in ``args``.

        This is required because :func:`scipy.optimize` is a
        *minimization* algorithm, whereas our goal is to *maximize*
        correlation.

        """
        A = args[0]
        C = np.matrix(C)
        # TODO This is element-wise multiplication. Is that the intent?
        Cij = np.multiply(C, C.transpose())
        return -pearsonr(A.flat, Cij.flat)[0]

    A = nx.to_numpy_matrix(G)
    # The optimizer needs a starting point; for now we use a random
    # starting point.
    #
    # TODO Can we do better? Is this important? Maybe use constraint or
    # centrality?
    initialC = np.random.rand(len(A))
    # Run a BFGS optimizer that optimizes correlation between calculated
    # coreness scores and the ideal model.
    bounds = [(0, 1) for v in G]
    solve = optimize.fmin_l_bfgs_b
    best = solve(core_fitness, initialC, args=(A, None), approx_grad=True,
                 bounds=bounds)
    coreness_values = dict(zip(G, best[0]))
    if return_correlation: 
        return coreness_values, -best[1]
    return coreness_values
