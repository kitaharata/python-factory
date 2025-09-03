import json
import sys
from urllib.parse import urlsplit


def extract_domain_name_components(input_string):
    """Parses an input string as a URL or bare domain into its first label and remaining domain name."""
    parsed_original = urlsplit(input_string)
    first_label = ""
    remaining_domain_name = ""

    if parsed_original.scheme in ("mailto", "sip", "sips"):
        path_content = parsed_original.path
        if "@" in path_content:
            domain_name_candidate = path_content.split("@")[-1]
        else:
            domain_name_candidate = path_content
    elif parsed_original.netloc:
        domain_name_candidate = parsed_original.netloc
    elif (
        parsed_original.path
        and "." in parsed_original.path
        and not parsed_original.scheme
        and not parsed_original.netloc
        and not parsed_original.path.startswith("/")
    ):
        temp_parsed = urlsplit(f"http://{parsed_original.path}")
        domain_name_candidate = temp_parsed.netloc
    elif parsed_original.path:
        domain_name_candidate = parsed_original.path

    if domain_name_candidate:
        if domain_name_candidate.count(".") >= 2:
            parts = domain_name_candidate.split(".", 1)
            first_label = parts[0]
            remaining_domain_name = parts[1]
        else:
            remaining_domain_name = domain_name_candidate

    return {"first_label": first_label, "remaining_domain_name": remaining_domain_name}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        error_data = {"error": "Usage: python script.py <url_or_domain>"}
        print(json.dumps(error_data, ensure_ascii=False, separators=(",", ":")))
        sys.exit(1)
    input_arg = sys.argv[1]
    result = extract_domain_name_components(input_arg)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
