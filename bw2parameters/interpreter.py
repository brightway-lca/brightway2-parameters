from collections.abc import Iterable

from asteval import Interpreter as ASTInterpreter
from asteval import NameFinder


class Interpreter(ASTInterpreter):

    def get_symbols(self, text):
        """
        Parses an expression and returns all symbols.
        """
        nf = NameFinder()
        nf.generic_visit(self.parse(text))
        return nf.names

    def get_unknown_symbols(self, text, known_symbols=None, ignore_symtable=False):
        """
        Parses an expression and returns all symbols which are neither in the symtable nor passed via known_symbols.
        """
        if known_symbols is None:
            known_symbols = set()
        elif isinstance(known_symbols, Iterable):
            known_symbols = set(known_symbols)
        else:
            raise ValueError(f"Parameter known_symbols must be iterable. Is {type(known_symbols)}.")
        if not ignore_symtable:
            known_symbols = known_symbols.union(set(self.symtable.keys()))
        all_symbols = set(self.get_symbols(text))
        return all_symbols.difference(known_symbols)

    def add_symbols(self, symbols):
        """Adds symbols to symtable."""
        self.symtable.update(symbols)

    def eval(self, expr, *args, known_symbols=None, **kwargs):
        if known_symbols is not None:
            self.symtable.update(known_symbols)
        return super().eval(expr=expr, *args, **kwargs)


class PintInterpreter(Interpreter):
    string_preprocessor = None
    Quantity = None
    ureg = None
    UndefinedUnitError = None

    @classmethod
    def _setup_pint(cls):
        try:
            from pint import UnitRegistry, UndefinedUnitError, Quantity
            from pint.util import string_preprocessor
        except ImportError:
            raise ImportError("Module pint could not be loaded. Please install pint: `pip install pint`.")
        cls.string_preprocessor = string_preprocessor
        cls.Quantity = Quantity
        cls.ureg = UnitRegistry()
        cls.ureg.define("unit = [] = dimensionless")
        cls.UndefinedUnitError = UndefinedUnitError
        # manual fix for pint parser (see https://github.com/hgrecco/pint/pull/1701)
        import pint.util
        import re
        pint.util._subs_re_list[-1] = (r"([\w\.\)])\s+(?=[\w\(])", r"\1*")
        pint.util._subs_re = [
            (re.compile(a.format(r"[_a-zA-Z][_a-zA-Z0-9]*")), b) for a, b in pint.util._subs_re_list
        ]

    def __init__(self, *args, units=None, **kwargs):
        if self.string_preprocessor is None:
            self._setup_pint()
        super().__init__(*args, **kwargs)
        if units is not None:
            self.add_symbols({u: self.ureg(u) for u in units})

    def parse(self, text):
        return super().parse(PintInterpreter.string_preprocessor(text))

    def get_pint_symbols(self, text, known_symbols=None, ignore_symtable=True, as_dict=True):
        """
        Parses an expression and returns all symbols which can be interpreted as pint units.
        """
        # get all unknown symbols
        unknown_symbols = self.get_unknown_symbols(text=text, known_symbols=known_symbols,
                                                   ignore_symtable=ignore_symtable)
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

    def add_symbols(self, symbols):
        """
        Adds symbols to symtable while making sure that pint Quantities are from same registry as self.ureg
        (otherwise self.eval will fail).
        """
        for k, v in symbols.items():
            if isinstance(v, self.Quantity) and v._REGISTRY != self.ureg:
                symbols[k] = self.ureg(str(v))
        self.symtable.update(symbols)

    def eval(self, expr, *args, known_symbols=None, **kwargs):
        if known_symbols is not None:
            self.add_symbols(known_symbols)
        pint_symbols = self.get_pint_symbols(text=expr, ignore_symtable=False, as_dict=True)
        self.add_symbols(pint_symbols)
        return super().eval(expr=expr, *args, **kwargs)
