"""A simple, safe arithmetic calculator.

Evaluates arithmetic expressions using the standard-library `ast` module so that
only math (no function calls, no attribute access, no imports) can be executed.
"""
from __future__ import annotations

import ast
import operator
from typing import Callable

# Only these operations are allowed. This is the whole point of the safe path:
# anything else (calls, subscripts, names, etc.) raises instead of executing.
_OPS: dict[type[ast.AST], Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY: dict[type[ast.AST], Callable] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_CONSTANTS = {True: 1, False: 0}


class CalculatorError(ValueError):
    """Raised when the expression cannot be safely evaluated."""


def _eval(node: ast.AST) -> int | float:
    """Recursively evaluate a restricted AST node."""
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if node.value in _CONSTANTS:
            return _CONSTANTS[node.value]
        raise CalculatorError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        op = _OPS.get(op_type)
        if op is None:
            raise CalculatorError(f"unsupported operator: {op_type.__name__}")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        op = _UNARY.get(op_type)
        if op is None:
            raise CalculatorError(f"unsupported unary op: {op_type.__name__}")
        return op(_eval(node.operand))
    # Anything else (function calls, names, subscripts, etc.) is rejected.
    raise CalculatorError(f"unsupported expression component: {node!r}")


def calculate(expression: str) -> int | float:
    """Safely evaluate an arithmetic expression.

    >>> calculate("2 + 3 * 4")
    14
    >>> calculate("(2 + 3) * 4")
    20
    >>> calculate("2 ** 10")
    1024
    """
    expression = expression.strip()
    if not expression:
        raise CalculatorError("empty expression")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError(f"could not parse expression: {exc}") from exc
    result = _eval(tree)
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


def main() -> None:
    """Interactive REPL: type expressions, 'q' or empty line to quit."""
    print("Simple Calculator — type an expression (q to quit)")
    while (expr := input(">>> ")).strip().lower() not in {"", "q", "quit", "exit"}:
        try:
            print(calculate(expr))
        except CalculatorError as exc:
            print(f"error: {exc}")


if __name__ == "__main__":
    main()
