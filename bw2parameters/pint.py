def check_pint_installed():
    try:
        import pint

        return True
    except ImportError:
        return False


class PintWrapper:
    pint_installed = check_pint_installed()
    pint_loaded = False

    string_preprocessor = None
    Quantity = None
    GeneralQuantity = None
    Unit = None
    ureg = None
    UndefinedUnitError = None
    DimensionalityError = None

    def __init__(self):
        if not self.pint_loaded:
            self.setup()

    @classmethod
    def setup(cls):
        try:
            from pint import Quantity, UndefinedUnitError, DimensionalityError, UnitRegistry  # noqa
            from pint.util import string_preprocessor  # noqa
        except ImportError:
            cls.pint_loaded = False
            raise ImportError(
                "Module pint could not be loaded. Please install pint: `pip install pint`."
            )
        cls.pint_loaded = True
        cls.string_preprocessor = string_preprocessor
        cls.ureg = UnitRegistry()
        cls.Quantity = cls.ureg.Quantity
        cls.Unit = cls.ureg.Unit
        cls.GeneralQuantity = Quantity
        cls.ureg.define("unit = [] = dimensionless")
        cls.UndefinedUnitError = UndefinedUnitError
        cls.DimensionalityError = DimensionalityError
        # manual fix for pint parser (see https://github.com/hgrecco/pint/pull/1701)
        import re

        import pint.util  # noqa

        pint.util._subs_re_list[-1] = (  # noqa
            r"([\w\.\)])\s+(?=[\w\(])",
            r"\1*",
        )
        pint.util._subs_re = [
            (re.compile(a.format(r"[_a-zA-Z][_a-zA-Z0-9]*")), b)
            for a, b in pint.util._subs_re_list  # noqa
        ]

    @classmethod
    def to_unit(cls, string, raise_errors=False):
        """Returns pint.Unit if the given string can be interpreted as a unit, returns None otherwise"""
        if string is None:
            return None
        try:
            return cls.Unit(string)
        except cls.UndefinedUnitError:
            if raise_errors:
                raise cls.UndefinedUnitError
            else:
                return None

    @classmethod
    def to_units(cls, iterable, raise_errors=False, drop_none=True):
        """
        Takes and iterable and tries to interpret each element as a pint.Unit. Returns a dict where key is
        the original element and value is the interpreted pint.Unit. Elements which cannot be interpreted as
        a pint.Unit are `None` (or dropped if `drop_none == True`).
        """
        units = {}
        for s in iterable:
            unit = cls.to_unit(s, raise_errors=raise_errors)
            if unit or not drop_none:
                units[s] = unit
        return units

    @classmethod
    def is_quantity(cls, value):
        return isinstance(value, cls.GeneralQuantity)

    @classmethod
    def is_quantity_from_same_registry(cls, value):
        return isinstance(value, cls.Quantity)

    @classmethod
    def get_dimensionality(cls, unit_name=None):
        if unit_name is None:
            return None
        else:
            return dict(
                **cls.to_unit(unit_name, raise_errors=True).dimensionality
            )

    @classmethod
    def to_quantity(cls, amount, unit=None):
        """Return a pint.Quantity if a unit is given, otherwise the amount."""
        if unit is None:
            return amount
        else:
            return cls.Quantity(value=amount, units=unit)
