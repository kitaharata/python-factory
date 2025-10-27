import os

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

DATA_DIR = "data"
MAX_DATA_SIZE = 128 * 1024 * 1024

app = Flask(__name__, template_folder=".")

os.makedirs(DATA_DIR, exist_ok=True)


def get_dir_size(path):
    """Calculate the total size of files in a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def is_allowed_file(filename):
    """Check if the filename has an allowed extension (must be zip)."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "zip"


@app.route("/", methods=["GET", "POST"])
def upload_zip():
    """Route for handling zip file upload to the data directory."""
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("1761490830.html", error="No file selected.")
        file = request.files["file"]
        if file.filename == "":
            return render_template("1761490830.html", error="No file selected.")
        if file and is_allowed_file(file.filename):
            current_size = get_dir_size(DATA_DIR)
            estimated_upload_size = request.content_length if request.content_length is not None else 0
            if current_size + estimated_upload_size > MAX_DATA_SIZE:
                size_limit_mb = MAX_DATA_SIZE / (1024 * 1024)
                error_msg = (
                    f"Upload rejected: Data directory size limit ({size_limit_mb:.0f}MB) is likely to be exceeded."
                )
                return render_template("1761490830.html", error=error_msg)

            try:
                filename = secure_filename(file.filename)
                save_path = os.path.join(DATA_DIR, filename)
                file.save(save_path)
                print(f"File uploaded successfully and saved at: {save_path}")
                return render_template(
                    "1761490830.html",
                    message=f"File {filename} uploaded successfully.",
                    uploaded_filename=filename,
                )
            except Exception:
                return render_template("1761490830.html", error="Error uploading file.")
        else:
            unsupported_format_msg = "Unsupported file format. Please upload a ZIP file."
            return render_template("1761490830.html", error=unsupported_format_msg)
    return render_template("1761490830.html")


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port=8080)
