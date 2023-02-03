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
    equations = {
        'D': {'formula': 'A * B * C'},
        'A': {'formula': '1 m'},
        'B': {'formula': 'A + 200 mm'},
        'C': {'formula': 'B * kg/m'},
    }

    def test_pint_parameters(self):
        ps = self.ParameterSet(self.equations)
        assert ps.evaluate() == {
            'A': ureg('1 m'),
            'B': ureg("1.2 m"),
            'C': ureg("1.2 kg"),
            'D': ureg("1.44 kg * m^2"),
        }

    def test_globals(self):
        global_params = {
            "kg": ureg("2 V")
        }
        ps = self.ParameterSet(
            params=self.equations,
            global_params=global_params
        )
        assert ps.evaluate() == {
            'kg': ureg("2 V"),
            'A': ureg('1 m'),
            'B': ureg("1.2 m"),
            'C': ureg("2.4 V"),
            'D': ureg("2.88 V * m^2"),
        }


if __name__ == "__main__":
    TestPintParameterSet().test_globals()
