#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/root/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/openclaw-auto-update.log"
WA_TARGET="+972525173322"

TS="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
BEFORE="$(openclaw --version 2>/dev/null || echo 'unknown')"
UPDATE_OUTPUT=""
RESULT="ok"

if ! UPDATE_OUTPUT="$(openclaw update 2>&1)"; then
  RESULT="warn"
fi

AFTER="$(openclaw --version 2>/dev/null || echo 'unknown')"

{
  echo "===== $TS ====="
  echo "Before: $BEFORE"
  echo "$UPDATE_OUTPUT"
  echo "After: $AFTER"
  echo "Result: $RESULT"
  echo
} >> "$LOG_FILE"

MSG="🔄 עדכון יומי OpenClaw הסתיים\n\nלפני: $BEFORE\nאחרי: $AFTER\nסטטוס: $RESULT"
if [[ "$RESULT" != "ok" ]]; then
  MSG+="\n\nשים לב: העדכון החזיר אזהרה. בדיקה מומלצת בלוג: $LOG_FILE"
fi

openclaw message send --channel whatsapp --target "$WA_TARGET" --message "$MSG" >/dev/null 2>&1 || true
