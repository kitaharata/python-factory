import os
import sys

from PIL import Image

A4_WIDTH, A4_HEIGHT = 3508, 2480
OUTPUT_FILENAME = "output_orihon.png"


def create_orihon(image_dir):
    valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
    files = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_exts)]
    files.sort()
    total_pages = (len(files) + 7) // 8

    for page_idx in range(total_pages):
        chunk = files[page_idx * 8 : (page_idx + 1) * 8]
        cell_width = A4_WIDTH // 4
        cell_height = A4_HEIGHT // 2
        page_order = [7, 6, 5, 4, 8, 1, 2, 3]
        new_img = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), "white")

        for idx, page_num in enumerate(page_order):
            if page_num > len(chunk):
                continue
            row = idx // 4
            col = idx % 4
            x = col * cell_width
            y = row * cell_height
            img_path = os.path.join(image_dir, chunk[page_num - 1])

            img = Image.open(img_path)
            w_ratio = cell_width / img.width
            h_ratio = cell_height / img.height
            ratio = min(w_ratio, h_ratio)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

            background = Image.new("RGB", (cell_width, cell_height), "white")
            x_offset = (cell_width - resized_img.width) // 2
            y_offset = (cell_height - resized_img.height) // 2
            background.paste(resized_img, (x_offset, y_offset))

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
