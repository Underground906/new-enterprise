#!/usr/bin/env python3
"""
Extract all video URLs from YouTube channels
Tags each video with its source channel
"""

import subprocess
import re
import json
from pathlib import Path

def extract_channel_urls(input_file):
    """Extract channel URLs from markdown file"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all YouTube channel URLs
    pattern = r'https://www\.youtube\.com/@[\w\-\.]+'
    channels = re.findall(pattern, content)

    # Remove duplicates while preserving order
    seen = set()
    unique_channels = []
    for channel in channels:
        # Clean URL
        channel = channel.rstrip('/')
        if channel not in seen:
            seen.add(channel)
            unique_channels.append(channel)

    return unique_channels

def get_channel_name(channel_url):
    """Extract channel name from URL"""
    match = re.search(r'@([\w\-\.]+)', channel_url)
    return match.group(1) if match else 'unknown'

def fetch_channel_videos(channel_url, max_videos=None):
    """Fetch all video URLs from a channel using yt-dlp"""
    try:
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s',
            '--no-warnings',
            '--quiet',
            f'{channel_url}/videos'
        ]

        if max_videos:
            cmd.extend(['--playlist-end', str(max_videos)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            return {'success': False, 'error': result.stderr}

        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                video_id, title = line.split('|', 1)
                videos.append({
                    'video_id': video_id.strip(),
                    'title': title.strip(),
                    'url': f'https://www.youtube.com/watch?v={video_id.strip()}'
                })

        return {'success': True, 'videos': videos}

    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_channels(channels_file, output_dir='channel_videos', max_videos_per_channel=None):
    """Process all channels and extract video URLs"""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print("=" * 80)
    print("YOUTUBE CHANNEL VIDEO EXTRACTOR")
    print("=" * 80)
    print()

    # Extract channel URLs
    channels = extract_channel_urls(channels_file)
    print(f"Found {len(channels)} unique channels")
    print()

    all_videos = []
    channel_stats = {}

    for i, channel_url in enumerate(channels, 1):
        channel_name = get_channel_name(channel_url)
        print(f"[{i}/{len(channels)}] Processing @{channel_name}...", end=' ', flush=True)

        result = fetch_channel_videos(channel_url, max_videos_per_channel)

        if result['success']:
            videos = result['videos']
            print(f"✓ {len(videos)} videos")

            # Tag each video with channel info
            for video in videos:
                video['channel_name'] = channel_name
                video['channel_url'] = channel_url
                all_videos.append(video)

            channel_stats[channel_name] = {
                'channel_url': channel_url,
                'video_count': len(videos),
                'videos': videos
            }

            # Save per-channel file
            channel_file = output_path / f'{channel_name}_videos.json'
            with open(channel_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2)
        else:
            print(f"✗ {result['error']}")
            channel_stats[channel_name] = {
                'channel_url': channel_url,
                'video_count': 0,
                'error': result['error']
            }

    # Save combined results
    print()
    print("=" * 80)
    print(f"TOTAL VIDEOS EXTRACTED: {len(all_videos)}")
    print("=" * 80)
    print()

    # Save all videos to single file
    all_videos_file = output_path / 'all_videos.json'
    with open(all_videos_file, 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, indent=2)
    print(f"✓ Saved all videos: {all_videos_file}")

    # Save video URLs only (for transcript fetching)
    urls_file = output_path / 'all_video_urls.txt'
    with open(urls_file, 'w', encoding='utf-8') as f:
        for video in all_videos:
            f.write(f"{video['url']}\n")
    print(f"✓ Saved URL list: {urls_file}")

    # Save channel stats
    stats_file = output_path / 'channel_stats.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(channel_stats, f, indent=2)
    print(f"✓ Saved channel stats: {stats_file}")

    # Create readable report
    report_file = output_path / 'channel_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"CHANNEL VIDEO EXTRACTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Channels: {len(channels)}\n")
        f.write(f"Total Videos: {len(all_videos)}\n\n")

        f.write("=" * 80 + "\n")
        f.write("PER-CHANNEL BREAKDOWN\n")
        f.write("=" * 80 + "\n\n")

        # Sort by video count
        sorted_stats = sorted(channel_stats.items(), key=lambda x: x[1].get('video_count', 0), reverse=True)

        for channel_name, stats in sorted_stats:
            f.write(f"@{channel_name}\n")
            f.write(f"  URL: {stats['channel_url']}\n")
            if 'error' in stats:
                f.write(f"  Status: ERROR - {stats['error']}\n")
            else:
                f.write(f"  Videos: {stats['video_count']}\n")
            f.write("\n")

    print(f"✓ Saved report: {report_file}")
    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print(f"1. Use 'all_video_urls.txt' to fetch transcripts")
    print(f"2. Each channel's videos are also saved separately in '{output_dir}/'")
    print(f"3. Run: python fetch_transcripts_ytdlp.py {output_dir}/all_video_urls.txt 2")
    print()

if __name__ == "__main__":
    import sys

    channels_file = sys.argv[1] if len(sys.argv) > 1 else 'youtube channels.md'
    max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else None

    if max_videos:
        print(f"NOTE: Limiting to {max_videos} videos per channel (for testing)")
        print()

    process_channels(channels_file, max_videos_per_channel=max_videos)
