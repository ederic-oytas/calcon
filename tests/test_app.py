"""Tests calcon/app.py."""


from decimal import Decimal

import pytest
from calcon.app import App, Quantity


def test_quantity_from_magnitude_str() -> None:
    """Tests App.quantity_from_magnitude_str()"""
    app = App()
    f = app.quantity_from_magnitude_str

    assert f("0") == Quantity(Decimal("0"), {})
    assert f("1") == Quantity(Decimal("1"), {})
    assert f("1.") == Quantity(Decimal("1"), {})
    assert f(".1") == Quantity(Decimal("0.1"), {})
    assert f("0.1") == Quantity(Decimal("0.1"), {})
    assert f("1.23e2") == Quantity(Decimal("1.23e2"), {})
    assert f("1.23e-200") == Quantity(Decimal("1.23e-200"), {})


def test_quantity_from_unit_name() -> None:
    """Tests App.quantity_from_unit_name()"""

    app = App()
    f = app.quantity_from_unit_name

    app.define_root_unit("meter", "length")
    app.define_derived_unit(
        "yard", Quantity(Decimal("0.9144"), {"meter": Decimal(1)})
    )
    app.define_alias("yard_alias", "yard")

    assert f("meter") == Quantity(Decimal(1), {"meter": Decimal(1)})
    assert (
        f("yard")
        == f("yard_alias")
        == Quantity(Decimal(1), {"yard": Decimal(1)})
    )
    with pytest.raises(ValueError):
        f("m")
