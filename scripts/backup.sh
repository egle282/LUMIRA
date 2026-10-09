#!/bin/bash
# LUMIRA Automated Database Backup Script
# Should be scheduled via cron (e.g. daily at 02:00 AM)

set -e

BACKUP_DIR="/var/backups/lumira"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
DB_USER=${DB_USER:-lumira_admin}
DB_NAME=${DB_NAME:-lumira_prod}
CONTAINER_NAME="lumira_db_1"

echo "[$(date)] Starting backup process for $DB_NAME..."

mkdir -p "$BACKUP_DIR"

# 1. Create SQL dump
BACKUP_FILE="$BACKUP_DIR/lumira_$DATE.sql.gz"
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "[$(date)] Backup created successfully: $BACKUP_FILE"

# 2. Upload to Cloud Storage (AWS S3 / Google Cloud Storage)
# aws s3 cp "$BACKUP_FILE" s3://lumira-backups-bucket/db/
# gsutil cp "$BACKUP_FILE" gs://lumira-backups-bucket/db/

# 3. Clean up old backups (keep last 30 days)
find "$BACKUP_DIR" -name "lumira_*.sql.gz" -type f -mtime +30 -delete

echo "[$(date)] Old backups cleaned up. Process finished."
