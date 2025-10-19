import os
import sys

from waitress import serve

if len(sys.argv) < 2:
    print("Usage: python 1760886000.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]

if not os.path.exists(image_path) or not os.path.isfile(image_path):
    print(f"Error: File not found or is not a file: {image_path}")
    sys.exit(1)

ext = os.path.splitext(image_path)[1].lower()
mime_type = None

if ext == ".png":
    mime_type = "image/png"
elif ext in (".jpg", ".jpeg"):
    mime_type = "image/jpeg"
elif ext == ".gif":
    mime_type = "image/gif"
elif ext == ".webp":
    mime_type = "image/webp"
elif ext == ".avif":
    mime_type = "image/avif"

if mime_type is None:
    print(f"Error: Unsupported image format: {ext}. Server will not start.")
    sys.exit(1)

file_size = os.path.getsize(image_path)


def wsgiapp(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path != "/":
        status = "404 Not Found"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [status.encode("utf-8")]

    try:
        f = open(image_path, "rb")
    except OSError:
        status = "500 Internal Server Error"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [status.encode("utf-8")]

    status = "200 OK"
    headers = [("Content-Type", mime_type), ("Content-Length", str(file_size))]
    start_response(status, headers)
    file_wrapper = environ.get("wsgi.file_wrapper")
    if file_wrapper is not None:
        return file_wrapper(f)
    return iter(f)


if __name__ == "__main__":
    serve(wsgiapp, host="127.0.0.1", port=8080)
