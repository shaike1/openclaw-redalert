---
name: oref-alerts
description: >
  Israeli Home Front Command (פיקוד העורף) real-time alert system.
  Docker-based proxy service + Home Assistant integration with TTS speaker
  announcements and WhatsApp notifications. Triggers on: (1) checking active
  alerts, (2) deploying/restarting the oref-alerts Docker service, (3) updating
  HA configuration, (4) testing the alert system.
---

# ORef Alerts Skill - פיקוד העורף

## Architecture

```
Pikud Ha-Oref API
       ↓
Docker: dmatik/oref-alerts (port 49000)
       ↓
Home Assistant REST sensor (every 5s)
       ↓
binary_sensor.redalert_glilyam (הרצליה - גליל ים)
       ↓
Automation triggers:
  🔊 TTS Speaker (media_player.home_assistant_voice_09a069)
  📱 WhatsApp → קבוצת עדכונים (120363417492964228@g.us)
  💡 Light flash (script.red_state_flash)
```

## Quick Commands

### Check active alerts
```bash
curl -s http://vps1.right-api.com:49000/current | python3 -m json.tool
```

### Docker service status
```bash
docker ps | grep oref
docker logs oref-alerts --tail 20
```

### Restart service (production mode - NO test mode)
```bash
docker stop oref-alerts && docker rm oref-alerts
docker run -d \
  -p 49000:9001 \
  --name oref-alerts \
  --restart unless-stopped \
  -e TZ="Asia/Jerusalem" \
  dmatik/oref-alerts:latest
```

### Restart with test mode (for testing only!)
```bash
docker run -d \
  -p 49000:9001 \
  --name oref-alerts-test \
  --restart unless-stopped \
  -e TZ="Asia/Jerusalem" \
  -e CURRENT_ALERT_TEST_MODE=TRUE \
  -e CURRENT_ALERT_TEST_MODE_LOC="הרצליה - גליל ים ומרכז" \
  dmatik/oref-alerts:latest
```

## Infrastructure

| Component | Value |
|-----------|-------|
| VPS IP (external) | 129.159.151.140 |
| VPS hostname | vps1.right-api.com |
| Docker port | 49000 |
| API URL (from HA) | http://vps1.right-api.com:49000/current |
| HA SSH | root@100.64.0.15 / Tr1C0late |
| HA URL | https://ha.right-api.com |
| HA local | http://192.168.88.253:8443 |

## Home Assistant Configuration

### Sensor (in /config/configuration.yaml)
```yaml
sensor:
  - platform: rest
    resource: http://vps1.right-api.com:49000/current
    name: redalert
    value_template: 'OK'
    json_attributes:
      - alert
      - current
    scan_interval: 5
    timeout: 30

binary_sensor:
  - platform: template
    sensors:
      redalert_glilyam:
        friendly_name: "Redalert GlilYam"
        value_template: >-
          {{ state_attr('sensor.redalert', 'alert') == true and
             'הרצליה - גליל ים ומרכז' in state_attr('sensor.redalert', 'current')['data'] }}
```

### Automation (in /config/automations.yaml)
- **ID:** 1697613231078
- **Alias:** redalert whatsapp Herzliya
- **Trigger:** `binary_sensor.redalert_glilyam` → on
- **Actions:**
  1. `script.red_alert` - main alert script
  2. `script.red_state_flash` - red light flash
  3. Push notification to mobile
  4. WhatsApp → `120363417492964228@g.us` (קבוצת עדכונים)
  5. TTS: "צבע אדום! היכנסו למרחב המוגן"
  6. After 10 min: all-clear notifications

## Monitored Areas

- **הרצליה - גליל ים ומרכז** → `binary_sensor.redalert_glilyam`

To add more areas, add binary_sensors in configuration.yaml:
```yaml
binary_sensor:
  - platform: template
    sensors:
      redalert_NEW_AREA:
        friendly_name: "Redalert New Area"
        value_template: >-
          {{ state_attr('sensor.redalert', 'alert') == true and
             'שם האזור' in state_attr('sensor.redalert', 'current')['data'] }}
```

## Testing

### 1. Check API directly
```bash
curl -s http://vps1.right-api.com:49000/current
```

### 2. Check HA sensor state (via SSH)
```bash
sshpass -p 'Tr1C0late' ssh root@100.64.0.15 \
  "curl -s http://localhost:8123/api/states/sensor.redalert \
  -H 'Authorization: Bearer TOKEN'"
```

### 3. Trigger test via HA (manually)
In HA → Developer Tools → Template:
```
{{ state_attr('sensor.redalert', 'alert') }}
{{ state_attr('sensor.redalert', 'current') }}
```

### 4. Force test alert (restart with test mode)
See "Restart with test mode" above - use הרצליה - גליל ים ומרכז as location.

## WhatsApp Groups

| Group | JID |
|-------|-----|
| קבוצת עדכונים (family) | 120363417492964228@g.us |

## Troubleshooting

**Docker not running:**
```bash
docker start oref-alerts
# or full restart:
docker stop oref-alerts && docker rm oref-alerts
# then run command above
```

**HA sensor not updating:**
- Check API accessible from HA: `curl http://vps1.right-api.com:49000/current`
- Check HA logs for REST sensor errors
- Verify configuration.yaml syntax

**WhatsApp not sending:**
- Verify wacli/whatsapp integration is active in OpenClaw
- Check group JID is correct
- Test manually via OpenClaw

**HA high load:**
- Normal during restart
- scan_interval=5 is aggressive - can increase to 10 if needed
- Check with: `ha core stats`
