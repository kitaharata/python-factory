import sys
import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError


def fetch_pypi_releases(package_name):
    """Fetches and displays release history for a PyPI package."""
    url = f"https://pypi.org/rss/project/{package_name}/releases.xml"
    print(f"Fetching updates for '{package_name}' from {url}...")

    try:
        with urllib.request.urlopen(url) as response:
            tree = ET.parse(response)
            root = tree.getroot()

            channel = root.find("channel")
            if channel is None:
                print("Error: Could not find 'channel' in the RSS feed.")
                return

            print(f"\n--- Release History for {package_name} ---")

            items = channel.findall("item")
            if not items:
                print("No releases found.")
                return

            for item in items:
                title = item.find("title").text.strip()
                pub_date = item.find("pubDate").text.strip()
                print(f"- version: {title}")
                print(f"  published: {pub_date}")

    except HTTPError as e:
        print(f"Error: Failed to fetch data. HTTP Status: {e.code}")
        if e.code == 404:
            print(f"Package '{package_name}' not found on PyPI.")
    except URLError as e:
        print(f"Error: Failed to fetch URL. Reason: {e.reason}")
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML. Reason: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """Main function to run the PyPI release checker."""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <package_name>")
        print(f"Example: python {sys.argv[0]} requests")
        sys.exit(1)

    package_name = sys.argv[1]
    fetch_pypi_releases(package_name)


if __name__ == "__main__":
    main()
