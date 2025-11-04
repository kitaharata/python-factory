import sys

import av


def print_media_metadata(file_path):
    """Outputs metadata tags for the specified media file."""
    try:
        container = av.open(file_path)
        metadata = container.metadata
        if metadata:
            for key, value in metadata.items():
                print(f"{key}: {value}")
    except av.AVError as e:
        print(f"Error processing file {file_path}: {e}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1762182000.py <media_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    print_media_metadata(file_path)
