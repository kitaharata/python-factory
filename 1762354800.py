import os
import sys

import av


def convert_gif_to_mp4(input_path, output_path):
    """Converts a GIF file to an MP4 file using PyAV."""
    try:
        with av.open(input_path) as input_container:
            in_stream = input_container.streams.video[0]

            with av.open(output_path, mode="w", format="mp4") as output_container:
                out_stream = output_container.add_stream("libx264", rate=in_stream.average_rate)
                out_stream.width = in_stream.width
                out_stream.height = in_stream.height
                out_stream.pix_fmt = "yuv420p"
                out_stream.time_base = in_stream.time_base

                for frame in input_container.decode(in_stream):
                    for packet in out_stream.encode(frame):
                        output_container.mux(packet)
                for packet in out_stream.encode():
                    output_container.mux(packet)
    except av.AVError as e:
        print(f"PyAV Error during conversion: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Usage: python {sys.argv[0]} <input_path> [output_path]")
        sys.exit(1)

    input_file = sys.argv[1]
    base, ext = os.path.splitext(input_file)

    if ext.lower() != ".gif":
        print(f"Error: Input file must be a GIF (.gif). Found extension: {ext}")
        sys.exit(1)

    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = base + ".mp4"

    print(f"Converting '{input_file}' to '{output_file}'...")
    convert_gif_to_mp4(input_file, output_file)
    print("Conversion complete.")
