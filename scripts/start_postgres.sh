#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="waste-db"
VOLUME_NAME="waste_db_data"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker start "${CONTAINER_NAME}" >/dev/null
  echo "Postgres container '${CONTAINER_NAME}' started."
  exit 0
fi

docker volume create "${VOLUME_NAME}" >/dev/null

docker run --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  -e POSTGRES_DB=waste_mvp \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=1234 \
  -p 5434:5432 \
  -v "${VOLUME_NAME}:/var/lib/postgresql/data" \
  -d postgres:16 >/dev/null

echo "Postgres container '${CONTAINER_NAME}' created with persistent volume '${VOLUME_NAME}'."
