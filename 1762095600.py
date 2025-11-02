import os
import sys

import av


def convert_mp4_to_m4a(input_path):
    """Converts an MP4 file to an M4A file (AAC audio)."""
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return

    base, ext = os.path.splitext(input_path)
    output_path = base + ".m4a"

    if ext.lower() not in (".mp4", ".m4v"):
        print(f"Warning: Input file extension '{ext}' is unusual for video input.")

    print(f"Converting: {input_path} => {output_path}")

    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        with av.open(input_path) as input_container:
            audio_streams = [s for s in input_container.streams if s.type == "audio"]

            if not audio_streams:
                raise ValueError("No audio stream found in the input file.")

            in_stream = audio_streams[0]

            with av.open(output_path, mode="w", format="mp4") as output_container:
                out_stream = output_container.add_stream("aac", rate=in_stream.rate)

                if in_stream.layout:
                    out_stream.layout = in_stream.layout
                elif in_stream.channels == 1:
                    out_stream.layout = "mono"
                elif in_stream.channels == 2:
                    out_stream.layout = "stereo"

                codec_name = out_stream.codec_context.name
                rate = out_stream.rate
                channels = out_stream.channels
                print(f"Encoding audio stream (codec: {codec_name}, rate: {rate}, channels: {channels})")

                for packet in input_container.demux(in_stream):
                    if packet.dts is None:
                        continue

                    for frame in packet.decode():
                        for new_packet in out_stream.encode(frame):
                            output_container.mux(new_packet)

                for new_packet in out_stream.encode():
                    output_container.mux(new_packet)

        print("Conversion successful.")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 1762095600.py <input_mp4_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    convert_mp4_to_m4a(input_file)
