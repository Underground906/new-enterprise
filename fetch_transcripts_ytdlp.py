#!/usr/bin/env python3
"""
Fetch transcripts for YouTube videos using yt-dlp
More robust than youtube-transcript-api
"""

import re
import json
import os
import subprocess
import time

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'youtube\.com/watch\?v=([^&]+)',
        r'youtube\.com/shorts/([^&?]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_transcript_ytdlp(video_id, url):
    """Fetch transcript using yt-dlp"""
    try:
        # Use yt-dlp to get subtitles
        cmd = [
            'yt-dlp',
            '--write-auto-sub',  # Get auto-generated subs
            '--write-sub',        # Get manual subs if available
            '--sub-lang', 'en',
            '--skip-download',    # Don't download video
            '--sub-format', 'json3',
            '--output', f'/tmp/yt_transcript_{video_id}',
            '--quiet',
            '--no-warnings',
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        # Check if subtitle file was created
        subtitle_files = [
            f'/tmp/yt_transcript_{video_id}.en.json3',
            f'/tmp/yt_transcript_{video_id}.en-US.json3',
            f'/tmp/yt_transcript_{video_id}.en-GB.json3',
        ]

        for subtitle_file in subtitle_files:
            if os.path.exists(subtitle_file):
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    subtitle_data = json.load(f)

                # Extract text from JSON subtitle format
                if 'events' in subtitle_data:
                    texts = []
                    for event in subtitle_data['events']:
                        if 'segs' in event:
                            for seg in event['segs']:
                                if 'utf8' in seg:
                                    texts.append(seg['utf8'])

                    full_text = ' '.join(texts).strip()

                    # Clean up temp files
                    os.remove(subtitle_file)

                    return {
                        'success': True,
                        'text': full_text,
                        'language': 'en',
                        'method': 'yt-dlp'
                    }

        return {'success': False, 'error': 'No subtitles found'}

    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def process_videos(input_file, output_dir='transcripts', delay=1):
    """Process all videos and fetch their transcripts"""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Read video URLs
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    total = len(urls)
    success_count = 0
    failed = []

    print(f"Processing {total} videos using yt-dlp...\n")
    print(f"Adding {delay}s delay between requests to avoid rate limiting\n")

    for i, url in enumerate(urls, 1):
        video_id = extract_video_id(url)

        if not video_id:
            print(f"[{i}/{total}] ✗ Invalid URL: {url}")
            failed.append({'url': url, 'error': 'Invalid URL'})
            continue

        print(f"[{i}/{total}] Fetching: {video_id}...", end=' ', flush=True)

        result = fetch_transcript_ytdlp(video_id, url)

        if result['success']:
            # Save transcript
            filename = f"{output_dir}/{video_id}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Video ID: {video_id}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Language: {result['language']}\n")
                f.write(f"Method: {result['method']}\n")
                f.write(f"\n{'='*80}\n\n")
                f.write(result['text'])

            print(f"✓ Saved ({len(result['text'])} chars)")
            success_count += 1
        else:
            print(f"✗ {result['error']}")
            failed.append({'url': url, 'video_id': video_id, 'error': result['error']})

        # Add delay to avoid rate limiting
        if i < total:
            time.sleep(delay)

    # Save failed list
    if failed:
        with open(f"{output_dir}/failed.json", 'w') as f:
            json.dump(failed, f, indent=2)

    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  Total videos: {total}")
    print(f"  ✓ Success: {success_count}")
    print(f"  ✗ Failed: {len(failed)}")
    print(f"  Success rate: {success_count/total*100:.1f}%")
    print(f"\nTranscripts saved to: {output_dir}/")
    if failed:
        print(f"Failed videos logged to: {output_dir}/failed.json")

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'youtube_videos_only.txt'
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1

    process_videos(input_file, delay=delay)
