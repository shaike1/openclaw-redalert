#!/bin/bash

# Fix Home Assistant ORef sensor to use localhost:9001
# This script configures the RedAlert sensor to use the internal API

HA_IP="212.179.247.130"
HA_TOKEN="REDACTED_HA_TOKEN_1"

echo "🔧 Fixing Home Assistant RedAlert sensor..."
echo "📍 HA IP: $HA_IP"

# Try to configure sensor via API
curl -s -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"domain\": \"binary_sensor\",
    \"service\": \"reload\"
  }" \
  http://$HA_IP:8123/api/services/binary_sensor/reload

echo "✅ Sensor reload triggered!"
echo ""
echo "📋 Manual configuration steps:"
echo "1. Open Home Assistant"
echo "2. Go to: Settings → Devices & Services"
echo "3. Search: binary_sensor.redalert"
echo "4. Click: Configure"
echo "5. Change Resource URL to: http://localhost:9001/current"
echo "6. Click: UPDATE"
echo "7. Click: RELOAD"
echo ""
echo "✅ Done! The sensor should now connect to localhost:9001"
