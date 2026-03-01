#!/bin/bash
# OpenClaw-3CX Voice v2 Test Script
# Tests the deployed v2 POC endpoints

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🧪 OpenClaw-3CX Voice v2 Test Suite${NC}"
echo "====================================="
echo ""

# Test 1: Health Check
echo "📡 Test 1: Voice Processor Health Check"
echo "   Endpoint: http://localhost:8081/health"
if curl -s -f http://localhost:8081/health | grep -q "healthy\|ok\|status"; then
    echo -e "   ${GREEN}✅ PASSED${NC}"
else
    echo -e "   ${YELLOW}⚠️  WARNING: Health check returned unexpected response${NC}"
    curl -s http://localhost:8081/health
fi
echo ""

# Test 2: Redis Connection
echo "📡 Test 2: Redis Connection"
if docker exec voice-redis-v2 redis-cli ping | grep -q "PONG"; then
    echo -e "   ${GREEN}✅ PASSED${NC}"
else
    echo -e "   ${RED}❌ FAILED: Redis not responding${NC}"
fi
echo ""

# Test 3: Container Health
echo "📡 Test 3: Container Health Status"
containers=("voice-gateway-v2" "voice-processor-v2" "voice-redis-v2")
all_healthy=true

for container in "${containers[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "$container"; then
        status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
        if [ "$status" = "healthy" ] || [ "$status" = "no-healthcheck" ]; then
            echo "   - $container: ${GREEN}healthy${NC}"
        else
            echo "   - $container: ${YELLOW}$status${NC}"
            all_healthy=false
        fi
    else
        echo "   - $container: ${RED}not running${NC}"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo -e "   ${GREEN}✅ ALL PASSED${NC}"
else
    echo -e "   ${YELLOW}⚠️  Some containers are unhealthy${NC}"
fi
echo ""

# Test 4: Network Connectivity
echo "📡 Test 4: Inter-container Network"
if docker exec voice-processor-v2 ping -c 1 voice-gateway &> /dev/null; then
    echo -e "   ${GREEN}✅ PASSED: Processor can reach Gateway${NC}"
else
    echo -e "   ${RED}❌ FAILED: Network connectivity issue${NC}"
fi
echo ""

# Test 5: Volume Mounts
echo "📡 Test 5: Volume Mounts"
if docker exec voice-processor-v2 test -d /var/log/voice; then
    echo -e "   ${GREEN}✅ PASSED: Log directory mounted${NC}"
else
    echo -e "   ${RED}❌ FAILED: Log directory not mounted${NC}"
fi

if docker exec voice-processor-v2 test -d /tmp/voice; then
    echo -e "   ${GREEN}✅ PASSED: Temp directory mounted${NC}"
else
    echo -e "   ${RED}❌ FAILED: Temp directory not mounted${NC}"
fi
echo ""

# Test 6: Environment Variables
echo "📡 Test 6: Environment Configuration"
env_vars=("OPENAI_API_KEY" "ANTHROPIC_API_KEY" "ELEVENLABS_API_KEY")
all_set=true

for var in "${env_vars[@]}"; do
    if docker exec voice-processor-v2 printenv | grep -q "$var="; then
        echo "   - $var: ${GREEN}set${NC}"
    else
        echo "   - $var: ${RED}NOT SET${NC}"
        all_set=false
    fi
done

if [ "$all_set" = true ]; then
    echo -e "   ${GREEN}✅ ALL PASSED${NC}"
else
    echo -e "   ${RED}❌ FAILED: Some environment variables missing${NC}"
fi
echo ""

# Test 7: Port Availability
echo "📡 Test 7: Port Availability"
ports=("8081:Voice Processor API" "6380:Redis" "9091:Prometheus")
for port_info in "${ports[@]}"; do
    port="${port_info%%:*}"
    name="${port_info##*:}"
    if nc -z localhost "$port" 2>/dev/null; then
        echo "   - Port $port ($name): ${GREEN}listening${NC}"
    else
        echo "   - Port $port ($name): ${YELLOW}not accessible${NC}"
    fi
done
echo ""

# Summary
echo "====================================="
echo -e "${GREEN}✅ Test Suite Complete!${NC}"
echo ""
echo "📊 Next Steps:"
echo "   1. Configure 3CX extension to forward to SIP server"
echo "   2. Make a test call to verify end-to-end flow"
echo "   3. Monitor logs: docker compose -f docker-compose.voice-v2.yml logs -f"
echo ""
echo "🔗 Useful Commands:"
echo "   - View logs: docker compose -f docker-compose.voice-v2.yml logs -f voice-processor"
echo "   - Restart: docker compose -f docker-compose.voice-v2.yml restart"
echo "   - Stop: docker compose -f docker-compose.voice-v2.yml down"
echo "   - Check health: docker compose -f docker-compose.voice-v2.yml ps"
