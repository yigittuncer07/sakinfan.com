#!/bin/bash
PROJECT_DIR="/home/jeff/projects/sakinfan.com"
BACKUP_DIR="$PROJECT_DIR/backups"

mkdir -p "$BACKUP_DIR"
cd "$PROJECT_DIR" || exit

FILENAME="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"

# export the database using the container's environment variables
docker compose exec -T postgre sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c' > "$FILENAME"

# keep only the 10 newest backups, remove the rest
ls -t "$BACKUP_DIR"/db_backup_*.sql | tail -n +4 | xargs -r rm -f