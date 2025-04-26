#!/bin/bash

###############################################################################
# Sync Backup Locations
#
# This script backs up your backups folder on your home server to your desktop
# it on a local NFS-mounted directory. It is intended to be run manually or
# scheduled via cron for automatic, periodic backups.
#
# What It Does:
#   - Uses rsync to back up your backup directory
#
# Requirements:
#   - rsync must be installed and in your PATH
#
# Usage:
#   - Make script executable: chmod +x sync_backup_locations.sh
#   - Run manually: ./sync_backup_locations.sh
#   - Or schedule with cron:
#       0 */6 * * * /path/to/sync_backup_locations.sh
###############################################################################

# Variables
BACKUP_SOURCE="/mnt/nfs/shared/backups/"
BACKUP_DESTINATION="/home/jason/backups/"
RSYNC_OPTIONS="-ah --info=progress2 --delete"
LOG_DIR="$HOME/logs/sync-backup-locations"
LOG_RETENTION_DAYS=30  

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Generate log file
LOG_FILE="$LOG_DIR/$(date +%F).log"

# Run rsync and log output
if rsync $RSYNC_OPTIONS "$BACKUP_SOURCE" "$BACKUP_DESTINATION" | tee -a "$LOG_FILE"; then
    echo "[$(date)] Backup completed successfully." | tee -a "$LOG_FILE"
else
    echo "[$(date)] Backup failed!" | tee -a "$LOG_FILE" >&2
fi

# Clean old logs
find "$LOG_DIR" -type f -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
