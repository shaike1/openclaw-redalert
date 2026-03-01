#!/bin/bash
# OpenClaw-3CX Voice v2 Deployment Script
# This script deploys the v2 POC alongside the existing v1 setup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 OpenClaw-3CX Voice v2 Deployment${NC}"
echo "======================================"

# Check if .env.voice-v2 exists
if [ ! -f .env.voice-v2 ]; then
    echo -e "${YELLOW}⚠️  .env.voice-v2 not found. Creating from example...${NC}"
    cp .env.voice-v2.example .env.voice-v2
    echo -e "${RED}❌ Please edit .env.voice-v2 with your API keys and passwords${NC}"
    echo "   Then run this script again."
    exit 1
fi

# Source environment variables
set -a
source .env.voice-v2
set +a

# Validate required variables
echo "🔍 Validating configuration..."
required_vars=("SIP_SERVER" "SIP_USERNAME" "SIP_PASSWORD" "OPENAI_API_KEY" "ANTHROPIC_API_KEY" "ELEVENLABS_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing required variables in .env.voice-v2:${NC}"
    printf "   - %s\n" "${missing_vars[@]}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration valid${NC}"

# Check Docker
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available${NC}"

# Check if v1 is running
echo "🔍 Checking existing Voice v1..."
if docker ps | grep -q "voice-gateway"; then
    echo -e "${YELLOW}⚠️  Voice v1 is currently running${NC}"
    echo "   v2 will run in parallel on different ports:"
    echo "   - SIP: 5060/UDP (same, will conflict if v1 uses it)"
    echo "   - API: 8081 (v1 uses 8080)"
    echo "   - Redis: 6380 (v1 uses 6379)"
    echo ""
    read -p "Continue with parallel deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/gateway logs/processor tmp/audio monitoring

# Create Prometheus config if it doesn't exist
if [ ! -f monitoring/prometheus.yml ]; then
    echo "📝 Creating Prometheus configuration..."
    mkdir -p monitoring
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'voice-gateway'
    static_configs:
      - targets: ['voice-gateway:8080']

  - job_name: 'voice-processor'
    static_configs:
      - targets: ['voice-processor:8080']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
fi

# Build and start containers
echo "🏗️  Building and starting containers..."
if docker compose version &> /dev/null; then
    docker compose -f docker-compose.voice-v2.yml up -d
else
    docker-compose -f docker-compose.voice-v2.yml up -d
fi

# Wait for services to be healthy
echo "⏳ Waiting for services to start healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.voice-v2.yml ps

echo ""
echo -e "${GREEN}✅ Voice v2 deployed successfully!${NC}"
echo ""
echo "🔗 Endpoints:"
echo "   - Health Check: http://localhost:8081/health"
echo "   - Prometheus: http://localhost:9091"
echo ""
echo "📝 Logs:"
echo "   - All services: docker compose -f docker-compose.voice-v2.yml logs -f"
echo "   - Gateway: docker compose -f docker-compose.voice-v2.yml logs -f voice-gateway"
echo "   - Processor: docker compose -f docker-compose.voice-v2.yml logs -f voice-processor"
echo ""
echo "🛑 Stop services:"
echo "   docker compose -f docker-compose.voice-v2.yml down"
echo ""
echo "🧪 Test the deployment:"
echo "   curl http://localhost:8081/health"
