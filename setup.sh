#!/bin/bash

# Webtop Homework Skill Setup Script
# This script helps set up the webtop-skill with all dependencies

set -e

echo "🚀 Setting up Webtop Homework Skill..."
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.7+ is installed
echo -e "${YELLOW}📋 Checking Python installation...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check pip
echo -e "${YELLOW}📋 Checking pip installation...${NC}"
pip3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ pip3 is required but not installed.${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# Install Playwright browsers
echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
python3 -m playwright install

# Check if calendar directory exists
if [ ! -d "calendar" ]; then
    echo -e "${YELLOW}📁 Creating calendar directory...${NC}"
    mkdir -p calendar
    chmod 700 calendar
fi

# Check if token file exists
TOKEN_FILE="/root/clawd/skills/calendar/token.pickle"
if [ ! -f "$TOKEN_FILE" ]; then
    echo -e "${YELLOW}🔑 Google Calendar API setup:${NC}"
    echo "1. Go to Google Cloud Console"
    echo "2. Create a new project"
    echo "3. Enable Google Calendar API"
    echo "4. Create OAuth 2.0 credentials"
    echo "5. Download the credentials file"
    echo "6. Save it as '$TOKEN_FILE'"
    echo ""
    echo -e "${YELLOW}📋 Instructions for Google Calendar API:${NC}"
    echo "   - Visit: https://console.cloud.google.com/"
    echo "   - Create project: Webtop-Homework-Integration"
    echo "   - Enable API: Google Calendar API"
    echo "   - Create credentials: OAuth 2.0 Client IDs"
    echo "   - Application type: Desktop app"
    echo "   - Download JSON and save as token.pickle"
    echo ""
fi

# Create configuration template
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️ Creating .env template...${NC}"
    cat > .env << 'EOF'
# Student credentials (username:password format)
STUDENT_CREDENTIALS=REDACTED_STUDENT_1:REDACTED_PASSWORD_1,REDACTED_STUDENT_2:REDACTED_PASSWORD_2

# WhatsApp settings
WHATSAPP_GROUP_JID=REDACTED_GROUP_ID@g.us
WHATSAPP_TARGET=REDACTED_PHONE

# Calendar settings
GOOGLE_TOKEN_FILE=/root/clawd/skills/calendar/token.pickle
GOOGLE_CALENDAR_ID=REDACTED_EMAIL

# Monitoring settings
EVENING_HOUR=18
MONITOR_INTERVAL=3600
TIMEZONE=Asia/Jerusalem

# Paths
WEBTOP_DIR=/root/clawd/skills/webtop-skill
LOG_FILE=/tmp/homework_monitor.log
EOF
    chmod 600 .env
fi

# Create students data template if it doesn't exist
if [ ! -f "students_data.json" ]; then
    echo -e "${YELLOW}👥 Creating students data template...${NC}"
    cat > students_data.json << 'EOF'
{
  "students": [
    {
      "name": "GENERIC_STUDENT_1",
      "username": "REDACTED_STUDENT_1",
      "password": "REDACTED_PASSWORD_1"
    },
    {
      "name": "GENERIC_STUDENT_2",
      "username": "REDACTED_STUDENT_2", 
      "password": "REDACTED_PASSWORD_2"
    }
  ]
}
EOF
fi

# Create systemd service file for automation
echo -e "${YELLOW}⚙️ Creating systemd service...${NC}"
cat > homework-monitor.service << 'EOF'
[Unit]
Description=Homework Monitor Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/clawd/skills/webtop-skill
ExecStart=/usr/bin/python3 /root/clawd/skills/webtop-skill/homework_monitor.py
Restart=always
RestartSec=30
Environment=PYTHONPATH=/root/clawd/skills/webtop-skill

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Configure Google Calendar API (if not done already)"
echo "2. Update .env with your student credentials"
echo "3. Test the basic functionality:"
echo "   python3 webtop.py homework <username> <password>"
echo "4. Set up cron jobs for automation:"
echo "   - Daily homework summary"
echo "   - Calendar cleanup"
echo "   - Continuous monitoring"
echo ""
echo -e "${YELLOW}📖 Documentation:${NC}"
echo "   See SKILL.md for complete documentation"
echo "   Check the troubleshooting section for common issues"
echo ""
echo -e "${GREEN}🎉 Webtop Homework Skill is ready to use!${NC}"