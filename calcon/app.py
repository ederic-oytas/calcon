"""Module containing the App and Quantity class."""


from dataclasses import dataclass
from decimal import Decimal
from typing import Union


_Unit = dict[Union[str, tuple[str, str]], Decimal]


@dataclass
class Quantity:
    """Represents a physical quantity."""

    magnitude: Decimal
    """Magnitude of this quantity."""

    unit: _Unit
    """Dictionary mapping single units (components) to the power they are
    raised to.
    
    Each key can either be a `str` or a tuple of two `str's`. If it is a `str`,
    then it is a canonical unit name. If it is a tuple, then the first element
    is a canonical prefix and the second element is a canonical unit name.
    """


@dataclass
class _UnitDefinition:
    """Base class for all unit definition dataclasses."""


@dataclass
class _RootUnitDefinition(_UnitDefinition):
    """Defines a root unit."""

    dimension: str


@dataclass
class _DerivedUnitDefinition(_UnitDefinition):
    """Defines a unit derived from a root unit."""

    root_value: Quantity


@dataclass
class _UnitAliasDefinition(_UnitDefinition):
    """Defines an alias for another unit."""

    canonical: str


@dataclass
class _PrefixDefinition:
    """Defines a unit prefix."""


@dataclass
class _CanonicalPrefixDefinition(_PrefixDefinition):
    """Defines a canonical prefix."""

    value: Decimal


@dataclass
class _PrefixAliasDefinition(_PrefixDefinition):
    """Defines a prefix alias."""

    canonical: str


class App:
    """Represents a Calcon app."""

    def __init__(self, /) -> None:
        """Creates a new Calcon app object."""
        self._unit_definitions: dict[str, _UnitDefinition] = {}
        self._dimensions_to_units: dict[str, str] = {}
        self._units_to_symbols: dict[str, str] = {}
        self._prefix_definitions: dict[str, _PrefixDefinition] = {}
        self._prefixes_to_symbols: dict[str, str] = {}

    #
    # Definitions
    #

    def define_root_unit(self, unit: str, dimension: str, /) -> None:
        """Defines a root unit.

        Raises `ValueError` if `unit` is already defined or if `dimension` is
        already associated to a root unit.
        """
        if unit in self._unit_definitions:
            raise ValueError(f"Unit {unit!r} is already defined.")
        if dimension in self._dimensions_to_units:
            raise ValueError(
                f"Dimension {dimension!r} is already associated to a root "
                "unit."
            )
        self._unit_definitions[unit] = _RootUnitDefinition(dimension=dimension)
        self._dimensions_to_units[dimension] = unit

    def define_derived_unit(self, unit: str, value: Quantity, /) -> None:
        """Defines a unit derived in terms of a root unit.

        Raises `ValueError` if `unit` is already defined.
        """
        if unit in self._unit_definitions:
            raise ValueError(f"Unit {unit!r} is already defined.")

        value_unit_root_value = self._unit_root_value(value.unit)

        self._unit_definitions[unit] = _DerivedUnitDefinition(
            root_value=Quantity(
                magnitude=value.magnitude * value_unit_root_value.magnitude,
                unit=value_unit_root_value.unit,
            )
        )

    def define_unit_alias(self, alias: str, canonical: str, /) -> None:
        """Defines an alias.

        Raises `ValueError` if `alias` is already defined.
        """
        if alias in self._unit_definitions:
            raise ValueError(f"Unit {alias!r} is already defined.")
        self._unit_definitions[alias] = _UnitAliasDefinition(
            canonical=canonical
        )

    def define_unit_symbol_alias(self, symbol: str, canonical: str, /) -> None:
        """Defines a symbol alias for a unit.

        Raises `ValueError` if the symbol alias is already an alias for a unit,
        or if the canonical unit already has a symbol defined for it.
        """
        self.define_unit_alias(symbol, canonical)
        if canonical in self._units_to_symbols:
            raise ValueError(
                f"Unit {canonical} already has a symbol defined for it."
            )
        self._units_to_symbols[canonical] = symbol

    def define_canonical_prefix(self, prefix: str, value: Decimal, /) -> None:
        """Defines a canonical unit prefix.

        Raises `ValueError` if a prefix is already defined.
        """
        if prefix in self._prefix_definitions:
            raise ValueError(f"Prefix {prefix} is already defined.")
        self._prefix_definitions[prefix] = _CanonicalPrefixDefinition(
            value=value
        )

    def define_prefix_alias(self, alias: str, canonical: str, /) -> None:
        """Defines a prefix alias.

        Raises `ValueError` if a prefix is already defined.
        """
        if alias in self._prefix_definitions:
            raise ValueError(f"Prefix {alias} is already defined.")
        self._prefix_definitions[alias] = _PrefixAliasDefinition(
            canonical=canonical
        )

    def define_prefix_symbol_alias(self, symbol: str, canonical: str) -> None:
        """Defines a prefix alias.

        Raises `ValueError` if a prefix is already defined or if a symbol has
        already been defined for the given prefix.
        """
        self.define_prefix_alias(symbol, canonical)
        if canonical in self._prefixes_to_symbols:
            raise ValueError(
                f"A symbol has already been defined for the prefix {canonical}"
            )
        self._prefixes_to_symbols[canonical] = symbol

    #
    # Unit operations
    #

    def _unit_lookup(self, unit_name: str, /) -> _Unit:
        """Looks up a unit by its name and returns it.

        Raises `ValueError` if the unit doesn't exist.
        """
        try:
            definition = self._unit_definitions[unit_name]
            if isinstance(definition, _UnitAliasDefinition):
                return {definition.canonical: Decimal(1)}
            assert isinstance(
                definition, (_RootUnitDefinition, _DerivedUnitDefinition)
            )
            return {unit_name: Decimal(1)}

        except KeyError:
            raise ValueError(f"Unknown unit {unit_name!r}") from None

    def _unit_multiply_power_in_place(
        self,
        multiplicand: _Unit,
        multiplier: _Unit,
        exponent: Decimal,
        /,
    ) -> None:
        """Multiplies a unit in-place by another unit raised to a power."""
        for component, multiplier_power in multiplier.items():
            multiplicand_power = multiplicand.get(component, 0)
            result_power = multiplicand_power + multiplier_power * exponent
            if result_power:
                multiplicand[component] = result_power
            else:
                multiplicand.pop(component, None)

    def _unit_root_value(self, unit: _Unit, /) -> Quantity:
        """Returns the root value of the given unit."""
        root_magnitude = Decimal(1)
        root_unit: _Unit = {}
        for component, power in unit.items():
            prefix_value: Decimal
            core: str
            if isinstance(component, str):
                prefix_value = Decimal(1)
                core = component
            else:
                assert isinstance(component, tuple)
                prefix, core = component
                prefix_value = self._prefix_value(prefix)

            core_definition = self._unit_definitions[core]

            # If component is a root unit, then just multiply the unit
            if isinstance(core_definition, _RootUnitDefinition):
                self._unit_multiply_power_in_place(
                    root_unit, {core: power}, Decimal(1)
                )
                continue

            # Multiply the term
            assert isinstance(core_definition, _DerivedUnitDefinition)
            root_magnitude *= prefix_value
            root_magnitude *= core_definition.root_value.magnitude
            self._unit_multiply_power_in_place(
                root_unit, core_definition.root_value.unit, power
            )

        return Quantity(root_magnitude, root_unit)

    #
    # Prefix operations
    #

    def _prefix_value(self, prefix: str) -> Decimal:
        """Returns the value of a prefix."""
        definition = self._prefix_definitions[prefix]
        if isinstance(definition, _CanonicalPrefixDefinition):
            return definition.value
        assert isinstance(definition, _PrefixAliasDefinition)
        canonical_definition = self._prefix_definitions[prefix]
        assert isinstance(canonical_definition, _CanonicalPrefixDefinition)
        return canonical_definition.value

    #
    # Quantity operations
    #
    def quantity_from_magnitude_str(self, magnitude_str: str, /) -> Quantity:
        """Creates a unitless quantity from the given magnitude (represented as
        a string) and returns the result.
        """
        return Quantity(Decimal(magnitude_str), {})

    def quantity_from_unit_name(self, unit_name: str, /) -> Quantity:
        """Creates a quantity of magnitude 1 from the given unit name and
        returns the result.

        Raises `ValueError` if the unit name is not in the unit namespace.
        """
        # Raises `ValueError` on lookup fail
        return Quantity(Decimal(1), self._unit_lookup(unit_name))

    def quantity_convert(
        self, quantity: Quantity, target_unit: _Unit, /
    ) -> Quantity:
        """Converts the first quantity to the same units as the second quantity
        and returns the result.

        Raises `ValueError` if the quantities have different dimensions.
        """

        source_unit_root_value = self._unit_root_value(quantity.unit)
        target_unit_root_value = self._unit_root_value(target_unit)

        if source_unit_root_value.unit != target_unit_root_value.unit:
            raise ValueError("Units have different dimensions.")

        return Quantity(
            magnitude=(
                quantity.magnitude
                * source_unit_root_value.magnitude
                / target_unit_root_value.magnitude
            ),
            unit=target_unit,
        )

    def quantity_negate(self, quantity: Quantity, /) -> Quantity:
        """Negates the given quantity and returns the result."""
        return Quantity(-quantity.magnitude, quantity.unit)

    def quantity_add(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Adds the given quantities and returns the result.

        Raises `ValueError` if the quantities have different dimensions.
        """
        y = self.quantity_convert(y, x.unit)
        return Quantity(x.magnitude + y.magnitude, x.unit)

    def quantity_subtract(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Subtracts the quantities and returns the result."""
        y = self.quantity_convert(y, x.unit)
        return Quantity(x.magnitude - y.magnitude, x.unit)

    def quantity_multiply(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Multiplies the given quantities and returns the result."""
        result_unit = dict(x.unit)
        self._unit_multiply_power_in_place(result_unit, y.unit, Decimal(1))
        return Quantity(x.magnitude * y.magnitude, result_unit)

    def quantity_divide(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Divides a quantity by another quantity and returns the result.

        Raises `ValueError` if a division by zero error occurs.
        """
        result_unit = dict(x.unit)
        self._unit_multiply_power_in_place(result_unit, y.unit, Decimal(-1))
        if y.magnitude == 0:
            raise ValueError("Cannot divide by zero!")
        return Quantity(x.magnitude / y.magnitude, result_unit)

    def quantity_exponentiate(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Raises a quantity to the power of another quantity and returns the
        result.

        Raises `ValueError` if the exponent isn't dimensionless.
        """
        y_unit_root_value = self._unit_root_value(y.unit)
        if y_unit_root_value.unit:
            raise ValueError("Exponent must be dimensionless.")

        y_root_magnitude = y.magnitude * y_unit_root_value.magnitude
        if y_root_magnitude == 0:
            return Quantity(Decimal(1), {})

        result_unit: _Unit = {}
        self._unit_multiply_power_in_place(
            result_unit, x.unit, y_root_magnitude
        )
        return Quantity(x.magnitude**y_root_magnitude, result_unit)

    def quantity_display_str(self, x: Quantity) -> str:
        """Returns a string representation for display for the given
        quantity."""

        factors = [str(x.magnitude)]
        for component, power in x.unit.items():
            symbol: str
            if isinstance(component, str):
                symbol = self._units_to_symbols.get(component, component)
            else:
                assert isinstance(component, tuple)
                prefix, core = component
                prefix_symbol = self._prefixes_to_symbols.get(prefix, prefix)
                core_symbol = self._units_to_symbols.get(core, core)
                symbol = f"{prefix_symbol}{core_symbol}"

            if power == 1:
                factors.append(symbol)
            else:
                factors.append(f"{symbol}^{power}")

        return " ".join(factors)
