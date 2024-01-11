"""Debug script for testing purposes."""


import lark
import typer


app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def parse(text: str, start: str = "expr"):
    """Parses the given text and prints the parse tree."""
    parser = lark.Lark.open("calcon/grammar.lark", start=start)
    tree = parser.parse(text)

    print(tree.pretty())


if __name__ == "__main__":
    app()
