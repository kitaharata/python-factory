import sys

import requests
from rich.console import Console
from rich.markdown import Markdown


def fetch_and_render(url):
    """Fetches content from URL and renders it using rich if content type is text/markdown."""
    console = Console()

    try:
        headers = {"Accept": "text/markdown"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content_type_header = response.headers.get("Content-Type", "")
        content_type = content_type_header.split(";")[0].strip().lower()
        if content_type in ("text/markdown", "text/x-markdown", "text/plain"):
            content = response.text

            try:
                md = Markdown(content)
                console.print(md)
            except Exception as e:
                console.print(f"[bold red]Markdown Render Error:[/bold red] {e}")
        else:
            console.print(f"[bold red]Unsupported Content Type:[/bold red] {content_type}")
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error ({e.response.status_code}):[/bold red] {e.response.reason}")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e}")


if __name__ == "__main__":
    console = Console()

    if len(sys.argv) != 2:
        console.print("Usage: python 1759590000.py <URL>", style="bold yellow")
        sys.exit(1)

    url = sys.argv[1]
    fetch_and_render(url)
