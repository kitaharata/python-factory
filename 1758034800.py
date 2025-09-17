import json
import os
import re
import sys
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__, template_folder=".")
if len(sys.argv) > 1:
    JSON_FILE = sys.argv[1]
else:
    JSON_FILE = "1758034840.json"


def read_youtube_data():
    """Reads YouTube data from the JSON file."""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"youtube": []}
    except json.JSONDecodeError:
        print(f"Warning: {JSON_FILE} is corrupt; initializing with empty data.")
        return {"youtube": []}


def write_youtube_data(data):
    """Writes YouTube data to the JSON file."""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_youtube_info(url):
    """Extracts YouTube video and playlist information from a URL."""
    video_info = {}
    try:
        if not url.startswith(("http://", "https://")):
            url_for_parse = "https://" + url
        else:
            url_for_parse = url
        parsed = urlparse(url_for_parse)
        host = parsed.netloc.lower()
        valid_hosts = {
            "www.youtube.com",
            "youtube.com",
            "m.youtube.com",
            "youtu.be",
            "music.youtube.com",
            "www.youtube-nocookie.com",
            "youtube-nocookie.com",
            "www.youtubekids.com",
            "youtubekids.com",
        }
        if host not in valid_hosts:
            return video_info
    except Exception:
        return video_info

    video_id_match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/|live/|v/)([a-zA-Z0-9_-]{11})", url)
    if video_id_match:
        video_info["v"] = video_id_match.group(1)
    list_id_match = re.search(r"(?:list=)([^&]+)", url)
    if list_id_match:
        video_info["list"] = list_id_match.group(1)
    time_match = re.search(r"(?:t=)([^&]+)", url)
    if time_match:
        video_info["t"] = time_match.group(1)
    return video_info


def build_embed_url(info):
    """Builds the embed URL from video info dictionary."""
    video_id = info.get("v")
    if not video_id:
        return None
    embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}"
    params = []
    list_id = info.get("list", "")
    if list_id:
        params.append(f"list={list_id}")
    t = info.get("t")
    if t:
        params.append(f"t={t}")
    if params:
        embed_url += "?" + "&".join(params)
    return embed_url


def build_watch_url(info):
    """Builds the watch URL from video info dictionary."""
    video_id = info.get("v")
    if not video_id:
        return None
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    params = []
    list_id = info.get("list", "")
    if list_id:
        params.append(f"list={list_id}")
    t = info.get("t")
    if t:
        params.append(f"t={t}")
    if params:
        watch_url += "&" + "&".join(params)
    return watch_url


@app.route("/", methods=["GET", "POST"])
def index():
    """Handles the main page, adding new YouTube videos and displaying saved ones."""
    if request.method == "POST":
        youtube_urls_text = request.form.get("youtube_urls", "").strip()
        if not youtube_urls_text:
            return redirect(url_for("index"))
        urls = [url.strip() for url in youtube_urls_text.splitlines() if url.strip()]
        if not urls:
            return redirect(url_for("index"))

        data = read_youtube_data()
        youtube_list = data.setdefault("youtube", [])
        for url in urls:
            video_info = extract_youtube_info(url)
            if "v" not in video_info:
                continue
            video_id = video_info["v"]
            for entry in youtube_list:
                if entry.get("v") == video_id:
                    if "list" in video_info:
                        entry["list"] = video_info["list"]
                    if "t" in video_info:
                        entry["t"] = video_info["t"]
                    break
            else:
                youtube_list.append(video_info)
        write_youtube_data(data)
        return redirect(url_for("index"))

    data = read_youtube_data()
    youtube_videos = data.get("youtube", [])
    index_param = request.args.get("i", type=int)
    if index_param is not None and 0 <= index_param < len(youtube_videos):
        video = youtube_videos[index_param].copy()
        video["embed_url"] = build_embed_url(video)
        return render_template("1758034820.html", mode="single", video=video, index=index_param + 1)

    for video in youtube_videos:
        video["embed_url"] = build_embed_url(video)
        video["watch_url"] = build_watch_url(video)
    return render_template("1758034820.html", youtube_videos=youtube_videos)


if __name__ == "__main__":
    from waitress import serve

    initial_data = read_youtube_data()
    if not os.path.exists(JSON_FILE):
        write_youtube_data({"youtube": []})
    serve(app, host="127.0.0.1", port=8080)
