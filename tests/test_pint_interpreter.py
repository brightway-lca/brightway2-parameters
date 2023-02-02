import pytest

from bw2parameters import PintInterpreter

pint = pytest.importorskip("pint")

if pint:
    ureg = pint.UnitRegistry()
    UndefinedUnitError = pint.UndefinedUnitError


def test_init():
    i = PintInterpreter(units=["kg", "V"])
    assert i.symtable["kg"] == ureg("1 kilogram")
    assert i.symtable["V"] == ureg("1 volt")


def test_parse():
    i = PintInterpreter()
    i.parse("1 kg")  # test no error raised


def test_get_pint_symbols():
    i = PintInterpreter()
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


def test_eval():
    i = PintInterpreter()
    text = "1 kg + 200 g"
    assert i(text) == ureg("1.2 kg")
    # test pint units in symtable
    assert i.symtable["kg"] == ureg("1 kg")
    assert i.symtable["g"] == ureg("1 g")
    # test g is a known symbol (and a quantity from other ureg than i.ureg)
    result = i(text, known_symbols={"g": ureg("1 kg")})
    assert result == ureg("201 kg")
    # test g in symtable
    assert i.symtable["g"] == ureg("1 kg")
