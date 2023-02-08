from collections.abc import Iterable

from asteval import Interpreter as ASTInterpreter
from asteval import NameFinder


class Interpreter(ASTInterpreter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.BUILTIN_SYMBOLS = set(self.symtable)

    def get_symbols(self, text):
        """
        Parses an expression and returns all symbols.
        """
        if text is None:
            return set()
        nf = NameFinder()
        nf.generic_visit(self.parse(text))
        return set(nf.names)

    def get_unknown_symbols(
        self, text, known_symbols=None, ignore_symtable=False
    ):
        """
        Parses an expression and returns all symbols which are neither in the symtable nor passed via known_symbols.
        """
        if text is None:
            return set()
        if known_symbols is None:
            known_symbols = set()
        elif isinstance(known_symbols, Iterable):
            known_symbols = set(known_symbols)
        else:
            raise ValueError(
                f"Parameter known_symbols must be iterable. Is {type(known_symbols)}."
            )
        if not ignore_symtable:
            known_symbols = known_symbols.union(set(self.symtable.keys()))
        all_symbols = set(self.get_symbols(text))
        return all_symbols.difference(known_symbols)

    def add_symbols(self, symbols):
        """Adds symbols to the symtable."""
        if symbols is None:
            return
        self.symtable.update(symbols)

    def remove_symbols(self, symbols):
        """Removes symbols from the symtable."""
        if symbols is None:
            return
        if isinstance(symbols, dict):
            symbols = set(symbols)
        for symbol in symbols:
            self.symtable.pop(symbol)

    def user_defined_symbols(self):
        return set(self.symtable).difference(self.BUILTIN_SYMBOLS)

    def eval(
        self, expr, *args, known_symbols=None, raise_errors=True, **kwargs
    ):
        self.add_symbols(known_symbols)
        result = super().eval(
            expr=expr, *args, raise_errors=raise_errors, **kwargs
        )
        self.remove_symbols(known_symbols)
        return result

    @classmethod
    def parameter_list_to_dict(cls, param_list):
        return {d["name"]: d["amount"] for d in param_list}

    @classmethod
    def is_quantity(cls, value):
        return False

    @classmethod
    def is_quantity_from_same_registry(cls, value):
        return False

    @classmethod
    def get_unit_dimensionality(cls, unit_name=None):
        return dict()

class PintInterpreter(Interpreter):
    string_preprocessor = None
    Quantity = None
    GeneralQuantity = None
    Unit = None
    ureg = None
    UndefinedUnitError = None

    @classmethod
    def _setup_pint(cls):
        try:
            from pint import Quantity, UndefinedUnitError, UnitRegistry
            from pint.util import string_preprocessor
        except ImportError:
            raise ImportError(
                "Module pint could not be loaded. Please install pint: `pip install pint`."
            )
        cls.string_preprocessor = string_preprocessor
        cls.ureg = UnitRegistry()
        cls.Quantity = cls.ureg.Quantity
        cls.Unit = cls.ureg.Unit
        cls.GeneralQuantity = Quantity
        cls.ureg.define("unit = [] = dimensionless")
        cls.UndefinedUnitError = UndefinedUnitError
        # manual fix for pint parser (see https://github.com/hgrecco/pint/pull/1701)
        import re

        import pint.util

        pint.util._subs_re_list[-1] = (r"([\w\.\)])\s+(?=[\w\(])", r"\1*")
        pint.util._subs_re = [
            (re.compile(a.format(r"[_a-zA-Z][_a-zA-Z0-9]*")), b)
            for a, b in pint.util._subs_re_list
        ]

    def __init__(self, *args, units=None, **kwargs):
        if self.string_preprocessor is None:
            self._setup_pint()
        super().__init__(*args, **kwargs)
        if units is not None:
            self.add_symbols({u: self.ureg(u) for u in units})

    def parse(self, text):
        return super().parse(PintInterpreter.string_preprocessor(text))

    def is_pint_unit_symbol(self, symbol):
        """Returns True if the given symbol can be interpreted as a pint unit, False otherwise"""
        try:
            self.ureg(symbol)
            return True
        except self.UndefinedUnitError:
            return False

    def get_unknown_symbols(
        self,
        text,
        known_symbols=None,
        ignore_symtable=False,
        include_pint_units=False,
        no_pint_units=None,
    ):
        """Parses the given expression and returns a list of symbols, which are neither contained in the symtable,
        nor in known_symbols, nor can be interpreted as pint units"""
        unknown_symbols = super().get_unknown_symbols(
            text=text,
            known_symbols=known_symbols,
            ignore_symtable=ignore_symtable,
        )

        # exclude symbols which can be parsed as pint units and are not in `no_pint_units`
        if not include_pint_units:
            if no_pint_units is None:
                no_pint_units = set()
            unknown_symbols = {
                s
                for s in unknown_symbols
                if s in no_pint_units or not self.is_pint_unit_symbol(s)
            }

        return unknown_symbols

    def get_pint_symbols(
        self, text, known_symbols=None, ignore_symtable=True, as_dict=True
    ):
        """
        Parses an expression and returns all symbols which can be interpreted as pint units.
        """
        if text is None:
            if as_dict:
                return dict()
            else:
                return set()
        # get all unknown symbols (incl. unit symbols)
        unknown_symbols = super().get_unknown_symbols(
            text=text,
            known_symbols=known_symbols,
            ignore_symtable=ignore_symtable,
        )
        # check which of them can be interpreted by pint
        pint_symbols = {}
        for s in unknown_symbols:
            try:
                pint_symbols[s] = self.ureg(s)
            except self.UndefinedUnitError:
                pass
        # return dict or set
        if not as_dict:
            pint_symbols = set(pint_symbols)
        return pint_symbols

    @classmethod
    def is_quantity(cls, value):
        return isinstance(value, cls.GeneralQuantity)

    @classmethod
    def is_quantity_from_same_registry(cls, value):
        return isinstance(value, cls.Quantity)

    def add_symbols(self, symbols):
        """
        Adds symbols to symtable while making sure that pint Quantities are from same registry as self.ureg
        (otherwise self.eval will fail).
        """
        if symbols is None:
            return
        for k, v in symbols.items():
            # if value is a quantity from another unit registry -> convert to current unit registry
            if self.is_quantity(v) and not self.is_quantity_from_same_registry(
                v
            ):
                symbols[k] = self.Quantity(value=v.m, units=v.u)
        super().add_symbols(symbols=symbols)

    def _raise_proper_pint_exception(func):  # noqa
        """Make sure that pint exceptions are correctly raised during evaluation"""

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)  # noqa
            except TypeError:
                expr = args[0] if len(args) > 0 else kwargs.get("expr")
                self.ureg.parse_expression(expr, **self.symtable)  # will raise proper exception

        return wrapper

    @_raise_proper_pint_exception  # noqa
    def eval(self, expr, *args, known_symbols=None, **kwargs):
        self.add_symbols(known_symbols)
        pint_symbols = self.get_pint_symbols(
            text=expr, ignore_symtable=False, as_dict=True
        )
        self.add_symbols(pint_symbols)
        result = super().eval(expr=expr, *args, **kwargs)
        self.remove_symbols(known_symbols)
        return result

    @classmethod
    def parameter_list_to_dict(cls, param_list):
        result = dict()
        for d in param_list:
            unit = d.get("unit") or d.get("data", {}).get("unit")
            if unit:
                result[d["name"]] = cls.Quantity(value=d["amount"], units=unit)
            else:
                result[d["name"]] = d["amount"]
        return result

    @classmethod
    def get_unit_dimensionality(cls, unit_name=None):
        return dict(**cls.Unit(unit_name or "").dimensionality)
