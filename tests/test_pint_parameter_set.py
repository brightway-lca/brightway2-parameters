# -*- coding: utf-8 -*-
import pytest

from bw2parameters import PintParameterSet
from test_parameter_set import TestParameterSet as ParameterSetTests

pint = pytest.importorskip("pint")

if pint:
    ureg = pint.UnitRegistry()
    UndefinedUnitError = pint.UndefinedUnitError


class TestPintParameterSet(ParameterSetTests):
    ParameterSet = PintParameterSet

    def test_pint_parameters(self):
        ps = self.ParameterSet({
            'A': {'formula': '1 m'},
            'B': {'formula': 'A + 200 mm'},
            'C': {'formula': 'B * kg/m'},
            'D': {'formula': 'A * B * C'},
        })
        assert ps.evaluate() == {
            'A': ureg('1 m'),
            'B': ureg("1.2 m"),
            'C': ureg("1.2 kg"),
            'D': ureg("1.44 kg * m^2"),
        }
