"""Module for Expression objects."""


from abc import abstractmethod
from dataclasses import dataclass

from calcon.app import App, Quantity


@dataclass
class Expression:
    """Base class for all Expression objects."""

    @abstractmethod
    def display_str(self) -> str:
        """Returns a string representation of this expression for display."""

    @abstractmethod
    def evaluate(self, app: App, /) -> Quantity:
        """Evaluates this expression in the context of an app."""


@dataclass
class Unsigned(Expression):
    """Represents an unsigned decimal value."""

    str_value: str

    def display_str(self) -> str:
        return self.str_value

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_from_magnitude_str(self.str_value)


@dataclass
class Ident(Expression):
    """Represents an identifier."""

    str_value: str

    def display_str(self) -> str:
        return self.str_value

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_from_unit_name(self.str_value)


@dataclass
class _UnaryOperation(Expression):
    """Represents a unary operation."""

    inner: Expression


@dataclass
class Positive(_UnaryOperation):
    """Represents an application of the unary plus."""

    def display_str(self) -> str:
        return f"+{self.inner.display_str()}"

    def evaluate(self, app: App, /) -> Quantity:
        return self.inner.evaluate(app)


@dataclass
class Negate(_UnaryOperation):
    """Represents a unary negation."""

    def display_str(self) -> str:
        return f"-{self.inner.display_str()}"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_negate(self.inner.evaluate(app))


@dataclass
class _BinaryOperation(Expression):
    """Represents a binary operation."""

    left: Expression
    right: Expression


@dataclass
class Convert(_BinaryOperation):
    """Represents a conversion operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()} -> {self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_convert(
            self.left.evaluate(app), self.right.evaluate(app).unit
        )


@dataclass
class Add(_BinaryOperation):
    """Represents an add operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()} + {self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_add(
            self.left.evaluate(app), self.right.evaluate(app)
        )


@dataclass
class Subtract(_BinaryOperation):
    """Represents an add operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()} - {self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_subtract(
            self.left.evaluate(app), self.right.evaluate(app)
        )


@dataclass
class Multiply(_BinaryOperation):
    """Represents an add operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()} * {self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_multiply(
            self.left.evaluate(app), self.right.evaluate(app)
        )


@dataclass
class Divide(_BinaryOperation):
    """Represents an add operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()} / {self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_divide(
            self.left.evaluate(app), self.right.evaluate(app)
        )


@dataclass
class Exponentiate(_BinaryOperation):
    """Represents an add operation."""

    def display_str(self) -> str:
        return f"({self.left.display_str()}^{self.right.display_str()})"

    def evaluate(self, app: App, /) -> Quantity:
        return app.quantity_exponentiate(
            self.left.evaluate(app), self.right.evaluate(app)
        )
