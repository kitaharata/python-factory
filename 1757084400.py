import os
import sys

from PIL import Image

SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")


def convert(input_path, output_path):
    """Converts an image to another format. INPUT_PATH: Source image file. OUTPUT_PATH: Converted image file."""
    input_ext = os.path.splitext(input_path)[1].lower()
    if input_ext not in SUPPORTED_EXTENSIONS:
        print(f"Error: Unsupported input file format: {input_ext}")
        return
    output_ext = os.path.splitext(output_path)[1].lower()
    if not output_ext:
        print("Error: Please specify an output file extension (e.g., .png, .jpg).")
        return
    if output_ext not in SUPPORTED_EXTENSIONS:
        print(f"Error: Unsupported output file format: {output_ext}")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            print(f"Error: Could not create output directory '{output_dir}': {e}")
            return

    print(f"Converting '{input_path}' to '{output_path}'...")
    try:
        with Image.open(input_path) as img:
            if (output_ext in (".jpg", ".jpeg")) and img.mode == "RGBA":
                img = img.convert("RGB")
            img.save(output_path)
        print("Conversion complete.")
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
    except Image.UnidentifiedImageError:
        print(f"Error: '{input_path}' is not a valid image file.")
    except Exception as e:
        print(f"Error during image processing: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python 1757084400.py <input_file_path> <output_file_path>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    convert(input_path, output_path)
