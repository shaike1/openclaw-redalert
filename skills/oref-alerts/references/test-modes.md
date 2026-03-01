# OREF Alerts - Test Modes

Guide for testing the OREF alerts system without waiting for real alerts.

## Environment Variables

The oref-alerts-proxy-ms service supports several test modes via Docker environment variables:

### Current Alert Test Mode

**Variable:** `CURRENT_ALERT_TEST_MODE`

**Values:** `"TRUE"` or `"FALSE"`

**Description:** When set to `"TRUE"`, the service will return a simulated active alert instead of real data.

**Usage:**
```yaml
docker run -d \
  --name oref-alerts \
  -e CURRENT_ALERT_TEST_MODE="TRUE" \
  -e CURRENT_ALERT_TEST_MODE_LOC="אשדוד" \
  -p 49000:9001 \
  dmatik/oref-alerts:latest
```

### Current Alert Test Location

**Variable:** `CURRENT_ALERT_TEST_MODE_LOC`

**Values:** Any Hebrew city name or area string

**Description:** Sets the area for the simulated alert.

**Example locations:**
- `"אשדוד"`
- `"אשקלון"`
- `"תל אביב"`
- `"ירושלים"`
- `"באר שבע"`

### History Test Mode

**Variable:** `HISTORY_TEST_MODE`

**Values:** `"TRUE"` or `"FALSE"`

**Description:** When set to `"TRUE"`, the service returns simulated historical alert data.

## Test Scenarios

### Scenario 1: Test Active Alert

Simulate an active red alert in Ashdod:

```bash
# Stop existing container
docker stop oref-alerts && docker rm oref-alerts

# Start with test mode
docker run -d \
  --name oref-alerts-test \
  --restart unless-stopped \
  -e CURRENT_ALERT_TEST_MODE="TRUE" \
  -e CURRENT_ALERT_TEST_MODE_LOC="אשדוד - יא,יב,טו,יז,מרינה" \
  -e TZ="Asia/Jerusalem" \
  -p 49001:9001 \
  dmatik/oref-alerts:latest

# Test the endpoint
curl http://localhost:49001/current | jq '.'
```

**Expected Output:**
```json
{
  "alert": true,
  "current": {
    "id": "132944072580000000",
    "cat": "1",
    "title": "ירי טילים ורקטות",
    "data": ["אשדוד - יא,יב,טו,יז,מרינה"],
    "desc": "היכנסו למרחב המוגן"
  }
}
```

### Scenario 2: Test Multiple Locations

Test alert for multiple cities:

```bash
docker run -d \
  --name oref-alerts-multi \
  -e CURRENT_ALERT_TEST_MODE="TRUE" \
  -e CURRENT_ALERT_TEST_MODE_LOC="אשדוד, אשקלון, תל אביב" \
  -p 49002:9001 \
  dmatik/oref-alerts:latest
```

### Scenario 3: Test History

Test historical alerts:

```bash
docker run -d \
  --name oref-alerts-history \
  -e HISTORY_TEST_MODE="TRUE" \
  -p 49003:9001 \
  dmatik/oref-alerts:latest

# Test history endpoint
curl http://localhost:49003/history | jq '.'
```

**Expected Output:**
```json
{
  "history": [
    {
      "alertDate": "2024-07-03 18:45:36",
      "title": "ירי רקטות וטילים",
      "data": "זרעית",
      "category": 1
    },
    {
      "alertDate": "2024-07-03 18:38:03",
      "title": "ירי רקטות וטילים",
      "data": "כפר סאלד",
      "category": 1
    }
  ]
}
```

### Scenario 4: Full Test with Both Modes

```bash
docker run -d \
  --name oref-alerts-full-test \
  -e CURRENT_ALERT_TEST_MODE="TRUE" \
  -e CURRENT_ALERT_TEST_MODE_LOC="אשדוד" \
  -e HISTORY_TEST_MODE="TRUE" \
  -p 49004:9001 \
  dmatik/oref-alerts:latest

# Test both endpoints
echo "=== Current Alert ==="
curl -s http://localhost:49004/current | jq '.'

echo "=== History ==="
curl -s http://localhost:49004/history | jq '.'
```

## Integration Testing

### Test Home Assistant Integration

1. Deploy test instance:
```bash
cd /root/.openclaw/workspace/skills/oref-alerts
./scripts/deploy-test.sh
```

2. Update Home Assistant configuration to use test port:
```yaml
sensor:
  - platform: rest
    resource: http://192.168.1.100:49001/current  # Test port
    name: redalert_test
    value_template: 'OK'
    json_attributes:
      - alert
      - current
    scan_interval: 5
```

3. Reload Home Assistant:
```bash
# In Home Assistant UI
Configuration > Server Controls > Reload REST
```

4. Check sensor state:
```yaml
{{ state_attr('sensor.redalert_test', 'alert') }}
# Should be true
```

### Test WhatsApp Notification Script

```bash
# Test connection to API
cd /root/.openclaw/workspace/skills/oref-alerts
./scripts/whatsapp-notify.sh test

# Start monitor (will detect test alerts)
./scripts/whatsapp-notify.sh start

# In another terminal, check status
./scripts/whatsapp-notify.sh status

# View logs
tail -f /var/log/oref-whatsapp.log
```

### Test Alert Transition

Simulate alert starting and ending:

```bash
# Start with alert
docker stop oref-alerts && docker rm oref-alerts
docker run -d \
  --name oref-alerts \
  -e CURRENT_ALERT_TEST_MODE="TRUE" \
  -e CURRENT_ALERT_TEST_MODE_LOC="אשדוד" \
  -p 49000:9001 \
  dmatik/oref-alerts:latest

# Wait for alert to trigger
sleep 10

# Stop alert
docker stop oref-alerts && docker rm oref-alerts
docker run -d \
  --name oref-alerts \
  -e CURRENT_ALERT_TEST_MODE="FALSE" \
  -p 49000:9001 \
  dmatik/oref-alerts:latest
```

## Automated Testing

### Test Script

Create `/root/.openclaw/workspace/skills/oref-alerts/test.sh`:

```bash
#!/bin/bash

echo "🧪 OREF Alerts Test Suite"

# Test 1: Service availability
echo "Test 1: Service availability..."
if curl -s http://localhost:49000/current > /dev/null; then
    echo "✅ Service is accessible"
else
    echo "❌ Service is not accessible"
    exit 1
fi

# Test 2: Valid JSON response
echo "Test 2: Valid JSON response..."
if curl -s http://localhost:49000/current | jq . > /dev/null; then
    echo "✅ JSON response is valid"
else
    echo "❌ Invalid JSON response"
    exit 1
fi

# Test 3: Current endpoint structure
echo "Test 3: Current endpoint structure..."
response=$(curl -s http://localhost:49000/current)
if echo "$response" | jq -e '.alert' > /dev/null; then
    echo "✅ Alert field exists"
else
    echo "❌ Alert field missing"
    exit 1
fi

# Test 4: History endpoint
echo "Test 4: History endpoint..."
if curl -s http://localhost:49000/history | jq . > /dev/null; then
    echo "✅ History endpoint works"
else
    echo "❌ History endpoint failed"
    exit 1
fi

echo "✅ All tests passed!"
```

**Run tests:**
```bash
chmod +x /root/.openclaw/workspace/skills/oref-alerts/test.sh
/root/.openclaw/workspace/skills/oref-alerts/test.sh
```

## Load Testing

### Test High-Frequency Polling

```bash
#!/bin/bash
# Load test: 100 requests in 10 seconds

for i in {1..100}; do
    curl -s http://localhost:49000/current > /dev/null &
    if [ $((i % 10)) -eq 0 ]; then
        echo "Sent $i requests..."
    fi
    sleep 0.1
done

wait
echo "✅ Load test complete"
```

### Monitor Service Performance

```bash
# Monitor CPU and memory usage
docker stats oref-alerts

# Monitor response times
while true; do
    start=$(date +%s%N)
    curl -s http://localhost:49000/current > /dev/null
    end=$(date +%s%N)
    diff=$(( ($end - $start) / 1000000 ))
    echo "Response time: ${diff}ms"
    sleep 5
done
```

## Cleanup After Testing

### Remove Test Containers

```bash
# Stop and remove all test containers
docker stop oref-alerts-test oref-alerts-multi oref-alerts-history oref-alerts-full-test 2>/dev/null
docker rm oref-alerts-test oref-alerts-multi oref-alerts-history oref-alerts-full-test 2>/dev/null

# Verify production container is still running
docker ps | grep oref-alerts
```

### Switch Back to Production

```bash
# Remove test container
docker stop oref-alerts && docker rm oref-alerts

# Start production container (without test modes)
docker run -d \
  --name oref-alerts \
  --restart unless-stopped \
  -e TZ="Asia/Jerusalem" \
  -p 49000:9001 \
  dmatik/oref-alerts:latest

# Verify
curl http://localhost:49000/current | jq '.'
```

## Best Practices

### Testing Checklist

- [ ] Test API endpoints are accessible
- [ ] Verify JSON response structure
- [ ] Test with simulated active alert
- [ ] Test with simulated history
- [ ] Test Home Assistant integration
- [ ] Test WhatsApp notifications
- [ ] Verify alert transitions (start/end)
- [ ] Test error handling
- [ ] Performance testing (if needed)
- [ ] Clean up test containers

### When to Use Test Mode

**Use test mode when:**
- Setting up the system for the first time
- Testing new features or integrations
- Troubleshooting issues
- Demonstrating the system
- Developing automations

**Use production mode when:**
- The system is live and monitoring
- Relying on real alerts
- In a production environment

### Safety Tips

1. **Always use a different port** for testing (e.g., 49001, 49002)
2. **Don't mix test and production** on the same port
3. **Clearly label test containers** with `-test` suffix
4. **Clean up test containers** after testing
5. **Document test procedures** for future use

## Summary

Test modes are essential for:
- Development and testing
- Troubleshooting issues
- Demonstrating functionality
- Training users

Always test thoroughly before deploying to production!
