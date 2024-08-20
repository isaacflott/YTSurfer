# Run this to create new channels
#
# Install:
    # pip3 install --upgrade yt-dlp tqdm
#
# Run:
    # python3 scraper.py
#
# Copy into channels.js

import yt_dlp
import re
import random
from collections import OrderedDict

def is_channel_url(url):
    """Check if the given URL is a YouTube channel URL."""
    channel_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/c\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/user\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/@[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in channel_patterns)

def is_video_url(url):
    """Check if the given URL is a YouTube video URL."""
    video_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=[\w-]+',
        r'(?:https?:\/\/)?youtu\.be\/[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in video_patterns)

def get_videos(url):
    """Fetch video information from a YouTube playlist, channel, or individual video using yt-dlp."""
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
    elif is_video_url(url):
        print("Detected individual video URL. Fetching video info...")
        ydl_opts['extract_flat'] = False
    else:
        print("Detected playlist URL. Fetching playlist videos...")

    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if info is None:
                print("Error: Could not extract info from URL")
                return []

            if is_video_url(url):
                entries = [info]
            else:
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

    return videos

def format_videos(videos):
    """Format video information as a JavaScript array of objects."""
    formatted = "[\n"
    for video in videos:
        formatted += f"    {{ id: \"{video['id']}\", duration: {video['duration']} }},\n"
    formatted = formatted.rstrip(",\n") + "\n  ]"
    return formatted

def remove_duplicates(videos):
    """Remove duplicate videos while preserving order."""
    seen = set()
    return [x for x in videos if not (x['id'] in seen or seen.add(x['id']))]

def main():
    all_videos = []
    randomize_option = input("Choose randomization option:\n1. No randomization\n2. Randomize each playlist/channel\n3. Randomize all videos together\nEnter 1, 2, or 3: ")

    while True:
        url = input("Enter a YouTube video, playlist, or channel URL (or type 'done' to finish): ")
        if url.lower() == 'done':
            break

        print("Fetching videos... This may take a while.")
        videos = get_videos(url)
        if videos:
            if randomize_option == '2':
                random.shuffle(videos)
            all_videos.extend(videos)
            print(f"Added {len(videos)} video{'s' if len(videos) > 1 else ''}. Total videos so far: {len(all_videos)}")
        else:
            print("No videos found or error occurred for this URL.")

    if not all_videos:
        print("No videos were added. Exiting.")
        return

    if randomize_option == '3':
        random.shuffle(all_videos)

    # Check for duplicates
    duplicate_count = len(all_videos) - len(set(video['id'] for video in all_videos))
    if duplicate_count > 0:
        print(f"\nFound {duplicate_count} duplicate video{'s' if duplicate_count > 1 else ''}.")
        remove_duplicates_option = input("Would you like to remove duplicates? (y/n): ").lower()
        if remove_duplicates_option == 'y':
            all_videos = remove_duplicates(all_videos)
            print(f"Duplicates removed. {len(all_videos)} unique videos remaining.")
        else:
            print("Duplicates were not removed.")

    while True:
        channel_name = input("Enter the channel name (no spaces allowed): ")
        if ' ' not in channel_name:
            break
        print("Channel name cannot contain spaces. Please try again.")

    formatted_videos = format_videos(all_videos)

    output = f"{channel_name}: {formatted_videos},"
    print("\nFormatted output:")
    print(output)

    with open("updated_channels.js", "w") as f:
        f.write("const channels = {\n")
        f.write(f"  {output}\n")
        f.write("};\n")

    print(f"\nOutput has been written to 'updated_channels.js'")
    print(f"Total videos processed: {len(all_videos)}")
    if randomize_option == '2':
        print("Each playlist/channel has been randomized individually.")
    elif randomize_option == '3':
        print("All videos have been randomized together.")
    else:
        print("No randomization was applied.")

if __name__ == "__main__":
    main()
