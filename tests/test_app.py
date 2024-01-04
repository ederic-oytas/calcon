"""Tests calcon/app.py."""


from decimal import Decimal

import pytest
from calcon.app import App, Quantity


class TestApp:
    """Tests the App class."""

    def test_define_root_unit_dimension_already_associated(self) -> None:
        """Tests that App.define_root_unit() raises `ValueError` when another
        unit is already associated with the given dimension."""

        app = App()
        app.define_root_unit("a", "length")
        app.define_root_unit("b", "time")

        with pytest.raises(ValueError):
            app.define_root_unit("c", "length")
        with pytest.raises(ValueError):
            app.define_root_unit("d", "time")

    def test_defines(self) -> None:
        """Tests the define methods"""
        Q = Quantity
        D = Decimal

        app = App()
        app.define_root_unit("a", "length")
        app.define_derived_unit("b", Q(D(2), {"a": D(1)}))
        app.define_unit_alias("c", "b")
        app.define_root_unit("d", "time")

        # Test ValueError raised when name is already taken
        with pytest.raises(ValueError):
            app.define_root_unit("a", "length")
        with pytest.raises(ValueError):
            app.define_root_unit("b", "length")
        with pytest.raises(ValueError):
            app.define_root_unit("c", "length")
        with pytest.raises(ValueError):
            app.define_derived_unit("a", Q(D(3), {}))
        with pytest.raises(ValueError):
            app.define_derived_unit("b", Q(D(3), {}))
        with pytest.raises(ValueError):
            app.define_derived_unit("c", Q(D(3), {}))
        with pytest.raises(ValueError):
            app.define_unit_alias("a", "d")
        with pytest.raises(ValueError):
            app.define_unit_alias("b", "d")
        with pytest.raises(ValueError):
            app.define_unit_alias("c", "d")

    def test_quantity_from_magnitude_str(self) -> None:
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

    def test_quantity_from_unit_name(self) -> None:
        """Tests App.quantity_from_unit_name()"""

        app = App()
        f = app.quantity_from_unit_name

        app.define_root_unit("meter", "length")
        app.define_derived_unit(
            "yard", Quantity(Decimal("0.9144"), {"meter": Decimal(1)})
        )
        app.define_unit_alias("yard_alias", "yard")

        assert f("meter") == Quantity(Decimal(1), {"meter": Decimal(1)})
        assert (
            f("yard")
            == f("yard_alias")
            == Quantity(Decimal(1), {"yard": Decimal(1)})
        )
        with pytest.raises(ValueError):
            f("m")
