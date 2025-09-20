import io
import os
import sys
import zipfile

from PIL import Image


def get_grid_pair(n):
    """Returns the most square-like factor pair (rows, cols) for n images."""
    pairs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            j = n // i
            pairs.append((i, j))
    pair = pairs[-1]
    return pair


def load_dithered_images(zip_path):
    """Loads images from ZIP file and converts to dithered 1-bit grayscale."""
    image_files = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for file_info in zf.infolist():
                if file_info.is_dir():
                    continue
                lower = file_info.filename.lower()
                if lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")):
                    image_files.append(file_info.filename)
    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
        sys.exit(1)

    dithered_images = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for img_file in image_files:
            with zf.open(img_file) as f:
                img_data = f.read()
                img = Image.open(io.BytesIO(img_data))
                if img.mode != "1":
                    img = img.convert("L").convert("1", dither=Image.Dither.FLOYDSTEINBERG)
                dithered_images.append(img)

    return dithered_images


def create_combined_image(dithered_images, rows, cols):
    """Combines dithered images into a grid-aligned single image."""
    col_widths = [0] * cols
    row_heights = [0] * rows
    n = len(dithered_images)
    for idx in range(n):
        r = idx // cols
        c = idx % cols
        w, h = dithered_images[idx].size
        row_heights[r] = max(row_heights[r], h)
        col_widths[c] = max(col_widths[c], w)

    total_width = sum(col_widths)
    total_height = sum(row_heights)

    combined = Image.new("1", (total_width, total_height), color=1)
    current_y = 0
    for r in range(rows):
        current_x = 0
        row_h = row_heights[r]
        for c in range(cols):
            img = dithered_images[r * cols + c]
            combined.paste(img, (current_x, current_y))
            current_x += col_widths[c]
        current_y += row_h

    return combined


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1758294000.py <zipfile>")
        sys.exit(1)

    zip_path = sys.argv[1]
    if not os.path.exists(zip_path):
        print(f"File not found: {zip_path}")
        sys.exit(1)

    dithered_images = load_dithered_images(zip_path)
    n = len(dithered_images)
    if n == 0:
        print("No images found.")
        sys.exit(1)

    pair = get_grid_pair(n)
    rows, cols = pair
    combined = create_combined_image(dithered_images, rows, cols)
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    output_path = f"{base_name}_combined_dithered.png"
    combined.save(output_path)
    print(f"Combined image saved as {output_path}")
