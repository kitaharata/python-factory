import sys


def get_divisor_pairs(n):
    """Returns a list of (i, n//i) pairs where i divides n."""
    pairs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            j = n // i
            pairs.append((i, j))
    return pairs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 1760108400.py <n>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError("Please enter a positive integer.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    result = get_divisor_pairs(n)
    print(result)
