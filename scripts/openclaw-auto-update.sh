#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/root/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/openclaw-auto-update.log"

{
  echo "===== $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
  BEFORE="$(openclaw --version 2>/dev/null || echo 'unknown')"
  echo "Before: $BEFORE"

  if openclaw update; then
    RESULT="ok"
  else
    RESULT="warn"
    echo "openclaw update returned non-zero (often due to service restart checks in non-systemd environments)."
  fi

  AFTER="$(openclaw --version 2>/dev/null || echo 'unknown')"
  echo "After: $AFTER"
  echo "Result: $RESULT"
  echo
} >> "$LOG_FILE" 2>&1
