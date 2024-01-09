"""Module for the command-line interface."""

import importlib.resources
from typing import Annotated
import lark
import typer

from calcon.app import App
from calcon.parsing import parse_expr, parse_statements


typer_app = typer.Typer()


def default_app() -> App:
    """Creates a default calcon app."""

    calcon_app = App()
    prelude_res = importlib.resources.files("calcon").joinpath(
        "prelude.calcon"
    )
    with importlib.resources.as_file(prelude_res) as file:
        statements = parse_statements(file.read_text(encoding="utf8"))
        for statement in statements:
            statement.execute(calcon_app)

    return calcon_app


@typer_app.command(no_args_is_help=True)
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

    app = default_app()

    try:
        expr_obj = parse_expr(expr)
        result = expr_obj.evaluate(app)
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
    print(f"  = {app.quantity_display_str(result)}")
    print()
