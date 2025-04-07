#!/bin/bash

# Variables
OBSIDIAN_VAULT="$HOME/Documents/Chronos"
BACKUP_DESTINATION="/mnt/nfs/shared/backups"
REPO_NAME="backup-restic-obsidian"
REPO_PATH="$BACKUP_DESTINATION/$REPO_NAME"
LOG_DIR="$HOME/logs/backup-restic-obsidian"
LOG_RETENTION_DAYS=30
DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H-%M-%S")
LOG_FILE="$LOG_DIR/$DATE.log"

# Restic password configuration
export RESTIC_PASSWORD_FILE="$HOME/.restic-password"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Log start of backup
log_message "Starting Obsidian vault backup for $DATE $TIME"

# Check if source directory exists
if [ ! -d "$OBSIDIAN_VAULT" ]; then
    log_message "ERROR: Obsidian vault directory not found at $OBSIDIAN_VAULT"
    exit 1
fi

# Attempt to trigger autofs by accessing the directory
log_message "Triggering autofs mount for $BACKUP_DESTINATION"
ls -la "$BACKUP_DESTINATION" > /dev/null 2>&1

# Give autofs a moment to mount
sleep 2


# Check if password file exists
if [ -n "$RESTIC_PASSWORD_FILE" ] && [ ! -f "$RESTIC_PASSWORD_FILE" ]; then
    log_message "ERROR: Restic password file not found at $RESTIC_PASSWORD_FILE"
    exit 1
fi

# Initialize repository if it doesn't exist
if [ ! -d "$REPO_PATH" ]; then
    log_message "Initializing Restic repository at $REPO_PATH"
    mkdir -p "$REPO_PATH"
    restic init --repo "$REPO_PATH" 2>&1 | tee -a "$LOG_FILE"
    
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log_message "ERROR: Failed to initialize Restic repository"
        exit 1
    fi
fi

# Perform backup
log_message "Backing up $OBSIDIAN_VAULT to $REPO_PATH"
restic backup --repo "$REPO_PATH" "$OBSIDIAN_VAULT" 2>&1 | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_message "ERROR: Backup failed"
    exit 1
fi

# Run forget command to remove old snapshots according to policy
log_message "Pruning old snapshots..."
restic forget --repo "$REPO_PATH" --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune 2>&1 | tee -a "$LOG_FILE"

# Check restic command for errors
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log_message "WARNING: Error during snapshot pruning"
else
    log_message "Old snapshots pruned successfully"
fi

# Remove old log files
log_message "Cleaning up log files older than $LOG_RETENTION_DAYS days"
find "$LOG_DIR" -name "*.log" -type f -mtime +$LOG_RETENTION_DAYS -delete

log_message "Backup process completed successfully"
exit 0