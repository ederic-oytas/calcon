"""Test invocations to the CLI typer interface."""

# In terms of test coverage, this file alone should cover the entire calcon
# package, except for definition errors.


from decimal import Decimal
from typing import Union
from typer.testing import CliRunner

import pytest
from calcon.main import app as main_app, create_default_calcon_app
from calcon.app import Quantity
from calcon.parsing import parse_expr


def q(magnitude: Union[int, str], /, **unit: Union[int, str]) -> Quantity:
    """Helper function to create a quantity, automatically converting the
    integers/strings to Decimal objects."""
    return Quantity(Decimal(magnitude), u(**unit))


def u(**unit: Union[int, str]) -> dict[str, Decimal]:
    return {c: Decimal(p) for c, p in unit.items()}


runner = CliRunner()


@pytest.mark.parametrize(
    "input_expr,expected_quantity",
    [
        ("1000 * gram -> kilogram", q(1, kilogram=1)),
        ("(3 * meter) * (4 * meter)", q(12, meter=2)),
        ("2 3 4", q(24)),
        ("3 meter * 4 meter", q(12, meter=2)),
        ("3 meter / 4 meter", q("0.75")),
        ("3 meter + 4 meter", q(7, meter=1)),
        ("3 meter - 4 meter", q(-1, meter=1)),
        ("---(4 meter)", q(-4, meter=1)),
        ("+++(4 meter)", q(4, meter=1)),
        ("(3 meter**2) + (4 meter^2)", q(7, meter=2)),
        ("(3 m**2) + (4 m^2)", q(7, meter=2)),
        ("(5 m)**0", q(1)),
        ("25.", q(25)),
        ("2.5", q("2.5")),
        (".25", q(".25")),
        ("2.5e12", q("2.5e12")),
        ("2.5e-12", q("2.5e-12")),
        ("2.5e+12", q("2.5e+12")),
        ("2.5E12", q("2.5E12")),
        ("1_2", q("12")),
        ("1_2_3.7_5e+6_7", q("123.75e67")),
        ("12 J / 3 m -> N", q(4, newton=1)),
        ("12 ohm * 3 A -> V", q(36, volt=1)),
        ("86400s -> d", q(1, day=1)),
    ],
)
def test_successes(input_expr: str, expected_quantity: Quantity):
    """Tests successful invocations."""
    result = runner.invoke(main_app, ["--", input_expr])
    output_str = result.stdout
    assert result.exit_code == 0

    calcon_app = create_default_calcon_app()
    output_expanded_expr_str, output_result_quantity_str = output_str.split(
        "="
    )
    output_expanded_expr_str = output_expanded_expr_str.strip()
    output_result_quantity_str = output_result_quantity_str.strip()

    # Requirement 1: Parsing the input expression should result in the same
    #    Expression tree as parsing the output expression before the =
    assert parse_expr(input_expr) == parse_expr(output_expanded_expr_str)

    # Requirement 2: Parsing the expression after the = should equal the
    #    expected quantity when parsed and evaluated.
    result_quantity_expr = parse_expr(output_result_quantity_str)
    assert result_quantity_expr.evaluate(calcon_app) == expected_quantity


@pytest.mark.parametrize(
    "input_expr",
    [
        "5 *",
        "5 +",
    ],
)
def test_syntax_errors(input_expr: str):
    """Tests invocations which result in a calculation error."""
    result = runner.invoke(main_app, ["--", input_expr])
    result_stdout = result.stdout
    assert result.exit_code == 1
    assert "syntax error" in result_stdout.lower()


@pytest.mark.parametrize(
    "input_expr",
    [
        "abcdef",  # abcdef doesn't exist
        "1000 * gram -> second",  # different dimensions
        "1 * m + 1 * s",  # different dimensions
        "1 * m - 1 * s",  # different dimensions
        "5 / 0",  # division by zero
        "2**(5 * m)",  # non-dimensionless exponent
        "2^(5 * m)",  # non-dimensionless exponent
    ],
)
def test_calculation_errors(input_expr: str):
    """Tests invocations which result in a calculation error."""
    result = runner.invoke(main_app, ["--", input_expr])
    result_stdout = result.stdout
    assert result.exit_code == 2
    assert "calculation error" in result_stdout.lower()
