import os
import sys

import yaml

INPUT_FILE = "1759762830.txt"
OUTPUT_FILE = "1759762831.txt"


def test_yaml_parsing():
    """Reads the input data file line by line, attempts to parse each line as YAML, and logs the results."""
    if not os.path.exists(INPUT_FILE):
        sys.stderr.write(f"Error: Input file {INPUT_FILE} not found.\n")
        sys.exit(1)

    print(f"Starting YAML parsing test on {INPUT_FILE}...")
    results = []

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except IOError as e:
        sys.stderr.write(f"Error reading input file: {e}\n")
        sys.exit(1)

    for i, line in enumerate(lines):
        line_content = line.rstrip("\r\n")
        status = "OK"
        parsed_data = None

        try:
            parsed_data = yaml.safe_load(line_content)
        except yaml.YAMLError:
            status = "yaml.YAMLError"
        except Exception:
            status = "Exception"

        output_str = ""

        if status == "OK":
            output_str = str(parsed_data)

        results.append(f'L{i + 1:03d}: Status={status}, Content: "{line_content}", Result: "{output_str}"')

    print(f"Finished parsing {len(lines)} lines. Writing results to {OUTPUT_FILE}...")

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
            out_f.write("\n".join(results) + "\n")
        print(f"Results saved to {OUTPUT_FILE}.")
    except Exception as e:
        sys.stderr.write(f"Failed to write results: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    test_yaml_parsing()
