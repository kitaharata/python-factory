import os
import sys
from collections import Counter

if len(sys.argv) != 2:
    print("Usage: python 1758380400.py <directory>")
    sys.exit(1)
dir_path = os.path.expandvars(os.path.expanduser(sys.argv[1]))
if not os.path.isdir(dir_path):
    print(f"Error: '{dir_path}' is not a valid directory.")
    sys.exit(1)

ext_count = Counter()
for root, dirs, files in os.walk(dir_path):
    for file in files:
        parts = file.split(".", 1)
        if len(parts) > 1:
            ext = "." + parts[1].lower()
            ext_count[ext] += 1
if not ext_count:
    print("No files with extensions found.")
    sys.exit(1)

sorted_exts = sorted(ext_count.items(), key=lambda x: x[1], reverse=True)
for ext, count in sorted_exts:
    print(f"{ext}: {count}")
