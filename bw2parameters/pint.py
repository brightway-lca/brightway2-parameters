from pathlib import Path
import re
import pint.util
from pint import DimensionalityError, Quantity, UndefinedUnitError, UnitRegistry
from pint.util import string_preprocessor

UNITS_FILE = Path(__file__).parent / "ecoinvent_units.txt"


class PintWrapperSingleton:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(PintWrapperSingleton, cls).__new__(cls)
        return cls.instance

    def __init__(self, units_file: Path | str = UNITS_FILE):
        if not hasattr(self, "string_preprocessor"):
            self.string_preprocessor = string_preprocessor
            self.ureg = UnitRegistry()
            self.Quantity = self.ureg.Quantity
            self.Unit = self.ureg.Unit
            self.GeneralQuantity = Quantity
            self.ureg.load_definitions(units_file)
            self.UndefinedUnitError = UndefinedUnitError
            self.DimensionalityError = DimensionalityError
            # fix to make sure ecoinvent-specific units "kilometer-year", "meter-year", "square meter-year"
            # can be processed (otherwise minus is interpreted as literal subtraction operator)
            self.ureg.preprocessors.append(
                lambda x: x.replace("meter-year", "meter * year")
            )
            pint.util._subs_re = [(re.compile("meter-year"), "meter * year")] + pint.util._subs_re

    def to_unit(self, string, raise_errors=False):
        """Returns pint.Unit if the given string can be interpreted as a unit, returns None otherwise"""
        if string is None:
            return None
        try:
            return self.Unit(string)
        except self.UndefinedUnitError:
            if raise_errors:
                raise self.UndefinedUnitError
            else:
                return None

    def to_units(self, iterable, raise_errors=False, drop_none=True):
        """
        Takes and iterable and tries to interpret each element as a pint.Unit. Returns a dict where key is
        the original element and value is the interpreted pint.Unit. Elements which cannot be interpreted as
        a pint.Unit are `None` (or dropped if `drop_none == True`).
        """
        units = {}
        for s in iterable:
            unit = self.to_unit(s, raise_errors=raise_errors)
            if unit or not drop_none:
                units[s] = unit
        return units

    def is_quantity(self, value):
        return isinstance(value, self.GeneralQuantity)

    def is_quantity_from_same_registry(self, value):
        return isinstance(value, self.Quantity)

    def get_dimensionality(self, unit_name=None):
        """
        Returns the dimensionality of the unit described by `unit_name`, e.g. {["mass"]: 1} for "kg" or
        {["length"]: 1, ["time"]: -1} for "m/s". Also makes sure the dimensions are sorted alphabetically.
        """
        if unit_name is None:
            return None
        else:
            d = self.to_unit(unit_name, raise_errors=True).dimensionality
            return {k: d[k] for k in sorted(d.keys())}

    def to_quantity(self, amount, unit=None):
        """Return a pint.Quantity if a unit is given, otherwise the amount."""
        if unit is None:
            return amount
        else:
            return self.Quantity(value=amount, units=unit)


PintWrapper = PintWrapperSingleton()
