"""Tests for calc.calculate — the CI gate."""
import math

import pytest

from calc import CalculatorError, calculate


def test_addition_and_precedence():
    assert calculate("2 + 3") == 5
    assert calculate("2 + 3 * 4") == 14
    assert calculate("(2 + 3) * 4") == 20


def test_unary_and_power():
    assert calculate("-5") == -5
    assert calculate("2 ** 10") == 1024
    assert calculate("2 + -3") == -1


def test_mod_and_floor_div():
    assert calculate("10 % 3") == 1
    assert calculate("10 // 3") == 3


def test_float_result_kept():
    assert calculate("1 / 4") == 0.25


def test_integer_result_collapsed():
    # 2 ** 10 is 1024.0 as a float; should collapse to int
    assert calculate("2 ** 10") == 1024 and isinstance(calculate("2 ** 10"), int)  # type: ignore[operator]


@pytest.mark.parametrize(
    "expr",
    [
        "",                 # empty
        "1 + + ",           # syntax
        "__import__('os')",  # call / injection attempt
        "1 + 2 . __class__",  # attribute access
        "x + 1",            # undefined name
        "1[0]",             # subscript
    ],
)
def test_rejects_unsafe_input(expr):
    with pytest.raises(CalculatorError):
        calculate(expr)


def test_doctest_runs():
    import doctest

    import calc

    results = doctest.testmod(calc, verbose=False, report=False)
    assert results.failed == 0
