#!/usr/bin/env bash
set -euo pipefail

REMOTE="${REMOTE:-gdrive:openclaw-full-backups}"
STAMP="$(date -u +%Y%m%d-%H%M%S)"
STAGE="/tmp/openclaw-full-backup-$STAMP"
LOG_DIR="/root/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/rclone-full-backup.log"
mkdir -p "$LOG_DIR" "$STAGE"

# Create compressed bundles first (more reliable uploads)
tar -czf "$STAGE/openclaw-home-$STAMP.tgz" /root/.openclaw 2>/dev/null || true
tar -czf "$STAGE/openclaw-3cx-$STAMP.tgz" /root/openclaw-3cx 2>/dev/null || true
tar -czf "$STAGE/openclaw-backups-$STAMP.tgz" /root/openclaw-backups 2>/dev/null || true

docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' > "$STAGE/docker-ps-$STAMP.txt" 2>/dev/null || true
docker volume ls > "$STAGE/docker-volumes-$STAMP.txt" 2>/dev/null || true

{
  echo "===== $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
  echo "Remote: $REMOTE"
  rclone copy "$STAGE" "$REMOTE/$STAMP" --transfers 4 --checkers 8 --create-empty-src-dirs --stats 20s
  echo "Upload done: $REMOTE/$STAMP"
  echo
} >> "$LOG_FILE" 2>&1

rm -rf "$STAGE"
