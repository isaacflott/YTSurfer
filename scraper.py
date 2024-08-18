# Run this to create new channels
#
# Install:
    # pip install --upgrade yt-dlp tqdm
#
# Run:
    # python3 scraper.py
#
# Copy into channels.js

import yt_dlp
import re
import random

def is_channel_url(url):
    """Check if the given URL is a YouTube channel URL."""
    channel_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/c\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/@[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in channel_patterns)

def get_videos(url, randomize):
    """Fetch video information from a YouTube playlist or channel using yt-dlp."""
    ydl_opts = {
        'ignoreerrors': True,
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
    }

    if is_channel_url(url):
        print("Detected channel URL. Fetching channel videos...")
        ydl_opts['extract_flat'] = False
        url = url + "/videos"
    else:
        print("Detected playlist URL. Fetching playlist videos...")

    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if info is None:
                print("Error: Could not extract info from URL")
                return []

            entries = info.get('entries', [])
            if not entries:
                print("No videos found in the provided URL.")
                return []

            print(f"Total videos found: {len(entries)}")

            for entry in entries:
                if entry:
                    video_id = entry.get('id')
                    duration = entry.get('duration')
                    if video_id and duration:
                        videos.append({'id': video_id, 'duration': int(duration)})
                    else:
                        print(f"Skipping a video due to missing id or duration: {entry.get('title', 'Unknown title')}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return []

    if randomize:
        random.shuffle(videos)

    return videos

def format_videos(videos):
    """Format video information as a JavaScript array of objects."""
    formatted = "[\n"
    for video in videos:
        formatted += f"    {{ id: \"{video['id']}\", duration: {video['duration']} }},\n"
    formatted = formatted.rstrip(",\n") + "\n  ]"
    return formatted

def main():
    url = input("Enter the YouTube playlist or channel URL: ")

    while True:
        channel_name = input("Enter the channel name (no spaces allowed): ")
        if ' ' not in channel_name:
            break
        print("Channel name cannot contain spaces. Please try again.")

    randomize = input("Do you want to randomize the order of videos? (y/n): ").lower() == 'y'

    print("Fetching videos... This may take a while.")
    videos = get_videos(url, randomize)
    if not videos:
        print("No videos found or error occurred.")
        return

    formatted_videos = format_videos(videos)

    output = f"{channel_name}: {formatted_videos},"
    print("\nFormatted output:")
    print(output)

    with open("updated_channels.js", "w") as f:
        f.write("const channels = {\n")
        f.write(f"  {output}\n")
        f.write("};\n")

    print(f"\nOutput has been written to 'updated_channels.js'")
    print(f"Total videos processed: {len(videos)}")
    if randomize:
        print("The order of videos has been randomized.")
    else:
        print("The original order of videos has been maintained.")

if __name__ == "__main__":
    main()
