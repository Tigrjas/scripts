"""
tv_show_renamer.py
------------------

A reusable Python script to rename TV show files into a clean, consistent format.

Example:
--------
Before:
    Pokemon (2012) - S02E08.mkv
    Danmachi S1 - 12.mkv
    Danmachi - 12.mkv
    Jujutsu Kaisen (2023) - 08 - The Shibuya Incident.mkv
After:
    Pokemon Adventure S02E08.mkv
    Danmachi S01E12.mkv
    Danmachi S01E12.mkv
    Jujutsu Kaisen S02E08.mkv

How to Use:
-----------
1. Adjust the variables in the CONFIGURATION section below.
2. Run:
       python tv_show_renamer.py
3. The script will:
   - Walk all subfolders in FOLDER_PATH
   - Detect various episode naming patterns
   - Rename to "SHOW_TITLE SxxExx.<original_extension>"
   - Keep them in place
   - If DRY_RUN=True → only show what would happen, no changes

Tip:
----
Test with DRY_RUN=True before renaming real files.
"""

import os
import re
import sys
import traceback


# === ⚙️ CONFIGURATION (CHANGE THESE VALUES) ==========================
FOLDER_PATH = r"/home/jason/Downloads/Jujutsu Kaisen (2020)/Season 02"  # Path to your show folder
SHOW_TITLE = "Jujutsu Kaisen"                         # Title for renamed files
DEFAULT_SEASON = 2                                # Used if no season number found
DRY_RUN = False                                    # True = preview only; False = rename
# =====================================================================


def rename_show_files(root_folder, show_name, default_season=1, dry_run=True):
    """
    Walk through all files, detect season/episode patterns,
    and rename to a consistent format.

    If dry_run=True, only prints what would be renamed.
    """

    patterns = [
        # Must be ordered from most specific to least specific
        re.compile(r'(S\d{1,2}E\d{1,2})', re.IGNORECASE),                          # e.g. S01E08
        re.compile(r'\(\d{4}\)\s*[-_]\s*(\d{1,2})\s*[-_]', re.IGNORECASE),         # e.g. (2023) - 08 -
        re.compile(r'S(\d{1,2})\s*[-_ ]\s*(\d{1,2})', re.IGNORECASE),              # e.g. S1 - 12
        re.compile(r'[-_]\s*(\d{1,2})\s*[-_]', re.IGNORECASE),                     # e.g. - 08 -
        re.compile(r'(?:E|Ep|Episode)\s*(\d{1,2})', re.IGNORECASE),                # e.g. "Episode 12"
    ]

    renamed_count = 0
    skipped_count = 0
    error_count = 0

    try:
        for root, _, files in os.walk(root_folder):
            for file in files:
                old_path = os.path.join(root, file)

                try:
                    base_name, extension = os.path.splitext(file)
                    if not extension:
                        skipped_count += 1
                        print(f"⚠️ Skipped (no file extension): {file}")
                        continue

                    season_episode = None

                    for pattern in patterns:
                        match = pattern.search(file)
                        if match:
                            if len(match.groups()) == 1 and 'E' in match.group(0).upper():
                                # Case like S01E08
                                season_episode = match.group(1).upper()
                            elif len(match.groups()) == 2:
                                # Case like S1 - 12
                                season_num = int(match.group(1))
                                episode_num = int(match.group(2))
                                season_episode = f"S{season_num:02d}E{episode_num:02d}"
                            elif len(match.groups()) == 1:
                                # Case like "Episode 12", "(2023) - 08 -", or "- 08 -"
                                episode_num = int(match.group(1))
                                season_episode = f"S{default_season:02d}E{episode_num:02d}"
                            break

                    if season_episode:
                        new_filename = f"{show_name} {season_episode}{extension}"
                        new_path = os.path.join(root, new_filename)

                        if new_path != old_path:
                            if dry_run:
                                print(f"🟡 [DRY RUN] Would rename: {file} → {new_filename}")
                            else:
                                os.rename(old_path, new_path)
                                print(f"✅ Renamed: {file} → {new_filename}")
                            renamed_count += 1
                        else:
                            skipped_count += 1
                    else:
                        print(f"⚠️ Skipped (no season/episode found): {file}")
                        skipped_count += 1

                except Exception as file_error:
                    error_count += 1
                    print(f"❌ Error processing {file}: {file_error}")
                    traceback.print_exc(limit=1)

    except Exception as folder_error:
        print(f"\n❌ Critical Error: Could not walk through folder '{root_folder}'")
        print(folder_error)
        sys.exit(1)

    print("\n📊 Summary")
    print("──────────────")
    print(f"✅ Renamed: {renamed_count}")
    print(f"⚠️ Skipped: {skipped_count}")
    print(f"❌ Errors:  {error_count}")
    print("──────────────")
    print("Dry Run Mode:", "ON" if dry_run else "OFF")


def main():
    print("📁 Checking folder path...\n")

    if not os.path.exists(FOLDER_PATH):
        print(f"❌ The folder path does not exist: {FOLDER_PATH}")
        sys.exit(1)
    if not os.path.isdir(FOLDER_PATH):
        print(f"❌ The path is not a directory: {FOLDER_PATH}")
        sys.exit(1)
    if not os.access(FOLDER_PATH, os.R_OK):
        print(f"❌ Permission denied: cannot read folder at {FOLDER_PATH}")
        sys.exit(1)
    if not os.access(FOLDER_PATH, os.W_OK) and not DRY_RUN:
        print(f"⚠️ Warning: write access denied — cannot rename files unless DRY_RUN=True")

    print(f"✅ Folder found: {FOLDER_PATH}\n")
    rename_show_files(
        root_folder=FOLDER_PATH,
        show_name=SHOW_TITLE,
        default_season=DEFAULT_SEASON,
        dry_run=DRY_RUN
    )


if __name__ == "__main__":
    main()