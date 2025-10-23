from jinja2 import Environment

template_str = """<?xml version="1.0" encoding="UTF-8"?>
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
{% set total_items = items | length %}
<summary total="{{ total_items }}"/>
{% for item in items %}
  {% set record_id = item.id %}
  <record id="{{ record_id }}" status="{{ item.status | lower }}">
    <info>
      <dc:title>{{ item.title | upper }}</dc:title>
      {% if item.status == "Published" %}
      <dc:description>{{ item.description | trim }}</dc:description>
      {% else %}
      <dc:description>Draft content. Length: {{ item.description | length }} chars.</dc:description>
      {% endif %}
      <dc:type>{{ item.type | default('Text') }}</dc:type>
    </info>
    <details>
      <keywords count="{{ item.keywords | length }}">
        <list>{{ item.keywords | join(', ') }}</list>
      </keywords>
    </details>
  </record>
{% endfor %}
</metadata>"""

env = Environment()
template = env.from_string(template_str)

data = {
    "items": [
        {
            "id": "R001",
            "status": "Published",
            "title": "Sample Title 1",
            "description": "This is the first description.",
            "type": "Text",
            "keywords": ["data", "report"],
        },
        {
            "id": "R002",
            "status": "Draft",
            "title": "Sample Title 2",
            "description": "This is the second description.",
            "type": "Image",
            "keywords": ["image", "design", "drafting"],
        },
        {
            "id": "R003",
            "status": "Published",
            "title": "Sample Title 3",
            "description": "This is the third description.",
            "type": "Sound",
            "keywords": ["audio", "tutorial"],
        },
    ]
}

output = template.render(items=data["items"])
print(output)
