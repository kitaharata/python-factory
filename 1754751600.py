import base64
import io
import os

from flask import Flask, render_template, request, send_file
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder=".")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}


def is_allowed_file(filename):
    """Check if the filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def upload_and_convert():
    """Route for handling image upload and conversion preview."""
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("1754751630.html", error="No file selected.")
        file = request.files["file"]
        if file.filename == "":
            return render_template("1754751630.html", error="No file selected.")
        if file and is_allowed_file(file.filename):
            try:
                filename_base = os.path.splitext(secure_filename(file.filename))[0]
                output_filename = f"{filename_base}_dithered_1bit.png"

                original_image_bytes = file.read()
                image = Image.open(io.BytesIO(original_image_bytes))

                original_preview_io = io.BytesIO()
                if hasattr(image, "n_frames") and image.n_frames > 1:
                    image.seek(0)
                image.save(original_preview_io, "PNG")
                original_preview_io.seek(0)
                original_image_b64 = base64.b64encode(original_preview_io.getvalue()).decode("utf-8")

                converted_image = image.convert("L").convert("1", dither=Image.Dither.FLOYDSTEINBERG)
                converted_io = io.BytesIO()
                converted_image.save(converted_io, "PNG")
                converted_io.seek(0)
                converted_image_b64 = base64.b64encode(converted_io.getvalue()).decode("utf-8")
                return render_template(
                    "1754751630.html",
                    original_image_data=original_image_b64,
                    converted_image_data=converted_image_b64,
                    output_filename=output_filename,
                )
            except Exception as e:
                return render_template("1754751630.html", error=f"An error occurred during image processing: {e}")
        else:
            unsupported_format_msg = "Unsupported file format. Supported formats: " + ", ".join(
                sorted(list(ALLOWED_EXTENSIONS))
            )
            return render_template("1754751630.html", error=unsupported_format_msg)
    return render_template("1754751630.html")


@app.route("/download", methods=["POST"])
def download():
    """Route for downloading the converted image."""
    try:
        b64_data = request.form.get("image_data")
        filename = request.form.get("filename", "converted_image.png")
        if not b64_data:
            return render_template("1754751630.html", error="No image data to download.")
        image_data = base64.b64decode(b64_data)
        img_io = io.BytesIO(image_data)
        return send_file(img_io, mimetype="image/png", as_attachment=True, download_name=filename)
    except Exception as e:
        return render_template("1754751630.html", error=f"An error occurred during download: {e}")


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port=8080)
