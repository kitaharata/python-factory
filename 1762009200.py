import os
import sys

import av

DEFAULT_TARGET_COUNT = 9


def extract_all_frames(video_path, target_frame_count):
    """Extracts and saves a target number of frames evenly spread throughout the video as WEBP files."""
    frame_counter_total = 0
    frame_count_saved = 0
    output_dir = "extracted_frames"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

    if target_frame_count <= 0:
        print("Error: Target frame count must be positive.")
        return

    try:
        duration_ts = stream.duration
        time_base = float(stream.time_base)
        if duration_ts is None or duration_ts <= 0 or stream.average_rate.numerator == 0:
            print("Error: Could not determine valid video duration or frame rate required for duration-based sampling.")
            return
        duration_sec = duration_ts * time_base
        fps = float(stream.average_rate)
        total_frames = int(round(duration_sec * fps))
        if total_frames <= 0:
            print("Error: Calculated total frames is zero or less.")
            return
        target_divisor = target_frame_count if target_frame_count == 1 else target_frame_count - 1
        frame_skip = max(1, total_frames // target_divisor)
    except Exception as e:
        print(f"Error calculating frame skip based on duration: {e}")
        return

    for packet in container.demux(stream):
        if packet.stream.type == "video":
            for frame in packet.decode():
                frame_counter_total += 1
                if (frame_counter_total - 1) % frame_skip == 0:
                    frame_count_saved += 1
                    img = frame.to_image()
                    output_path = os.path.join(output_dir, f"frame_{frame_count_saved:05d}.webp")
                    img.save(output_path, format="WEBP", quality=75, method=4)
                    print(f"Frame saved successfully to {output_path} (Original index: {frame_counter_total})")

    if frame_count_saved == 0:
        print("Could not find any frames to extract or the skip ratio was too high.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python 1762009200.py <video_file> [target_frame_count]")
        print(f"target_frame_count: Number of frames to extract evenly (Default: {DEFAULT_TARGET_COUNT}).")
        sys.exit(1)

    video_file = sys.argv[1]
    target_frame_count = DEFAULT_TARGET_COUNT

    if len(sys.argv) == 3:
        try:
            target_frame_count = int(sys.argv[2])
            if target_frame_count < 1:
                print("Error: target_frame_count must be 1 or greater.")
                sys.exit(1)
        except ValueError:
            print("Error: target_frame_count must be an integer.")
            sys.exit(1)

    if not os.path.exists(video_file):
        print(f"Error: Input video file not found: {video_file}")
    else:
        extract_all_frames(video_file, target_frame_count)
