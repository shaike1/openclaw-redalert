#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/root/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/proactive-heartbeat.log"
LOCK_FILE="/tmp/proactive-heartbeat.lock"
WA_TARGET="+972525173322"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  exit 0
fi

ts="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
issues=()
fixed=()

check_container() {
  local name="$1"
  if ! docker ps --format '{{.Names}}' | grep -qx "$name"; then
    issues+=("Container down: $name")
    if docker start "$name" >/dev/null 2>&1; then
      fixed+=("Restarted container: $name")
      unset 'issues[${#issues[@]}-1]'
    fi
  fi
}

for c in 3cx-sbc drachtio freeswitch voice-app claude-api-server; do
  check_container "$c"
done

{
  echo "===== $ts ====="
  if ((${#issues[@]}==0)); then
    echo "status=ok"
  else
    echo "status=issues"
    printf 'issue: %s\n' "${issues[@]}"
  fi
  if ((${#fixed[@]})); then
    printf 'fixed: %s\n' "${fixed[@]}"
  fi
  echo
} >> "$LOG_FILE"

if ((${#issues[@]})); then
  msg="⚠️ Heartbeat זיהה תקלות\n\n$(printf -- '- %s\n' "${issues[@]}")"
  if ((${#fixed[@]})); then
    msg+="\n✅ פעולות תיקון אוטומטיות:\n$(printf -- '- %s\n' "${fixed[@]}")"
  fi
  openclaw message send --channel whatsapp --target "$WA_TARGET" --message "$msg" >/dev/null 2>&1 || true
fi
