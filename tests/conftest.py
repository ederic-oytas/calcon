"""Pytest config file for tests."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "-F",
        "--fast",
        dest="fast",
        action="store_true",
        help="Optimize testing performance through caching.",
    )
