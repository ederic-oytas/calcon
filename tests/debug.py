"""Debug script for testing purposes."""


import typer

from calcon.parsing import parse_expr


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def parse(expr: str):
    """Parses the given expression and prints the parse tree."""
    print(parse_expr(expr).pretty())


if __name__ == "__main__":
    app()
