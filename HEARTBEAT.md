# HEARTBEAT Tasks (Luky Bot)

Run these checks on each heartbeat poll and alert only on problems.

## 1) Gateway health
- Verify OpenClaw gateway is reachable locally.
- If unreachable, alert with a short reason.

## 2) Channel health
- Verify WhatsApp and Discord are enabled and connected.
- Alert only if a channel is down/disconnected.

## 3) Homework automation
- Verify cron job exists:
  - `0 6 * * * cd /root/.openclaw/skills/pywebtop-skill && python3 fetch_and_send_homework.py >> /var/log/webtop_homework.log 2>&1`
- Verify `/var/log/webtop_homework.log` has a successful run in last 36h.
- Alert if missing cron entry or no recent successful run.

## 4) Backup automation
- Verify backup cron exists:
  - `0 3 * * * /root/.openclaw/backup/backup-local.sh >> /root/.openclaw/backup/backup.log 2>&1`
- Alert if missing.

## Response policy
- If everything is OK: reply exactly `HEARTBEAT_OK`
- If anything fails: send concise alert bullets with what failed and suggested fix.
