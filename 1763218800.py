from waitress import serve

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tako Magic</title>
  </head>
  <body>
    <h1>See Console</h1>
    <script type="module">
      import { Tako } from "https://esm.sh/@takojs/tako";

      const tako = new Tako();

      tako.cli({}, (c) => c.print({ message: crypto.randomUUID() }));
    </script>
  </body>
</html>
"""


def wsgiapp(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/":
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        start_response(status, headers)
        return [INDEX_HTML.encode("utf-8")]
    else:
        status = "404 Not Found"
        headers = [("Content-Type", "text/plain")]
        start_response(status, headers)
        return [b"404 Not Found"]


if __name__ == "__main__":
    serve(wsgiapp, host="127.0.0.1", port=8080)
