
# Calcon - Calculator with physical quantities

This is a calculator with support for physical quantities, coded in Python.

## Installation

```
pip install calcon
```

## Usage

Use `calcon --help` to show help.

Use `calcon EXPR` to calculate an expression.

Example output for `calcon "5 * kilogram + 5 * gram"`:

```
((5 * kilogram) + (5 * gram))

  = 5.005 * kilogram
```

Currently, there are only a limited number of units supported, but more will
be supported in the future.
