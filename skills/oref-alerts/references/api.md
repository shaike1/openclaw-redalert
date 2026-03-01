# OREF Alerts API Reference

Complete API documentation for the oref-alerts-proxy-ms service.

## Base URL

```
http://localhost:49000
```

Change `localhost` to the actual host IP if accessing from another machine.

## Endpoints

### GET /current

Returns the current active alert status.

**Response Format:**

```json
{
  "alert": true,
  "current": {
    "id": "132944072580000000",
    "cat": "1",
    "title": "ירי טילים ורקטות",
    "data": ["סעד", "אשדוד - יא,יב,טו,יז,מרינה"],
    "desc": "היכנסו למרחב המוגן"
  }
}
```

**Fields:**

- `alert` (boolean): Whether there is an active alert
- `current.id` (string): Unique alert ID
- `current.cat` (string): Alert category code
- `current.title` (string): Alert title (Hebrew)
- `current.data` (array): List of affected areas (Hebrew)
- `current.desc` (string): Instructions (Hebrew)

**Example Request:**

```bash
curl http://localhost:49000/current
```

**Example Response (No Alert):**

```json
{
  "alert": false,
  "current": null
}
```

### GET /history

Returns the alert history.

**Response Format:**

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

**Fields:**

- `history` (array): List of historical alerts
- `history[].alertDate` (string): Alert timestamp (YYYY-MM-DD HH:MM:SS)
- `history[].title` (string): Alert title (Hebrew)
- `history[].data` (string): Affected area (Hebrew)
- `history[].category` (number): Alert category code

**Example Request:**

```bash
curl http://localhost:49000/history
```

## Alert Categories

The `cat` or `category` field contains alert type codes:

| Code | Type | Description |
|------|------|-------------|
| 1 | מיסילים ורקטות | Missiles and rockets |
| 2 | חדירת מחבלים | Terrorist infiltration |
| 3 | רעידת אדמה | Earthquake |
| 4 | צונאמי | Tsunami |
| 5 | זיהום רדיואקטיבי | Radioactive contamination |

## Usage Examples

### Check if there's an active alert

```bash
#!/bin/bash
response=$(curl -s http://localhost:49000/current)
if echo "$response" | grep -q '"alert": true'; then
    echo "🚨 Active alert!"
    echo "$response" | jq -r '.current.title, .current.data'
else
    echo "✅ No active alerts"
fi
```

### Monitor for alerts

```bash
#!/bin/bash
while true; do
    response=$(curl -s http://localhost:49000/current)
    if echo "$response" | grep -q '"alert": true'; then
        title=$(echo "$response" | jq -r '.current.title')
        data=$(echo "$response" | jq -r '.current.data | join(", ")')
        echo "🚨 $title - $data"
    fi
    sleep 5
done
```

### Get last alert from history

```bash
curl -s http://localhost:49000/history | jq '.history[0]'
```

### Count alerts in last hour

```bash
#!/bin/bash
one_hour_ago=$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S')
curl -s http://localhost:49000/history | \
  jq --arg date "$one_hour_ago" \
     '[.history[] | select(.alertDate >= $date)] | length'
```

## Testing

Use curl to test endpoints:

```bash
# Test current alerts
curl http://localhost:49000/current | jq '.'

# Test history
curl http://localhost:49000/history | jq '.'

# Test with formatted output
curl -s http://localhost:49000/current | \
  jq -r 'if .alert then "🚨 \(.current.title): \(.current.data | join(", "))" else "✅ No alerts" end'
```

## Error Handling

### Common Errors

**Connection Refused:**
```
curl: (7) Failed to connect to localhost port 49000
```
**Solution:** Check if the Docker container is running: `docker ps | grep oref-alerts`

**Empty Response:**
```
curl: (52) Empty reply from server
```
**Solution:** Check container logs: `docker logs oref-alerts`

### Best Practices

1. **Rate Limiting:** Don't poll more frequently than every 5 seconds
2. **Error Handling:** Always check response validity before parsing JSON
3. **Time Zones:** All timestamps are in `Asia/Jerusalem` timezone
4. **Encoding:** API returns UTF-8 encoded Hebrew text

## Docker Access

From another machine, use the host's IP:

```bash
curl http://192.168.1.100:49000/current
```

Make sure port 49000 is accessible through the firewall:

```bash
sudo ufw allow 49000/tcp
```
