import html
import sys

print("<!doctype html>")
print('<meta name="viewport" content="width=device-width">')
print("<pre>")

if len(sys.argv) > 1:
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url:
                    escaped_url = html.escape(url)
                    print(f'<a href="{escaped_url}">{escaped_url}</a>')
    except FileNotFoundError:
        print(f"Error: File not found: {html.escape(file_path)}")

print("</pre>")
