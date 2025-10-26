import sys
import zipfile


def process_zip_file(zip_path):
    """Calculates total line count of text files in a ZIP archive and outputs zero-padded line counts."""
    try:
        total_lines = 0
        file_results = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            for file_info in zf.infolist():
                file_name = file_info.filename
                if file_info.is_dir():
                    continue

                line_count = 0
                try:
                    file_content_bytes = zf.read(file_name)
                    file_content = file_content_bytes.decode("utf-8")
                    line_count = len(file_content.splitlines())
                except Exception:
                    pass

                file_results.append((line_count, file_name))
                total_lines += line_count

        padding_width = len(str(total_lines)) if total_lines > 0 else 1
        for line_count, file_name in file_results:
            print(f"{line_count:0{padding_width}d} {file_name}")
        print(f"{total_lines:0{padding_width}d} .")
    except zipfile.BadZipFile:
        print(f"Error: Invalid or corrupt ZIP file: {zip_path}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: ZIP file not found: {zip_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <zip_file_path>")
        sys.exit(1)

    zip_file_path = sys.argv[1]
    process_zip_file(zip_file_path)
