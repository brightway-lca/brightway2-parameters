from bw2parameters.pint import PintWrapper


def test_ecoinvent_unit_definitions():
    """Ensure that typical ecoinvent units are properly defined"""
    # unit "unit" is defined and has its own dimensionality
    assert PintWrapper.ureg("1 unit").dimensionality == {'[unit]': 1}
    # test that ton is 1000 kg (not short ton of 2000 pounds)
    assert PintWrapper.ureg("1 ton").to("kg").m == 1000
    # "night" is a time unit
    assert PintWrapper.ureg("1 night").dimensionality == {'[time]': 1}
    # "person" and "guest" defined and have "person" dimensionality
    assert PintWrapper.ureg("1 person").dimensionality == \
           PintWrapper.ureg("1 guest").dimensionality == \
           {'[person]': 1}
    # test that minus in kilometer-year is not interpreted as subtraction
    kmyear = PintWrapper.ureg("1 kilometer-year")
    assert kmyear.dimensionality == {'[length]': 1, '[time]': 1}
    assert PintWrapper.ureg("square meter-year").dimensionality == {'[length]': 2, '[time]': 1}
    # test kilo == 1000
    assert kmyear.to("meter-year").m == 1000
    # EURO2005
    assert PintWrapper.ureg("1 EUR2005").dimensionality == {'[currency]': 1}
    # Sm3 is not really cubic meter...more of a quantity? keeping it separate for now
    assert PintWrapper.ureg("1 Sm3").dimensionality == {'[Sm3]': 1}