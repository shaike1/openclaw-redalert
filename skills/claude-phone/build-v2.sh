#!/bin/bash
# Build Voice v2 Docker Images

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🏗️  Building OpenClaw Voice v2 Docker Images${NC}"
echo "=========================================="
echo ""

# Check if .env.voice-v2 exists
if [ ! -f .env.voice-v2 ]; then
    echo -e "${YELLOW}⚠️  .env.voice-v2 not found${NC}"
    echo "Creating from example..."
    cp .env.voice-v2.example .env.voice-v2
    echo -e "${RED}❌ Please edit .env.voice-v2 with your API keys${NC}"
    exit 1
fi

# Load environment variables
set -a
source .env.voice-v2
set +a

# Build voice-processor
echo -e "${YELLOW}Building voice-processor...${NC}"
docker build \
  -f Dockerfile.voice-processor \
  -t voice-processor:v2 \
  -t voice-processor:latest \
  .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ voice-processor built successfully${NC}"
else
    echo -e "${RED}❌ voice-processor build failed${NC}"
    exit 1
fi

echo ""

# Build voice-gateway
echo -e "${YELLOW}Building voice-gateway...${NC}"
docker build \
  -f Dockerfile.voice-gateway \
  -t voice-gateway:v2 \
  -t voice-gateway:latest \
  .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ voice-gateway built successfully${NC}"
else
    echo -e "${RED}❌ voice-gateway build failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All images built successfully!${NC}"
echo ""
echo "📊 Images:"
docker images | grep -E "voice-processor|voice-gateway"
echo ""
echo "🚀 Next: Deploy with ./voice-v2-deploy.sh"
