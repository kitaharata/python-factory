import heapq
import operator
import sys


def format_number_for_display(num):
    """If the number is mathematically an integer float, return it as an integer."""
    if num == int(num):
        return int(num)
    return num


def heappop_stack(h):
    """Pops a value from the heap, following LIFO order."""
    if not h:
        raise IndexError("pop from empty RPN stack")
    _, value = heapq.heappop(h)
    return value


def rpn_calculate_with_heapq(tokens):
    """Calculates an RPN expression using heapq internally to simulate a LIFO stack structure."""

    sequence_counter = 0
    h = []

    def heappush_stack_local(value):
        nonlocal sequence_counter
        heapq.heappush(h, (-sequence_counter, value))
        sequence_counter += 1

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

            operand2 = heappop_stack(h)
            operand1 = heappop_stack(h)

            result = ops[token](operand1, operand2)

            op1_display = format_number_for_display(operand1)
            op2_display = format_number_for_display(operand2)
            res_display = format_number_for_display(result)

            print(f"{op1_display} {token} {op2_display} = {res_display}")
            heappush_stack_local(result)
        else:
            try:
                num = float(token)
                heappush_stack_local(num)
            except ValueError:
                raise ValueError(f"Unknown token: {token}")

    if len(h) != 1:
        raise ValueError("Invalid RPN expression (too many operands or missing operators)")

    return heappop_stack(h)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1760799600.py RPN_EXPRESSION...")
        print("Example: python 1760799600.py 3 4 + 2 *")
        sys.exit(1)

    tokens = sys.argv[1:]

    try:
        result = rpn_calculate_with_heapq(tokens)
        res_display = format_number_for_display(result)
        print(res_display)
    except Exception as e:
        print(f"Calculation Error: {e}")
        sys.exit(1)
