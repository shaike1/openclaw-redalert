# OpenClaw-3CX Voice v2 POC Guide

## 🎯 Overview

This is a **parallel deployment POC** for testing the new Voice v2 architecture without affecting the production v1 setup.

### What's New in v2?

1. **Dockerized Architecture** - All services in Docker containers
2. **Separate Voice Processor** - STT → LLM → TTS in dedicated container
3. **Redis State Management** - Call state and session tracking
4. **Monitoring Built-in** - Prometheus metrics + Grafana dashboards
5. **No Downtime Deployment** - Run v2 alongside v1 for testing

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        3CX PBX                              │
│                   (pbx.right-api.com)                       │
└────────────────────┬────────────────────────────────────────┘
                     │ SIP Extension (voice-bot-v2)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              voice-gateway-v2 (SIP/3CX)                     │
│         • Receive incoming calls                            │
│         • Audio stream handling                             │
│         • Forward to processor                              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP webhook
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           voice-processor-v2 (AI Pipeline)                  │
│         • OpenAI Whisper (STT)                              │
│         • Claude AI (Conversation)                          │
│         • ElevenLabs (TTS)                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                voice-redis-v2 (State)                       │
│         • Call sessions                                     │
│         • Conversation context                              │
│         • Temporary data                                    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

1. **Docker & Docker Compose** installed
2. **API Keys:**
   - OpenAI API (Whisper STT)
   - Anthropic API (Claude AI)
   - ElevenLabs API (TTS)
3. **3CX Extension** configured (e.g., extension 999)
4. **Ports Available:**
   - 5060/UDP (SIP)
   - 8081/TCP (Voice Processor API)
   - 6380/TCP (Redis)
   - 9091/TCP (Prometheus)

## 🚀 Quick Start

### Step 1: Configure Environment

```bash
cd /root/.openclaw/workspace/skills/claude-phone

# Copy example env file
cp .env.voice-v2.example .env.voice-v2

# Edit with your actual values
nano .env.voice-v2
```

**Required variables:**
```bash
# SIP Configuration
SIP_SERVER=pbx.right-api.com
SIP_USERNAME=voice-bot-v2
SIP_PASSWORD=your_secure_password

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=xi-...

# Voice Configuration
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel voice
LANGUAGE=he  # Hebrew
```

### Step 2: Deploy

```bash
# Run deployment script
./voice-v2-deploy.sh
```

This will:
- ✅ Validate configuration
- ✅ Create necessary directories
- ✅ Build and start all containers
- ✅ Run health checks
- ✅ Show service status

### Step 3: Test

```bash
# Run test suite
./test-voice-v2.sh
```

Expected output:
```
🧪 OpenClaw-3CX Voice v2 Test Suite
=====================================

📡 Test 1: Voice Processor Health Check
   ✅ PASSED

📡 Test 2: Redis Connection
   ✅ PASSED

📡 Test 3: Container Health Status
   - voice-gateway-v2: healthy
   - voice-processor-v2: healthy
   - voice-redis-v2: healthy
   ✅ ALL PASSED
...
```

### Step 4: Configure 3CX

1. **Create new extension** in 3CX (e.g., 999)
2. **Set forward rule:**
   - Forward all calls to: `voice-bot-v2@pbx.right-api.com`
   - Or use SIP URI: `sip:voice-bot-v2@pbx.right-api.com`
3. **Test call:** Dial extension 999 from any phone

## 🔍 Monitoring

### Check Service Status

```bash
docker compose -f docker-compose.voice-v2.yml ps
```

### View Logs

```bash
# All services
docker compose -f docker-compose.voice-v2.yml logs -f

# Specific service
docker compose -f docker-compose.voice-v2.yml logs -f voice-processor
```

### Health Checks

```bash
# Voice Processor
curl http://localhost:8081/health

# Prometheus metrics
curl http://localhost:9091/metrics
```

### Grafana Dashboards

1. Access Grafana: `http://localhost:3000`
2. Add Prometheus data source: `http://prometheus:9091`
3. Import dashboards from `monitoring/dashboards/`

## 🧪 Testing Scenarios

### Test 1: Health Check
```bash
curl http://localhost:8081/health
```

### Test 2: Simple Call Flow
1. Call the 3CX extension
2. Speak in Hebrew
3. Verify AI responds
4. Check logs for flow

### Test 3: Concurrent Calls
1. Make multiple calls simultaneously
2. Verify Redis handles sessions
3. Check performance metrics

### Test 4: Long Conversation
1. Have a 5-minute conversation
2. Verify context maintained
3. Check Redis session data

## 🔧 Troubleshooting

### Container Not Starting

```bash
# Check logs
docker compose -f docker-compose.voice-v2.yml logs voice-gateway

# Common issues:
# - Port 5060 already in use (v1 running)
# - Missing environment variables
# - Invalid SIP credentials
```

### No Audio

```bash
# Check RTP ports
docker exec voice-gateway-v2 netstat -tlnp | grep RTP

# Verify audio forwarding
docker compose -f docker-compose.voice-v2.yml logs voice-processor | grep audio
```

### Redis Connection Failed

```bash
# Test Redis from processor
docker exec voice-processor-v2 ping voice-redis-v2

# Check Redis logs
docker compose -f docker-compose.voice-v2.yml logs redis
```

### API Key Errors

```bash
# Verify env vars loaded
docker exec voice-processor-v2 printenv | grep API_KEY

# Rebuild with new env
docker compose -f docker-compose.voice-v2.yml down
docker compose -f docker-compose.voice-v2.yml up -d
```

## 📊 Performance Tuning

### Redis Optimization

```yaml
# In docker-compose.voice-v2.yml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

### Voice Processor Scaling

```bash
# Scale to 2 instances
docker compose -f docker-compose.voice-v2.yml up -d --scale voice-processor=2
```

### Monitor Resources

```bash
# Container stats
docker stats voice-gateway-v2 voice-processor-v2 voice-redis-v2
```

## 🔄 Migration from v1 to v2

### Phase 1: Parallel Testing (Current)
- ✅ v1 continues handling production calls
- ✅ v2 runs on separate ports for testing
- ✅ Compare quality and performance

### Phase 2: Gradual Cutover
1. Point 10% of calls to v2
2. Monitor for 24-48 hours
3. Increase to 50%
4. Final cutover to 100%

### Phase 3: v1 Decommission
1. Stop v1 services
2. Repurpose ports if needed
3. Clean up v1 containers

## 🛑 Cleanup

### Stop v2 (Keep Data)
```bash
docker compose -f docker-compose.voice-v2.yml stop
```

### Stop v2 (Remove Containers)
```bash
docker compose -f docker-compose.voice-v2.yml down
```

### Complete Cleanup (Including Data)
```bash
docker compose -f docker-compose.voice-v2.yml down -v
docker volume rm voice-v2-redis-data voice-v2-prometheus-data
```

## 📝 Next Steps

1. **Build Docker Images** - Currently using placeholders
2. **Implement SIP Handler** - voice-gateway container
3. **Implement Voice Pipeline** - voice-processor container
4. **Add Call Recording** - Optional feature
5. **Add Analytics** - Conversation insights
6. **Add Multi-language** - Beyond Hebrew

## 🆘 Support

For issues or questions:
- Check logs: `docker compose -f docker-compose.voice-v2.yml logs -f`
- Test suite: `./test-voice-v2.sh`
- Status check: `docker compose -f docker-compose.voice-v2.yml ps`

## 📚 Documentation

- Migration Plan: `MIGRATION_PLAN.md`
- Original v1 Setup: `SKILL.md`
- 3CX Configuration: Contact your 3CX administrator

---

**Status:** 🟡 POC - Ready for Testing
**Last Updated:** 2026-02-27
**Version:** 2.0.0-POC
