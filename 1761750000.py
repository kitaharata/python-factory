from jinja2 import Environment


def format_indent(depth):
    """Generates indentation string based on depth (4 spaces per level)."""
    return "    " * depth


def format_bounds(region):
    """Formats a list of bounds into a comma-separated string."""
    return ", ".join(map(str, region))


macro_template_str = """{% macro render_node(node, depth=1) -%}
{% set N = '\n' -%}
{{ depth | indent }}<region id="{{ node.id }}" bounds="{{ node.region | bounds }}">{{ N }}
{%- if node.points -%}
{{ (depth + 1) | indent }}<items>{{ N }}
{%- for item in node.points -%}
{{ (depth + 2) | indent }}<point x="{{ item.x }}" y="{{ item.y }}" label="{{ item.label | upper }}"/>{{ N }}
{%- endfor -%}
{{ (depth + 1) | indent }}</items>{{ N }}
{%- endif -%}
{%- if node.children -%}
{{ (depth + 1) | indent }}<subregions>{{ N }}
{%- for child in node.children -%}
{{ render_node(child, depth + 2) }}
{%- endfor -%}
{{ (depth + 1) | indent }}</subregions>{{ N }}
{%- endif -%}
{{ depth | indent }}</region>{{ N }}
{%- endmacro %}"""

template_str = """<?xml version="1.0" encoding="UTF-8"?>
<quadtree root_id="{{ root.id }}">
{{ render_node(root, depth=1) -}}
</quadtree>"""

env = Environment()
env.filters["indent"] = format_indent
env.filters["bounds"] = format_bounds
macro_template = env.from_string(macro_template_str)
env.globals["render_node"] = macro_template.module.render_node
template = env.from_string(template_str)

data = {
    "root": {
        "id": "R0",
        "region": [0, 0, 100, 100],
        "points": [{"x": 50, "y": 50, "label": "Center_Point"}],
        "children": [
            {
                "id": "R1",
                "region": [0, 0, 50, 50],
                "points": [{"x": 10, "y": 10, "label": "P1_nw"}, {"x": 45, "y": 45, "label": "P1_corner"}],
            },
            {
                "id": "R2",
                "region": [50, 0, 50, 50],
                "points": [{"x": 75, "y": 25, "label": "P_R2_mid"}],
                "children": [
                    {"id": "R2a", "region": [50, 0, 25, 25], "points": [{"x": 55, "y": 5, "label": "P4_ne_child"}]},
                    {"id": "R2b", "region": [75, 0, 25, 25], "points": [{"x": 80, "y": 15, "label": "P5_ne_child"}]},
                    {"id": "R2c", "region": [50, 25, 25, 25], "points": [{"x": 51, "y": 26, "label": "P_R2c"}]},
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
                    {
                        "id": "R4d",
                        "region": [75, 75, 25, 25],
                        "points": [{"x": 87.5, "y": 87.5, "label": "R4d_center"}],
                        "children": [
                            {
                                "id": "R4d_1",
                                "region": [75, 75, 12.5, 12.5],
                                "points": [{"x": 76, "y": 76, "label": "Deeper_NW"}],
                            },
                            {
                                "id": "R4d_2",
                                "region": [87.5, 75, 12.5, 12.5],
                                "points": [{"x": 90, "y": 78, "label": "Deeper_NE"}],
                            },
                            {
                                "id": "R4d_3",
                                "region": [75, 87.5, 12.5, 12.5],
                                "points": [{"x": 80, "y": 90, "label": "Deepest_SW_Point"}],
                                "children": [
                                    {"id": "R4d_3a", "region": [75, 87.5, 6.25, 6.25], "points": []},
                                    {"id": "R4d_3b", "region": [81.25, 87.5, 6.25, 6.25], "points": []},
                                    {"id": "R4d_3c", "region": [75, 93.75, 6.25, 6.25], "points": []},
                                    {
                                        "id": "R4d_3d",
                                        "region": [81.25, 93.75, 6.25, 6.25],
                                        "points": [{"x": 82, "y": 94, "label": "Tiny_P"}],
                                    },
                                ],
                            },
                            {"id": "R4d_4", "region": [87.5, 87.5, 12.5, 12.5], "points": []},
                        ],
                    },
                ],
            },
        ],
    }
}

output = template.render(root=data["root"])
print(output)
