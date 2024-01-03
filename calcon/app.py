"""Module containing the App and Quantity class."""


from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Quantity:
    """Represents a physical quantity."""

    magnitude: Decimal
    unit: dict[str, Decimal]


@dataclass
class _Definition:
    """Base class for all definition dataclasses."""


@dataclass
class _RootUnitDefinition(_Definition):
    """Defines a root unit."""

    dimension: str


@dataclass
class _DerivedUnitDefinition(_Definition):
    """Defines a unit derived from a root unit."""

    root_value: Quantity


@dataclass
class _AliasDefinition(_Definition):
    """Defines an alias for another unit."""

    canonical: str


class App:
    """Represents a Calcon app."""

    def __init__(self, /):
        """Creates a new Calcon app object."""
        self._definitions: dict[str, _Definition] = {}

    #
    # Definitions
    #

    def define_root_unit(self, name: str, dimension: str, /) -> None:
        """Defines a root unit."""
        self._definitions[name] = _RootUnitDefinition(dimension=dimension)

    def define_derived_unit(self, name: str, root_value: Quantity, /) -> None:
        """Defines a unit derived in terms of a root unit."""
        self._definitions[name] = _DerivedUnitDefinition(root_value=root_value)

    def define_alias(self, alias: str, canonical: str, /) -> None:
        """Defines an alias."""
        self._definitions[alias] = _AliasDefinition(canonical=canonical)

    #
    # Unit operations
    #
    def _unit_multiply(
        self, unit_a: dict[str, Decimal], unit_b: dict[str, Decimal], /
    ) -> dict[str, Decimal]:
        """Multiplies the two units and returns the result."""
        unit_c: dict[str, Decimal] = dict(unit_a)
        for component_b, power_b in unit_b.items():
            if power_c := unit_a[component_b] + power_b:
                unit_c[component_b] = power_c
        return unit_c

    def _unit_divide(
        self, unit_a: dict[str, Decimal], unit_b: dict[str, Decimal], /
    ) -> dict[str, Decimal]:
        """Divides the two units and returns the result."""
        unit_c: dict[str, Decimal] = dict(unit_a)
        for component_b, power_b in unit_b.items():
            if power_c := unit_a[component_b] - power_b:
                unit_c[component_b] = power_c
        return unit_c

    def _unit_exponentiate(
        self, unit: dict[str, Decimal], exponent: Decimal, /
    ) -> dict[str, Decimal]:
        """Raises the given unit to the given exponent and returns the
        result."""
        if exponent == 0:
            return {}
        return {
            component: component_power * exponent
            for component, component_power in unit.items()
        }

    def _unit_to_root_unit(
        self, unit: dict[str, Decimal], /
    ) -> dict[str, Decimal]:
        """Converts the given unit into an equivalent root unit and returns the
        result."""
        result_unit: dict[str, Decimal] = {}
        return result_unit

    #
    # Quantity operations
    #
    def quantity_negate(self, x: Quantity, /) -> Quantity:
        """Negates the given quantity and returns the result."""
        # TODO test
        return Quantity(-x.magnitude, x.unit)

    def quantity_add(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Adds the given quantities and returns the result.

        Raises `ValueError` if the quantities have different dimensions.
        """
        # TODO test
        if self._unit_to_root_unit(x.unit) != self._unit_to_root_unit(y.unit):
            raise ValueError("Cannot add units of different dimensions.")
        return Quantity(x.magnitude + y.magnitude, x.unit)

    def quantity_subtract(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Subtracts the quantities and returns the result."""
        # TODO test
        ...

    def quantity_multiply(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Multiplies the given quantities and returns the result."""
        # TODO test
        return Quantity(
            x.magnitude * y.magnitude,
            self._unit_multiply(x.unit, y.unit),
        )

    def quantity_divide(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Divides a quantity by another quantity and returns the result."""
        # TODO test
        return Quantity(
            x.magnitude / y.magnitude,
            self._unit_divide(x.unit, y.unit),
        )

    def quantity_exponentiate(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Raises a quantity to the power of another quantity and returns the
        result."""
        ...
        # TODO test