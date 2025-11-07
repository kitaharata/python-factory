import hashlib
import sys


def calculate_sha256(filepath):
    """Calculates the SHA256 hash of the specified file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return None
    except IOError as e:
        print(f"Error reading file '{filepath}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <filepath>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    sha256_hex = calculate_sha256(filepath)

    if sha256_hex:
        print(sha256_hex)
