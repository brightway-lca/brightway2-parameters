import pytest
from bw2parameters import PintWrapper

pytest.importorskip(modname="pint")


@pytest.fixture
def init():
    PintWrapper()


def test_pint_setup(init):
    # ensure that setup worked
    assert PintWrapper.ureg is not None
    # ensure that setup is only called once per runtime
    ureg1 = PintWrapper.ureg
    PintWrapper()
    ureg2 = PintWrapper.ureg
    assert ureg1 == ureg2


def test_pint_is_class_variable(init):
    """ensure that pint stays available during whole runtime"""
    assert PintWrapper.ureg is not None


def test_custom_unit_definitions(init):
    """Ensure custom unit "unit" is defined"""
    assert PintWrapper.ureg("1 unit") == PintWrapper.Quantity(
        value=1, units="dimensionless"
    )


def test_different_unit_registries(init):
    """Test that quantities from different unit registries are identified correctly."""
    q1 = PintWrapper.ureg("1 kg")
    q2 = PintWrapper.Quantity(value=1, units="kg")
    q3 = PintWrapper.GeneralQuantity(value=1, units="kg")
    assert all(PintWrapper.is_quantity(q) for q in [q1, q2, q3])
    assert all(PintWrapper.is_quantity_from_same_registry(q) for q in [q1, q2])
    assert not PintWrapper.is_quantity_from_same_registry(q3)
