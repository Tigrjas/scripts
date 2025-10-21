"""
rename_show_files.py
--------------------

A reusable Python script to rename TV show files into a clean, consistent format.

Example:
--------
Before:
    Pokemon (2012) - S02E08.mkv
    Danmachi S1 - 12.mkv
    Danmachi - 12.mkv
After:
    Pokemon Adventure S02E08.mkv
    Danmachi S01E12.mkv
    Danmachi S01E12.mkv

How to Use:
-----------
1. Adjust the variables in the CONFIGURATION section below.
2. Run:
       python rename_show_files.py
3. The script will:
   - Walk all subfolders in FOLDER_PATH
   - Detect S01E01, S1 - 12, or just "12"
   - Rename to "SHOW_TITLE SxxExx.<original_extension>"
   - Keep them in place
   - If DRY_RUN=True → only show what would happen, no changes

Tip:
----
Test with DRY_RUN=True before renaming real files.
"""

import os
import re


# === ⚙️ CONFIGURATION (CHANGE THESE VALUES) ==========================
FOLDER_PATH = r"/home/user/Downloads/Show Title"  # Path to your show folder
SHOW_TITLE = "Show Title"                         # Title for renamed files
DEFAULT_SEASON = 1                                # Used if no season number found
DRY_RUN = True                                    # True = preview only; False = rename
# =====================================================================


def rename_show_files(root_folder, show_name, default_season=1, dry_run=True):
    """
    Walk through all files, detect season/episode patterns,
    and rename to a consistent format.

    If dry_run=True, only prints what would be renamed.
    """

    # Regex patterns for different filename styles
    patterns = [
        re.compile(r'(S\d{1,2}E\d{1,2})', re.IGNORECASE),              # e.g. S01E08
        re.compile(r'S(\d{1,2})\s*[-_ ]\s*(\d{1,2})', re.IGNORECASE),  # e.g. S1 - 12
        re.compile(r'(?:E|Ep|Episode)?\s*(\d{1,2})', re.IGNORECASE),   # e.g. "12" or "Episode 12"
    ]

    for root, _, files in os.walk(root_folder):
        for file in files:
            old_path = os.path.join(root, file)
            base_name, extension = os.path.splitext(file)

            if not extension:
                continue

            season_episode = None

            # Try to match one of the filename patterns
            for pattern in patterns:
                match = pattern.search(file)
                if match:
                    if len(match.groups()) == 1 and 'E' in match.group(1).upper():
                        # Case like S01E08
                        season_episode = match.group(1).upper()
                    elif len(match.groups()) == 2:
                        # Case like S1 - 12
                        season_num = int(match.group(1))
                        episode_num = int(match.group(2))
                        season_episode = f"S{season_num:02d}E{episode_num:02d}"
                    elif len(match.groups()) == 1:
                        # Case like "Episode 12" or just "12"
                        episode_num = int(match.group(1))
                        season_episode = f"S{default_season:02d}E{episode_num:02d}"
                    break  # Stop after the first successful match

            if season_episode:
                new_filename = f"{show_name} {season_episode}{extension}"
                new_path = os.path.join(root, new_filename)

                if new_path != old_path:
                    if dry_run:
                        print(f"🟡 [DRY RUN] Would rename: {file} → {new_filename}")
                    else:
                        os.rename(old_path, new_path)
                        print(f"✅ Renamed: {file} → {new_filename}")
            else:
                print(f"⚠️ Skipped (no season/episode found): {file}")


def main():
    if os.path.isdir(FOLDER_PATH):
        print(f"The folder at ({FOLDER_PATH}) exists")
        rename_show_files(
            root_folder=FOLDER_PATH,
            show_name=SHOW_TITLE,
            default_season=DEFAULT_SEASON,
            dry_run=DRY_RUN
        )
    else:
        print(f"The folder path does not exist")


if __name__ == "__main__":
    main()
