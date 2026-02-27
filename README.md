# Useful Scripts Collection

This repository contains a collection of useful scripts to automate various tasks in your personal or development setup.

## Folder Structure:
- **backup/**: Scripts related to backup and synchronization.
  - **backup_restic_obsidian.sh**: Backs up your Obsidian vault using Restic.
  - **sync_backup_locations.sh**: Syncs your backup with your desktop.

- **media_management/**: Scripts for managing and processing media files.
  - **/immich_uploader**: Helps upload process to immich
  - **add_chapters_to_video.py**: Adds chapters to a video file.
  - **merge_xmp_files.py**: Merges XMP metadata with its corresponding image file.
  - **tv_show_renamer.py**: Renames TV shows.

- **system/**: System maintenance and update scripts.
  - **update_pi.sh**: Updates a Raspberry Pi system (works with any system using `apt`).

## How to Use
Navigate to the appropriate directory and execute the scripts:

For example, to sync your backup:
```bash
cd scripts/backup
bash sync-backup-to-desktop.sh