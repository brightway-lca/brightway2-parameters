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
        cls.UndefinedUnitError = UndefinedUnitError
        # manual fix for pint parser (see https://github.com/hgrecco/pint/pull/1701)
        import pint.util
        import re
        pint.util._subs_re_list[-1] = (r"([\w\.\)])\s+(?=[\w\(])", r"\1*")
        pint.util._subs_re = [
            (re.compile(a.format(r"[_a-zA-Z][_a-zA-Z0-9]*")), b) for a, b in pint.util._subs_re_list
        ]

    def __init__(self, *args, **kwargs):
        if self.string_preprocessor is None:
            self._setup_pint()
        super().__init__(*args, **kwargs)

    def parse(self, text):
        return super().parse(PintInterpreter.string_preprocessor(text))
