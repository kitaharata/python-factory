import operator
import sys


def format_number_for_display(num):
    """If the number is mathematically an integer float, return it as an integer."""
    if num == int(num):
        return int(num)
    return num


def pop_stack(h):
    """Pops a value from the RPN stack (LIFO)."""
    if not h:
        raise IndexError("pop from empty RPN stack")
    return h.pop()


def rpn_calculate(tokens):
    """Calculates an RPN expression using a standard Python list as a LIFO stack."""

    h = []

    ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    for token in tokens:
        if token in ops:
            if len(h) < 2:
                raise ValueError("Insufficient operands")

            operand2 = pop_stack(h)
            operand1 = pop_stack(h)

            result = ops[token](operand1, operand2)

            op1_display = format_number_for_display(operand1)
            op2_display = format_number_for_display(operand2)
            res_display = format_number_for_display(result)

            print(f"{op1_display} {token} {op2_display} = {res_display}")
            h.append(result)
        else:
            try:
                num = float(token)
                h.append(num)
            except ValueError:
                raise ValueError(f"Unknown token: {token}")

    if len(h) != 1:
        raise ValueError("Invalid RPN expression (too many operands or missing operators)")

    return pop_stack(h)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1760799600.py RPN_EXPRESSION...")
        print("Example: python 1760799600.py 3 4 + 2 *")
        sys.exit(1)

    tokens = sys.argv[1:]

    try:
        result = rpn_calculate(tokens)
        res_display = format_number_for_display(result)
        print(res_display)
    except Exception as e:
        print(f"Calculation Error: {e}")
        sys.exit(1)
