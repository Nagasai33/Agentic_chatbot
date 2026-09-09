import ast
import operator as op

from langchain_core.tools import tool


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Div) and right == 0:
            raise ValueError("Cannot divide by zero.")

        return _ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _evaluate(node.operand)

        if isinstance(node.op, ast.USub):
            return -value

        return value

    raise ValueError(
        "Only basic arithmetic (+, -, *, /) is supported."
    )


@tool
def calculator(expression: str) -> str:
    """Calculate a basic arithmetic expression."""

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree)

        return str(result)

    except (SyntaxError, ValueError, TypeError, ZeroDivisionError) as e:
        return f"Calculator error: {e}"