import sys

from markdown_it import MarkdownIt


def extract_text_from_children(children):
    """Recursively extracts text content from markdown-it tokens (children array)."""
    text = ""
    if not children:
        return text
    for child in children:
        if child.type == "text":
            text += child.content
        elif child.type == "code_inline":
            text += f"`{child.content}`"
        elif child.children:
            text += extract_text_from_children(child.children)
    return text


def process_markdown_file(file_path):
    """Reads a markdown file, extracts headings, and prints the Table of Contents (TOC)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            markdown_input = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)
    md = MarkdownIt()
    tokens = md.parse(markdown_input)
    headings = []

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "heading_open":
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                inline_token = tokens[i + 1]
                level = int(token.tag[1])
                text = extract_text_from_children(inline_token.children)
                headings.append((level, text))
                i += 2
        i += 1
    if not headings:
        return
    min_level = min(h[0] for h in headings)
    for level, text in headings:
        indentation = "  " * (level - min_level)
        print(f"{indentation}* {text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <markdown_file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    process_markdown_file(file_path)
