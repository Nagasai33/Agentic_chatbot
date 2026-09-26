import ast
import operator as op
MAX_EXPRESSION_LENGTH = 500
MAX_NUMBER_DIGITS = 100
MAX_AST_NODES = 100

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

        if isinstance(node.value, int):
            if len(str(abs(node.value))) > MAX_NUMBER_DIGITS:
                raise ValueError(
                    "Number is too large."
                )

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
    """
    Use this tool ONLY for mathematical calculations.

    Use it when the user explicitly asks you to calculate,
    add, subtract, multiply, divide, or evaluate an arithmetic expression.

    Do NOT use this tool for:
    - web searches
    - latest or current information
    - news
    - software versions
    - dates or events
    - general questions
    - factual questions

    Input must be a basic arithmetic expression using numbers
    and +, -, *, or /.
    """