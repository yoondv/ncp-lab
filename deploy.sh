#!/usr/bin/env bash

set -Eeuo pipefail

readonly IMAGE="ghcr.io/yoondv/ncp-lab:latest"
readonly CONTAINER_NAME="ncp-lab"

docker pull "$IMAGE"
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p 80:8000 \
  "$IMAGE"

for attempt in {1..10}; do
  if docker exec "$CONTAINER_NAME" python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2)" \
    >/dev/null 2>&1; then
    echo "Deployment succeeded."
    exit 0
  fi

  sleep 1
done

docker logs "$CONTAINER_NAME"
exit 1
