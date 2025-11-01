import os
import sys

import av


def extract_thumbnail(video_path):
    """Extracts a thumbnail from a video file at the start (0.0s) and saves it."""
    output_path = "maxresdefault.webp"

    try:
        container = av.open(video_path)
    except av.AVError as e:
        print(f"Error opening video file: {e}")
        return

    try:
        stream = container.streams.video[0]
    except IndexError:
        print("Error: No video streams found.")
        return

    for packet in container.demux(stream):
        if packet.stream.type == "video":
            for frame in packet.decode():
                img = frame.to_image()

                img.save(output_path, format="WEBP", quality=75, method=4)
                print(f"Thumbnail saved successfully to {output_path}")
                return

    print("Could not find a frame to extract.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 1761922800.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]

    if not os.path.exists(video_file):
        print(f"Error: Input video file not found: {video_file}")
    else:
        extract_thumbnail(video_file)
