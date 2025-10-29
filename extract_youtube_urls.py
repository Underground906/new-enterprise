#!/usr/bin/env python3
"""
Extract YouTube video URLs from bookmark list
Filters out websites and channel URLs, keeping only video links
"""

import re

def extract_youtube_videos(input_file, output_file):
    """Extract YouTube video URLs from input file"""

    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://(?:www\.)?youtube\.com/shorts/[\w-]+',
    ]

    video_urls = []

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

        for pattern in youtube_patterns:
            matches = re.findall(pattern, content)
            video_urls.extend(matches)

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in video_urls:
        # Clean URL (remove extra parameters after &ab_channel etc)
        clean_url = url.split('&')[0] if '&' in url else url
        if clean_url not in seen:
            seen.add(clean_url)
            unique_urls.append(clean_url)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in unique_urls:
            f.write(f"{url}\n")

    return unique_urls

if __name__ == "__main__":
    input_file = "Long bookmark list.txt"
    output_file = "youtube_videos_only.txt"

    urls = extract_youtube_videos(input_file, output_file)

    print(f"✓ Extracted {len(urls)} unique YouTube video URLs")
    print(f"✓ Saved to: {output_file}")
    print(f"\nFirst 5 videos:")
    for url in urls[:5]:
        print(f"  - {url}")
