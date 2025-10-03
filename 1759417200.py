import sys

import markdown_it


def process_markdown_file(file_path):
    """Reads a markdown file, converts it to HTML, and prints the result."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_input = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)
    md = markdown_it.MarkdownIt()
    html_output = md.render(markdown_input)
    print(html_output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <markdown_file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    process_markdown_file(file_path)
