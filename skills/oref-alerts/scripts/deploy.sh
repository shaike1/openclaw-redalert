#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚨 ORef Alerts - Interactive Deploy Script
# פיקוד העורף - סקריפט התקנה אינטראקטיבי
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set -e

ENV_FILE="/root/.openclaw/workspace/skills/oref-alerts/.env"
SERVICE_NAME="oref-monitor-openclaw"
MONITOR_SCRIPT="/root/.openclaw/workspace/skills/oref-alerts/monitor.py"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

banner() {
  echo -e "${RED}"
  echo "  🚨 ┌─────────────────────────────────────────┐"
  echo "     │   ORef Alerts - OpenClaw Integration    │"
  echo "     │   מערכת התרעות פיקוד העורף              │"
  echo "     └─────────────────────────────────────────┘"
  echo -e "${NC}"
}

ask() {
  local var=$1 prompt=$2 default=$3 secret=$4
  if [ -n "$default" ]; then
    prompt="$prompt [${CYAN}$default${NC}]"
  fi
  echo -ne "${YELLOW}${prompt}: ${NC}"
  if [ "$secret" = "true" ]; then
    read -rs value; echo
  else
    read -r value
  fi
  eval "$var='${value:-$default}'"
}

ask_yn() {
  local var=$1 prompt=$2 default=${3:-n}
  echo -ne "${YELLOW}${prompt} (y/n) [${default}]: ${NC}"
  read -r value
  value="${value:-$default}"
  eval "$var='$([[ $value =~ ^[Yy] ]] && echo true || echo false)'"
}

section() {
  echo -e "\n${BLUE}${BOLD}━━━ $1 ━━━${NC}\n"
}

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️  $1${NC}"; }

# ──────────────────────────────────────
banner

# ──────────────────────────────────────
section "1️⃣  ORef API Docker Container"

info "מפעיל את container פיקוד העורף..."
if docker ps --format '{{.Names}}' | grep -q "^oref-alerts$"; then
  warn "Container 'oref-alerts' כבר פועל"
else
  docker stop oref-alerts 2>/dev/null || true
  docker rm   oref-alerts 2>/dev/null || true
  docker run -d \
    --name oref-alerts \
    --network host \
    --restart unless-stopped \
    -e TZ="Asia/Jerusalem" \
    dmatik/oref-alerts:latest
  sleep 4
fi

OREF_PORT=9001
if curl -sf "http://localhost:${OREF_PORT}/current" > /dev/null 2>&1; then
  ok "ORef API עובד על localhost:${OREF_PORT}"
  OREF_API_URL="http://localhost:${OREF_PORT}/current"
else
  warn "port 9001 לא מגיב, מנסה 49000..."
  OREF_PORT=49000
  OREF_API_URL="http://localhost:${OREF_PORT}/current"
fi

# ──────────────────────────────────────
section "2️⃣  WhatsApp"

ask WHATSAPP_GROUP "JID קבוצת WhatsApp (לדוגמה: 120363...@g.us)" ""
ask WHATSAPP_OWNER "מספר אישי WhatsApp (לדוגמה: +972525173322)" ""

# ──────────────────────────────────────
section "3️⃣  Home Assistant (אופציונלי - TTS קולי + אורות)"

ask_yn HA_SETUP "האם להגדיר Home Assistant?" "y"

if [ "$HA_SETUP" = "true" ]; then
  ask HA_URL   "כתובת Home Assistant" "https://ha.right-api.com"
  ask HA_TOKEN "Long-Lived Access Token" "" true
  ask HA_TTS   "Entity ID של הרמקול" "media_player.home_assistant_voice_09a069"
  ask HA_LIGHTS "Entity IDs של אורות (מופרדים בפסיק, אפשר לרוקן)" ""

  info "בודק חיבור ל-HA..."
  if curl -sf -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/" > /dev/null 2>&1; then
    ok "Home Assistant מחובר!"
    HA_ENABLED=true
  else
    warn "לא הצלחתי להתחבר ל-HA — יישמר בהגדרות, ניתן לתקן מאוחר יותר"
    HA_ENABLED=true
  fi
else
  HA_URL=""; HA_TOKEN=""; HA_TTS=""; HA_LIGHTS=""
  HA_ENABLED=false
  warn "Home Assistant מושבת — לא תהיה התרעה קולית!"
fi

# ──────────────────────────────────────
section "4️⃣  חיוג טלפוני דרך openclaw-3CX (אופציונלי)"

ask_yn CX3_SETUP "האם להגדיר חיוג טלפוני דרך 3CX?" "n"

if [ "$CX3_SETUP" = "true" ]; then
  ask CX3_GATEWAY  "כתובת openclaw-3cx gateway" "http://localhost:8090"
  ask CX3_EXTENSION "מספר שלוחה" "100"
  ask PHONE_NUMBERS "מספרי טלפון לחייג בהתרעה (מופרדים בפסיק)" "+972525173322"
  PHONE_CALL_ENABLED=true
  ok "3CX מוגדר"
else
  CX3_GATEWAY="http://localhost:8090"
  CX3_EXTENSION=""
  PHONE_NUMBERS=""
  PHONE_CALL_ENABLED=false
  info "חיוג טלפוני מושבת"
fi

# ──────────────────────────────────────
section "5️⃣  שמירת הגדרות"

cat > "$ENV_FILE" << ENVEOF
# ORef Alerts - OpenClaw Configuration
# נוצר: $(date)

# ── ORef API ──
OREF_API_URL=${OREF_API_URL}
OREF_POLL_INTERVAL=5
OREF_COOLDOWN=60

# ── WhatsApp ──
WHATSAPP_GROUP_JID=${WHATSAPP_GROUP}
WHATSAPP_OWNER=${WHATSAPP_OWNER}

# ── Home Assistant ──
HASS_SERVER=${HA_URL}
HASS_TOKEN=${HA_TOKEN}
HA_TTS_SPEAKER=${HA_TTS}
HA_ALERT_LIGHTS=${HA_LIGHTS}

# ── 3CX Phone Calls ──
OREF_PHONE_CALL=${PHONE_CALL_ENABLED}
CX3_GATEWAY_URL=${CX3_GATEWAY}
CX3_EXTENSION=${CX3_EXTENSION}
PHONE_ALERT_NUMBERS=${PHONE_NUMBERS}
ENVEOF

chmod 600 "$ENV_FILE"
ok "הגדרות נשמרו ב: $ENV_FILE"

# ──────────────────────────────────────
section "6️⃣  systemd Service"

cat > /etc/systemd/system/${SERVICE_NAME}.service << SVCEOF
[Unit]
Description=ORef Alerts Monitor (OpenClaw)
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${MONITOR_SCRIPT}
EnvironmentFile=${ENV_FILE}
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}
sleep 2

if systemctl is-active --quiet ${SERVICE_NAME}; then
  ok "Service פועל! (${SERVICE_NAME})"
else
  err "Service לא הצליח להתחיל"
  journalctl -u ${SERVICE_NAME} -n 10 --no-pager
  exit 1
fi

# ──────────────────────────────────────
section "✅ סיכום"

echo -e "${GREEN}${BOLD}"
echo "  המערכת מותקנת ופועלת!"
echo ""
echo "  📡 ORef API:    ${OREF_API_URL}"
echo "  📱 WhatsApp:    ${WHATSAPP_GROUP:-לא מוגדר}"
echo "  🏠 Home Assist: ${HA_URL:-מושבת}"
echo "  📞 חיוג 3CX:    ${PHONE_CALL_ENABLED}"
echo -e "${NC}"
echo ""
echo -e "${CYAN}פקודות שימושיות:${NC}"
echo "  systemctl status ${SERVICE_NAME}     # סטטוס"
echo "  journalctl -u ${SERVICE_NAME} -f     # לוגים חיים"
echo "  systemctl restart ${SERVICE_NAME}    # הפעלה מחדש"
echo "  nano ${ENV_FILE}                     # עריכת הגדרות"
echo ""
echo -e "${YELLOW}⚠️  לשינוי הגדרות: ערוך את .env ואז הפעל מחדש את השירות${NC}"
