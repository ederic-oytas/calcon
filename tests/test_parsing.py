"""Testing module for parsing.py"""

import lark
import pytest
from calcon.expressions import Expression
from calcon.parsing import parse_expr, parse_statements


def test_statements() -> None:
    assert len(parse_statements("")) == 0
    assert len(parse_statements("\n\n\n\n")) == 0
    assert len(parse_statements("#comment")) == 0
    assert len(parse_statements("1 liter = 0.001 m^3")) == 1
    assert len(parse_statements("1 liter (L) = 0.001 m^3")) == 1
    assert len(parse_statements("1 liter [litre] = 0.001 m^3")) == 1
    assert len(parse_statements("1 liter (L) [litre] = 0.001 m^3")) == 1
    assert (
        len(parse_statements("1 liter (L) [litre, litres] = 0.001 m^3")) == 1
    )

    statements = parse_statements(
        """

        1 inch (in) [inches] = 25.4 mm
        # comment line

        1 liter (L) [litre, litres] = 0.001 m^3
        # comment line

        """
    )
    assert len(statements) == 2

    statements = parse_statements(
        """
        1 inch (in) [inches] = 25.4 mm
        1 foot (ft) [feet] = 12 in  # comment
        1 liter (L) [litre, litres] = 0.001 m^3
        """
    )
    assert len(statements) == 3

    # Test unicode characters
    assert len(parse_statements("1 angstrom (Å)  = 10e-10 m")) == 1
    assert len(parse_statements("1 degree (°) = (pi/180) rad")) == 1
    assert len(parse_statements("1 rankine (R) [°R, °Ra] = (5/9) K")) == 1
    assert len(parse_statements("1 pi (π) = 3.14")) == 1

    # Test that numbers in identifiers aren't valid

    with pytest.raises(lark.LarkError):
        parse_statements("1 dozen (12) = 12")
    with pytest.raises(lark.LarkError):
        parse_statements("1 square_meter (m2) = m^2")
    with pytest.raises(lark.LarkError):
        parse_statements("1 one_unit (1u) = unit")


def test_expr() -> None:
    assert isinstance(parse_expr("5"), Expression)
    assert isinstance(parse_expr("5  # comment"), Expression)
    assert isinstance(parse_expr("5 meters  # comment"), Expression)
