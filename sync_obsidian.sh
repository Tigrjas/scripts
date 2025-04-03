#!/bin/bash

################################################################################
#                             Obsidian Sync Script                              #
#-------------------------------------------------------------------------------#
# Script Name : sync_obsidian.sh                                                #
# Description : Syncs your Obsidian vault from your Linux Mint desktop          #
#               to your Raspberry Pi home server.                               #
#                                                                               #
# Requirements:                                                                 #
#   - autofs server                                                             #
#   - autofs client                                                             #
#                                                                               #
# Usage:                                                                        #
#   bash sync_obsidian.sh                                                       #
#                                                                               #
# Author      : Jason Tran                                                      #
# Date        : January 12, 2025                                                #
# GitHub      : https://github.com/Tigrjas/scripts                              #
################################################################################

# Define the sync mode (automate: push or pull)
SYNC_TYPE="push"  # Change to "pull" if needed

# Configuration
VAULT_NAME="Chronos"
LOCAL_DIR="/home/jason/Documents/$VAULT_NAME"
NFS_MOUNT="/mnt/nfs/shared/documents/obsidian"
LOG_DIR="$HOME/logs/obsidian_sync"
LOG_FILE="$LOG_DIR/sync.log"
SCRIPT_PATH="$(realpath "$0")"  # Get the script's absolute path

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Add script location at the top of the log if it's a new file
if [ ! -f "$LOG_FILE" ]; then
  cat <<EOF > "$LOG_FILE"
################################################################################
#                             Obsidian Sync Log                                #
#------------------------------------------------------------------------------#
# Script Path : $SCRIPT_PATH
# Vault Name  : $VAULT_NAME
# Local Dir   : $LOCAL_DIR
# NFS Mount   : $NFS_MOUNT
# Log File    : $LOG_FILE
# Timestamp   : $(date)
# Github      : https://github.com/Tigrjas/scripts  
################################################################################

EOF
fi

# Function to log session start
log_session_start() {
  echo -e "\n################################################################################" >> "$LOG_FILE"
  echo "# Sync Session Started: $(date)" >> "$LOG_FILE"
  echo "# Mode: $1" >> "$LOG_FILE"
  echo "################################################################################" >> "$LOG_FILE"
}

# Function to push (sync local to NFS)
push_sync() {
  log_session_start "PUSH (Local → NFS)"
  echo "$(date): Pushing local folder to NFS share..." >> "$LOG_FILE"
  rsync -avz --delete "$LOCAL_DIR" "$NFS_MOUNT" >> "$LOG_FILE" 2>&1
  echo "$(date): Push sync completed." >> "$LOG_FILE"
}

# Function to pull (sync NFS to local)
pull_sync() {
  log_session_start "PULL (NFS → Local)"
  echo "$(date): Pulling remote folder from NFS share..." >> "$LOG_FILE"
  rsync -avz --delete "$NFS_MOUNT/$VAULT_NAME/" "$LOCAL_DIR" >> "$LOG_FILE" 2>&1
  echo "$(date): Pull sync completed." >> "$LOG_FILE"
}

# Trigger autofs to mount the NFS share
if [ ! -d "$NFS_MOUNT" ]; then
  echo "$(date): Error - NFS mount point does not exist: $NFS_MOUNT" >> "$LOG_FILE"
  exit 1
fi

# Access the directory to trigger autofs
ls "$NFS_MOUNT" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "$(date): Error - Could not access $NFS_MOUNT. Is autofs working?" >> "$LOG_FILE"
  exit 1
fi


# Check above for sync mode (default=push)
if [ "$SYNC_TYPE" == "push" ]; then
  push_sync
elif [ "$SYNC_TYPE" == "pull" ]; then
  pull_sync
else
  echo "$(date): Invalid SYNC_TYPE set in script." >> "$LOG_FILE"
  exit 1
fi
