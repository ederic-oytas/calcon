"""Module which contains the statement classes."""


from abc import abstractmethod
from dataclasses import dataclass

from calcon.app import App
from calcon.expressions import Expression


@dataclass
class Statement:
    """Base class for all Statement classes."""

    @abstractmethod
    def execute(self, app: App, /) -> None:
        """Executes this statement in the context of the app."""


@dataclass
class DefineRoot(Statement):
    """Represents a statement which defines a root unit."""

    unit: str
    dimension: str

    def execute(self, app: App, /) -> None:
        app.define_root_unit(self.unit, self.dimension)


@dataclass
class DefineDerived(Statement):
    """Represents a statement which defines a derived unit."""

    unit: str
    value: Expression

    def execute(self, app: App, /) -> None:
        app.define_derived_unit(self.unit, self.value.evaluate(app))


@dataclass
class DefineAlias(Statement):
    """Represents a statement which defines a unit alias."""

    alias: str
    canonical: str

    def execute(self, app: App, /) -> None:
        app.define_unit_alias(self.alias, self.canonical)
