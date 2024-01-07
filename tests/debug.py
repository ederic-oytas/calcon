"""Debug script for testing purposes."""


import lark
import typer

from calcon.parsing import parse_expr


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def parse(expr: str):
    """Parses the given expression and prints the parse tree."""
    parser = lark.Lark.open("calcon/grammar.lark", start="expr")
    tree = parser.parse(expr)

    print(tree.pretty())


if __name__ == "__main__":
    app()
