import os
import sys

from PIL import Image


def split_animated_gif(gif_path):
    """Splits an animated GIF into individual frames."""
    if not os.path.exists(gif_path):
        print(f"Error: File not found: {gif_path}")
        return

    try:
        img = Image.open(gif_path)
    except IOError:
        print(f"Error: {gif_path} is not a valid image file.")
        return

    if not getattr(img, "is_animated", False):
        print(f"Error: {gif_path} is not an animated GIF.")
        return

    base_name = os.path.splitext(os.path.basename(gif_path))[0]
    output_dir = f"{base_name}_frames"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Splitting '{gif_path}'...")
    print(f"Output directory: '{output_dir}'")

    frame_num = 0
    try:
        while True:
            current_frame = img.copy()
            output_path = os.path.join(output_dir, f"frame_{frame_num:03d}.gif")
            current_frame.save(output_path, "GIF")
            print(f"Saved frame {frame_num} to {output_path}")

            frame_num += 1
            img.seek(frame_num)
    except EOFError:
        pass

    print(f"Processing complete. Split a total of {frame_num} frames.")


def main():
    """Main process."""
    if len(sys.argv) < 2:
        print("Usage: python 1755442800.py <path_to_gif_file>")
        print("Example: python 1755442800.py my_animation.gif")
        sys.exit(1)

    gif_file = sys.argv[1]
    split_animated_gif(gif_file)


if __name__ == "__main__":
    main()
