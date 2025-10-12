import sys
from urllib.parse import urlparse

import requests


def normalize_url(target):
    """Return a valid URL with scheme if only a domain is provided."""
    parsed = urlparse(target)
    if not parsed.scheme:
        return "https://" + target
    return target


def check_trace(url):
    """Check if /cdn-cgi/trace is available and print the response or status."""
    url = normalize_url(url)
    trace_url = url.rstrip("/") + "/cdn-cgi/trace"
    try:
        response = requests.get(trace_url)
        if response.status_code == 200:
            print(f"{trace_url}\n")
            print(response.text)
        elif response.status_code == 404:
            print(f"{trace_url} -> 404 Not Found")
        else:
            print(f"{trace_url} -> HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"{trace_url} -> Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 1760194800.py <url_or_domain>")
        sys.exit(1)

    target = sys.argv[1]
    check_trace(target)
