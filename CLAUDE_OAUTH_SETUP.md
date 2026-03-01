# Claude OAuth Setup for OpenClaw

## Problem Summary

`sk-ant-oat01-` tokens from the `claude` CLI are short-lived OAuth access tokens (~8 hours).
Simply pasting them via `openclaw models auth paste-token` stores a static copy that expires and breaks.

## Solution: Auto-Refreshing OAuth Profile

OpenClaw supports a proper `oauth` profile type with automatic token refresh.
The profile `anthropic:claude-cli` is configured to use the Claude CLI's refresh token,
so it refreshes automatically before expiry — no manual action needed.

---

## How It Works

### Token Flow
1. `~/.claude/.credentials.json` — Claude Code's credentials (access + refresh tokens)
2. `/root/.openclaw/agents/main/agent/auth-profiles.json` — OpenClaw stores `anthropic:claude-cli` OAuth profile here
3. OpenClaw calls `https://console.anthropic.com/v1/oauth/token` to refresh before expiry

### Refresh Endpoint
```
POST https://console.anthropic.com/v1/oauth/token
{
  "grant_type": "refresh_token",
  "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
  "refresh_token": "<current refresh token>"
}
```

---

## Files Modified

| File | Change |
|------|--------|
| `~/.claude/.credentials.json` | Updated access + refresh tokens after manual refresh |
| `/root/.openclaw/agents/main/agent/auth-profiles.json` | Added `anthropic:claude-cli` OAuth profile |
| `/root/.openclaw/openclaw.json` | Added `anthropic:claude-cli` to `auth.profiles` |

---

## Token Refresh (Manual)

Run this when you need to force-refresh the token (e.g. after a long server downtime):

```bash
CLIENT_ID="9d1c250a-e61b-44d9-88ed-5944d1962f5e"
REFRESH_TOKEN=$(python3 -c "
import json
with open('/root/.claude/.credentials.json') as f:
    d = json.load(f)
print(d['claudeAiOauth']['refreshToken'])
")

RESPONSE=$(curl -s -X POST https://console.anthropic.com/v1/oauth/token \
  -H "Content-Type: application/json" \
  -d "{\"grant_type\":\"refresh_token\",\"client_id\":\"$CLIENT_ID\",\"refresh_token\":\"$REFRESH_TOKEN\"}")

echo "$RESPONSE" | python3 -c "
import json, sys, time
d = json.load(sys.stdin)
new_access = d['access_token']
new_refresh = d['refresh_token']
expires_at = int(time.time() * 1000) + (d['expires_in'] - 300) * 1000

# Update Claude CLI credentials
with open('/root/.claude/.credentials.json') as f:
    creds = json.load(f)
creds['claudeAiOauth']['accessToken'] = new_access
creds['claudeAiOauth']['refreshToken'] = new_refresh
creds['claudeAiOauth']['expiresAt'] = expires_at
with open('/root/.claude/.credentials.json', 'w') as f:
    json.dump(creds, f, indent=2)

# Update OpenClaw auth-profiles
with open('/root/.openclaw/agents/main/agent/auth-profiles.json') as f:
    profiles = json.load(f)
profiles['profiles']['anthropic:claude-cli'] = {
    'type': 'oauth', 'provider': 'anthropic',
    'access': new_access, 'refresh': new_refresh, 'expires': expires_at
}
with open('/root/.openclaw/agents/main/agent/auth-profiles.json', 'w') as f:
    json.dump(profiles, f, indent=2)

print(f'Refreshed. New expiry: {expires_at}')
"
```

---

## Switching Models in the Bot

**Recommended (via WhatsApp chat):**
```
/model anthropic/claude-sonnet-4-6   ← switch to Claude
/model zai/glm-4.7                   ← switch back to GLM
```

**Default model:** `zai/glm-4.7` (stable, free, always works)
**Claude model:** `anthropic/claude-sonnet-4-6` (requires valid OAuth)

---

## Common Issues & Fixes

### Bot stops responding after model switch via Nerve UI
The Nerve UI writes `modelOverride` + `authProfileOverride` into `sessions.json`.
If the model override points to an invalid token, all messages fail silently.

**Fix:**
```bash
systemctl stop openclaw-gateway

python3 -c "
import json
path = '/root/.openclaw/agents/main/sessions/sessions.json'
with open(path) as f: d = json.load(f)
key = 'agent:main:whatsapp:direct:+972525173322'
entry = d.get(key, {})
for field in ['modelOverride','providerOverride','authProfileOverride','modelProvider','model','provider']:
    entry.pop(field, None)
d[key] = entry
with open(path,'w') as f: json.dump(d, f)
print('overrides cleared')
"

systemctl start openclaw-gateway
```

### 401 Invalid bearer token
Token expired or was truncated during paste. Run the manual refresh script above.

### 403 OAuth authentication is currently not allowed
Old/expired token from a previous Claude Code session is stored in auth-profiles.json.
The `anthropic:claude-cli` OAuth profile (not `anthropic:default` or `anthropic:manual`) must be used.

---

## Do NOT use `paste-token` for Anthropic
`openclaw models auth paste-token --provider anthropic` stores a **static** token with no refresh.
These tokens expire in ~8 hours and then the bot silently fails.
Use the `anthropic:claude-cli` OAuth profile (already configured) instead.
