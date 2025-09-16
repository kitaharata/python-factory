import math
import sys

from PIL import Image, ImageDraw


def generate_ellipse_image():
    """Generates an image with random circle and saves it to a file."""
    image_size = (480, 480)
    background_color = (255, 255, 255)
    img = Image.new("RGB", image_size, background_color)
    draw = ImageDraw.Draw(img)
    num_circles = 12
    if len(sys.argv) > 1:
        try:
            num_circles = int(sys.argv[1])
        except ValueError:
            print("Invalid number of circles provided. Using default (12).")
    circle_diameter = 120
    circle_radius = circle_diameter // 2
    base_center_x = image_size[0] // 2
    base_center_y = image_size[1] // 2
    orbit_radius = min(base_center_x, base_center_y) - circle_radius
    for i in range(num_circles):
        angle = (i / float(num_circles)) * (2 * math.pi)
        center_x = base_center_x + orbit_radius * math.cos(angle)
        center_y = base_center_y + orbit_radius * math.sin(angle)
        x1 = center_x - circle_radius
        y1 = center_y - circle_radius
        x2 = center_x + circle_radius
        y2 = center_y + circle_radius
        draw.ellipse([x1, y1, x2, y2], outline=(0, 0, 0), width=1)
    output_filename = "generated_circle.png"
    img.save(output_filename)
    print(f"Generated image '{output_filename}'.")


if __name__ == "__main__":
    generate_ellipse_image()
