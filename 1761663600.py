from jinja2 import Environment

macro_template_str = """{% macro render_node(node) %}
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
{% endmacro %}"""

template_str = """<?xml version="1.0" encoding="UTF-8"?>
<quadtree root_id="{{ root.id }}">
    {{ render_node(root) }}
</quadtree>"""

env = Environment()
macro_template = env.from_string(macro_template_str)
env.globals["render_node"] = macro_template.module.render_node
template = env.from_string(template_str)

data = {
    "root": {
        "id": "R0",
        "region": [0, 0, 100, 100],
        "children": [
            {"id": "R1", "region": [0, 0, 50, 50], "points": [{"x": 10, "y": 10, "label": "P1_nw"}]},
            {
                "id": "R2",
                "region": [50, 0, 50, 50],
                "children": [
                    {"id": "R2a", "region": [50, 0, 25, 25], "points": [{"x": 55, "y": 5, "label": "P4_ne_child"}]},
                    {"id": "R2b", "region": [75, 0, 25, 25], "points": [{"x": 80, "y": 15, "label": "P5_ne_child"}]},
                    {"id": "R2c", "region": [50, 25, 25, 25], "points": []},
                    {"id": "R2d", "region": [75, 25, 25, 25], "points": []},
                ],
            },
            {"id": "R3", "region": [0, 50, 50, 50], "points": [{"x": 20, "y": 60, "label": "P2_sw"}]},
            {
                "id": "R4",
                "region": [50, 50, 50, 50],
                "points": [],
                "children": [
                    {"id": "R4a", "region": [50, 50, 25, 25], "points": [{"x": 52, "y": 52, "label": "P6_sw_deep"}]},
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
