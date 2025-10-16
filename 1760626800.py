from waitress import serve


def wsgiapp(environ, start_response):
    status = "200 OK"
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response(status, headers)
    body = environ.get("REMOTE_ADDR", "0.0.0.0")
    return [body.encode("utf-8")]


if __name__ == "__main__":
    serve(wsgiapp, host="127.0.0.1", port=8080)
