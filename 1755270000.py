import sys

from PIL import Image


def get_main_colors(image_path, num_colors=5):
    """Extracts the main colors from an image."""
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: File '{image_path}' not found.")
        return None
    except IOError:
        print(f"Error: Cannot open '{image_path}' as an image file.")
        return None
    img.thumbnail((512, 512))
    img = img.convert("RGB")
    quantized_img = img.quantize(colors=num_colors)
    palette = quantized_img.getpalette()
    palette_rgb = [tuple(palette[i : i + 3]) for i in range(0, len(palette), 3)]
    color_counts = quantized_img.getcolors()
    if not color_counts:
        print("Error: Could not extract colors from the image.")
        return None
    sorted_colors = sorted(color_counts, key=lambda x: x[0], reverse=True)
    main_colors = []
    for count, index in sorted_colors:
        if index < len(palette_rgb):
            main_colors.append(palette_rgb[index])
    return main_colors[:num_colors]


def create_palette_image(colors, size_per_color=50):
    """Creates a color palette image from a list of colors."""
    if not colors:
        return None
    num_colors = len(colors)
    palette_img = Image.new("RGB", (size_per_color * num_colors, size_per_color))
    for i, color in enumerate(colors):
        color_box = Image.new("RGB", (size_per_color, size_per_color), color)
        palette_img.paste(color_box, (i * size_per_color, 0))
    return palette_img


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1755270000.py <image_path> [num_colors]")
        print("Example: python 1755270000.py my_image.jpg 8")
        sys.exit(1)
    image_file = sys.argv[1]
    num_main_colors = 5
    if len(sys.argv) > 2:
        try:
            num_main_colors = int(sys.argv[2])
        except ValueError:
            print("Error: Number of colors must be an integer.")
            sys.exit(1)

    extracted_colors = get_main_colors(image_file, num_colors=num_main_colors)
    if extracted_colors:
        print(f"Main {len(extracted_colors)} colors (RGB) for '{image_file}':")
        for rgb_color in extracted_colors:
            print(f"- {rgb_color}")

        try:
            palette_image = create_palette_image(extracted_colors)
            if palette_image:
                palette_image.show(title="Color Palette")
                save_path = "palette.png"
                palette_image.save(save_path)
                print(f"Saved color palette image to '{save_path}'.")
        except Exception as e:
            print(f"An error occurred while displaying/saving the palette image: {e}")
