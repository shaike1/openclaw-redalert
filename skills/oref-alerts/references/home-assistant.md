# Home Assistant Integration - OREF Alerts

Complete guide for integrating OREF alerts with Home Assistant.

## Prerequisites

1. OREF alerts service running and accessible
2. Home Assistant instance (tested on 2024.x+)
3. Network connectivity between HA and the alerts service

## REST Sensor Configuration

Add the following sensors to your `configuration.yaml` or create a new file `sensors.yaml`:

### Basic REST Sensors

```yaml
# Current alerts sensor
sensor:
  - platform: rest
    resource: http://192.168.1.100:49000/current
    name: redalert
    value_template: 'OK'
    json_attributes:
      - alert
      - current
    scan_interval: 5
    timeout: 30

# Alert history sensor
sensor:
  - platform: rest
    resource: http://192.168.1.100:49000/history
    name: redalert_history
    value_template: 'OK'
    json_attributes:
      - history
    scan_interval: 120
    timeout: 30
```

**Important:** Replace `192.168.1.100` with your OREF alerts service IP.

## Binary Sensors

Add binary sensors for alert detection:

```yaml
binary_sensor:
  - platform: template
    sensors:
      redalert_all:
        friendly_name: "Redalert All Israel"
        device_class: safety
        value_template: >-
          {{ state_attr('sensor.redalert', 'alert') == true }}

      redalert_home:
        friendly_name: "Redalert Home"
        device_class: safety
        value_template: >-
          {{ state_attr('sensor.redalert', 'alert') == true and
          state_attr('sensor.redalert', 'current') is not none and
          'אשדוד' in state_attr('sensor.redalert', 'current')['data'] | join(' ') }}
```

**Customization:** Replace `'אשדוד'` with your city name.

## Automations

### Basic Alert Notification

```yaml
automation:
  - alias: "Send WhatsApp Red Alert"
    description: "Send WhatsApp notification when red alert detected"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_home
        to: "on"
    action:
      - service: script.send_whatsapp_notification
        data:
          message: "🚨 צבע אדום! היכנסו למרחב המוגן!"
          group_id: "your-group-id@g.us"
    mode: single
```

### Alert Cleared Notification

```yaml
automation:
  - alias: "Red Alert Cleared"
    description: "Notify when alert is cleared"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_home
        from: "on"
        to: "off"
    condition:
      - condition: template
        value_template: >
          {{ trigger.from_state.state == 'on' }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "✅ ההתראה הסתיימה"
    mode: single
```

### Alert with Details

```yaml
automation:
  - alias: "Detailed Red Alert"
    description: "Send alert with area details"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_home
        to: "on"
    action:
      - service: script.send_whatsapp_notification
        data:
          message: >
            🚨 צבע אדום!
            {% set current = state_attr('sensor.redalert', 'current') %}
            {{ current.title if current else 'התראה' }}
            {% if current %}
            - {{ current.data | join(', ') }}
            {% endif %}
            היכנסו למרחב המוגן!
          group_id: "your-group-id@g.us"
    mode: single
```

## Advanced Automations

### Multi-Location Alerting

```yaml
automation:
  - alias: "Red Alert Multiple Locations"
    description: "Alert for multiple locations"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_all
        to: "on"
    action:
      - variables:
          current: "{{ state_attr('sensor.redalert', 'current') }}"
          areas: "{{ current.data if current else [] }}"
      - choose:
          # Ashdod
          - conditions:
              - condition: template
                value_template: >
                  {{ areas is iterable and 'אשדוד' in areas | join(' ') }}
            sequence:
              - service: script.send_whatsapp_notification
                data:
                  message: "🚨 צבע אדום באשדוד! היכנסו למרחב המוגן!"
                  group_id: "ashdod-group@g.us"
          # Ashkelon
          - conditions:
              - condition: template
                value_template: >
                  {{ areas is iterable and 'אשקלון' in areas | join(' ') }}
            sequence:
              - service: script.send_whatsapp_notification
                data:
                  message: "🚨 צבע אדום באשקלון! היכנסו למרחב המוגן!"
                  group_id: "ashkelon-group@g.us"
    mode: single
```

### Alert Count Tracking

```yaml
sensor:
  - platform: template
    sensors:
      daily_alert_count:
        friendly_name: "Daily Alert Count"
        value_template: >
          {% set history = state_attr('sensor.redalert_history', 'history') %}
          {% set today = now().strftime('%Y-%m-%d') %}
          {% if history %}
            {% set alerts = history | selectattr('alertDate', 'search', today) | list %}
            {{ alerts | length }}
          {% else %}
            0
          {% endif %}
```

### Last Alert Information

```yaml
sensor:
  - platform: template
    sensors:
      last_alert_title:
        friendly_name: "Last Alert Title"
        value_template: >
          {% set history = state_attr('sensor.redalert_history', 'history') %}
          {{ history[0].title if history else 'No alerts' }}

      last_alert_time:
        friendly_name: "Last Alert Time"
        value_template: >
          {% set history = state_attr('sensor.redalert_history', 'history') %}
          {{ history[0].alertDate if history else 'N/A' }}

      last_alert_area:
        friendly_name: "Last Alert Area"
        value_template: >
          {% set history = state_attr('sensor.redalert_history', 'history') %}
          {{ history[0].data if history else 'N/A' }}
```

## Dashboard Cards

### Current Alert Card

```yaml
type: conditional
conditions:
  - entity: binary_sensor.redalert_home
    state: "on"
card:
  type: markdown
  title: "🚨 צבע אדום"
  content: >
    {% set current = state_attr('sensor.redalert', 'current') %}
    ## {{ current.title if current else 'התראה' }}

    **אזורים:** {{ current.data | join(', ') if current else 'N/A' }}

    **הוראות:** {{ current.desc if current else 'N/A' }}
```

### History Card

```yaml
type: entities
title: "📜 היסטוריית התראות"
entities:
  - sensor.last_alert_title
  - sensor.last_alert_time
  - sensor.last_alert_area
  - sensor.daily_alert_count
```

## Troubleshooting

### Sensor Not Updating

**Symptoms:** Sensor shows `unknown` or doesn't update

**Solutions:**
1. Check REST endpoint is accessible:
   ```bash
   curl http://192.168.1.100:49000/current
   ```
2. Check Home Assistant logs:
   ```bash
   journalctl -u home-assistant -f
   ```
3. Verify network connectivity between HA and alerts service
4. Check firewall rules

### Binary Sensor Not Working

**Symptoms:** Binary sensor always shows `off`

**Solutions:**
1. Check sensor attributes:
   ```yaml
   {{ state_attr('sensor.redalert', 'alert') }}
   ```
2. Verify JSON is being parsed correctly
3. Check template syntax in Developer Tools

### Automations Not Triggering

**Symptoms:** Automations don't run when alert changes

**Solutions:**
1. Check automation trace:
   Settings > Automations > [Your Automation] > Trace
2. Verify binary sensor state change:
   Developer Tools > State
3. Check automation conditions

## Performance Optimization

### Reduce Scan Intervals

For production, you may want to reduce scan frequency:

```yaml
sensor:
  - platform: rest
    resource: http://192.168.1.100:49000/current
    name: redalert
    value_template: 'OK'
    json_attributes:
      - alert
      - current
    scan_interval: 10  # Changed from 5 to 10 seconds
    timeout: 30
```

### Use Webhook (Advanced)

For high-availability setups, consider using webhook instead of polling:

1. Set up webhook endpoint in Home Assistant
2. Configure alerts service to push updates
3. Reduces load on both systems

## Security

### SSL/TLS

For production, use HTTPS:

```yaml
sensor:
  - platform: rest
    resource: https://alerts.yourdomain.com/current
    # Add verify_ssl: false if using self-signed certs
    verify_ssl: true
```

### Firewall Rules

Restrict access to the alerts service:

```bash
# Only allow Home Assistant IP
sudo ufw allow from 192.168.1.50 to any port 49000
```

## Integration with Other Services

### Telegram Notifications

```yaml
automation:
  - alias: "Send Telegram Red Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_home
        to: "on"
    action:
      - service: notify.telegram_bot
        data:
          message: "🚨 צבע אדום! היכנסו למרחב המוגן!"
```

### Email Notifications

```yaml
automation:
  - alias: "Send Email Red Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.redalert_home
        to: "on"
    action:
      - service: notify.email
        data:
          title: "🚨 צבע אדום"
          message: "צבע אדום פעיל! היכנסו למרחב המוגן!"
```

## Summary

1. Add REST sensors to fetch alert data
2. Create binary sensors for alert detection
3. Set up automations for notifications
4. Add dashboard cards for visualization
5. Test thoroughly before relying on it
