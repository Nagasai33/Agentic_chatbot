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
    """Evaluate a basic arithmetic expression using +, -, *, and /."""

    if not isinstance(expression, str):
        return "Calculator error: Invalid expression."

    if len(expression) > MAX_EXPRESSION_LENGTH:
        return "Calculator error: Expression is too long."

    try:
        tree = ast.parse(expression, mode="eval")

        node_count = sum(1 for _ in ast.walk(tree))

        if node_count > MAX_AST_NODES:
            return "Calculator error: Expression is too complex."

        result = _evaluate(tree)
        return str(result)

    except ZeroDivisionError:
        return "Calculator error: Cannot divide by zero."

    except (SyntaxError, ValueError, TypeError) as e:
        return f"Calculator error: {e}"

    except Exception:
        return "Calculator error: Invalid expression."