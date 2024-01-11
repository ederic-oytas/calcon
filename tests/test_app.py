"""Tests calcon/app.py."""


from decimal import Decimal
from typing import Optional, Union

import pytest
from calcon.app import App, Quantity


_Unit = dict[Union[str, tuple[str, str]], Decimal]


def q(
    magnitude: Union[int, str],
    unit1: Optional[dict[Union[str, tuple[str, str]], Union[int, str]]] = None,
    /,
    **unit2: Union[int, str],
) -> Quantity:
    """Helper function to create a quantity, automatically converting the
    integers/strings to Decimal objects."""
    if unit1 is None:
        unit1 = {}
    unit = unit1 | unit2
    return Quantity(
        Decimal(magnitude),
        {c: Decimal(p) for c, p in unit.items()},
    )


def u(
    unit1: Optional[dict[Union[str, tuple[str, str]], Union[int, str]]] = None,
    **unit2: Union[int, str],
) -> _Unit:
    if unit1 is None:
        unit1 = {}
    unit = unit1 | unit2
    return {c: Decimal(p) for c, p in unit.items()}


class TestApp:
    """Tests the App class."""

    def test_define_root_unit__dimension_already_associated_error(
        self,
    ) -> None:
        """Tests that App.define_root_unit() raises ValueError if the
        dimension is already associated to a unit."""

        app = App()
        app.define_root_unit("a", "length")
        app.define_root_unit("b", "time")

        with pytest.raises(ValueError):
            app.define_root_unit("c", "length")
        with pytest.raises(ValueError):
            app.define_root_unit("d", "time")
        with pytest.raises(ValueError):
            app.define_root_unit("b", "time")

    def test_define_core_unit_alias__unit_not_defined_error(self) -> None:
        app = App()
        app.define_root_unit("a", "Length")

        with pytest.raises(ValueError):
            app.define_core_unit_alias("c", "b")
        with pytest.raises(ValueError):
            app.define_core_unit_alias("d", "c")
        app.define_core_unit_alias("b", "a")
        app.define_core_unit_alias("c", "b")

    def test_define_symbol_alias__symbol_already_defined(self) -> None:
        """Tests that App.define_symbol_alias() raises `ValueError` when a
        symbol is already defined for a unit."""
        app = App()
        app.define_root_unit("a", "length")
        app.define_core_unit_symbol_alias("A1", "a")

        with pytest.raises(ValueError):
            app.define_core_unit_symbol_alias("A2", "a")

    def test_quantity_display_str_shows_symbol(self) -> None:
        """Tests that App.quantity_display_str() displays the symbols for the
        units by default (if any)."""

        app = App()
        app.define_root_unit("a", "length")
        app.define_core_unit_symbol_alias("A", "a")
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
        app.define_derived_core_unit("b", Q(D(2), {"a": D(1)}))
        app.define_core_unit_alias("c", "b")
        app.define_root_unit("d", "time")
        app.define_core_unit_symbol_alias("D", "d")

        # Test ValueError raised when name is already taken
        for unit in "abcdD":
            with pytest.raises(ValueError):
                app.define_root_unit(unit, "length")
            with pytest.raises(ValueError):
                app.define_derived_core_unit(unit, Q(D(3), {}))
            with pytest.raises(ValueError):
                app.define_core_unit_alias(unit, "d")
            with pytest.raises(ValueError):
                app.define_core_unit_symbol_alias(unit, "d")

    def test_define_prefix_methods_redefine_error(self) -> None:
        """Tests the define prefix methods that they raise a `ValueError`
        when we attempt to redefine a prefix."""

        app = App()
        app.define_canonical_prefix("a", q(12))
        app.define_prefix_alias("b", "a")
        app.define_prefix_symbol_alias("c", "a")
        app.define_canonical_prefix("d", q(23))

        # Test ValueError raised when name is already taken
        for prefix in "abcd":
            with pytest.raises(ValueError):
                app.define_canonical_prefix(prefix, q(21))
            with pytest.raises(ValueError):
                app.define_prefix_alias(prefix, "d")
            with pytest.raises(ValueError):
                app.define_prefix_symbol_alias(prefix, "d")

    def test_define_chained_aliases(self) -> None:
        """Test that chained aliases work properly"""
        app = App()
        app.define_root_unit("a", "Length")
        app.define_core_unit_alias("b", "a")
        app.define_core_unit_alias("c", "b")
        assert app.quantity_from_unit_name("c") == q(1, a=1)

    def test_define_prefix_symbol_alias__symbol_already_defined(self) -> None:
        """Tests that App.define_prefix_symbol_alias() raises a `ValueError`
        when the symbol is already defined for the prefix.
        """
        app = App()
        app.define_canonical_prefix("a", q(12))
        app.define_prefix_symbol_alias("A1", "a")

        with pytest.raises(ValueError):
            app.define_prefix_symbol_alias("A2", "a")

    def test_define_canonical_prefix__value_not_dimensionless(self) -> None:
        """Tests that App.define_canonical_prefix() raises a ValueError when
        the prefix value is not dimensionless."""

        app = App()
        app.define_root_unit("meter", "Length")
        app.define_derived_core_unit("pi", q("3.14159"))
        app.define_canonical_prefix("kilo", q(1000))
        app.define_canonical_prefix("pi_times_", q(1, pi=1))

        with pytest.raises(ValueError):
            app.define_canonical_prefix("meter_times_", q(1, meter=1))
        with pytest.raises(ValueError):
            app.define_canonical_prefix("cube_meter_times_", q(1, meter=3))
        with pytest.raises(ValueError):
            app.define_canonical_prefix(
                "kilometer_times_", q(1, {("kilo", "meter"): 1})
            )

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
        app.define_derived_core_unit(
            "yard", Quantity(Decimal("0.9144"), {"meter": Decimal(1)})
        )
        app.define_core_unit_alias("yard_alias", "yard")

        assert f("meter") == Quantity(Decimal(1), {"meter": Decimal(1)})
        assert (
            f("yard")
            == f("yard_alias")
            == Quantity(Decimal(1), {"yard": Decimal(1)})
        )
        with pytest.raises(ValueError):
            f("m")

    def test_quantity_from_unit_name_with_prefixes(self) -> None:
        """Tests App.quantity_from_unit_name()"""

        app = App()
        f = app.quantity_from_unit_name

        app.define_root_unit("meter", "Length")
        app.define_core_unit_symbol_alias("m", "meter")
        app.define_core_unit_alias("metre", "meter")
        app.define_canonical_prefix("kilo", q(1000))
        app.define_prefix_symbol_alias("k", "kilo")
        app.define_prefix_alias("K", "k")

        x = q(1, {("kilo", "meter"): 1})
        assert f("kilometer") == x
        assert f("kilom") == x
        assert f("kilometre") == x
        assert f("kmeter") == x
        assert f("km") == x
        assert f("kmetre") == x
        assert f("Kmeter") == x
        assert f("Km") == x
        assert f("Kmetre") == x

    def test_quantity_from_unit_name_with_prefixes__shadowing(self) -> None:
        """Tests shadowing for units."""

        app = App()
        f = app.quantity_from_unit_name

        app.define_root_unit("a", "A")
        app.define_canonical_prefix("aaaaaa", q(1))
        assert f("aaaaaaa") == q(1, {("aaaaaa", "a"): 1})

        # A unit with a smaller prefix shadows a unit with a larger prefix
        app.define_root_unit("aa", "AA")
        app.define_canonical_prefix("aaaaa", q(1))
        assert f("aaaaaaa") == q(1, {("aaaaa", "aa"): 1})

        app.define_root_unit("aaa", "AAA")
        app.define_canonical_prefix("aaaa", q(1))
        assert f("aaaaaaa") == q(1, {("aaaa", "aaa"): 1})

        # A unit with no prefix shadows any unit with a prefix
        app.define_root_unit("aaaaaaa", "AAAAAAA")
        assert f("aaaaaaa") == q(1, {"aaaaaaa": 1})

    def test_quantity_from_unit_name_with_s_suffix(self) -> None:
        """Tests quantity_from_unit_name() with -s suffix."""

        app = App()
        f = app.quantity_from_unit_name
        app.define_root_unit("meter", "Length")
        app.define_core_unit_alias("metre", "meter")
        app.define_core_unit_symbol_alias("m", "meter")
        app.define_canonical_prefix("milli", q("0.001"))
        app.define_prefix_symbol_alias("m", "milli")

        one_meter = q(1, meter=1)
        one_millimeter = q(1, {("milli", "meter"): 1})

        assert f("meters") == one_meter
        assert f("metres") == one_meter
        assert f("ms") == one_meter
        assert f("millimeters") == one_millimeter
        assert f("millimetres") == one_millimeter
        assert f("millims") == one_millimeter
        assert f("mmeters") == one_millimeter
        assert f("mmetres") == one_millimeter
        assert f("mms") == one_millimeter

        app.define_root_unit("second", "Time")
        app.define_core_unit_symbol_alias("s", "second")

        # millisecond (ms) shadows meter symbol + 's'
        assert f("ms") == q(1, {("milli", "second"): 1})

        # ss represents seconds
        assert f("ss") == q(1, {"second": 1})

        # Test that multiple -s don't work
        with pytest.raises(ValueError):
            f("metersssssss")
        with pytest.raises(ValueError):
            f("meterss")

    def test_quantity_convert_to_root_units(self) -> None:
        app = App()
        app.define_root_unit("i", "Length")
        app.define_derived_core_unit("v", q(5, i=1))
        app.define_derived_core_unit("x", q(10, i=1))

        f = app.quantity_convert_to_root_units
        assert f(q(12, i=1)) == q(12, i=1)
        assert f(q(12, v=1)) == q(60, i=1)
        assert f(q(12, x=1)) == q(120, i=1)

    def test_quantity_convert__time(self) -> None:
        """Tests App.quantity_convert_to_same_unit() with time units"""

        # Define apps (all have equivalent unit systems)
        app1 = App()
        app1.define_root_unit("second", "time")
        app1.define_derived_core_unit("minute", q(60, second=1))
        app1.define_derived_core_unit("hour", q(60, minute=1))
        app1.define_derived_core_unit("day", q(24, hour=1))
        app1.define_derived_core_unit("week", q(7, day=1))

        app2 = App()
        app2.define_root_unit("second", "time")
        app2.define_derived_core_unit("minute", q(60, second=1))
        app2.define_derived_core_unit("hour", q(3600, second=1))
        app2.define_derived_core_unit("day", q(86400, second=1))
        app2.define_derived_core_unit("week", q(604800, second=1))

        app3 = App()
        app3.define_root_unit("second", "time")
        app3.define_derived_core_unit("minute", q(60, second=1))
        app3.define_derived_core_unit("hour", q(60, minute=1))
        app3.define_derived_core_unit("day", q(86400, second=1))
        app3.define_derived_core_unit("week", q(7, day=1))

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
        app.define_derived_core_unit("kilogram", q(1000, gram=1))
        app.define_root_unit("meter", "length")
        app.define_root_unit("second", "time")
        app.define_derived_core_unit(
            "pascal", q(1, kilogram=1, meter=-1, second=-2)
        )
        app.define_derived_core_unit(
            "standard_atmosphere", q(101_325, pascal=1)
        )

        equivalent: list[Quantity] = [
            q(3, standard_atmosphere=1),
            q(303_975, pascal=1),
            q(303_975, kilogram=1, meter=-1, second=-2),
        ]
        for a in equivalent:
            for b in equivalent:
                assert app.quantity_convert(a, b.unit) == b

    def test_quantity_convert__frequency(self) -> None:
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_core_unit("minute", q(60, second=1))
        app.define_derived_core_unit("hour", q(60, minute=1))
        app.define_derived_core_unit("day", q(24, hour=1))
        app.define_derived_core_unit("year", q(365, day=1))
        f = app.quantity_convert

        assert f(q(3600, hour=-1), u(second=-1)) == q(1, second=-1)
        assert f(q(365, year=-1), u(day=-1)) == q(1, day=-1)

    def test_quantity_convert__different_dimensions(self) -> None:
        app = App()
        app.define_root_unit("second", "time")
        app.define_derived_core_unit("minute", q(60, second=1))
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
        app.define_derived_core_unit("minute", q(60, second=1))
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
        app.define_derived_core_unit("minute", q(60, second=1))
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
        app.define_derived_core_unit("minute", q(60, second=1))
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
        app.define_derived_core_unit("minute", q(60, second=1))
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
        app.define_derived_core_unit("dozen", q(12))

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
        app.define_derived_core_unit("kilogram", q(1000, gram=1))

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

    def test_quantity_convert_with_prefixes(self) -> None:
        app = App()
        app.define_root_unit("meter", "Length")
        app.define_canonical_prefix("kilo", q(1000))
        app.define_canonical_prefix("milli", q("0.001"))

        f = app.quantity_convert

        equivalent = [
            q(12, {("kilo", "meter"): 1}),
            q(12_000, {"meter": 1}),
            q(12_000_000, {("milli", "meter"): 1}),
        ]
        for a in equivalent:
            for b in equivalent:
                assert app.quantity_convert(a, b.unit) == b

        equivalent = [
            q("12", {("kilo", "meter"): 3}),
            q("12e9", {"meter": 3}),
            q("12e18", {("milli", "meter"): 3}),
        ]
        for a in equivalent:
            for b in equivalent:
                assert app.quantity_convert(a, b.unit) == b

    def test_quantity_display_str_with_prefixes(self) -> None:
        # Note: if no symbol is defined for either the core unit or prefix,
        # then the canonical name should be displayed.

        app0 = App()
        app0.define_root_unit("meter", "Length")
        app0.define_canonical_prefix("kilo", q(1000))

        app1 = App()
        app1.define_root_unit("meter", "Length")
        app1.define_canonical_prefix("kilo", q(1000))
        app1.define_core_unit_symbol_alias("m", "meter")

        app2 = App()
        app2.define_root_unit("meter", "Length")
        app2.define_canonical_prefix("kilo", q(1000))
        app2.define_prefix_symbol_alias("k", "kilo")

        app3 = App()
        app3.define_root_unit("meter", "Length")
        app3.define_canonical_prefix("kilo", q(1000))
        app3.define_core_unit_symbol_alias("m", "meter")
        app3.define_prefix_symbol_alias("k", "kilo")

        apps = [app0, app1, app2, app3]

        for i in range(0, 3):
            app = apps[i]
            s = app.quantity_display_str(q(12, {("kilo", "meter"): 3}))
            assert "kilometer" in s
            assert "3" in s

        s = app3.quantity_display_str(q(12, {("kilo", "meter"): 3}))
        assert "km" in s
        assert "3" in s
