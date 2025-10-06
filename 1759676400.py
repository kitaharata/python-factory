import os
import sys

from PIL import Image

A4_WIDTH, A4_HEIGHT = 3508, 2480
ROWS, COLS = 2, 4
PAGE_ORDER = [7, 6, 5, 4, 8, 1, 2, 3]
OUTPUT_FILENAME = "output_orihon.png"


def create_orihon(image_dir):
    valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
    files = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_exts)]
    files.sort()
    total_pages = (len(files) + 7) // 8

    for page_idx in range(total_pages):
        chunk = files[page_idx * 8:(page_idx + 1) * 8]
        cell_width = A4_WIDTH // COLS
        cell_height = A4_HEIGHT // ROWS
        new_img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")

        for idx, page_num in enumerate(PAGE_ORDER):
            if page_num > len(chunk):
                continue
            row = idx // COLS
            col = idx % COLS
            x = col * cell_width
            y = row * cell_height
            img_path = os.path.join(image_dir, chunk[page_num - 1])

            img = Image.open(img_path)
            w_percent = cell_width / img.width
            new_height = int(img.height * w_percent)
            resized_img = img.resize((cell_width, new_height), Image.Resampling.LANCZOS)

            background = Image.new("RGB", (cell_width, cell_height), "white")
            y_offset = (cell_height - new_height) // 2
            background.paste(resized_img, (0, y_offset))
            if page_num in [4, 5, 6, 7]:
                background = background.rotate(180, expand=True)
            new_img.paste(background, (x, y))

        output_filename = f"output_orihon_{page_idx + 1}.png"
        new_img.save(output_filename)
        print(f"Orihon page {page_idx + 1} saved as: {output_filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_image_directory>")
        sys.exit(1)

    image_dir = sys.argv[1]
    if not os.path.isdir(image_dir):
        print("The specified path is not a directory.")
        sys.exit(1)

    create_orihon(image_dir)
