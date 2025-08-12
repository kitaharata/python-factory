import math

from PIL import Image, ImageDraw

IMG_WIDTH = 1280
IMG_HEIGHT = 720
HEX_RADIUS = 60
COLORS = [
    (255, 128, 128),
    (128, 255, 128),
    (128, 128, 255),
]
COLOR_MAP = [
    [0, 1, 2],
    [2, 0, 1],
]


def create_hexagon_vertices(center_x, center_y, radius):
    vertices = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.pi / 180 * angle_deg
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        vertices.append((x, y))
    return vertices


def main():
    img = Image.new("P", (IMG_WIDTH, IMG_HEIGHT))
    palette = []
    for color in COLORS:
        for value in color:
            palette.append(value)
    img.putpalette(palette)

    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, IMG_WIDTH, IMG_HEIGHT], fill=3)

    hex_width = HEX_RADIUS * 2
    hex_height = math.sqrt(3) * HEX_RADIUS
    horiz_dist = hex_width * 3 / 4
    vert_dist = hex_height
    num_cols = int(IMG_WIDTH / horiz_dist) + 2
    num_rows = int(IMG_HEIGHT / vert_dist) + 2

    for c in range(num_cols):
        for r in range(num_rows):
            cx = c * horiz_dist
            cy = r * vert_dist
            if c % 2 != 0:
                cy += vert_dist / 2

            vertices = create_hexagon_vertices(cx, cy, HEX_RADIUS)
            color_index = COLOR_MAP[c % 2][r % len(COLOR_MAP[0])]
            draw.polygon(vertices, fill=color_index)

    output_filename = "hexagonal_tiling_2bit.png"
    img.save(output_filename)
    print(f"Saved image as '{output_filename}'.")


if __name__ == "__main__":
    main()
