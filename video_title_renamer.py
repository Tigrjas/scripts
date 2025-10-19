
import os
import re


def rename_show_files(root_folder, show_name, default_season=1):
    """
    Walk through all files, detect season/episode patterns,
    and rename to a consistent format.
    """

    # Regex patterns for different filename styles
    patterns = [
        re.compile(r'(S\d{1,2}E\d{1,2})', re.IGNORECASE),           # e.g. S01E08
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
                    break  # Stop after first successful match

            if season_episode:
                new_filename = f"{show_name} {season_episode}{extension}"
                new_path = os.path.join(root, new_filename)

                if new_path != old_path:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed: {file} → {new_filename}")
            else:
                print(f"⚠️ Skipped (no season/episode found): {file}")

def main():
    folder_path = r"/home/user/Downloads/show title"
    show_name = "Show Title"
    default_season = 1

    if os.path.isdir(folder_path):
        print(f"The folder at ({folder_path}) exists")
        rename_show_files(folder_path, show_name, default_season)
    else:
        print(f"The folder path does not exist")


if __name__ == "__main__":
    main()
