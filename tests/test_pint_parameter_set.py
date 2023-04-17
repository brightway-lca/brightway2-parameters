# -*- coding: utf-8 -*-
import pytest

from bw2parameters import PintParameterSet

import pint

ureg = pint.UnitRegistry()
UndefinedUnitError = pint.UndefinedUnitError


ParameterSet = PintParameterSet
equations = {
    'D': {'formula': 'A * B * C'},
    'A': {'formula': '1 m'},
    'B': {'formula': 'A + 200 mm'},
    'C': {'formula': 'B * kg/m'},
}

def test_pint_parameters():
    ps = ParameterSet(equations)
    assert ps.evaluate() == {
        'A': ureg('1 m'),
        'B': ureg("1.2 m"),
        'C': ureg("1.2 kg"),
        'D': ureg("1.44 kg * m^2"),
    }

def test_globals():
    global_params = {
        "kg": ureg("2 V")
    }
    ps = ParameterSet(
        params=equations,
        global_params=global_params
    )
    assert ps.evaluate() == {
        'kg': ureg("2 V"),
        'A': ureg('1 m'),
        'B': ureg("1.2 m"),
        'C': ureg("2.4 V"),
        'D': ureg("2.88 V * m^2"),
    }
