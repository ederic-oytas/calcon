"""Module containing the App and Quantity class."""


from dataclasses import dataclass
from decimal import Decimal
from pprint import pprint


@dataclass
class Quantity:
    """Represents a physical quantity."""

    magnitude: Decimal
    unit: dict[str, Decimal]


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


class App:
    """Represents a Calcon app."""

    def __init__(self, /) -> None:
        """Creates a new Calcon app object."""
        self._unit_definitions: dict[str, _UnitDefinition] = {}
        self._dimensions_to_units: dict[str, str] = {}

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
        pprint(self._unit_definitions)

    def define_unit_alias(self, alias: str, canonical: str, /) -> None:
        """Defines an alias.

        Raises `ValueError` if `alias` is already defined.
        """
        if alias in self._unit_definitions:
            raise ValueError(f"Unit {alias!r} is already defined.")
        self._unit_definitions[alias] = _UnitAliasDefinition(
            canonical=canonical
        )

    #
    # Unit operations
    #

    def _unit_lookup(self, unit_name: str, /) -> dict[str, Decimal]:
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
        multiplicand: dict[str, Decimal],
        multiplier: dict[str, Decimal],
        exponent: Decimal,
        /,
    ) -> None:
        """Multiplies a unit in-place by another unit raised to a power."""
        for component, multiplier_power in multiplier.items():
            multiplicand_power = multiplicand.get(component, 0)
            result_power = multiplicand_power + multiplier_power * exponent
            if result_power:
                multiplicand[component] = result_power

    def _unit_root_value(self, unit: dict[str, Decimal], /) -> Quantity:
        """Returns the root value of the given unit."""
        root_magnitude = Decimal(1)
        root_unit = {}
        for component, power in unit.items():
            definition = self._unit_definitions[component]

            # If component is a root unit, then just multiply the unit
            if isinstance(definition, _RootUnitDefinition):
                self._unit_multiply_power_in_place(
                    root_unit, {component: power}, Decimal(1)
                )
                continue

            # Multiply the term
            assert isinstance(definition, _DerivedUnitDefinition)
            root_magnitude *= definition.root_value.magnitude
            self._unit_multiply_power_in_place(
                root_unit, definition.root_value.unit, power
            )

        return Quantity(root_magnitude, root_unit)

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
        self, quantity: Quantity, target_unit: dict[str, Decimal], /
    ) -> Quantity:
        """Converts the first quantity to the same units as the second quantity
        and returns the result.

        Raises `ValueError` if the quantities have different dimensions.
        """

        source_unit_root_value = self._unit_root_value(quantity.unit)
        target_unit_root_value = self._unit_root_value(target_unit)

        print(target_unit)
        print(target_unit_root_value)

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
        # TODO test
        result_unit = dict(x.unit)
        self._unit_multiply_power_in_place(result_unit, y.unit, Decimal(1))
        return Quantity(x.magnitude * y.magnitude, result_unit)

    def quantity_divide(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Divides a quantity by another quantity and returns the result."""
        # TODO test
        result_unit = dict(x.unit)
        self._unit_multiply_power_in_place(result_unit, y.unit, Decimal(-1))
        return Quantity(x.magnitude / y.magnitude, result_unit)

    def quantity_exponentiate(self, x: Quantity, y: Quantity, /) -> Quantity:
        """Raises a quantity to the power of another quantity and returns the
        result."""
        ...
        # TODO finish and test
        return Quantity(Decimal(0), {})
