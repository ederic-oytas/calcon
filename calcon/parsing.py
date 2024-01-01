"""Module for parsing strings into parse trees."""

import lark


_expr_parser = lark.Lark.open_from_package(
    __name__, "grammar.lark", start="expr"
)


def parse_expr(text: str, /) -> lark.Tree:
    """Parses the given text as an expression and returns the parse tree."""
    return _expr_parser.parse(text)
