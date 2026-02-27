#!/bin/bash

# Raspberry Pi 4 Automatic Update Script
# ==============================================
# This script updates the system packages, removes unnecessary files, 
# and optionally reboots the system if needed.
#
# USAGE:
# 1. Make the script executable: chmod +x update_pi.sh
# 2. Run it manually: ./update_pi.sh
# 3. (Optional) Schedule it via cron for automation.

# Logging setup
LOG_DIR="$HOME/logs/pi-update"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/update-$(date +%Y-%m-%d).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "================================================"
echo " Raspberry Pi 4 Update - $(date)"
echo "================================================"

# Update package list and upgrade packages
echo "Updating package lists..."
sudo apt-get update || { echo "Failed to update package lists"; exit 1; }

echo "Upgrading installed packages..."
sudo apt-get full-upgrade -y || { echo "Failed to upgrade packages"; exit 1; }

# Remove unnecessary packages
echo "Removing unused packages..."
sudo apt-get autoremove -y

echo "Cleaning up package cache..."
sudo apt-get autoclean

# Check if a reboot is needed
if [ -f /var/run/reboot-required ]; then
    echo "Reboot is required."
    read -p "Do you want to reboot now? (y/N) " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Rebooting..."
        sudo reboot
    else
        echo "Reboot skipped. Remember to reboot later!"
    fi
else
    echo "No reboot required."
fi

echo "Update completed successfully!"