#!/usr/bin/env python3
"""
Filter transcripts to find fitness-related videos
Uses semantic keyword matching
"""

import os
import json
import re
from pathlib import Path

# Comprehensive fitness keyword list
FITNESS_KEYWORDS = {
    # Exercise types
    'workout', 'exercise', 'training', 'fitness', 'gym',

    # Body parts
    'muscle', 'chest', 'back', 'legs', 'arms', 'shoulders',
    'biceps', 'triceps', 'abs', 'core', 'glutes', 'hamstrings',
    'quadriceps', 'calves', 'lats', 'delts', 'pecs',

    # Exercise movements
    'squat', 'deadlift', 'bench press', 'push up', 'pull up',
    'curl', 'press', 'row', 'lunge', 'plank', 'crunch',
    'burpee', 'jump', 'sprint', 'cardio', 'hiit',

    # Equipment
    'dumbbell', 'barbell', 'kettlebell', 'weight', 'resistance',
    'cable', 'machine', 'bodyweight', 'calisthenics',

    # Training concepts
    'reps', 'sets', 'repetitions', 'strength', 'hypertrophy',
    'endurance', 'conditioning', 'mobility', 'flexibility',
    'stretching', 'recovery', 'rest day', 'progressive overload',

    # Body composition
    'muscle gain', 'fat loss', 'cutting', 'bulking', 'lean',
    'body composition', 'physique', 'shredded', 'jacked',

    # Disciplines
    'powerlifting', 'bodybuilding', 'crossfit', 'olympic lifting',
    'martial arts', 'boxing', 'mma', 'wrestling', 'jiu jitsu',
    'yoga', 'pilates', 'running', 'cycling', 'swimming',

    # Health/performance
    'nutrition', 'protein', 'calories', 'diet', 'supplements',
    'performance', 'athletic', 'athlete', 'sports'
}

def load_transcript(filepath):
    """Load transcript file and extract metadata"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from header
        lines = content.split('\n')
        video_id = ''
        url = ''

        for line in lines[:10]:  # Check first 10 lines for metadata
            if line.startswith('Video ID:'):
                video_id = line.replace('Video ID:', '').strip()
            elif line.startswith('URL:'):
                url = line.replace('URL:', '').strip()

        # Get transcript text (after the separator line)
        separator_idx = content.find('=' * 80)
        if separator_idx != -1:
            transcript_text = content[separator_idx:].lower()
        else:
            transcript_text = content.lower()

        return {
            'video_id': video_id,
            'url': url,
            'text': transcript_text,
            'filename': filepath.name
        }
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def calculate_fitness_score(text):
    """Calculate how fitness-related the content is"""
    # Count keyword matches
    matches = {}
    total_score = 0

    for keyword in FITNESS_KEYWORDS:
        count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
        if count > 0:
            matches[keyword] = count
            total_score += count

    return total_score, matches

def find_fitness_videos(transcripts_dir, min_score=5):
    """Find all fitness-related videos"""

    transcripts_path = Path(transcripts_dir)

    if not transcripts_path.exists():
        print(f"ERROR: Directory not found: {transcripts_dir}")
        return []

    print(f"Scanning {transcripts_dir}...")
    print(f"Minimum fitness score threshold: {min_score}")
    print()

    # Get all transcript files
    transcript_files = list(transcripts_path.glob('*.txt'))

    if not transcript_files:
        print("No transcript files found!")
        return []

    print(f"Found {len(transcript_files)} transcript files")
    print()

    fitness_videos = []

    for filepath in transcript_files:
        transcript = load_transcript(filepath)
        if not transcript:
            continue

        score, matches = calculate_fitness_score(transcript['text'])

        if score >= min_score:
            fitness_videos.append({
                'video_id': transcript['video_id'],
                'url': transcript['url'],
                'filename': transcript['filename'],
                'fitness_score': score,
                'top_keywords': sorted(matches.items(), key=lambda x: x[1], reverse=True)[:10]
            })

    # Sort by fitness score (highest first)
    fitness_videos.sort(key=lambda x: x['fitness_score'], reverse=True)

    return fitness_videos

def save_results(fitness_videos, output_file='fitness_videos.json'):
    """Save results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fitness_videos, f, indent=2)
    print(f"\nResults saved to: {output_file}")

def create_readable_report(fitness_videos, output_file='fitness_videos.txt'):
    """Create human-readable report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"FITNESS VIDEOS FOUND: {len(fitness_videos)}\n")
        f.write("=" * 80 + "\n\n")

        for i, video in enumerate(fitness_videos, 1):
            f.write(f"{i}. VIDEO ID: {video['video_id']}\n")
            f.write(f"   URL: {video['url']}\n")
            f.write(f"   Fitness Score: {video['fitness_score']}\n")
            f.write(f"   Top Keywords: {', '.join([f\"{kw}({count})\" for kw, count in video['top_keywords'][:5]])}\n")
            f.write("\n")

    print(f"Readable report saved to: {output_file}")

if __name__ == "__main__":
    import sys

    # Get transcripts directory
    transcripts_dir = sys.argv[1] if len(sys.argv) > 1 else 'transcripts'
    min_score = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    print("=" * 80)
    print("FITNESS VIDEO FILTER")
    print("=" * 80)
    print()

    # Find fitness videos
    fitness_videos = find_fitness_videos(transcripts_dir, min_score)

    if fitness_videos:
        print()
        print("=" * 80)
        print(f"FOUND {len(fitness_videos)} FITNESS VIDEOS!")
        print("=" * 80)
        print()
        print("Top 10 by fitness score:")
        print()

        for i, video in enumerate(fitness_videos[:10], 1):
            print(f"{i}. Score: {video['fitness_score']:3d} | {video['url']}")
            top_5_keywords = ', '.join([f"{kw}({count})" for kw, count in video['top_keywords'][:5]])
            print(f"   Keywords: {top_5_keywords}")
            print()

        # Save results
        save_results(fitness_videos, 'fitness_videos.json')
        create_readable_report(fitness_videos, 'fitness_videos_report.txt')

        print()
        print(f"Total fitness videos: {len(fitness_videos)} out of {len(list(Path(transcripts_dir).glob('*.txt')))} total")
        print(f"Success rate: {len(fitness_videos)/len(list(Path(transcripts_dir).glob('*.txt')))*100:.1f}%")
    else:
        print("No fitness videos found!")
