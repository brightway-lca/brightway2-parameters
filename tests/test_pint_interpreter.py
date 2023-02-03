import pytest

from bw2parameters import PintInterpreter
from test_interpreter import TestInterpreter as InterpreterTests

pint = pytest.importorskip("pint")

if pint:
    ureg = pint.UnitRegistry()
    UndefinedUnitError = pint.UndefinedUnitError


class TestPintInterpreter(InterpreterTests):
    Interpreter = PintInterpreter

    def test_init(self):
        super().test_init()
        i = self.Interpreter(units=["kg", "V"])
        assert i.symtable["kg"] == ureg("1 kilogram")
        assert i.symtable["V"] == ureg("1 volt")

    def test_parse(self):
        i = self.Interpreter()
        i.parse("1 kg")  # test no error raised

    def test_get_unknown_symbols(self, **kwargs):
        # PintInterpreter.get_unknown_units() behaves like Interpreter.get_unknown_units() if
        # `include_pint_units = True`
        super().test_get_unknown_symbols(include_pint_units=True)
        # default: include_pint_units = False
        i = self.Interpreter()
        assert set() == i.get_unknown_symbols('a * b + c', **kwargs)  # a: year, b: barn, c: light year
        assert set() == i.get_unknown_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)', **kwargs)
        assert {'sqrt', 'log'} == i.get_unknown_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)', ignore_symtable=True,
                                                        **kwargs)
        assert {"f", "i"} == i.get_unknown_symbols('f * i + n', known_symbols={'n'}, **kwargs)
        assert {"f", "i"} == i.get_unknown_symbols('f * i + n', known_symbols={'n': 1}, **kwargs)
        assert {"f", "i"} == i.get_unknown_symbols('f * i + n', known_symbols=['n'], **kwargs)
        assert {"f", "i"} == i.get_unknown_symbols('f * i + n', known_symbols=('n',), **kwargs)
        assert set() == i.get_unknown_symbols(None, **kwargs)

    def test_get_pint_symbols(self):
        i = self.Interpreter()
        text = "1 kg + 2 g"
        # test default call
        result = i.get_pint_symbols(text=text)
        assert result == {
            "kg": ureg("1 kg"),
            "g": ureg("1 g"),
        }
        # test as_dict flag
        result = i.get_pint_symbols(text=text, as_dict=False)
        assert result == {"kg", "g"}
        # test known_symbols parameter
        result = i.get_pint_symbols(text=text, known_symbols=["kg"], as_dict=False)
        assert result == {"g"}
        result = i.get_pint_symbols(text=text, known_symbols={"kg": 1}, as_dict=False)
        assert result == {"g"}
        result = i.get_pint_symbols(text=text, known_symbols={"kg"}, as_dict=False)
        assert result == {"g"}
        # test ignore_symtable
        i.symtable["kg"] = 1
        result = i.get_pint_symbols(text=text, ignore_symtable=True, as_dict=False)
        assert result == {"kg", "g"}
        result = i.get_pint_symbols(text=text, ignore_symtable=False, as_dict=False)
        assert result == {"g"}
        # test text=None
        assert i.get_pint_symbols(None) == dict()
        assert i.get_pint_symbols(None, as_dict=False) == set()

    def test_eval(self):
        i = self.Interpreter()
        text = "1 kg + 200 g"
        assert i(text) == ureg("1.2 kg")
        # test pint units in symtable
        assert i.symtable["kg"] == ureg("1 kg")
        assert i.symtable["g"] == ureg("1 g")
        # test g is a known symbol (and a quantity from other ureg than i.ureg)
        result = i(text, known_symbols={"g": ureg("1 kg")})
        assert result == ureg("201 kg")
        # test known_symbols not permanently added to symtable
        assert "g" not in i.symtable
        assert i("1 kg + 200 g") == ureg("1.2 kg")
