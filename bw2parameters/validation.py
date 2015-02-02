from scipy.sparse.csgraph import connected_components


def test_no_circular_references(parameter_set):
    """Check if the given parameter set has circular references.

    Returns ``True`` if no circular references are present."""
    graph = parameter_set.to_csgraph()
    # ``connected_components`` returns number of strongly connected subgraphs
    # if there are no cycles, then this will be the same as the number of
    # parameters. See http://en.wikipedia.org/wiki/Strongly_connected_component
    return csgraph.connected_components(graph, connection='strong',
                                        return_labels=False) == graph.shape[0]
