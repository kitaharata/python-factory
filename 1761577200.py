import mimetypes
import os
import sys

from waitress import serve

if len(sys.argv) < 2:
    print("Usage: python 1760886000.py <directory_path>")
    sys.exit(1)

base_dir = sys.argv[1]

if not os.path.exists(base_dir) or not os.path.isdir(base_dir):
    print(f"Error: Directory not found or is not a directory: {base_dir}")
    sys.exit(1)

base_dir = os.path.abspath(base_dir)


def wsgiapp(environ, start_response):
    path_info = environ.get("PATH_INFO", "/").lstrip("/")
    if path_info == "":
        file_path = os.path.join(base_dir, "index.html")
    else:
        file_path = os.path.join(base_dir, path_info)

    abs_file_path = os.path.abspath(file_path)
    if not abs_file_path.startswith(base_dir):
        status = "403 Forbidden"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [status.encode("utf-8")]
    if not os.path.isfile(abs_file_path):
        status = "404 Not Found"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [status.encode("utf-8")]

    mime_type, encoding = mimetypes.guess_type(abs_file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    try:
        f = open(abs_file_path, "rb")
    except OSError:
        status = "500 Internal Server Error"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [status.encode("utf-8")]

    file_size = os.path.getsize(abs_file_path)

    status = "200 OK"
    headers = [("Content-Type", mime_type), ("Content-Length", str(file_size))]
    if encoding:
        headers.append(("Content-Encoding", encoding))
    start_response(status, headers)
    file_wrapper = environ.get("wsgi.file_wrapper")
    if file_wrapper is not None:
        return file_wrapper(f)
    return iter(f)


if __name__ == "__main__":
    serve(wsgiapp, host="127.0.0.1", port=8080)
