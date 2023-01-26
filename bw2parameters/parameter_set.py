# -*- coding: utf-8 -*-
from numbers import Number
from pprint import pformat

import numpy as np
from asteval import Interpreter

from stats_arrays import uncertainty_choices
from .errors import *
from .utils import EXISTING_SYMBOLS, get_symbols, isidentifier, isstr

MC_ERROR_TEXT = """Formula returned array of wrong shape:
Name: {}
Formula: {}
Expected shape: {}
Returned shape: {}"""


class ParameterSet(object):
    def __init__(self, params, global_params=None, interpreter=None):
        self.params = params
        self.global_params = global_params or {}
        self.interpreter = interpreter or Interpreter()
        self.basic_validation()
        self.references = self.get_references()
        for name, references in self.references.items():
            if name in references:
                raise SelfReference(
                    u"Formula for parameter {} references itself".format(name)
                )

        self.order = self.get_order()

    def get_order(self):
        """Get a list of parameter name in an order that they can be safely evaluated"""
        order = []
        seen = set(self.interpreter.symtable.keys())
        refs = self.references.copy()

        while refs:
            last_iteration = set(refs.keys())
            for k, v in refs.items():
                if not v.difference(seen):
                    seen.add(k)
                    order.append(k)
                    refs.pop(k)
                    break
            if not last_iteration.difference(set(refs.keys())):
                seen_lower_case = {x.lower() for x in seen}
                # Iterate over all remaining references,
                # and see if references would match if lower cased
                wrong_case = [
                    (k, v)
                    for k, v in refs.items()
                    if not {x.lower() for x in v}.difference(seen_lower_case)
                ]
                if wrong_case:
                    raise CapitalizationError(
                        (
                            u"Possible errors in upper/lower case letters for some parameters.\n"
                            u"Unmatched references:\n{}\nMatched references:\n{}"
                        ).format(
                            pformat(refs, indent=2), pformat(sorted(seen), indent=2)
                        )
                    )
                raise ParameterError(
                    (
                        u"Undefined or circular references for the following:"
                        u"\n{}\nExisting references:\n{}"
                    ).format(pformat(refs, indent=2), pformat(sorted(order), indent=2))
                )

        return order

    def get_references(self):
        """Create dictionary of parameter references"""
        refs = {
            key: get_symbols(value["formula"], interpreter=self.interpreter) if value.get("formula") else set()
            for key, value in self.params.items()
        }
        refs.update({key: set() for key in self.global_params})
        return refs

    def basic_validation(self):
        """Basic validation needed to build ``references`` and ``order``"""
        if not isinstance(self.params, dict):
            raise ValueError(u"Parameters are not a dictionary")
        if not isinstance(self.global_params, dict):
            raise ValueError(u"Global parameters are not a dictionary")
        for key, value in self.params.items():
            if not isinstance(value, dict):
                raise ValueError(u"Parameter value {} is not a dictionary".format(key))
            elif not (
                    isinstance(value.get("amount"), (Number, np.ndarray))
                    or isstr(value.get("formula"))
            ):
                raise ValueError(
                    (
                        u"Parameter {} must have either ``amount`` "
                        u"or ``formula`` field"
                    ).format(key)
                )
            elif not isidentifier(key):
                raise ValueError(
                    u"Parameter label {} not a valid Python name".format(key)
                )
            elif key in EXISTING_SYMBOLS:
                raise DuplicateName(
                    u"Parameter name {} is a built-in symbol".format(key)
                )
        for key, value in self.global_params.items():
            if not isinstance(value, (Number, np.ndarray)):
                raise ValueError(
                    (
                        u"Global parameter {} does not have a " u"numeric value: {}"
                    ).format(key, value)
                )
            elif not isidentifier(key):
                raise ValueError(
                    u"Global parameter label {} not a valid " u"Python name".format(
                        key
                    )
                )

    def evaluate(self):
        """Evaluate each formula. Returns dictionary of parameter names and values."""
        interpreter = self.interpreter
        result = {}
        for key in self.order:
            if key in self.global_params:
                interpreter.symtable[key] = result[key] = self.global_params[key]
            elif self.params[key].get("formula"):
                value = interpreter(self.params[key]["formula"])
                interpreter.symtable[key] = result[key] = value
            elif "amount" in self.params[key]:
                interpreter.symtable[key] = result[key] = self.params[key]["amount"]
            else:
                raise ValueError(
                    u"No suitable formula or static amount found " u"in {}".format(key)
                )
        return result

    def evaluate_and_set_amount_field(self):
        """Evaluate each formula. Updates the ``amount`` field of each parameter."""
        result = self.evaluate()
        for key, value in self.params.items():
            value[u"amount"] = result[key]
        return result

    def evaluate_monte_carlo(self, iterations=1000):
        """Evaluate each formula using Monte Carlo and variable uncertainty data, if present.

        Formulas **must** return a one-dimensional array, or ``BroadcastingError`` is raised.

        Returns dictionary of ``{parameter name: numpy array}``."""
        interpreter = self.interpreter
        result = {}

        def get_rng_sample(obj):
            if isinstance(obj, np.ndarray):
                # Already a Monte Carlo sample
                return obj
            if "uncertainty_type" not in obj:
                if "uncertainty type" not in obj:
                    obj = obj.copy()
                    obj["uncertainty_type"] = 0
                else:
                    obj["uncertainty_type"] = obj["uncertainty type"]
                obj["loc"] = obj.get("loc") or obj["amount"]
            kls = uncertainty_choices[obj["uncertainty_type"]]
            return kls.bounded_random_variables(kls.from_dicts(obj), iterations).ravel()

        def fix_shape(array):
            if array is None:
                return np.zeros((iterations,))
            elif isinstance(array, Number):
                return np.ones((iterations,)) * array
            elif not isinstance(array, np.ndarray):
                return np.zeros((iterations,))
            elif array.shape in {(1, iterations), (iterations, 1)}:
                return array.reshape((iterations,))
            else:
                return array

        for key in self.order:
            if key in self.global_params:
                interpreter.symtable[key] = result[key] = get_rng_sample(
                    self.global_params[key]
                )
            elif self.params[key].get("formula"):
                sample = fix_shape(interpreter(self.params[key]["formula"]))
                if sample.shape != (iterations,):
                    raise BroadcastingError(
                        MC_ERROR_TEXT.format(
                            key,
                            self.params[key]["formula"],
                            (iterations,),
                            sample.shape,
                        )
                    )
                interpreter.symtable[key] = result[key] = sample
            else:
                interpreter.symtable[key] = result[key] = get_rng_sample(
                    self.params[key]
                )
        return result

    def __call__(self, ds=None):
        """Evaluate each formula, and update ``exchanges`` if they reference a ``parameter`` name."""
        if ds is None:
            return self.evaluate_and_set_amount_field()

        self.evaluate_and_set_amount_field()

        # Evaluate formulas in exchanges
        interpreter = self.get_interpreter()
        for obj in ds:
            if "formula" in obj and "amount" not in obj:
                obj[u"amount"] = interpreter(obj["formula"])

        # Changes in-place, but return anyway
        return ds

    def get_interpreter(self, evaluate_first=True):
        """Get an instance of ``asteval.Interpreter`` that is prepopulated with global and local \
        symbol names and values."""
        if evaluate_first:
            self.evaluate_and_set_amount_field()

        interpreter = self.interpreter
        for key, value in self.global_params.items():
            interpreter.symtable[key] = value
        for key, value in self.params.items():
            interpreter.symtable[key] = value["amount"]

        return interpreter


class PintParameterSet(ParameterSet):
    string_preprocessor = None
    ureg = None

    @classmethod
    def _setup_pint(cls):
        from pint import UnitRegistry
        from pint.util import string_preprocessor
        cls.string_preprocessor = string_preprocessor
        cls.ureg = UnitRegistry()

    @staticmethod
    def _preprocess_params(params):
        """Convert 1 m -> 1 * m etc."""
        # pre-process all formulas
        if isinstance(params, dict):
            for k, v in params.items():
                if isinstance(v, dict) and v.get("formula"):
                    v["_formula"] = v.get("formula")
                    v["formula"] = PintParameterSet.string_preprocessor(v["_formula"])

    def __init__(self, params, global_params=None, interpreter=None):
        if self.string_preprocessor is None:
            self._setup_pint()
        self._preprocess_params(params)
        self._preprocess_params(global_params)
        super().__init__(params=params, global_params=global_params, interpreter=interpreter)

    def _add_units_to_symtable(self):
        """Add unit references to interpreter symtable"""
        params = set(self.references.keys())
        all_refs = set(p for refs in self.references.values() for p in refs)
        units = all_refs.difference(params)
        for u in units:
            self.interpreter.symtable[u] = self.ureg(u)

    def get_order(self):
        """Get a list of parameter name in an order that they can be safely evaluated"""
        self._add_units_to_symtable()
        return super().get_order()
