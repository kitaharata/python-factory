import os
import shutil
import sys


def rename_untitled_files(src_dir, dest_dir):
    """Renames specific files in a source directory and moves them to a destination directory."""
    file_mapping = {}
    try:
        files = os.listdir(src_dir)
    except FileNotFoundError:
        print(f"Error: Source directory '{src_dir}' not found.")
        return
    for src_filename in files:
        if src_filename.startswith("untitled-"):
            basename, ext = os.path.splitext(src_filename)
            core_name = basename[len("untitled-") :]
            parts = core_name.split("-", 1)
            if len(parts) == 2:
                new_core_name_segment = parts[1]
                dest_filename = f"untitled-{new_core_name_segment}{ext}"
                file_mapping[src_filename] = dest_filename
    print(f"Source directory: {src_dir}")
    print(f"Destination directory: {dest_dir}")
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create destination directory '{dest_dir}': {e}")
        return
    success_count = 0
    for src_filename, dest_filename in file_mapping.items():
        src_path = os.path.join(src_dir, src_filename)
        dest_path = os.path.join(dest_dir, dest_filename)
        if not os.path.exists(src_path):
            print(f"Warning: File not found: {src_path}")
            continue
        if os.path.exists(dest_path):
            print(f"Skipping move: Destination file already exists: {dest_path}. Overwrite avoided.")
            continue
        try:
            shutil.move(src_path, dest_path)
            print(f"Rename and move complete: {src_filename} -> {dest_path}")
            success_count += 1
        except Exception as e:
            print(f"Error processing {src_filename}: {e}")
    print(f"Completed: Successfully processed {success_count} out of {len(file_mapping)} files.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 1763737200.py <source_directory> <destination_directory>")
        sys.exit(1)
    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]
    rename_untitled_files(source_dir, destination_dir)
