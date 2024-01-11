"""Module for parsing strings into parse trees."""

from typing import Any, Optional
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
from calcon.statements import (
    DefineDerivedSymbolAliases,
    DefinePrefixSymbolAliases,
    DefineRootSymbolAliases,
    Statement,
)

_stmtseq_parser = lark.Lark.open_from_package(
    __name__, "grammar.lark", start="stmtseq"
)
_expr_parser = lark.Lark.open_from_package(
    __name__, "grammar.lark", start="expr"
)


def parse_statements(text: str, /) -> tuple[Statement, ...]:
    """Parses the given text as a tuple of statements and returns it."""
    parse_result = _stmtseq_parser.parse(text)
    assert isinstance(parse_result, lark.Tree)
    assert parse_result.data == "statement_sequence"
    transformer = _Transformer()
    statements = transformer.transform(parse_result)
    assert isinstance(statements, tuple)
    return statements


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

    def statement_sequence(self, *statements: Statement):
        return statements

    def define_root_symbol_aliases(
        self,
        unit: str,
        symbol: Optional[str],
        *rest: Any,
    ) -> Statement:
        # converts lark.Token into strings
        unit = str(unit)
        if symbol is not None:
            symbol = str(symbol)

        aliases: list[str]
        dimension: str
        *aliases, dimension = rest
        assert all(isinstance(alias, lark.Token) for alias in aliases)
        for i, alias in enumerate(aliases):
            aliases[i] = str(alias)
        dimension = str(dimension)

        return DefineRootSymbolAliases(
            unit=unit,
            symbol_alias=symbol,
            aliases=aliases,
            dimension=dimension,
        )

    def define_derived_symbol_aliases(
        self,
        unit: str,
        symbol: Optional[str],
        *rest: Any,
    ) -> Statement:
        # converts lark.Token into strings
        unit = str(unit)
        if symbol is not None:
            symbol = str(symbol)

        aliases: list[str]
        value: Expression
        *aliases, value = rest
        assert all(isinstance(alias, lark.Token) for alias in aliases)
        for i, alias in enumerate(aliases):
            aliases[i] = str(alias)
        assert isinstance(value, Expression)

        return DefineDerivedSymbolAliases(
            unit=unit,
            symbol_alias=symbol,
            aliases=aliases,
            value=value,
        )

    def define_prefix_symbol_aliases(
        self,
        prefix: str,
        symbol: Optional[str],
        *rest: Any,
    ) -> Statement:
        # converts lark.Token into strings
        prefix = str(prefix)
        if symbol is not None:
            symbol = str(symbol)

        aliases: list[str]
        value: Expression
        *aliases, value = rest
        assert all(isinstance(alias, lark.Token) for alias in aliases)
        for i, alias in enumerate(aliases):
            aliases[i] = str(alias)
        assert isinstance(value, Expression)

        return DefinePrefixSymbolAliases(
            prefix=prefix,
            symbol_alias=symbol,
            aliases=aliases,
            value=value,
        )

    convert = Convert

    add = Add
    subtract = Subtract

    multiply = Multiply
    divide = Divide

    positive = Positive
    negate = Negate

    exponentiate = Exponentiate

    # For unsigned and ident, the token needs to be converted to str because
    # the repr() of the token is different.

    def unsigned(self, token: lark.Token) -> Expression:
        return Unsigned(str(token))

    def ident(self, token: lark.Token) -> Expression:
        return Ident(str(token))
