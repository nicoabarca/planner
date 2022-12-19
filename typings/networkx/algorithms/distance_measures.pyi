"""
This type stub file was generated by pyright.
"""

from networkx.utils import not_implemented_for

"""Graph diameter, radius, eccentricity and other properties."""
__all__ = ["extrema_bounding", "eccentricity", "diameter", "radius", "periphery", "center", "barycenter", "resistance_distance"]
def extrema_bounding(G, compute=...): # -> int | list[Unknown] | dict[Unknown, int] | None:
    """Compute requested extreme distance metric of undirected graph G

    .. deprecated:: 2.8

       extrema_bounding is deprecated and will be removed in NetworkX 3.0.
       Use the corresponding distance measure with the `usebounds=True` option
       instead.

    Computation is based on smart lower and upper bounds, and in practice
    linear in the number of nodes, rather than quadratic (except for some
    border cases such as complete graphs or circle shaped graphs).

    Parameters
    ----------
    G : NetworkX graph
       An undirected graph

    compute : string denoting the requesting metric
       "diameter" for the maximal eccentricity value,
       "radius" for the minimal eccentricity value,
       "periphery" for the set of nodes with eccentricity equal to the diameter,
       "center" for the set of nodes with eccentricity equal to the radius,
       "eccentricities" for the maximum distance from each node to all other nodes in G

    Returns
    -------
    value : value of the requested metric
       int for "diameter" and "radius" or
       list of nodes for "center" and "periphery" or
       dictionary of eccentricity values keyed by node for "eccentricities"

    Raises
    ------
    NetworkXError
        If the graph consists of multiple components
    ValueError
        If `compute` is not one of "diameter", "radius", "periphery", "center",
        or "eccentricities".

    Notes
    -----
    This algorithm was proposed in the following papers:

    F.W. Takes and W.A. Kosters, Determining the Diameter of Small World
    Networks, in Proceedings of the 20th ACM International Conference on
    Information and Knowledge Management (CIKM 2011), pp. 1191-1196, 2011.
    doi: https://doi.org/10.1145/2063576.2063748

    F.W. Takes and W.A. Kosters, Computing the Eccentricity Distribution of
    Large Graphs, Algorithms 6(1): 100-118, 2013.
    doi: https://doi.org/10.3390/a6010100

    M. Borassi, P. Crescenzi, M. Habib, W.A. Kosters, A. Marino and F.W. Takes,
    Fast Graph Diameter and Radius BFS-Based Computation in (Weakly Connected)
    Real-World Graphs, Theoretical Computer Science 586: 59-80, 2015.
    doi: https://doi.org/10.1016/j.tcs.2015.02.033
    """
    ...

def eccentricity(G, v=..., sp=...): # -> dict[Unknown, Unknown]:
    """Returns the eccentricity of nodes in G.

    The eccentricity of a node v is the maximum distance from v to
    all other nodes in G.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    v : node, optional
       Return value of specified node

    sp : dict of dicts, optional
       All pairs shortest path lengths as a dictionary of dictionaries

    Returns
    -------
    ecc : dictionary
       A dictionary of eccentricity values keyed by node.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> dict(nx.eccentricity(G))
    {1: 2, 2: 3, 3: 2, 4: 2, 5: 3}

    >>> dict(nx.eccentricity(G, v=[1, 5]))  # This returns the eccentrity of node 1 & 5
    {1: 2, 5: 3}

    """
    ...

def diameter(G, e=..., usebounds=...): # -> int | list[Unknown] | dict[Unknown, int] | None:
    """Returns the diameter of the graph G.

    The diameter is the maximum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    d : integer
       Diameter of graph

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.diameter(G)
    3

    See Also
    --------
    eccentricity
    """
    ...

def periphery(G, e=..., usebounds=...): # -> int | list[Unknown] | dict[Unknown, int] | None:
    """Returns the periphery of the graph G.

    The periphery is the set of nodes with eccentricity equal to the diameter.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    p : list
       List of nodes in periphery

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.periphery(G)
    [2, 5]

    See Also
    --------
    barycenter
    center
    """
    ...

def radius(G, e=..., usebounds=...): # -> int | list[Unknown] | dict[Unknown, int] | None:
    """Returns the radius of the graph G.

    The radius is the minimum eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    r : integer
       Radius of graph

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.radius(G)
    2

    """
    ...

def center(G, e=..., usebounds=...): # -> int | list[Unknown] | dict[Unknown, int] | None:
    """Returns the center of the graph G.

    The center is the set of nodes with eccentricity equal to radius.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    e : eccentricity dictionary, optional
      A precomputed dictionary of eccentricities.

    Returns
    -------
    c : list
       List of nodes in center

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> list(nx.center(G))
    [1, 3, 4]

    See Also
    --------
    barycenter
    periphery
    """
    ...

def barycenter(G, weight=..., attr=..., sp=...): # -> list[Unknown]:
    r"""Calculate barycenter of a connected graph, optionally with edge weights.

    The :dfn:`barycenter` a
    :func:`connected <networkx.algorithms.components.is_connected>` graph
    :math:`G` is the subgraph induced by the set of its nodes :math:`v`
    minimizing the objective function

    .. math::

        \sum_{u \in V(G)} d_G(u, v),

    where :math:`d_G` is the (possibly weighted) :func:`path length
    <networkx.algorithms.shortest_paths.generic.shortest_path_length>`.
    The barycenter is also called the :dfn:`median`. See [West01]_, p. 78.

    Parameters
    ----------
    G : :class:`networkx.Graph`
        The connected graph :math:`G`.
    weight : :class:`str`, optional
        Passed through to
        :func:`~networkx.algorithms.shortest_paths.generic.shortest_path_length`.
    attr : :class:`str`, optional
        If given, write the value of the objective function to each node's
        `attr` attribute. Otherwise do not store the value.
    sp : dict of dicts, optional
       All pairs shortest path lengths as a dictionary of dictionaries

    Returns
    -------
    list
        Nodes of `G` that induce the barycenter of `G`.

    Raises
    ------
    NetworkXNoPath
        If `G` is disconnected. `G` may appear disconnected to
        :func:`barycenter` if `sp` is given but is missing shortest path
        lengths for any pairs.
    ValueError
        If `sp` and `weight` are both given.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.barycenter(G)
    [1, 3, 4]

    See Also
    --------
    center
    periphery
    """
    ...

@not_implemented_for("directed")
def resistance_distance(G, nodeA, nodeB, weight=..., invert_weight=...):
    """Returns the resistance distance between node A and node B on graph G.

    The resistance distance between two nodes of a graph is akin to treating
    the graph as a grid of resistorses with a resistance equal to the provided
    weight.

    If weight is not provided, then a weight of 1 is used for all edges.

    Parameters
    ----------
    G : NetworkX graph
       A graph

    nodeA : node
      A node within graph G.

    nodeB : node
      A node within graph G, exclusive of Node A.

    weight : string or None, optional (default=None)
       The edge data key used to compute the resistance distance.
       If None, then each edge has weight 1.

    invert_weight : boolean (default=True)
        Proper calculation of resistance distance requires building the
        Laplacian matrix with the reciprocal of the weight. Not required
        if the weight is already inverted. Weight cannot be zero.

    Returns
    -------
    rd : float
       Value of effective resistance distance

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> nx.resistance_distance(G, 1, 3)
    0.625

    Notes
    -----
    Overview discussion:
    * https://en.wikipedia.org/wiki/Resistance_distance
    * http://mathworld.wolfram.com/ResistanceDistance.html

    Additional details:
    Vaya Sapobi Samui Vos, “Methods for determining the effective resistance,” M.S.,
    Mathematisch Instituut, Universiteit Leiden, Leiden, Netherlands, 2016
    Available: `Link to thesis <https://www.universiteitleiden.nl/binaries/content/assets/science/mi/scripties/master/vos_vaya_master.pdf>`_
    """
    ...

