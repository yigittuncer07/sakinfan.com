#!/bin/bash
PROJECT_DIR="/home/jeff/projects/sakinfan.com"
BACKUP_SCRIPT="$PROJECT_DIR/database/backup_db.sh"
INTERVAL=86400 # 24 hours in seconds

echo "Starting continuous backup service..."
echo "Backups will run every 24 hours. Press Ctrl+C to stop."
echo "------------------------------------------------------"

while true; do
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Running backup..."
    
    # run the backup script
    bash "$BACKUP_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup completed successfully."
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Backup failed!"
    fi
    
    echo "Waiting 24 hours for the next backup..."
    sleep $INTERVAL
done