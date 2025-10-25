import sys

from charset_normalizer import from_bytes


def decode_raw(raw):
    """Decode raw bytes using charset_normalizer."""
    result = from_bytes(raw).best()
    if result is None:
        print("Could not detect encoding.")
        return None
    content = raw.decode(result.encoding, errors="replace")
    return content


if __name__ == "__main__":
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        with open(filepath, "rb") as f:
            raw = f.read()
        content = decode_raw(raw)
        if content is not None:
            print(content, end="")
    elif len(sys.argv) == 1:
        if sys.stdin.isatty():
            print(f"Usage: python {sys.argv[0]} [filepath]")
            sys.exit(1)
        raw = sys.stdin.buffer.read()
        content = decode_raw(raw)
        if content is not None:
            print(content, end="")
    else:
        print(f"Usage: python {sys.argv[0]} [filepath]")
        sys.exit(1)
