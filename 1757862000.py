import random

from PIL import Image, ImageDraw


def generate_ellipse_image():
    """Generates an image with random ellipses and saves it to a file."""
    image_size = (480, 480)
    background_color = (255, 255, 255)
    img = Image.new("RGB", image_size, background_color)
    draw = ImageDraw.Draw(img)
    for _ in range(120):
        center_x = random.randint(0, image_size[0])
        center_y = random.randint(0, image_size[1])

        diameter = random.randint(120, 480)
        radius = diameter // 2

        x1 = center_x - radius
        y1 = center_y - radius
        x2 = center_x + radius
        y2 = center_y + radius
        draw.ellipse([x1, y1, x2, y2], outline=(0, 0, 0), width=1)
    output_filename = "generated_ellipses.png"
    img.save(output_filename)
    print(f"Generated image '{output_filename}'.")


if __name__ == "__main__":
    generate_ellipse_image()
