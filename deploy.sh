#!/usr/bin/env bash

set -Eeuo pipefail

readonly IMAGE="ghcr.io/yoondv/ncp-lab:latest"
readonly NGINX_LINK="/etc/nginx/conf.d/ncp-lab-upstream.conf"
readonly BLUE_CONFIG="/etc/nginx/ncp-lab-upstreams/blue.conf"
readonly GREEN_CONFIG="/etc/nginx/ncp-lab-upstreams/green.conf"

active_config="$(readlink -f "$NGINX_LINK")"

case "$active_config" in
  "$BLUE_CONFIG")
    current_config="$BLUE_CONFIG"
    next_config="$GREEN_CONFIG"
    next_container="ncp-lab-green"
    next_port="8002"
    ;;
  "$GREEN_CONFIG")
    current_config="$GREEN_CONFIG"
    next_config="$BLUE_CONFIG"
    next_container="ncp-lab-blue"
    next_port="8001"
    ;;
  *)
    echo "Unknown Nginx upstream: $active_config" >&2
    exit 1
    ;;
esac

readonly current_config next_config next_container next_port

restore_current() {
  ln -sfn "$current_config" "$NGINX_LINK"
  nginx -t
  systemctl reload nginx
}

remove_next() {
  docker rm -f "$next_container" >/dev/null 2>&1 || true
}

docker pull "$IMAGE"
remove_next

docker run -d \
  --name "$next_container" \
  --restart unless-stopped \
  -p "127.0.0.1:$next_port:8000" \
  "$IMAGE"

for attempt in {1..10}; do
  if docker exec "$next_container" python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" \
    >/dev/null 2>&1; then
    break
  fi

  if [ "$attempt" -eq 10 ]; then
    docker logs "$next_container"
    remove_next
    exit 1
  fi

  sleep 1
done

ln -sfn "$next_config" "$NGINX_LINK"

if ! nginx -t; then
  ln -sfn "$current_config" "$NGINX_LINK"
  remove_next
  exit 1
fi

if ! systemctl reload nginx; then
  if ! restore_current; then
    echo "Nginx rollback failed; keeping $next_container running." >&2
    exit 1
  fi
  remove_next
  exit 1
fi

if ! python3 -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1/health', timeout=2)" \
  >/dev/null 2>&1; then
  if ! restore_current; then
    echo "Nginx rollback failed; keeping $next_container running." >&2
    exit 1
  fi
  remove_next
  exit 1
fi

