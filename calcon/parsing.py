"""Module for parsing strings into parse trees."""

import lark

from calcon.expressions import (
    Add,
    Convert,
    Divide,
    Exponentiate,
    Expression,
    Ident,
    Multiply,
    Negate,
    Positive,
    Subtract,
    Unsigned,
)


_expr_parser = lark.Lark.open_from_package(
    __name__, "grammar.lark", start="expr"
)


def parse_expr(text: str, /) -> Expression:
    """Parses the given text as an expression and returns the parse tree."""
    parse_result = _expr_parser.parse(text)
    assert isinstance(parse_result, lark.Tree)
    transformer = _Transformer()
    expression = transformer.transform(parse_result)
    assert isinstance(expression, Expression)
    return expression


@lark.v_args(inline=True)
class _Transformer(lark.Transformer):
    """Transforms the tree into an Expression tree."""

    convert = Convert

    add = Add
    subtract = Subtract

    multiply = Multiply
    divide = Divide

    positive = Positive
    negate = Negate

    exponentiate = Exponentiate

    unsigned = Unsigned
    ident = Ident
