"""Module for the command-line interface."""

from decimal import Decimal
import importlib.resources
from typing import Annotated, Union
import lark
import typer

from calcon.app import App as CalconApp, Quantity
from calcon.parsing import parse_expr, parse_statements


app = typer.Typer()


def create_default_calcon_app() -> CalconApp:
    """Creates a default calcon app."""

    calcon_app = CalconApp()
    prelude_res = importlib.resources.files("calcon").joinpath(
        "prelude.calcon"
    )
    with importlib.resources.as_file(prelude_res) as file:
        statements = parse_statements(file.read_text(encoding="utf8"))
        for statement in statements:
            statement.execute(calcon_app)

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
