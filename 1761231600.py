from jinja2 import Environment

template_str = """{% macro render_node(node) %}
    <region id="{{ node.id }}" bounds="{{ node.region | join(', ') }}">
        {% if node.points %}
        <items>
            {% for item in node.points %}
            <point x="{{ item.x }}" y="{{ item.y }}" label="{{ item.label | upper }}"/>
            {% endfor %}
        </items>
        {% endif %}

        {% if node.children %}
        <subregions>
            {% for child in node.children %}
                {{ render_node(child) }}
            {% endfor %}
        </subregions>
        {% endif %}
    </region>
{% endmacro %}

<?xml version="1.0" encoding="UTF-8"?>
<quadtree root_id="{{ root.id }}">
    {{ render_node(root) }}
</quadtree>"""

env = Environment()
template = env.from_string(template_str)

data = {
    "root": {
        "id": "R0",
        "region": [0, 0, 100, 100],
        "children": [
            {"id": "R1", "region": [0, 0, 50, 50], "points": [{"x": 10, "y": 10, "label": "P1_nw"}]},
            {"id": "R2", "region": [50, 0, 50, 50], "points": []},
            {"id": "R3", "region": [0, 50, 50, 50], "points": [{"x": 20, "y": 60, "label": "P2_sw"}]},
            {
                "id": "R4",
                "region": [50, 50, 50, 50],
                "points": [],
                "children": [
                    {"id": "R4a", "region": [50, 50, 25, 25], "points": []},
                    {"id": "R4b", "region": [75, 50, 25, 25], "points": []},
                    {"id": "R4c", "region": [50, 75, 25, 25], "points": [{"x": 60, "y": 80, "label": "P3_sw_child"}]},
                    {"id": "R4d", "region": [75, 75, 25, 25], "points": []},
                ],
            },
        ],
    }
}

output = template.render(root=data["root"])
print(output)
