"""Module for the command-line interface."""

from typing import Annotated
import typer


app = typer.Typer()


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

    print("Hello world!")
