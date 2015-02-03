from .errors import *
from .utils import get_symbols, EXISTING_SYMBOLS
from asteval import Interpreter
from numbers import Number
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import connected_components


class ParameterSet(object):
    def __init__(self, params):
        self.params = params
        self.basic_validation()
        self.references = self.get_references()
        self.order = self.get_order()

    def get_order(self):
        """Get a list of parameter name in an order that they can be safely evaluated"""
        order = []
        seen = set()
        refs = self.references.copy()
        while refs:
            for k, v in refs.items():
                if not v.difference(seen):
                    seen.add(k)
                    order.append(k)
                    break
            refs.pop(k)
        return order

    def get_references(self):
        """Create dictionary of parameter references"""
        return {p['name']: get_symbols(p['formula'])
                if p.get('formula')
                else set()
                for p in self.params}

    def mapping(self):
        """Map sorted parameter names to integer indices"""
        return {n: i for i, n in enumerate(sorted([obj['name'] for obj in
                                                   self.params]))}

    def to_csgraph(self):
        """Create sparse matrix graph representation of formula references"""
        mapping = self.mapping()
        matrix = lil_matrix((len(mapping), len(mapping)))
        for name, row in mapping.items():
            for reference in self.references[name]:
                matrix[row, mapping[reference]] = 1
        return matrix.tocsr()

    def test_no_circular_references(self):
        """Check if the given parameter set has circular references.

        Returns ``True`` if no circular references are present."""
        graph = self.to_csgraph()
        # ``connected_components`` returns number of strongly connected subgraphs
        # if there are no cycles, then this will be the same as the number of
        # parameters. See http://en.wikipedia.org/wiki/Strongly_connected_component
        return connected_components(graph,
                                    connection='strong',
                                    return_labels=False
                                    ) == graph.shape[0]

    def basic_validation(self):
        """Basic validation needed to build ``references`` and ``order``"""
        seen = set()
        for p in self.params:
            if not isinstance(p, dict):
                raise ValueError(u"Parameter {} is not a dictionary".format(p))
            if not (isinstance(p.get('amount'), Number) or
                    isinstance(p.get('formula'), basestring)):
                raise ValueError((u"Parameter {} must have either ``amount`` "
                                  u"for ``formula`` field").format(p))
            if p.get('name') is None:
                raise MissingName(
                    u"Parameter dataset {} is missing the `name` field".format(p)
                )
            # TODO: Other illegal characters?
            elif u" " in p['name']:
                raise ValueError(
                    "Parameter name {} has a space".format(p['name'])
                )
            elif p['name'] in EXISTING_SYMBOLS:
                raise DuplicateName(
                    u"Parameter name {} is a built-in symbol".format(p['name'])
                )
            elif p['name'] in seen:
                raise DuplicateName(
                    u"Parameter {} is defined twice".format(p['name'])
                )
            seen.add(p['name'])

    def validate(self):
        """Check parameter set is valid. Raises a validation error if necessary."""
        for k, v in self.references.items():
            if k in v:
                raise SelfReference(
                    u"Formula for parameter {} references itself".format(k)
                )
        missing_refs = reduce(set.union, self.references.values()).difference(
                              set(self.references.keys()))
        if missing_refs:
            raise MissingParameter((u"Parameter(s) '{}' are referenced but "
                                    u"not defined").format(missing_refs))
        if not self.test_no_circular_references():
            # TODO
            # raise CircularReference(
            #     u"Parameters {} have a circular reference".format(
            #         self.find_circular_references()
            #     )
            # )
            raise CircularReference(
                u"Parameters have a circular reference"
            )

    def evaluate(self):
        """Evaluate each formula. Returns """
        interpreter = Interpreter()
        result = {}
        params_as_dict = {p['name']: p for p in self.params}
        for p in self.order:
            if not self.references[p]:
                interpreter.symtable[p] = result[p] = params_as_dict[p]['amount']
            else:
                value = interpreter(params_as_dict[p]['formula'])
                interpreter.symtable[p] = result[p] = value
        return result

    def evaluate_and_update_params(self):
        result = self.evaluate()
        for p in self.params:
            p['amount'] = result[p['name']]
