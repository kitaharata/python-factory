import math

import click
from PIL import Image, ImageDraw


def draw_squares(draw, width, height, size, palette_map):
    """Draws square tiles."""
    for y in range(-size, height + size, size):
        for x in range(-size, width + size, size):
            row = y // size
            col = x // size
            color_key = (row + col) % 2
            fill_color = palette_map[color_key]
            draw.rectangle([x, y, x + size, y + size], fill=fill_color)


def draw_hexagons(draw, width, height, size, palette_map):
    """Draws hexagonal tiles."""
    s = size
    h = math.sqrt(3) * s
    w = 2 * s
    color_map_data = [
        [0, 1, 2],
        [2, 0, 1],
    ]

    horiz_dist = w * 3 / 4
    vert_dist = h
    num_cols = int(width / horiz_dist) + 2
    num_rows = int(height / vert_dist) + 2

    for c in range(num_cols):
        for r in range(num_rows):
            cx = c * horiz_dist
            cy = r * vert_dist
            if c % 2 != 0:
                cy += vert_dist / 2

            points = []
            for i in range(6):
                angle_deg = 60 * i
                angle_rad = math.radians(angle_deg)
                px = cx + s * math.cos(angle_rad)
                py = cy + s * math.sin(angle_rad)
                points.append((px, py))

            color_key = color_map_data[c % 2][r % len(color_map_data[0])]
            fill_color = palette_map[color_key]
            draw.polygon(points, fill=fill_color)


def draw_triangles(draw, width, height, size, palette_map):
    """Draws triangular tiles."""
    s = size
    h = s * math.sqrt(3) / 2
    for r in range(-2, int(height / h) + 2):
        for c in range(-2, int(width / (s / 2)) + 2):
            cx = c * s / 2
            cy = r * h

            if (c + r) % 2 == 0:
                p1 = (cx, cy - h / 2)
                p2 = (cx + s / 2, cy + h / 2)
                p3 = (cx - s / 2, cy + h / 2)
            else:
                p1 = (cx, cy + h / 2)
                p2 = (cx + s / 2, cy - h / 2)
                p3 = (cx - s / 2, cy - h / 2)

            color_key = (c - r) % 3
            fill_color = palette_map[color_key]
            draw.polygon([p1, p2, p3], fill=fill_color)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "--shape",
    type=click.Choice(["triangle", "square", "hexagon"], case_sensitive=False),
    default="square",
    show_default=True,
    help="Select the shape of the tiles.",
)
@click.option("--width", type=int, default=1280, show_default=True, help="Width of the image in pixels.")
@click.option("--height", type=int, default=720, show_default=True, help="Height of the image in pixels.")
@click.option(
    "--size",
    type=int,
    default=60,
    show_default=True,
    help="Size of the tiles (side length).",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Output filename. If not specified, it is generated from the shape (e.g. hexagonal_tiling_2bit.png).",
)
def generate(shape, width, height, size, output):
    """Generates a tessellation image with triangles, squares, or hexagons."""
    if output is None:
        if shape == "triangle":
            name = "triangular"
        elif shape == "hexagon":
            name = "hexagonal"
        else:
            name = shape
        output = f"{name}_tiling_2bit.png"

    COLORS = [
        (255, 128, 128),
        (128, 255, 128),
        (128, 128, 255),
    ]
    palette_data = []
    for color in COLORS:
        palette_data.extend(color)

    img = Image.new("P", (width, height))
    img.putpalette(palette_data)
    draw = ImageDraw.Draw(img)

    palette_map_3color = {0: 0, 1: 1, 2: 2}
    palette_map_2color = {0: 0, 1: 1}

    if shape == "square":
        draw_squares(draw, width, height, size, palette_map_2color)
    elif shape == "hexagon":
        draw_hexagons(draw, width, height, size, palette_map_3color)
    elif shape == "triangle":
        draw_triangles(draw, width, height, size, palette_map_3color)

    try:
        img.save(output)
        click.echo(f"Image saved to '{output}'.")
    except (IOError, ValueError) as e:
        click.echo(f"Error: Failed to save image. {e}", err=True)


if __name__ == "__main__":
    generate()
