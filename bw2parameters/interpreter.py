from asteval import Interpreter as Interpreter


class PintInterpreter(Interpreter):
    string_preprocessor = None
    ureg = None
    UndefinedUnitError = None

    @classmethod
    def _setup_pint(cls):
        from pint import UnitRegistry, UndefinedUnitError
        from pint.util import string_preprocessor
        cls.string_preprocessor = string_preprocessor
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
