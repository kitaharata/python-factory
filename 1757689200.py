import random

from PIL import Image, ImageDraw


def generate_ellipse_image():
    """Generates an image with random ellipses and saves it to a file."""
    image_size = (480, 480)
    background_color = (255, 255, 255)
    img = Image.new("RGB", image_size, background_color)
    draw = ImageDraw.Draw(img)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
    center_coords_options = [i for i in range(0, 481, 32)]
    size_options = [i for i in range(256, 481, 16)]
    num_ellipses = random.randint(1, 6)
    for _ in range(num_ellipses):
        fill_color = random.choice(colors)
        center_x = random.choice(center_coords_options)
        center_y = random.choice(center_coords_options)
        width = random.choice(size_options)
        height = random.choice(size_options)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        x2 = center_x + width // 2
        y2 = center_y + height // 2
        draw.ellipse([x1, y1, x2, y2], fill=fill_color)
    output_filename = "generated_ellipses.png"
    img.save(output_filename)
    print(f"Generated image '{output_filename}'.")


if __name__ == "__main__":
    generate_ellipse_image()
