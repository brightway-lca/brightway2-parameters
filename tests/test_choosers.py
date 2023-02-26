import warnings

import pytest
from bw2parameters import (
    DefaultInterpreter,
    DefaultParameterSet,
    Interpreter,
    ParameterSet,
    PintInterpreter,
    PintParameterSet,
    PintWrapper,
    config,
    MissingName
)


def test_choosers():
    def without_pint():
        # InterpreterChooser.interpreter returns default interpreter
        assert Interpreter().__class__ == DefaultInterpreter

        # InterpreterChooser.__call__ raises error if units are in expression
        config.use_pint = False
        with pytest.raises(MissingName):
            Interpreter()("1kg + 200g")

        # ParameterSet() returns empty default ParameterSet
        assert ParameterSet({}).__class__ == DefaultParameterSet

    def with_pint():
        # InterpreterChooser.interpreter return PintInterpreter
        assert Interpreter().__class__ == PintInterpreter

        # InterpreterChooser.__call__ returns Quantity
        assert Interpreter()("1kg + 200g") == PintWrapper.Quantity(
            value=1.2, units="kg"
        )

        # ParameterSet() returns empty PintParameterSet
        assert ParameterSet({}).__class__ == PintParameterSet

    # no pint installed  # noqa
    if not PintWrapper.pint_installed:
        # warn if trying to switch on pint support
        with pytest.warns():
            config.use_pint = True
        without_pint()

        # does not warn if switched off
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            config.use_pint = False
        without_pint()

    # pint is installed
    else:
        config.use_pint = True
        with_pint()
        config.use_pint = False
        without_pint()
