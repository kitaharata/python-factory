import json
import sys

import requests


def build_watch_url(info):
    """Builds the watch URL from video info dictionary."""
    video_id = info.get("v")
    list_id = info.get("list", "")
    if video_id:
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        params = []
        if list_id:
            params.append(f"list={list_id}")
        t = info.get("t")
        if t:
            params.append(f"t={t}")
        if params:
            watch_url += "&" + "&".join(params)
        return watch_url
    elif list_id:
        return f"https://www.youtube.com/playlist?list={list_id}"
    else:
        return None


def read_youtube_data(json_file):
    """Reads YouTube data from the JSON file."""
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"youtube": []}
    except json.JSONDecodeError:
        print(f"Warning: {json_file} is corrupt; initializing with empty data.")
        return {"youtube": []}


def process_youtube_videos(data):
    """Process YouTube videos to fetch oembed data."""
    youtube_videos = data.get("youtube", [])

    combined = []
    for video in youtube_videos:
        watch_url = build_watch_url(video)
        if watch_url:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url={watch_url}&format=json"
                response = requests.get(oembed_url)
                response.raise_for_status()
                oembed = response.json()
                combined.append(oembed)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching oembed for {watch_url}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Unexpected error for {watch_url}: {e}", file=sys.stderr)
    return combined


def output_results(combined, key):
    """Outputs the results either as full JSON or extracted key values."""
    if key:
        values = [item.get(key) for item in combined if item.get(key)]
        for value in values:
            print(value)
    else:
        result = {"youtube": combined}
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <json_file> [key]")
        sys.exit(1)
    json_file = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else None

    data = read_youtube_data(json_file)
    combined = process_youtube_videos(data)
    output_results(combined, key)
