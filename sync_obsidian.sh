#!/bin/bash

# This script syncs from your linux mint to your raspberry pi

# ------------------------------------------------------------------------------
# Script Name: sync_obsidian.sh
# Description: This script syncs your Obsidian vault from your Linux Mint 
#              desktop to your raspberry pi home server. Make sure to run this 
#              on your desktop terminal.
#
# Requirements:
#   - autofs server
#   - autofs client
# 
# Usage: 
#   bash sync_obsidian.sh
#
# Author: Jason Tran
# Date: January 12, 2025
# ------------------------------------------------------------------------------

# Configuration variables
VAULT_NAME="Chronos"
LOCAL_DIR="/home/jason/Documents/$VAULT_NAME"  # Local Obsidian vault
NFS_MOUNT="/mnt/nfs/shared/documents/obsidian"               # Mounted NFS directory

# Function to push (sync from local to NFS)
push_sync() {
  echo "Pushing local folder to NFS share..."
  rsync -avz --delete "$LOCAL_DIR" "$NFS_MOUNT"
}

# Function to pull (sync from NFS to local)
pull_sync() {
  echo "Pulling remote folder from NFS share..."
  rsync -avz --delete "$NFS_MOUNT/$VAULT_NAME/" "$LOCAL_DIR"
}

# Trigger autofs to mount the NFS share
if [ ! -d "$NFS_MOUNT" ]; then
  echo "Error: NFS mount point does not exist: $NFS_MOUNT"
  exit 1
fi

# Access the directory to trigger autofs
ls "$NFS_MOUNT" > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Error: Could not access $NFS_MOUNT. Is autofs working?"
  exit 1
fi

# Main script logic
echo "Choose an option:"
echo "1) Push (local to NFS)"
echo "2) Pull (NFS to local)"
read -p "Enter your choice (1 or 2): " choice

# Execute based on user input
case "$choice" in
  1) push_sync ;;
  2) pull_sync ;;
  *) echo "Invalid choice, please enter 1 or 2." ;;
esac
