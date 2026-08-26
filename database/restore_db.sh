#!/bin/bash
PROJECT_DIR="/home/jeff/projects/sakinfan.com"

if [ -z "$1" ]; then
    echo "Usage: $0 path/to/backup_file.sql"
    exit 1
fi

cd "$PROJECT_DIR" || exit

# Pipe the backup file into the postgres container
cat "$1" | docker compose exec -T postgre sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'