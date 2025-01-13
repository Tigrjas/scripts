#!/bin/bash

# This script syncs from your linux mint to your raspberry pi

# ------------------------------------------------------------------------------
# Script Name: sync_obsidian.sh
# Description: This script syncs your Obsidian vault from your Linux Mint 
#              desktop to your raspberry pi home server. Make sure to run this 
#              on your desktop terminal.
#
# Usage: 
#   bash sync_obsidian.sh
#
# Author: Jason Tran
# Date: January 12, 2025
# ------------------------------------------------------------------------------

# Configuration variables
LOCAL_DIR="/home/jason/Documents/Chronos"      # Local directory with Obsidian notes
REMOTE_USER="jason"                        # Your Raspberry Pi username
REMOTE_HOST="192.168.5.40"               # IP address of your Raspberry Pi
REMOTE_DIR="/mnt/seagate/docker/filebrowser/files/Documents/Chronos"          # Directory on Raspberry Pi where you want to sync Obsidian

# Function to push (sync from local to Raspberry Pi)
push_sync() {
  echo "Pushing local folder to Raspberry Pi..."
  rsync -avz --delete "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"
}

# Function to pull (sync from Raspberry Pi to local)
pull_sync() {
  echo "Pulling remote folder from Raspberry Pi..."
  rsync -avz --delete "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/" "$LOCAL_DIR"
}

# Main script logic
echo "Choose an option:"
echo "1) Push (local to Raspberry Pi)"
echo "2) Pull (Raspberry Pi to local)"
read -p "Enter your choice (1 or 2): " choice

# Execute based on user input
if [ "$choice" -eq 1 ]; then
  push_sync
elif [ "$choice" -eq 2 ]; then
  pull_sync
else
  echo "Invalid choice, please enter 1 or 2."
fi

