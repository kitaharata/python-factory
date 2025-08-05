import os
import sys
import time
import zipfile


def zip_items(paths_to_zip, zip_filename):
    """Compresses files and directories into a zip archive."""
    try:
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in paths_to_zip:
                if os.path.isfile(path):
                    zf.write(path)
                    print(f"Adding file: {path}")
                elif os.path.isdir(path):
                    print(f"Adding directory: {path}")
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zf.write(file_path)
        print(f"Successfully created archive '{zip_filename}'")
    except Exception as e:
        print(f"Error while creating zip archive: {e}")
        sys.exit(1)


def unzip_archive(zip_filepath):
    """Extracts a zip archive to a directory named after the archive."""
    target_dir = os.path.splitext(os.path.basename(zip_filepath))[0]
    if os.path.exists(target_dir):
        print(f"Error: Target '{target_dir}' already exists. Unzipping aborted.")
        sys.exit(1)

    try:
        with zipfile.ZipFile(zip_filepath, "r") as zf:
            zf.extractall(target_dir)
        print(f"Successfully extracted '{zip_filepath}' to '{target_dir}/'")
    except Exception as e:
        print(f"Error while extracting zip archive: {e}")
        sys.exit(1)


def main():
    """Handles command-line arguments to zip or unzip."""
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  Zip:   python {sys.argv[0]} [file_or_dir1] [file_or_dir2] ...")
        print(f"  Unzip: python {sys.argv[0]} [archive.zip]")
        sys.exit(1)

    first_arg = sys.argv[1]

    if len(sys.argv) == 2 and first_arg.endswith(".zip"):
        if not os.path.isfile(first_arg):
            print(f"Error: Zip file not found at '{first_arg}'")
            sys.exit(1)
        unzip_archive(first_arg)
    else:
        args_to_zip = sys.argv[1:]
        for path in args_to_zip:
            if not os.path.exists(path):
                print(f"Error: Path does not exist: '{path}'")
                sys.exit(1)

        timestamp = int(time.time())
        zip_filename = f"{timestamp}.zip"
        zip_items(args_to_zip, zip_filename)


if __name__ == "__main__":
    main()
