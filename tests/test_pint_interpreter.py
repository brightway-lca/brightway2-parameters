import pytest

from bw2parameters import PintInterpreter, PintWrapper
from test_default_interpreter import TestInterpreter as InterpreterTests

pint = pytest.importorskip("pint")

if pint:
    ureg = PintWrapper().ureg
    other_ureg = pint.UnitRegistry()
    UndefinedUnitError = PintWrapper.UndefinedUnitError
    DimensionalityError = pint.DimensionalityError


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
        assert set() == i.get_unknown_symbols('kg * m + 2', **kwargs)
        assert {'kg'} == i.get_unknown_symbols('kg * m + 2', no_pint_units={'kg'}, **kwargs)

    def test_get_pint_symbols(self):
        i = self.Interpreter()
        text = "1 kg + 2 g"
        # test default call
        result = i.get_pint_symbols(text=text)
        assert result == {
            "kg": ureg("1 kg"),
            "g": ureg("1 g"),
        }
        # test known_symbols parameter
        result = set(i.get_pint_symbols(text=text, known_symbols=["kg"]))
        assert result == {"g"}
        result = set(i.get_pint_symbols(text=text, known_symbols={"kg": 1}))
        assert result == {"g"}
        result = set(i.get_pint_symbols(text=text, known_symbols={"kg"}))
        assert result == {"g"}
        # test ignore_symtable
        i.symtable["kg"] = 1
        result = set(i.get_pint_symbols(text=text, ignore_symtable=True))
        assert result == {"kg", "g"}
        result = set(i.get_pint_symbols(text=text, ignore_symtable=False))
        assert result == {"g"}
        # test text=None
        assert i.get_pint_symbols(None) == dict()

    def test_eval(self):
        i = self.Interpreter()
        text = "1 kg + 200 g"
        assert i(text) == ureg("1.2 kg")
        # test pint units in symtable
        assert i.symtable["kg"] == ureg("1 kg")
        assert i.symtable["g"] == ureg("1 g")
        # test g is a known symbol (and a quantity from other ureg than PintWrapper.ureg)
        result = i(text, known_symbols={"g": other_ureg("1 kg")})
        assert result == ureg("201 kg")
        # test known_symbols not permanently added to symtable
        assert "g" not in i.symtable
        assert i("1 kg + 200 g") == ureg("1.2 kg")
        # test unit "unit" defined
        assert i("1 unit") == PintWrapper.Quantity(1, "dimensionless")
        # test formula without unit returns no quantity
        assert i("1+2") == 3

    def test_parameter_list_to_dict(self):
        i = self.Interpreter()
        param_list = [
            {"name": "A", "amount": 1, "data": {"unit": "kg"}},
            {"name": "B", "amount": 2, "unit": "m"},
            {"name": "C", "amount": 3, "unit": "unit"},
            {"name": "parameter_1", "formula": "2 kg", "amount": 1},
            {
                "name": "parameter_2",
                "formula": "2 kg",
                "amount": 1,
                "unit": "kg",
            },
            {
                "name": "parameter_3",
                "formula": "2 kg",
                "amount": 1,
                "data": {"unit": "kg"},
            },
            {
                "name": "parameter_4",
                "formula": "2 kg",
                "amount": 1,
                "data": {"unit": "m"},
            },
            {"name": "parameter_5", "amount": 2},
            {"name": "parameter_6", "amount": 2, "unit": "kg"},
            {"name": "parameter_7", "amount": 2, "data": {"unit": "kg"}},
            {"name": "parameter_8", "amount": 2, "data": {"unit": "m"}},
            {"name": "parameter_9", "amount": 2, "data": {}},
            {"name": "parameter_10", "formula": "2 + 3", "amount": 5},
        ]
        expected = {
            "A": PintWrapper.Quantity(1, "kg"),
            "B": PintWrapper.Quantity(2, "m"),
            "C": PintWrapper.Quantity(3, "unit"),
            "parameter_1": 1,
            "parameter_2": PintWrapper.Quantity(1, "kg"),
            "parameter_3": PintWrapper.Quantity(1, "kg"),
            "parameter_4": PintWrapper.Quantity(1, "m"),
            "parameter_5": 2,
            "parameter_6": PintWrapper.Quantity(2, "kg"),
            "parameter_7": PintWrapper.Quantity(2, "kg"),
            "parameter_8": PintWrapper.Quantity(2, "m"),
            "parameter_9": 2,
            "parameter_10": 5,
        }
        result = self.Interpreter.parameter_list_to_dict(
            param_list=param_list
        )
        assert result == expected
        # no amount raises error
        with pytest.raises(KeyError):
            i.parameter_list_to_dict(
                [{"name": "parameter_1", "formula": "2 kg"}]
            )

    def test_pint_errors_properly_raised(self):
        i = self.Interpreter()
        with pytest.raises(DimensionalityError):
            i("2 kg + 1")
