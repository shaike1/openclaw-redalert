#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="${1:-/tmp/openclaw-full-backup-20260227-120545}"
DEST_BASE="${2:-gdrive:openclaw-full-backups/$(basename "$SRC_DIR")}"
LOG="/root/.openclaw/workspace/logs/rclone-gdrive-resilient.log"
mkdir -p "$(dirname "$LOG")"

upload_one() {
  local f="$1"
  local name
  name="$(basename "$f")"
  local attempt=1
  local max=8
  while (( attempt <= max )); do
    echo "[$(date -u '+%F %T')] upload $name attempt $attempt" | tee -a "$LOG"
    if rclone copyto "$f" "$DEST_BASE/$name" \
      --transfers 1 --checkers 1 --tpslimit 0.1 --bwlimit 2M \
      --retries 2 --low-level-retries 5 --drive-chunk-size 8M --stats 20s >> "$LOG" 2>&1; then
      echo "[$(date -u '+%F %T')] success $name" | tee -a "$LOG"
      return 0
    fi
    sleep $(( attempt * 20 ))
    attempt=$((attempt+1))
  done
  echo "[$(date -u '+%F %T')] FAILED $name" | tee -a "$LOG"
  return 1
}

for f in "$SRC_DIR"/*; do
  [ -f "$f" ] || continue
  upload_one "$f"
done

echo "[$(date -u '+%F %T')] all done" | tee -a "$LOG"
