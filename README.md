
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

## Changelog

### 0.1.1

- Added this changelog

- Fixed parsing numbers with leading period (`.`)

### 0.2.0

- Added adjacent multiplication (e.g. `5 meters` vs. `5 * meters`)

- Added E notation (e.g. `3.43E+2 m/s`, which equals `343 m/s`)

- Added support for single underscores in numbers (e.g. `1_000` or `1_000_000`)

- Added comments (Python-style) (e.g. `5 meters  # this is a comment`)

- Added more units

### 0.3.0

- Added unit prefixes (e.g. `kilo-`, `centi-`)

- Units can be appended with -s (e.g. `meters`, `liters`)

- Results now display as their unit symbols

- Bug fixes
