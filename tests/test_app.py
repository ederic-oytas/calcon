"""Tests calcon/app.py."""


from decimal import Decimal
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
