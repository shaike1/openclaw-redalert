#!/usr/bin/env bash
set -euo pipefail
LOG_FILE="/root/.openclaw/workspace/logs/proactive-heartbeat.log"
WA_TARGET="+972525173322"

if [[ ! -f "$LOG_FILE" ]]; then
  exit 0
fi

summary="$(tail -n 300 "$LOG_FILE" | awk '
  /status=ok/{ok++}
  /status=issues/{bad++}
  /issue:/{issues[$0]++}
  END {
    printf("📊 סיכום יומי ניטור\n\n✅ בדיקות תקינות: %d\n⚠️ בדיקות עם תקלות: %d\n", ok, bad);
    if (bad>0) {
      printf("\nתקלות שחזרו:\n");
      for (i in issues) printf("- %s (x%d)\n", substr(i,8), issues[i]);
    }
  }
')"

openclaw message send --channel whatsapp --target "$WA_TARGET" --message "$summary" >/dev/null 2>&1 || true
