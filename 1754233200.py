import html
import os
import sys
import urllib.parse

print("<!doctype html>")
print('<meta name="viewport" content="width=device-width">')
print("<pre>")

if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    directory = "."

for name in sorted(os.listdir(directory)):
    if os.path.isfile(os.path.join(directory, name)):
        url = urllib.parse.quote(name)
        print(f'<a href="{url}">{html.escape(name)}</a>')

print("</pre>")
