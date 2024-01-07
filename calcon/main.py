"""Module for the command-line interface."""

from decimal import Decimal
from typing import Annotated, Union
import lark
import typer

from calcon.app import App as CalconApp, Quantity
from calcon.parsing import parse_expr


app = typer.Typer()


def create_default_calcon_app() -> CalconApp:
    """Creates a default calcon app."""

    def q(magnitude: Union[int, str], /, **unit: Union[int, str]) -> Quantity:
        return Quantity(
            Decimal(magnitude),
            {c: Decimal(p) for c, p in unit.items()},
        )

    calcon_app = CalconApp()

    calcon_app.define_root_unit("meter", "length")
    calcon_app.define_unit_alias("m", "meter")

    calcon_app.define_root_unit("gram", "mass")
    calcon_app.define_unit_alias("g", "gram")
    calcon_app.define_derived_unit("kilogram", q(1000, gram=1))
    calcon_app.define_unit_alias("kg", "kilogram")

    calcon_app.define_root_unit("second", "time")
    calcon_app.define_unit_alias("s", "second")

    calcon_app.define_root_unit("ampere", "current")
    calcon_app.define_unit_alias("A", "ampere")

    calcon_app.define_root_unit("kelvin", "temperature")
    calcon_app.define_unit_alias("K", "kelvin")

    calcon_app.define_root_unit("mole", "substance")
    calcon_app.define_unit_alias("mol", "mole")

    calcon_app.define_root_unit("candela", "luminosity")
    calcon_app.define_unit_alias("cd", "candela")

    return calcon_app


@app.command(no_args_is_help=True)
def main(
    expr: Annotated[
        str,
        typer.Argument(
            metavar="EXPR",
            help="Expression to evaluate.",
            show_default=False,
        ),
    ],
) -> None:
    """Calculator app with physical quantities."""

    calcon_app = create_default_calcon_app()

    try:
        expr_obj = parse_expr(expr)
        result = expr_obj.evaluate(calcon_app)
    except lark.LarkError as error:
        print("SYNTAX ERROR:")
        print(error)
        raise typer.Exit(1)
    except ValueError as error:
        print()
        print("CALCULATION ERROR: ", end="")
        if len(error.args) >= 1:
            print(error.args[0])
        print()
        raise typer.Exit(2)

    print()
    print(expr_obj.display_str())
    print()
    print(f"  = {calcon_app.quantity_display_str(result)}")
    print()
