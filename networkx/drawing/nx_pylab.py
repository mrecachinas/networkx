"""
**********
Matplotlib
**********

Draw networks with matplotlib.

See Also
--------

matplotlib:     http://matplotlib.org/

pygraphviz:     http://pygraphviz.github.io/

"""
# Author: Aric Hagberg (hagberg@lanl.gov)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

#    Copyright (C) 2008 by
#    Maciej Kurant <maciej.kurant@epfl.ch>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
from __future__ import division

from collections import Counter
from itertools import chain

try:
    import matplotlib
    import matplotlib.path
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
except ImportError:
    is_matplotlib_available = False
except RuntimeError:
    # Unable to open display.
    is_matplotlib_available = True
else:
    is_matplotlib_available = True

import networkx as nx
from networkx.drawing.layout import shell_layout, circular_layout, \
    spectral_layout, spring_layout, random_layout

__all__ = ['draw',
           'draw_circular',
           'draw_graphviz',
           'draw_networkx',
           'draw_networkx_nodes',
           'draw_networkx_edges',
           'draw_networkx_labels',
           'draw_networkx_edge_labels',
           'draw_path',
           'draw_paths',
           'draw_random',
           'draw_spectral',
           'draw_spring',
           'draw_shell']


#: The default distance between nodes drawn in a path.
DEFAULT_SHIFT = 0.02


def draw(G, pos=None, ax=None, hold=None, **kwds):
    """Draw the graph G with Matplotlib.

    Draw the graph as a simple representation with no node
    labels or edge labels and using the full Matplotlib figure area
    and no axis labels by default.  See draw_networkx() for more
    full-featured drawing that allows title, axis labels etc.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.

    ax : Matplotlib Axes object, optional
       Draw the graph in specified Matplotlib axes.

    hold : bool, optional
       Set the Matplotlib hold state.  If True subsequent draw
       commands will be added to the current axes.

    kwds : optional keywords
       See networkx.draw_networkx() for a description of optional keywords.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    See Also
    --------
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()

    Notes
    -----
    This function has the same name as pylab.draw and pyplot.draw
    so beware when using

    >>> from networkx import *

    since you might overwrite the pylab.draw function.

    With pyplot use

    >>> import matplotlib.pyplot as plt
    >>> import networkx as nx
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)  # networkx draw()
    >>> plt.draw()  # pyplot draw()

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        cf = plt.gcf()
    else:
        cf = ax.get_figure()
    cf.set_facecolor('w')
    if ax is None:
        if cf._axstack() is None:
            ax = cf.add_axes((0, 0, 1, 1))
        else:
            ax = cf.gca()

    if 'with_labels' not in kwds:
        kwds['with_labels'] = 'labels' in kwds
    b = plt.ishold()
    # allow callers to override the hold state by passing hold=True|False
    h = kwds.pop('hold', None)
    if h is not None:
        plt.hold(h)
    try:
        draw_networkx(G, pos=pos, ax=ax, **kwds)
        ax.set_axis_off()
        plt.draw_if_interactive()
    except:
        plt.hold(b)
        raise
    plt.hold(b)
    return


def draw_networkx(G, pos=None, arrows=True, with_labels=True, **kwds):
    """Draw the graph G using Matplotlib.

    Draw the graph with Matplotlib with options for node positions,
    labeling, titles, and many other drawing features.
    See draw() for simple drawing without labels or axes.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary, optional
       A dictionary with nodes as keys and positions as values.
       If not specified a spring layout positioning will be computed.
       See networkx.layout for functions that compute node positions.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    with_labels :  bool, optional (default=True)
       Set to True to draw labels on the nodes.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional (default G.nodes())
       Draw only specified nodes

    edgelist : list, optional (default=G.edges())
       Draw only specified edges

    node_size : scalar or array, optional (default=300)
       Size of nodes.  If an array is specified it must be the
       same length as nodelist.

    node_color : color string, or array of floats, (default='r')
       Node color. Can be a single color format string,
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string, optional (default='o')
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8'.

    alpha : float, optional (default=1.0)
       The node and edge transparency

    cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of nodes

    vmin,vmax : float, optional (default=None)
       Minimum and maximum for node colormap scaling

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    width : float, optional (default=1.0)
       Line width of edges

    edge_color : color string, or array of floats (default='r')
       Edge color. Can be a single color format string,
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    edge_cmap : Matplotlib colormap, optional (default=None)
       Colormap for mapping intensities of edges

    edge_vmin,edge_vmax : floats, optional (default=None)
       Minimum and maximum for edge colormap scaling

    style : string, optional (default='solid')
       Edge line style (solid|dashed|dotted,dashdot)

    labels : dictionary, optional (default=None)
       Node labels in a dictionary keyed by node of text labels

    font_size : int, optional (default=12)
       Font size for text labels

    font_color : string, optional (default='k' black)
       Font color string

    font_weight : string, optional (default='normal')
       Font weight

    font_family : string, optional (default='sans-serif')
       Font family

    label : string, optional
        Label for graph legend

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nx.draw(G)
    >>> nx.draw(G,pos=nx.spring_layout(G)) # use spring layout

    >>> import matplotlib.pyplot as plt
    >>> limits=plt.axis('off') # turn of axis

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if pos is None:
        pos = nx.drawing.spring_layout(G)  # default to spring layout

    node_collection = draw_networkx_nodes(G, pos, **kwds)
    edge_collection = draw_networkx_edges(G, pos, arrows=arrows, **kwds)
    if with_labels:
        draw_networkx_labels(G, pos, **kwds)
    plt.draw_if_interactive()


def draw_networkx_nodes(G, pos,
                        nodelist=None,
                        node_size=300,
                        node_color='r',
                        node_shape='o',
                        alpha=1.0,
                        cmap=None,
                        vmin=None,
                        vmax=None,
                        ax=None,
                        linewidths=None,
                        label=None,
                        **kwds):
    """Draw the nodes of the graph G.

    This draws only the nodes of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    nodelist : list, optional
       Draw only specified nodes (default G.nodes())

    node_size : scalar or array
       Size of nodes (default=300).  If an array is specified it must be the
       same length as nodelist.

    node_color : color string, or array of floats
       Node color. Can be a single color format string (default='r'),
       or a  sequence of colors with the same length as nodelist.
       If numeric values are specified they will be mapped to
       colors using the cmap and vmin,vmax parameters.  See
       matplotlib.scatter for more details.

    node_shape :  string
       The shape of the node.  Specification is as matplotlib.scatter
       marker, one of 'so^>v<dph8' (default='o').

    alpha : float
       The node transparency (default=1.0)

    cmap : Matplotlib colormap
       Colormap for mapping intensities of nodes (default=None)

    vmin,vmax : floats
       Minimum and maximum for node colormap scaling (default=None)

    linewidths : [None | scalar | sequence]
       Line width of symbol border (default =1.0)

    label : [None| string]
       Label for legend

    Returns
    -------
    matplotlib.collections.PathCollection
        `PathCollection` of the nodes.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> nodes=nx.draw_networkx_nodes(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_edges()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if nodelist is None:
        nodelist = list(G)

    if not nodelist or len(nodelist) == 0:  # empty nodelist, no drawing
        return None

    try:
        xy = numpy.asarray([pos[v] for v in nodelist])
    except KeyError as e:
        raise nx.NetworkXError('Node %s has no position.'%e)
    except ValueError:
        raise nx.NetworkXError('Bad value in node positions.')

    node_collection = ax.scatter(xy[:, 0], xy[:, 1],
                                 s=node_size,
                                 c=node_color,
                                 marker=node_shape,
                                 cmap=cmap,
                                 vmin=vmin,
                                 vmax=vmax,
                                 alpha=alpha,
                                 linewidths=linewidths,
                                 label=label)

    node_collection.set_zorder(2)
    return node_collection


def draw_networkx_edges(G, pos,
                        edgelist=None,
                        width=1.0,
                        edge_color='k',
                        style='solid',
                        alpha=1.0,
                        edge_cmap=None,
                        edge_vmin=None,
                        edge_vmax=None,
                        ax=None,
                        arrows=True,
                        label=None,
                        **kwds):
    """Draw the edges of the graph G.

    This draws only the edges of the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    edgelist : collection of edge tuples
       Draw only specified edges(default=G.edges())

    width : float, or array of floats
       Line width of edges (default=1.0)

    edge_color : color string, or array of floats
       Edge color. Can be a single color format string (default='r'),
       or a sequence of colors with the same length as edgelist.
       If numeric values are specified they will be mapped to
       colors using the edge_cmap and edge_vmin,edge_vmax parameters.

    style : string
       Edge line style (default='solid') (solid|dashed|dotted,dashdot)

    alpha : float
       The edge transparency (default=1.0)

    edge_ cmap : Matplotlib colormap
       Colormap for mapping intensities of edges (default=None)

    edge_vmin,edge_vmax : floats
       Minimum and maximum for edge colormap scaling (default=None)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    arrows : bool, optional (default=True)
       For directed graphs, if True draw arrowheads.

    label : [None| string]
       Label for legend

    Returns
    -------
    matplotlib.collection.LineCollection
        `LineCollection` of the edges

    Notes
    -----
    For directed graphs, "arrows" (actually just thicker stubs) are drawn
    at the head end.  Arrows can be turned off with keyword arrows=False.
    Yes, it is ugly but drawing proper arrows with Matplotlib this
    way is tricky.

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edges=nx.draw_networkx_edges(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_labels()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        from matplotlib.colors import colorConverter, Colormap
        from matplotlib.collections import LineCollection
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if edgelist is None:
        edgelist = list(G.edges())

    if not edgelist or len(edgelist) == 0:  # no edges!
        return None

    # set edge positions
    edge_pos = numpy.asarray([(pos[e[0]], pos[e[1]]) for e in edgelist])

    if not cb.iterable(width):
        lw = (width,)
    else:
        lw = width

    if not cb.is_string_like(edge_color) \
           and cb.iterable(edge_color) \
           and len(edge_color) == len(edge_pos):
        if numpy.alltrue([cb.is_string_like(c)
                         for c in edge_color]):
            # (should check ALL elements)
            # list of color letters such as ['k','r','k',...]
            edge_colors = tuple([colorConverter.to_rgba(c, alpha)
                                 for c in edge_color])
        elif numpy.alltrue([not cb.is_string_like(c)
                           for c in edge_color]):
            # If color specs are given as (rgb) or (rgba) tuples, we're OK
            if numpy.alltrue([cb.iterable(c) and len(c) in (3, 4)
                             for c in edge_color]):
                edge_colors = tuple(edge_color)
            else:
                # numbers (which are going to be mapped with a colormap)
                edge_colors = None
        else:
            raise ValueError('edge_color must consist of either color names or numbers')
    else:
        if cb.is_string_like(edge_color) or len(edge_color) == 1:
            edge_colors = (colorConverter.to_rgba(edge_color, alpha), )
        else:
            raise ValueError('edge_color must be a single color or list of exactly m colors where m is the number or edges')

    edge_collection = LineCollection(edge_pos,
                                     colors=edge_colors,
                                     linewidths=lw,
                                     antialiaseds=(1,),
                                     linestyle=style,
                                     transOffset = ax.transData,
                                     )

    edge_collection.set_zorder(1)  # edges go behind nodes
    edge_collection.set_label(label)
    ax.add_collection(edge_collection)

    # Note: there was a bug in mpl regarding the handling of alpha values for
    # each line in a LineCollection.  It was fixed in matplotlib in r7184 and
    # r7189 (June 6 2009).  We should then not set the alpha value globally,
    # since the user can instead provide per-edge alphas now.  Only set it
    # globally if provided as a scalar.
    if cb.is_numlike(alpha):
        edge_collection.set_alpha(alpha)

    if edge_colors is None:
        if edge_cmap is not None:
            assert(isinstance(edge_cmap, Colormap))
        edge_collection.set_array(numpy.asarray(edge_color))
        edge_collection.set_cmap(edge_cmap)
        if edge_vmin is not None or edge_vmax is not None:
            edge_collection.set_clim(edge_vmin, edge_vmax)
        else:
            edge_collection.autoscale()

    arrow_collection = None

    if G.is_directed() and arrows:

        # a directed graph hack
        # draw thick line segments at head end of edge
        # waiting for someone else to implement arrows that will work
        arrow_colors = edge_colors
        a_pos = []
        p = 1.0-0.25  # make head segment 25 percent of edge length
        for src, dst in edge_pos:
            x1, y1 = src
            x2, y2 = dst
            dx = x2-x1   # x offset
            dy = y2-y1   # y offset
            d = numpy.sqrt(float(dx**2 + dy**2))  # length of edge
            if d == 0:   # source and target at same position
                continue
            if dx == 0:  # vertical edge
                xa = x2
                ya = dy*p+y1
            if dy == 0:  # horizontal edge
                ya = y2
                xa = dx*p+x1
            else:
                theta = numpy.arctan2(dy, dx)
                xa = p*d*numpy.cos(theta)+x1
                ya = p*d*numpy.sin(theta)+y1

            a_pos.append(((xa, ya), (x2, y2)))

        arrow_collection = LineCollection(a_pos,
                                colors=arrow_colors,
                                linewidths=[4*ww for ww in lw],
                                antialiaseds=(1,),
                                transOffset = ax.transData,
                                )

        arrow_collection.set_zorder(1)  # edges go behind nodes
        arrow_collection.set_label(label)
        ax.add_collection(arrow_collection)

    # update view
    minx = numpy.amin(numpy.ravel(edge_pos[:, :, 0]))
    maxx = numpy.amax(numpy.ravel(edge_pos[:, :, 0]))
    miny = numpy.amin(numpy.ravel(edge_pos[:, :, 1]))
    maxy = numpy.amax(numpy.ravel(edge_pos[:, :, 1]))

    w = maxx-minx
    h = maxy-miny
    padx,  pady = 0.05*w, 0.05*h
    corners = (minx-padx, miny-pady), (maxx+padx, maxy+pady)
    ax.update_datalim(corners)
    ax.autoscale_view()

#    if arrow_collection:

    return edge_collection


def draw_networkx_labels(G, pos,
                         labels=None,
                         font_size=12,
                         font_color='k',
                         font_family='sans-serif',
                         font_weight='normal',
                         alpha=1.0,
                         bbox=None,
                         ax=None,
                         **kwds):
    """Draw node labels on the graph G.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    labels : dictionary, optional (default=None)
       Node labels in a dictionary keyed by node of text labels

    font_size : int
       Font size for text labels (default=12)

    font_color : string
       Font color string (default='k' black)

    font_family : string
       Font family (default='sans-serif')

    font_weight : string
       Font weight (default='normal')

    alpha : float
       The text transparency (default=1.0)

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    Returns
    -------
    dict
        `dict` of labels keyed on the nodes

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> labels=nx.draw_networkx_labels(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html


    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_edge_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()

    if labels is None:
        labels = dict((n, n) for n in G.nodes())

    # set optional alignment
    horizontalalignment = kwds.get('horizontalalignment', 'center')
    verticalalignment = kwds.get('verticalalignment', 'center')

    text_items = {}  # there is no text collection so we'll fake one
    for n, label in labels.items():
        (x, y) = pos[n]
        if not cb.is_string_like(label):
            label = str(label)  # this will cause "1" and 1 to be labeled the same
        t = ax.text(x, y,
                  label,
                  size=font_size,
                  color=font_color,
                  family=font_family,
                  weight=font_weight,
                  horizontalalignment=horizontalalignment,
                  verticalalignment=verticalalignment,
                  transform=ax.transData,
                  bbox=bbox,
                  clip_on=True,
                  )
        text_items[n] = t

    return text_items


def draw_networkx_edge_labels(G, pos,
                              edge_labels=None,
                              label_pos=0.5,
                              font_size=10,
                              font_color='k',
                              font_family='sans-serif',
                              font_weight='normal',
                              alpha=1.0,
                              bbox=None,
                              ax=None,
                              rotate=True,
                              **kwds):
    """Draw edge labels.

    Parameters
    ----------
    G : graph
       A networkx graph

    pos : dictionary
       A dictionary with nodes as keys and positions as values.
       Positions should be sequences of length 2.

    ax : Matplotlib Axes object, optional
       Draw the graph in the specified Matplotlib axes.

    alpha : float
       The text transparency (default=1.0)

    edge_labels : dictionary
       Edge labels in a dictionary keyed by edge two-tuple of text
       labels (default=None). Only labels for the keys in the dictionary
       are drawn.

    label_pos : float
       Position of edge label along edge (0=head, 0.5=center, 1=tail)

    font_size : int
       Font size for text labels (default=12)

    font_color : string
       Font color string (default='k' black)

    font_weight : string
       Font weight (default='normal')

    font_family : string
       Font family (default='sans-serif')

    bbox : Matplotlib bbox
       Specify text box shape and colors.

    clip_on : bool
       Turn on clipping at axis boundaries (default=True)

    Returns
    -------
    dict
        `dict` of labels keyed on the edges

    Examples
    --------
    >>> G=nx.dodecahedral_graph()
    >>> edge_labels=nx.draw_networkx_edge_labels(G,pos=nx.spring_layout(G))

    Also see the NetworkX drawing examples at
    http://networkx.github.io/documentation/latest/gallery.html

    See Also
    --------
    draw()
    draw_networkx()
    draw_networkx_nodes()
    draw_networkx_edges()
    draw_networkx_labels()
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cbook as cb
        import numpy
    except ImportError:
        raise ImportError("Matplotlib required for draw()")
    except RuntimeError:
        print("Matplotlib unable to open display")
        raise

    if ax is None:
        ax = plt.gca()
    if edge_labels is None:
        labels = dict(((u, v), d) for u, v, d in G.edges(data=True))
    else:
        labels = edge_labels
    text_items = {}
    for (n1, n2), label in labels.items():
        (x1, y1) = pos[n1]
        (x2, y2) = pos[n2]
        (x, y) = (x1 * label_pos + x2 * (1.0 - label_pos),
                  y1 * label_pos + y2 * (1.0 - label_pos))

        if rotate:
            angle = numpy.arctan2(y2-y1, x2-x1)/(2.0*numpy.pi)*360  # degrees
            # make label orientation "right-side-up"
            if angle > 90:
                angle -= 180
            if angle < - 90:
                angle += 180
            # transform data coordinate angle to screen coordinate angle
            xy = numpy.array((x, y))
            trans_angle = ax.transData.transform_angles(numpy.array((angle,)),
                                                        xy.reshape((1, 2)))[0]
        else:
            trans_angle = 0.0
        # use default box of white with white border
        if bbox is None:
            bbox = dict(boxstyle='round',
                        ec=(1.0, 1.0, 1.0),
                        fc=(1.0, 1.0, 1.0),
                        )
        if not cb.is_string_like(label):
            label = str(label)  # this will cause "1" and 1 to be labeled the same

        # set optional alignment
        horizontalalignment = kwds.get('horizontalalignment', 'center')
        verticalalignment = kwds.get('verticalalignment', 'center')

        t = ax.text(x, y,
                    label,
                    size=font_size,
                    color=font_color,
                    family=font_family,
                    weight=font_weight,
                    horizontalalignment=horizontalalignment,
                    verticalalignment=verticalalignment,
                    rotation=trans_angle,
                    transform=ax.transData,
                    bbox=bbox,
                    zorder=1,
                    clip_on=True,
                    )
        text_items[(n1, n2)] = t

    return text_items


def draw_circular(G, **kwargs):
    """Draw the graph G with a circular layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, circular_layout(G), **kwargs)


def draw_random(G, **kwargs):
    """Draw the graph G with a random layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, random_layout(G), **kwargs)


def draw_spectral(G, **kwargs):
    """Draw the graph G with a spectral layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, spectral_layout(G), **kwargs)


def draw_spring(G, **kwargs):
    """Draw the graph G with a spring layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    draw(G, spring_layout(G), **kwargs)


def draw_shell(G, **kwargs):
    """Draw networkx graph with shell layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords,
       with the exception of the pos parameter which is not used by this
       function.
    """
    nlist = kwargs.get('nlist', None)
    if nlist is not None:
        del(kwargs['nlist'])
    draw(G, shell_layout(G, nlist=nlist), **kwargs)


def draw_graphviz(G, prog="neato", **kwargs):
    """Draw networkx graph with graphviz layout.

    Parameters
    ----------
    G : graph
       A networkx graph

    prog : string, optional
      Name of Graphviz layout program

    kwargs : optional keywords
       See networkx.draw_networkx() for a description of optional keywords.
    """
    pos = nx.drawing.graphviz_layout(G, prog)
    draw(G, pos, **kwargs)


def draw_nx(G, pos, **kwds):
    """For backward compatibility; use draw or draw_networkx."""
    draw(G, pos, **kwds)


def is_valid_edge_path(G, path):
    """Returns ``True`` if and only if the path consists of consecutive edges
    in ``G``.

    """
    return (all(v == w and v in G[u] and z in G[w]
                for (u, v), (w, z) in zip(path, path[1:]))
            and G.has_edge(*path[0]) and G.has_edge(*path[-1]))


def is_valid_node_path(G, path):
    """Returns ``True`` if and only if the path is a valid node path in ``G``.

    This function does not consider a single node to be a valid path.

    """
    return len(path) >= 2 and all(v in G[u] for u, v in zip(path, path[1:]))


def to_node_path(path):
    """Converts a list of consecutive edges to a list of nodes representing the
    same path.

    For example::

        >>> to_node_path([(10, 3), (3, 6), (6, 11)]
        [10, 3, 6, 11]

    Pre-condition: the list of edges is a valid edge path in a graph.

    """
    return [u for u, v in path] + [path[-1][1]]


def to_edge_path(path, G=None):
    """Converts a node path to an edge path.

    For example::

        >>> to_edge_path([10, 3, 6, 11])
        [(10, 3), (3, 6), (6, 11)]

    If ``G`` is given, then the path validity is checked. In this case,
    ``path`` may be provided as an edge path; in this case it is
    returned directly.

    """
    if G is None:
        return list(zip(path, path[1:]))
    if is_valid_node_path(G, path):
        return to_edge_path(path)
    if is_valid_edge_path(G, path):
        return path
    raise ValueError('Not a valid path: {}'.format(path))


def vector_length(v):
    """Returns the Euclidean norm of the vector ``v``, a NumPy array."""
    return math.sqrt(numpy.dot(v, v))


def norm_vector(v):
    """Returns a vector of norm one, pointing in the same direction as
    ``v``, a NumPy array.

    """
    l = vector_length(v)
    if l == 0:
        raise ValueError('Vector {} has length 0!'.format(v))
    return v / l


def perpendicular_vector(v):
    """Returns a two-dimensional vector perpendicular to ``v``, a
    two-dimensional NumPy array.

    """
    return numpy.array([v[1],-v[0]])


def crossing_point(p1a, p1b, p2a, p2b):
    """Returns the crossing of line1 defined by two points p1a and p1b,
    and line2 defined by two points p2a, p2b.

    All points should be of format numpy.array([x,y]).

    If line1 and line2 are parallel then returns None.

    """
    # See e.g.: http://stackoverflow.com/questions/153592/how-do-i-determine-the-intersection-point-of-two-lines-in-gdi

    if tuple(p1a) == tuple(p1b) or tuple(p2a) == tuple(p2b):
        raise ValueError('Two points defining a line are identical!')
    v1 = p1b - p1a
    v2 = p2b - p2a
    x12 = p2a - p1a
    D = numpy.dot(v1, v1) * numpy.dot(v2, v2) - numpy.dot(v1, v2) * numpy.dot(v1, v2)
    if D == 0:
        # Lines are parallel!
        return None
    a = (numpy.dot(v2, v2) * numpy.dot(v1, x12) - numpy.dot(v1, v2) * numpy.dot(v2, x12)) / D
    return p1a + v1 * a


def is_layout_normalized(pos):
    """Returns ``True`` if and only if all the values of the given
    dictionary are points within the unit square with center `(.5, .5)`.

    """
    return all(0 <= x <= 1 and 0 <= y <= 1 for x, y in pos.values())
    # A = numpy.asarray(pos.values())
    # return (0 <= min(A[:, 0]) <= max(A[:, 0]) <= 1
    #         and 0 <= min(A[:, 1]) <= max(A[:, 1]) <= 1)


# TODO This already almost exists as _rescale_layout in layout.py
#
# TODO This should be `normalized` and return a new dictionary.
def normalize_layout(pos):
    """All node positions are normalized to fit in the unit square
    centered at `(.5, .5)`.

    """
    if len(pos) == 1:
        v = next(iter(pos))
        pos[v] = numpy.array([0.5, 0.5])
        return
    A = numpy.asarray(pos.values())
    x0, y0, x1, y1 = min(A[:, 0]), min(A[:, 1]), max(A[:, 0]), max(A[:, 1])
    for v in pos:
        pos[v] = (pos[v] - (x0, y0)) / (x1 - x0, y1 - y0) * 0.8 + (0.1, 0.1)
    return


def draw_path(G, pos, path, shifts=None, color='r', linestyle='solid',
              linewidth=1.0):
    """Draw a path in the given graph.

    Parameters
    ----------
    pos : dictionary
        A node layout used to draw G. Must be normalized so that both
        the *x* and *y* values of the points are in the interval [0, 1]
        (for example, as returned by :func:`normalize_layout`).

    path : list
        A list of nodes or a list of edges representing a valid path in
        the graph.

    shifts : list

        A list whose length equals the length of the given path (that
        is, as an edge path) specifying the distances at which to place
        the nodes in the path.

    color : string
        Must be one of ``('b', 'g', 'r', 'c', 'm', 'y')``.

    linestyle : string
        Must be one of ``('solid', 'dashed', 'dashdot', 'dotted')``.

    linewidth : float
        The width of the line in number of pixels.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> import networkx as nx
    >>> G = nx.krackhardt_kite_graph()
    >>> pos = nx.drawing.spring_layout(G)
    >>> normalize_layout(pos)
    >>> nx.draw(G, pos)
    >>> path = networkx.shortest_path(G, 3, 9)
    >>> nx.draw_path(G, pos, path, color='g', linewidth=2)
    >>> plt.show()
    
    """
    if not is_layout_normalized(pos):
        raise ValueError('Layout is not normalized; use normalize_layout().')
    edge_path = to_edge_path(path, G)
    # If the path is empty, draw nothing.
    if not edge_path:
        return
    if shifts is None:
        shifts = [DEFAULT_SHIFT] * len(edge_path)
    if len(shifts) != len(edge_path):
        raise ValueError('The length of `shifts` does not match that of'
                         ' `edge_path`.')

    # Store the positions of the edges.
    edge_pos = [numpy.array([pos[u], pos[v]]) for u, v in edge_path]
    # Shift each edge along a perpendicular vector of length determined
    # by `shifts`.
    edge_shifts = [shift * perpendicular_vector(norm_vector(t - s))
                   for shift, (s, t) in zip(shifts, edge_pos)]

      
    # prepare vertices and codes for object
    # matplotlib.path.Path(vertices, codes) - the path to display

    # vertices: an Nx2 float array of vertices  (not the same as graph nodes!)

    # codes: an N-length uint8 array of vertex types (such as MOVETO,
    # LINETO, CURVE4) - a cube Bezier curve

    # See e.g. http://matplotlib.sourceforge.net/api/path_api.html

    # First, for every corner (that is, every node on the path), we
    # define four points to help smooth it.
    corners = []
    
    # The first corner is on a straight line, making it easier to
    # process the next ones.
    p1a, p1b = edge_pos[0] + edge_shifts[0]
    V1 = p1b-p1a
    corners.append([p1a, p1a + 0.1 * V1, p1a + 0.1 * V1, p1a + 0.2 * V1])
   
    #All real corners - with edes on both sides
    for i in range(len(edge_pos)-1):
        # crossing point of the original (i)th and (i + 1)th edges 
        p_node = edge_pos[i][1]
        # two points defining the shifted (i)th edge 
        p1a, p1b = edge_pos[i] + edge_shifts[i]
        # two points defining the shifted (i + 1)th edge
        p2a, p2b = edge_pos[i + 1] + edge_shifts[i + 1]
        # unit vector along the (i)th edge
        V1 = norm_vector(p1b - p1a)
        # unit vector along the (i + 1)th edge
        V2 = norm_vector(p2b - p2a)
        # a point that splits evenly the angle between the original
        # (i)th and (i + 1)th edges
        p_middle_angle = p_node + (V2 - V1)
        # crossing point of the shifted (i)th and (i + 1)th edges
        c12 = crossing_point(p1a, p1b, p2a, p2b)
        # Check if the edges are parallel.
        if c12 is None:
            c12 = (p1b + p2a) / 2
            p_middle_angle = c12
        # crossing point of the shifted (i)th edge and the
        # middle-angle-line
        c1 = crossing_point(p1a, p1b, p_node, p_middle_angle)
        # crossing point of the shifted (i + 1)th edge and the
        # middle-angle-line
        c2 = crossing_point(p2a, p2b, p_node, p_middle_angle)
        # average shift - a reasonable normalized distance measure
        D= 0.5 * (shifts[i] + shifts[i + 1])

        # if the crossing point c12 is relatively close to the node
        if vector_length(p_node - c12) < 2.5 * D:
            # then c12 defines two consecutive reference points in the
            # cube Bezier curve
            corners.append([c12 - D * V1, c12, c12, c12 + D * V2])
        # the crossing point c12 is NOT relatively close to the node
        else:
            P1 = p1b + D * V1
            if numpy.dot(c1 - P1, V1) < 0:
                P1 = c1
            P2 = p2a - D * V2
            if numpy.dot(c2 - P2, V2) > 0:
                P2 = c2
            corners.append([P1 - D * V1, P1, P2, P2 + D * V2])

    # The last corner: on one line, easier to process next
    p1a, p1b = edge_pos[-1] + edge_shifts[-1]
    V1 = p1b - p1a
    corners.append([p1b - 0.2 * V1, p1b - 0.1 * V1, p1b - 0.1 * V1, p1b])
 
    # Now, based on corners, we prepare vertices and codes
    vertices = []
    codes = []
    # First operation must be a MOVETO, move pen to first vertex on the path
    vertices += [corners[0][0]]
    codes += [Path.MOVETO]

    for i, corner in enumerate(corners):
        # If there is not enough space to draw a corner, then replace
        # the last two vertices from the previous section, by the last
        # two vertices of the current section
        if i > 0:
            if vector_length(norm_vector(corner[0] - vertices[-1])
                             - norm_vector(corner[1] - corner[0])) > 1:
                vertices.pop();
                vertices.pop();
                vertices += corner[-2:]
                continue
        
        codes += [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        vertices += corner

    # Finally, create a nice path and display it
    path = Path(vertices, codes)
    patch = PathPatch(path, edgecolor=color, linestyle=linestyle,
                      linewidth=linewidth, fill=False, alpha=1)
    ax = matplotlib.pylab.gca()
    ax.add_patch(patch)
    ax.update_datalim(((0, 0), (1, 1)))
    ax.autoscale_view()
    return


def draw_paths(G, pos, paths, max_shift=0.02, linewidth=2.0):
    """Draw each path specified in ``paths`` in the graph ``G``.

    Colors and line styles are chosen automatically.

    All paths are visible, no path section can be covered by another
    path.

    Parameters
    ----------
    pos : dictionary
        A node layout used to draw G. Must be normalized so that both
        the *x* and *y* values of the points are in the interval [0, 1]
        (for example, as returned by :func:`normalize_layout`).

    paths : list
        A list of paths. Each path must be a list of nodes or a list of
        edges representing a valid path in the graph.

    max_shift : float
        Maximum allowable distance between an edge and a path traversing
        it.

    linewidth : float
        The width of the line in number of pixels.

    Examples
    --------

    Each path can be provided as a list of edges or as a list of nodes::

        >>> import matplotlib.pyplot as plt
        >>> import networkx as nx
        >>> G = nx.krackhardt_kite_graph()
        >>> G.remove_node(9)
        >>> path1 = networkx.shortest_path(G, 2, 8)
        >>> path2 = networkx.shortest_path(G, 0, 8)
        >>> path3 = [(1, 0), (0, 5), (5, 7)]  # A path as a list of edges.
        >>> path4 = [3, 5, 7, 6]  # A path as a list of nodes.
        >>> pos = nx.drawing.spring_layout(G)
        >>> normalize_layout(pos)
        >>> nx.draw(G, pos, node_size=140)
        >>> nx.draw_many_paths(G, pos, [path1, path2, path3, path4],
        ...                    max_shift=0.03)
        >>> plt.show()

    """
    
    if not paths:
        return
    if not is_layout_normalized(pos):
        raise ValueError('Layout is not normalized; use normalize_layout().')
        
    edge_paths = [to_edge_path(path, G) for path in paths]
    # Sort edge_paths from the longest to the shortest
    edge_paths.sort(key=len, reverse=True)
    
    # Find the largest number of edge_paths traversing the same edge and
    # set single_shift accordingly
    edge2count = Counter(chain.from_iterable(path for path in edge_paths))
    single_shift = max_shift / max(edge2count.values())

    # Draw the edge_paths by calling draw_path(...). Use edge2shift to
    # prevent the path overlap on some edges.q
    colors = ('b', 'g', 'r', 'c', 'm', 'y')
    linestyles = ('solid', 'dashed', 'dashdot', 'dotted')
    edge2shift = {}
    for i, path in enumerate(edge_paths):
        shifts = [edge2shift.setdefault(e, single_shift) for e in path]
        color = colors[i % len(colors)]
        linestyle = linestyles[i / len(colors) % len(linestyles)],
        draw_path(G, pos, path, color=color, linestyle=linestyle,
                  linestyle=linestyle, linewidth=linewidth, shifts=shifts)
        for e in path:
            edge2shift[e] += single_shift
    return


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import matplotlib as mpl
        mpl.use('PS', warn=False)
        import matplotlib.pyplot as plt
    except:
        raise SkipTest("matplotlib not available")
