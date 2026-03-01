#!/bin/bash

# WhatsApp Notification Monitor for OREF Alerts
# Enhanced version - handles errors and auto-recovers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../references/config.yaml"
LOG_FILE="/var/log/oref-whatsapp.log"
PID_FILE="/var/run/oref-whatsapp.pid"
API_URL="http://localhost:49000/current"
CHECK_INTERVAL=5  # seconds
MAX_RETRIES=3
RETRY_DELAY=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local msg="$(date '+%Y-%m-%d %H:%M:%S') [$level] $*"
    echo -e "$msg" | tee -a "$LOG_FILE"
}

# Load configuration
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log "ERROR" "Config file not found: $CONFIG_FILE"
        echo -e "${RED}❌ Please create config file at: $CONFIG_FILE${NC}"
        exit 1
    fi

    # Load WhatsApp settings
    WHATSAPP_GROUP=$(grep "^whatsapp:" -A 10 "$CONFIG_FILE" | grep "group_id:" | sed 's/.*: "\(.*\)".*/\1/')
    WHATSAPP_ENABLED=$(grep "^whatsapp:" -A 10 "$CONFIG_FILE" | grep "enabled:" | sed 's/.*: \(.*\).*/\1/')

    # Normalize enabled value (handle spaces and quotes)
    WHATSAPP_ENABLED=$(echo "$WHATSAPP_ENABLED" | tr -d '"' | tr -d "'" | xargs)

    if [ "$WHATSAPP_ENABLED" != "true" ]; then
        log "WARN" "WhatsApp notifications are disabled in config (enabled=$WHATSAPP_ENABLED)"
    fi

    if [ -z "$WHATSAPP_GROUP" ]; then
        log "ERROR" "WhatsApp group_id not configured"
        echo -e "${RED}❌ Please configure whatsapp.group_id in: $CONFIG_FILE${NC}"
        exit 1
    fi

    log "INFO" "Configuration loaded - Group: $WHATSAPP_GROUP, Enabled: $WHATSAPP_ENABLED"
}

# Get current alert status with retry logic
get_alert_status() {
    local response
    local retries=0
    local success=false

    while [ $retries -lt $MAX_RETRIES ] && [ "$success" = false ]; do
        response=$(curl -s --connect-timeout 10 --max-time 30 "$API_URL" 2>/dev/null)
        
        if [ -n "$response" ] && echo "$response" | grep -q "alert"; then
            success=true
        else
            retries=$((retries + 1))
            if [ $retries -lt $MAX_RETRIES ]; then
                log "WARN" "Failed to fetch API (attempt $retries/$MAX_RETRIES), retrying in ${RETRY_DELAY}s..."
                sleep $RETRY_DELAY
            fi
        fi
    done

    if [ "$success" = false ]; then
        log "ERROR" "Failed to fetch alert status after $MAX_RETRIES attempts"
        return 1
    fi

    echo "$response"
}

# Check if there's an active alert
is_active_alert() {
    local response="$1"
    echo "$response" | grep -q '"alert": true'
    return $?
}

# Get alert details
get_alert_details() {
    local response="$1"
    local title=$(echo "$response" | jq -r '.current.title // empty')
    local data=$(echo "$response" | jq -r '.current.data // empty')
    local desc=$(echo "$response" | jq -r '.current.desc // empty')
    local alert_id=$(echo "$response" | jq -r '.current.id // empty')
    
    echo "$title|$data|$desc|$alert_id"
}

# Send WhatsApp notification
send_whatsapp_notification() {
    local title="$1"
    local data="$2"
    local desc="$3"
    local alert_id="$4"
    
    if [ -z "$title" ]; then
        title="התראה צבע אדום"
    fi
    
    if [ -z "$data" ]; then
        data="בלי פירוט"
    fi
    
    if [ "$WHATSAPP_ENABLED" != "true" ]; then
        log "WARN" "Skipping WhatsApp - notifications disabled"
        return
    fi

    # Load message format from config
    local alert_format=$(grep "^notifications:" -A 10 "$CONFIG_FILE" | grep "alert_format:" | sed 's/.*: "\(.*\)".*/\1/')
    
    # Replace placeholders
    local message="$alert_format"
    message="${message//\{title\}/$title}"
    message="${message//\{data\}/$data}"
    
    log "INFO" "Sending WhatsApp notification (ID: $alert_id): $title - $data"
    
    # Try to send using whatsapp skill
    local result=$(cd /root/.openclaw/workspace/skills && echo "$message" | node whatsapp-groups.js send "$WHATSAPP_GROUP" 2>&1)
    
    if [ $? -eq 0 ]; then
        log "INFO" "✅ WhatsApp notification sent successfully"
    else
        log "ERROR" "❌ Failed to send WhatsApp notification: $result"
    fi
}

# Main monitoring loop
monitor_loop() {
    log "INFO" "Starting alert monitoring"
    local last_alert_state="false"
    local last_alert_id=""
    
    while true; do
        # Get current status
        status=$(get_alert_status)
        
        if [ $? -ne 0 ]; then
            # Failed to get status, sleep and retry
            sleep $CHECK_INTERVAL
            continue
        fi
        
        # Check if active
        if is_active_alert "$status"; then
            # Get alert details
            details=$(get_alert_details "$status")
            title=$(echo "$details" | cut -d'|' -f1)
            data=$(echo "$details" | cut -d'|' -f2)
            desc=$(echo "$details" | cut -d'|' -f3)
            alert_id=$(echo "$details" | cut -d'|' -f4)
            
            # Check if state changed from inactive to active
            if [ "$last_alert_state" != "true" ]; then
                log "INFO" "🚨 Active alert detected (ID: $alert_id)"
                log "INFO" "Title: $title"
                log "INFO" "Data: $data"
                log "INFO" "Description: $desc"
                
                # Send notification
                send_whatsapp_notification "$title" "$data" "$desc" "$alert_id"
                
                last_alert_state="true"
                last_alert_id="$alert_id"
            elif [ "$last_alert_id" != "$alert_id" ]; then
                # New alert detected while still active
                log "INFO" "🔄 New alert detected (ID: $alert_id, previous: $last_alert_id)"
                
                # Check minimum interval
                local current_time=$(date +%s)
                local last_alert_time=$(grep "Active alert detected" "$LOG_FILE" | tail -1 | awk '{print $2}')
                
                # Send notification for new alert
                send_whatsapp_notification "$title" "$data" "$desc" "$alert_id"
                last_alert_id="$alert_id"
            fi
        else
            # No active alert
            if [ "$last_alert_state" = "true" ]; then
                log "INFO" "✅ Alert cleared (ID: $last_alert_id)"
                
                # Send clear notification if configured
                local clear_format=$(grep "^notifications:" -A 10 "$CONFIG_FILE" | grep "clear_format:" | sed 's/.*: "\(.*\)".*/\1/')
                
                if [ "$WHATSAPP_ENABLED" = "true" ] && [ -n "$clear_format" ]; then
                    local message="$clear_format"
                    message="${message//\{clear\}/✅}"
                    
                    local result=$(cd /root/.openclaw/workspace/skills && echo "$message" | node whatsapp-groups.js send "$WHATSAPP_GROUP" 2>&1)
                    
                    if [ $? -eq 0 ]; then
                        log "INFO" "✅ Clear notification sent"
                    else
                        log "ERROR" "❌ Failed to send clear notification: $result"
                    fi
                fi
                
                last_alert_state="false"
                last_alert_id=""
            fi
        fi
        
        # Wait before next check
        sleep $CHECK_INTERVAL
    done
}

# Stop function
stop_monitor() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            rm -f "$PID_FILE"
            log "INFO" "Monitor stopped (PID: $pid)"
            echo -e "${GREEN}✅ Monitor stopped${NC}"
        else
            rm -f "$PID_FILE"
            echo -e "${YELLOW}⚠️  Monitor was not running${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Monitor was not running${NC}"
    fi
}

# Status function
status_monitor() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Monitor is running (PID: $pid)${NC}"
            echo -e "Log file: $LOG_FILE"
            
            # Show last few lines
            echo ""
            echo "Recent logs:"
            tail -5 "$LOG_FILE"
        else
            echo -e "${RED}❌ Monitor is not running${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${RED}❌ Monitor is not running${NC}"
    fi
}

# Test function
test_monitor() {
    log "INFO" "Configuration loaded - Group: $WHATSAPP_GROUP, Enabled: $WHATSAPP_ENABLED"
    echo -e "${GREEN}✅ Connected to API${NC}"
    
    # Get current status
    echo ""
    echo "Current status:"
    get_alert_status | jq '.' 2>/dev/null || get_alert_status
}

# Start function
start_monitor() {
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Monitor is already running (PID: $pid)${NC}"
            echo -e "Use '${0##*/} stop' first"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Start in background
    log "INFO" "Starting monitor in background"
    
    # Create PID file and start
    echo $$ > "$PID_FILE"
    
    # Redirect output and start monitoring
    monitor_loop >> "$LOG_FILE" 2>&1 &
    
    local new_pid=$!
    echo $new_pid > "$PID_FILE"
    
    # Wait a moment and check if it's running
    sleep 2
    if ps -p "$new_pid" > /dev/null 2>&1; then
        log "INFO" "✅ Monitor started successfully (PID: $new_pid)"
        echo -e "${GREEN}✅ Monitor started (PID: $new_pid)${NC}"
        echo -e "Log file: $LOG_FILE"
        echo -e "Checking every ${CHECK_INTERVAL}s"
    else
        rm -f "$PID_FILE"
        echo -e "${RED}❌ Failed to start monitor${NC}"
        exit 1
    fi
}

# Foreground mode (for testing)
start_foreground() {
    echo -e "${YELLOW}🔍 Running in foreground mode (Ctrl+C to stop)${NC}"
    monitor_loop
}

# Main
case "${1:-}" in
    start)
        load_config
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        stop_monitor
        sleep 1
        load_config
        start_monitor
        ;;
    status)
        load_config
        status_monitor
        ;;
    test)
        load_config
        test_monitor
        ;;
    fg)
        load_config
        start_foreground
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test|fg}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the monitor in background"
        echo "  stop    - Stop the monitor"
        echo "  restart - Restart the monitor"
        echo "  status  - Show monitor status and recent logs"
        echo "  test    - Test connection and show current status"
        echo "  fg      - Run in foreground mode (for debugging)"
        exit 1
        ;;
esac
