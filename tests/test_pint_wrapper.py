from bw2parameters.pint import PintWrapper, PintWrapperSingleton


def test_pint_setup():
    # ensure that setup worked
    assert PintWrapper.ureg is not None
    # ensure that setup is only called once per runtime
    ureg1 = PintWrapperSingleton().ureg
    ureg2 = PintWrapperSingleton().ureg
    assert ureg1 == ureg2
    assert ureg1 == PintWrapper.ureg


def test_pint_is_class_variable():
    """ensure that pint stays available during whole runtime"""
    assert PintWrapper.ureg is not None


def test_custom_unit_definitions():
    """Ensure custom unit "unit" is defined"""
    assert PintWrapper.ureg("1 unit") == PintWrapper.Quantity(
        value=1, units="dimensionless"
    )


def test_different_unit_registries():
    """Test that quantities from different unit registries are identified correctly."""
    q1 = PintWrapper.ureg("1 kg")
    q2 = PintWrapper.Quantity(value=1, units="kg")
    q3 = PintWrapper.GeneralQuantity(value=1, units="kg")
    assert all(PintWrapper.is_quantity(q) for q in [q1, q2, q3])
    assert all(PintWrapper.is_quantity_from_same_registry(q) for q in [q1, q2])
    assert not PintWrapper.is_quantity_from_same_registry(q3)
