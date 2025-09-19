import base64
import os
import sys
import zipfile

from flask import Flask, render_template

app = Flask(__name__, template_folder=".")
processed_files = []


def process_file(zip_ref, info, mime_map):
    """Process a file from the zip archive."""
    rel_path = info.filename
    ext = os.path.splitext(rel_path)[1].lower()

    try:
        bin_content = zip_ref.read(info.filename)
        if ext in mime_map:
            content = base64.b64encode(bin_content).decode("utf-8")
            return {"name": rel_path, "content": content, "is_image": True, "mime": mime_map[ext]}
        else:
            content = bin_content.decode("utf-8", errors="ignore")
            return {"name": rel_path, "content": content}
    except Exception:
        return {"name": rel_path, "content": "[Error reading file]"}


def process_zip_file(zip_path):
    """Process a zip file and extract its contents."""
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".avif": "image/avif",
    }
    files_list = []

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for info in zip_ref.infolist():
                if info.is_dir():
                    continue
                processed = process_file(zip_ref, info, mime_map)
                files_list.append(processed)
        return files_list
    except Exception as e:
        print(f"Error processing {zip_path}: {str(e)}")
        return None


@app.route("/")
def index():
    """Render the index page with processed files."""
    files = processed_files
    return render_template("1758207630.html", files=files)


if __name__ == "__main__":
    from waitress import serve

    if len(sys.argv) > 1:
        zip_path = sys.argv[1]
        if zip_path.endswith(".zip"):
            files_list = process_zip_file(zip_path)
            if files_list is not None:
                processed_files = files_list
    serve(app, host="127.0.0.1", port=8080)
