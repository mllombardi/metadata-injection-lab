#!/usr/bin/env bash
# Throw the database away and rebuild it from sql/ in a few seconds.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose down -v
docker compose up -d

echo "Waiting for Postgres..."
until docker exec labdb pg_isready -U postgres -d labdb >/dev/null 2>&1; do sleep 1; done
sleep 2   # give init scripts a moment to finish
echo "Ready. Clean baseline loaded."
