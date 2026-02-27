#!/usr/bin/env python3
"""
Add chapters to video files using simple timestamp format.

Usage:

    # This uses default names for all variables
    python3 add_chapters_to_video.py

    # Specify names of variables of video, chapters, and output
    python3 add_chapters_to_video.py video.mp4 chapters.txt output.mp4
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Default file names
DEFAULT_VIDEO = "video.mp4"
DEFAULT_CHAPTERS = "chapters.txt"
DEFAULT_OUTPUT = "output_with_chapters.mp4"


# ------------------------
# Utilities
# ------------------------
def run(cmd, capture_output=False):
    """Execute a shell command."""
    try:
        if capture_output:
            return subprocess.run(cmd, check=True, capture_output=True, text=True)
        else:
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        sys.exit(1)


def is_ffmpeg_installed():
    """Check if ffmpeg is available in PATH."""
    return shutil.which("ffmpeg") is not None


def get_video_duration(video_file):
    """Get video duration in seconds using ffprobe."""
    try:
        result = run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_file,
            ],
            capture_output=True,
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.CalledProcessError):
        return None


# ------------------------
# Timestamp parsing
# ------------------------
def parse_timestamp(timestamp_str):
    """
    Convert timestamp string to milliseconds.
    Supports formats:
    - MM:SS (e.g., "08:10")
    - HH:MM:SS (e.g., "1:23:45")
    - M:SS (e.g., "8:10")
    """
    timestamp_str = timestamp_str.strip()
    parts = timestamp_str.split(":")

    try:
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return (minutes * 60 + seconds) * 1000
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return (hours * 3600 + minutes * 60 + seconds) * 1000
        else:
            return None
    except ValueError:
        return None


def parse_chapters_file(chapter_file):
    """
    Parse simple chapter format:
    00:00 Chapter Title
    08:10 Another Chapter

    Returns list of (start_ms, title) tuples.
    """
    chapters = []

    with open(chapter_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#") or line.startswith(";"):
                continue

            # Match timestamp at start of line (MM:SS or HH:MM:SS)
            match = re.match(r"^(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+)$", line)
            if match:
                timestamp_str, title = match.groups()
                start_ms = parse_timestamp(timestamp_str)

                if start_ms is not None:
                    chapters.append((start_ms, title.strip()))
                else:
                    print(
                        f"Warning: Invalid timestamp on line {line_num}: {timestamp_str}"
                    )
            else:
                print(f"Warning: Skipping malformed line {line_num}: {line}")

    if not chapters:
        print("Error: No valid chapters found in file.")
        sys.exit(1)

    # Sort by timestamp
    chapters.sort(key=lambda x: x[0])

    return chapters


def create_ffmetadata(chapters, video_duration_ms=None):
    """
    Create FFmpeg metadata format from chapters list.

    Args:
        chapters: List of (start_ms, title) tuples
        video_duration_ms: Video duration in milliseconds (optional)

    Returns:
        String containing FFmpeg metadata format
    """
    metadata = ";FFMETADATA1\n"

    for i, (start_ms, title) in enumerate(chapters):
        # Determine end time (start of next chapter or video end)
        if i + 1 < len(chapters):
            end_ms = chapters[i + 1][0]
        elif video_duration_ms:
            end_ms = int(video_duration_ms)
        else:
            # If we don't know video duration, use a large value
            end_ms = start_ms + 600000  # +10 minutes

        metadata += "\n[CHAPTER]\n"
        metadata += "TIMEBASE=1/1000\n"
        metadata += f"START={start_ms}\n"
        metadata += f"END={end_ms}\n"
        metadata += f"title={title}\n"

    return metadata


# ------------------------
# Chapter template
# ------------------------
def create_chapter_template(chapter_file):
    """Create a simple template chapter file."""
    template = """\
# Simple chapter format
# Format: MM:SS Title or HH:MM:SS Title
# Lines starting with # or ; are ignored

00:00 Introduction
05:30 Main Content
15:45 Conclusion
"""
    with open(chapter_file, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"✓ Created template: {chapter_file}")
    print("\nEdit the file with your timestamps and titles, then re-run the script.")
    print("Format: MM:SS Title  or  HH:MM:SS Title")


# ------------------------
# Main workflow
# ------------------------
def add_chapters(video_file, chapter_file, output_file):
    """Add chapters from simple timestamp file to video."""

    # Validate inputs
    if not os.path.exists(video_file):
        print(f"Error: Video file not found: {video_file}")
        sys.exit(1)

    if not os.path.exists(chapter_file):
        print(f"Error: Chapter file not found: {chapter_file}")
        print("Create a template using: --create-template")
        sys.exit(1)

    # Get video duration
    print(f"Reading video: {video_file}")
    duration_seconds = get_video_duration(video_file)
    duration_ms = int(duration_seconds * 1000) if duration_seconds else None

    if duration_ms:
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        print(f"Video duration: {minutes}:{seconds:02d}")

    # Parse chapters
    print(f"Parsing chapters: {chapter_file}")
    chapters = parse_chapters_file(chapter_file)
    print(f"Found {len(chapters)} chapters:")
    for start_ms, title in chapters:
        total_seconds = start_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            timestamp = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            timestamp = f"{minutes}:{seconds:02d}"
        print(f"  {timestamp} - {title}")

    # Create FFmpeg metadata
    ffmetadata = create_ffmetadata(chapters, duration_ms)

    # Write to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as temp_file:
        temp_file.write(ffmetadata)
        metadata_file = temp_file.name

    try:
        # Check if output already exists
        if os.path.exists(output_file):
            response = input(f"\n{output_file} already exists. Overwrite? [y/N]: ")
            if response.lower() != "y":
                print("Aborted.")
                sys.exit(0)
            os.remove(output_file)

        # Add chapters using ffmpeg
        print("\nAdding chapters to video...")
        run(
            [
                "ffmpeg",
                "-i",
                video_file,
                "-i",
                metadata_file,
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-codec",
                "copy",
                "-y",  # Overwrite output file
                output_file,
            ]
        )

        print(f"\n✓ Success! Chapters added to: {output_file}")

    finally:
        # Clean up temporary file
        if os.path.exists(metadata_file):
            os.remove(metadata_file)


def main():
    parser = argparse.ArgumentParser(
        description="Add chapters to video files using simple timestamp format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a template file
  python3 add_chapters_to_video.py --create-template

  # Add chapters using default files
  python3 add_chapters_to_video.py

  # Specify custom files
  python3 add_chapters_to_video.py my_video.mp4 my_chapters.txt output.mp4

Chapter file format:
  00:00 First Chapter
  05:30 Second Chapter
  15:45 Third Chapter
  1:23:45 Chapter After One Hour
""",
    )
    parser.add_argument(
        "video",
        nargs="?",
        default=DEFAULT_VIDEO,
        help=f"Input video file (default: {DEFAULT_VIDEO})",
    )
    parser.add_argument(
        "chapters",
        nargs="?",
        default=DEFAULT_CHAPTERS,
        help=f"Chapter file with timestamps (default: {DEFAULT_CHAPTERS})",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=DEFAULT_OUTPUT,
        help=f"Output video file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create a chapter template file and exit",
    )

    args = parser.parse_args()

    # Check for ffmpeg
    if not is_ffmpeg_installed():
        print("Error: ffmpeg not found. Please install it:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  Fedora: sudo dnf install ffmpeg")
        print("  Arch: sudo pacman -S ffmpeg")
        print("  macOS: brew install ffmpeg")
        sys.exit(1)

    # Create template if requested
    if args.create_template:
        chapter_file = (
            args.chapters if args.chapters != DEFAULT_CHAPTERS else DEFAULT_CHAPTERS
        )
        create_chapter_template(chapter_file)
        return

    # Add chapters to video
    add_chapters(args.video, args.chapters, args.output)


if __name__ == "__main__":
    main()
