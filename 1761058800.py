from jinja2 import Environment

template_str = """<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
{% for item in items %}
  <item>
    <dc:title>{{ item.title }}</dc:title>
    <dc:description>{{ item.description }}</dc:description>
    <dc:type>{{ item.type }}</dc:type>
  </item>
{% endfor %}
</metadata>"""

env = Environment()
template = env.from_string(template_str)

data = {
    "items": [
        {"title": "Sample Title 1", "description": "This is the first description.", "type": "Text"},
        {"title": "Sample Title 2", "description": "This is the second description.", "type": "Text"},
        {"title": "Sample Title 3", "description": "This is the third description.", "type": "Text"},
    ]
}

output = template.render(items=data["items"])
print(output)
