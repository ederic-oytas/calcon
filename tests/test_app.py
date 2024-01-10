"""Tests calcon/app.py."""


from decimal import Decimal
from typing import Union

import pytest
from calcon.app import App, Quantity


_Unit = dict[Union[str, tuple[str, str]], Decimal]


def q(magnitude: Union[int, str], /, **unit: Union[int, str]) -> Quantity:
    """Helper function to create a quantity, automatically converting the
    integers/strings to Decimal objects."""
    return Quantity(
        Decimal(magnitude),
        {c: Decimal(p) for c, p in unit.items()},
    )


def u(**unit: Union[int, str]) -> _Unit:
    return {c: Decimal(p) for c, p in unit.items()}


class TestApp:
    """Tests the App class."""

    def test_define_root__unit_dimension_already_associated(self) -> None:
        """Tests that App.define_root_unit() raises `ValueError` when another
        unit is already associated with the given dimension."""

        app = App()
        app.define_root_unit("a", "length")
        app.define_root_unit("b", "time")

        with pytest.raises(ValueError):
            app.define_root_unit("c", "length")
        with pytest.raises(ValueError):
            app.define_root_unit("d", "time")

    def test_define_symbol_alias__symbol_already_defined(self) -> None:
        """Tests that App.define_symbol_alias() raises `ValueError` when a
        symbol is already defined for a unit."""
        app = App()
        app.define_root_unit("a", "length")
        app.define_unit_symbol_alias("A1", "a")

        with pytest.raises(ValueError):
            app.define_unit_symbol_alias("A2", "a")

    def test_quantity_display_str_shows_symbol(self) -> None:
        """Tests that App.quantity_display_str() displays the symbols for the
        units by default (if any)."""

        app = App()
        app.define_root_unit("a", "length")
        app.define_unit_symbol_alias("A", "a")
        app.define_root_unit("b", "time")

        quantity = q(12, a=1, b=1)
        display_str = app.quantity_display_str(quantity)
        assert "a" not in display_str
        assert "A" in display_str
        assert "b" in display_str

    def test_define_unit_methods_redefine_error(self) -> None:
        """Tests that a `ValueError` is raised for the define unit methods when
        a unit is attempted to be redefined."""
        Q = Quantity
        D = Decimal

        app = App()
        app.define_root_unit("a", "length")
        app.define_derived_unit("b", Q(D(2), {"a": D(1)}))
        app.define_unit_alias("c", "b")
        app.define_root_unit("d", "time")
        app.define_unit_symbol_alias("D", "d")

        # Test ValueError raised when name is already taken
        for unit in "abcdD":
            with pytest.raises(ValueError):
                app.define_root_unit(unit, "length")
            with pytest.raises(ValueError):
                app.define_derived_unit(unit, Q(D(3), {}))
            with pytest.raises(ValueError):
                app.define_unit_alias(unit, "d")
            with pytest.raises(ValueError):
                app.define_unit_symbol_alias(unit, "d")

    def test_define_prefix_methods_redefine_error(self) -> None:
        """Tests the define prefix methods that they raise a `ValueError`
        when we attempt to redefine a prefix."""

        app = App()
        app.define_canonical_prefix("a", Decimal(12))
        app.define_prefix_alias("b", "a")
        app.define_prefix_symbol_alias("c", "a")
        app.define_canonical_prefix("d", Decimal(23))

        # Test ValueError raised when name is already taken
        for prefix in "abcd":
            with pytest.raises(ValueError):
                app.define_canonical_prefix(prefix, Decimal(21))
            with pytest.raises(ValueError):
                app.define_prefix_alias(prefix, "d")
            with pytest.raises(ValueError):
                app.define_prefix_symbol_alias(prefix, "d")

    def test_define_prefix_symbol_alias__symbol_already_defined(self) -> None:
        """Tests that App.define_prefix_symbol_alias() raises a `ValueError`
        when the symbol is already defined for the prefix.
        """
        app = App()
        app.define_canonical_prefix("a", Decimal(12))
        app.define_prefix_symbol_alias("A1", "a")

        with pytest.raises(ValueError):
            app.define_prefix_symbol_alias("A2", "a")

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

    def test_quantity_convert__time(self) -> None:
        """Tests App.quantity_convert_to_same_unit() with time units"""

        # Define apps (all have equivalent unit systems)
        app1 = App()
        app1.define_root_unit("second", "time")
        app1.define_derived_unit("minute", q(60, second=1))
        app1.define_derived_unit("hour", q(60, minute=1))
        app1.define_derived_unit("day", q(24, hour=1))
        app1.define_derived_unit("week", q(7, day=1))

        app2 = App()
        app2.define_root_unit("second", "time")
        app2.define_derived_unit("minute", q(60, second=1))
        app2.define_derived_unit("hour", q(3600, second=1))
        app2.define_derived_unit("day", q(86400, second=1))
        app2.define_derived_unit("week", q(604800, second=1))

        app3 = App()
        app3.define_root_unit("second", "time")
        app3.define_derived_unit("minute", q(60, second=1))
        app3.define_derived_unit("hour", q(60, minute=1))
        app3.define_derived_unit("day", q(86400, second=1))
        app3.define_derived_unit("week", q(7, day=1))

        equivalent = [
            q(1, week=1),
            q(7, day=1),
            q(168, hour=1),
            q(10080, minute=1),
            q(604800, second=1),
        ]
        for app in [app1, app2, app3]:
            for a in equivalent:
                for b in equivalent:
                    assert app.quantity_convert(a, b.unit) == b

    def test_quantity_convert__pressure(self) -> None:
        """Tests App.quantity_convert_to_same_unit() with pressure units"""

        # Pressure dimensions: Mass * Length^-1 * Time^-2

        app = App()
        app.define_root_unit("gram", "mass")
        app.define_derived_unit("kilogram", q(1000, gram=1))
        app.define_root_unit("meter", "length")
        app.define_root_unit("second", "time")
        app.define_derived_unit(
            "pascal", q(1, kilogram=1, meter=-1, second=-2)
        )
        app.define_derived_unit("standard_atmosphere", q(101_325, pascal=1))

        equivalent: list[Quantity] = [
            q(3, standard_atmosphere=1),
            q(303_975, pascal=1),
            q(303_975, kilogram=1, meter=-1, second=-2),
        ]
        for a in equivalent:
            for b in equivalent:
                assert app.quantity_convert(a, b.unit) == b

    def test_quantity_convert__different_dimensions(self) -> None:
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_unit("minute", q(60, second=1))
        app.define_root_unit("gram", "mass")

        with pytest.raises(ValueError):
            app.quantity_convert(q(1, second=1), u(gram=1))
        with pytest.raises(ValueError):
            app.quantity_convert(q(1, second=1), u(gram=1))
        with pytest.raises(ValueError):
            app.quantity_convert(q(1, gram=1), u(second=1))
        with pytest.raises(ValueError):
            app.quantity_convert(q(1, second=1), u(second=2))
        with pytest.raises(ValueError):
            app.quantity_convert(q(1, second=1), u(minute=2))
        with pytest.raises(ValueError):
            app.quantity_convert(q(1, second=1), u(second=-1))

    def test_quantity_negate(self) -> None:
        """Tests App.quantity_negate()."""
        Q = Quantity
        D = Decimal

        app = App()
        f = app.quantity_negate

        assert f(Q(D(12), {})) == Q(D(-12), {})
        assert f(Q(D(12), {"u": D(2)})) == Q(D(-12), {"u": D(2)})
        assert f(Q(D(0), {})) == Q(D(0), {})
        assert f(Q(D(-35), {})) == Q(D(35), {})

    def test_quantity_add(self) -> None:
        """Tests App.quantity_add()"""
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_unit("minute", q(60, second=1))
        app.define_root_unit("meter", "length")

        f = app.quantity_add

        assert f(q(1, second=1), q(3, second=1)) == q(4, second=1)
        assert f(q(1, minute=1), q(3, second=1)) == q("1.05", minute=1)
        assert f(q(1, second=1), q(3, minute=1)) == q(181, second=1)
        assert f(q(1, minute=1), q(3, minute=1)) == q(4, minute=1)

        # different dimensions -> ValueError
        with pytest.raises(ValueError):
            f(q(1, second=1), q(2, meter=1))
        with pytest.raises(ValueError):
            f(q(1, second=1), q(2, second=-1))

    def test_quantity_subtract(self) -> None:
        """Tests App.quantity_subtract()"""
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_unit("minute", q(60, second=1))
        app.define_root_unit("meter", "length")

        f = app.quantity_subtract

        assert f(q(1, second=1), q(3, second=1)) == q(-2, second=1)
        assert f(q(1, minute=1), q(3, second=1)) == q("0.95", minute=1)
        assert f(q(1, second=1), q(3, minute=1)) == q(-179, second=1)
        assert f(q(1, minute=1), q(3, minute=1)) == q(-2, minute=1)

        # different dimensions -> ValueError
        with pytest.raises(ValueError):
            f(q(1, second=1), q(2, meter=1))
        with pytest.raises(ValueError):
            f(q(1, second=1), q(2, second=-1))

    def test_quantity_multiply(self) -> None:
        """Tests App.quantity_multiply()"""
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_unit("minute", q(60, second=1))
        app.define_root_unit("meter", "length")

        f = app.quantity_multiply

        assert f(q(3, second=2), q(4, meter=5)) == q(12, second=2, meter=5)
        assert f(q(3, second=2), q(4, second=2)) == q(12, second=4)
        assert f(q(3, second=2), q(4, second=-2)) == q(12)
        assert f(q(3, second=2), q(4, second=-2, meter=3)) == q(12, meter=3)

    def test_quantity_divide(self) -> None:
        """Tests App.quantity_divide()"""
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_unit("minute", q(60, second=1))
        app.define_root_unit("meter", "length")

        f = app.quantity_divide

        assert f(q(3, second=2), q(4, meter=5)) == q(".75", second=2, meter=-5)
        assert f(q(3, second=2), q(4, second=2)) == q(".75")
        assert f(q(3, second=2), q(4, second=-2)) == q(".75", second=4)
        assert f(q(3, second=2), q(4, second=-2, meter=3)) == q(
            ".75", second=4, meter=-3
        )
        with pytest.raises(ValueError):
            f(q(1), q(0))
        with pytest.raises(ValueError):
            f(q(1, second=5), q(0, second=5))

    def test_quantity_exponentiate(self) -> None:
        """Tests App.quantity_exponentiate()"""

        app = App()
        app.define_root_unit("meter", "length")
        app.define_derived_unit("dozen", q(12))

        f = app.quantity_exponentiate

        assert f(q(2, meter=1), q(0)) == q(1)
        assert f(q(2, meter=1), q(1)) == q(2, meter=1)
        assert f(q(2, meter=1), q(2)) == q(4, meter=2)
        assert f(q(2, meter=1), q(5)) == q(32, meter=5)
        assert f(q(2, meter=1), q(1, dozen=1)) == q(4096, meter=12)
        assert f(q(2, meter=1), q(-1)) == q("0.5", meter=-1)

        with pytest.raises(ValueError):
            f(q(2, meter=1), q(1, meter=1))
            f(q(2, meter=1), q(1, meter=-1))

    def test_quantity_display_str(self) -> None:
        """Tests App.quantity_display_str()"""

        app = App()
        f = app.quantity_display_str
        app.define_root_unit("gram", "Mass")
        app.define_root_unit("meter", "Length")
        app.define_root_unit("second", "Time")
        app.define_derived_unit("kilogram", q(1000, gram=1))

        # Tests shouldn't be too strict. This is mainly for sanity tests and
        # test coverage (this file should completely cover app.py).

        # If unitless, then no units should be displayed at all
        assert f(q(5)) == "5"

        # Just check that the units are in there.
        s = f(q(303_975, kilogram=1, meter=-1, second=-2))
        assert "303975" in s
        assert "kilogram" in s
        assert "meter" in s
        assert "second" in s
