#!/bin/bash
# 
# setup_backup_cron.sh
# 
# Script to set up automated backups using cron jobs.
# This will schedule regular backups to Google Drive.

set -e

# Configuration
ANCHORWORK_DIR="/Users/rebeccamorris/Desktop/anchorwork"
PYTHON_PATH=$(which python3)
BACKUP_SCRIPT="$ANCHORWORK_DIR/backup_to_google_drive.py"
LOG_DIR="$ANCHORWORK_DIR/logs"

# Create backup log directory
mkdir -p "$LOG_DIR/backup_logs"

# Function to add cron job if it doesn't exist
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local job="$schedule $command"
    
    # Check if job already exists
    if ! crontab -l 2>/dev/null | grep -q "$command"; then
        # Add new job to existing crontab
        (crontab -l 2>/dev/null; echo "$job") | crontab -
        echo "✓ Added cron job: $job"
    else
        echo "ℹ️ Cron job already exists: $command"
    fi
}

echo "🕒 Setting up automated backup schedule..."
echo "========================================"

# Daily full backup at 2 AM
add_cron_job "0 2 * * *" "cd $ANCHORWORK_DIR && $PYTHON_PATH $BACKUP_SCRIPT --type full >> $LOG_DIR/backup_logs/daily_backup.log 2>&1"

# Hourly logs backup (business hours only: 9 AM to 6 PM, weekdays)
add_cron_job "0 9-18 * * 1-5" "cd $ANCHORWORK_DIR && $PYTHON_PATH $BACKUP_SCRIPT --type logs >> $LOG_DIR/backup_logs/hourly_logs.log 2>&1"

# Redis snapshot backup every 6 hours
add_cron_job "0 */6 * * *" "cd $ANCHORWORK_DIR && $PYTHON_PATH $BACKUP_SCRIPT --type redis >> $LOG_DIR/backup_logs/redis_backup.log 2>&1"

# Weekly configuration backup on Sunday at 1 AM
add_cron_job "0 1 * * 0" "cd $ANCHORWORK_DIR && $PYTHON_PATH $BACKUP_SCRIPT --type configs >> $LOG_DIR/backup_logs/weekly_configs.log 2>&1"

echo ""
echo "📋 Current cron schedule:"
echo "========================"
crontab -l | grep -E "(backup_to_google_drive|anchorwork)" || echo "No backup jobs found"

echo ""
echo "📁 Backup logs will be stored in:"
echo "  $LOG_DIR/backup_logs/"

echo ""
echo "🎯 Backup Schedule Summary:"
echo "=========================="
echo "• Full backup:     Daily at 2:00 AM"
echo "• Logs backup:     Hourly (9 AM - 6 PM, weekdays)"  
echo "• Redis backup:    Every 6 hours"
echo "• Config backup:   Weekly (Sunday 1:00 AM)"

echo ""
echo "⚙️  Management Commands:"
echo "======================"
echo "• View cron jobs:    crontab -l"
echo "• Edit cron jobs:    crontab -e"
echo "• Remove all jobs:   crontab -r"
echo "• Manual backup:     cd $ANCHORWORK_DIR && python3 backup_to_google_drive.py"
echo "• View backup logs:  tail -f $LOG_DIR/backup_logs/daily_backup.log"

echo ""
echo "✅ Automated backup setup complete!"
echo ""
echo "⚠️  Important Notes:"
echo "• Ensure Google Drive credentials are properly configured"
echo "• Monitor backup logs regularly for any issues"
echo "• Adjust schedule in this script if needed, then re-run"
