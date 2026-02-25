#!/bin/bash
TEXT="$1"
OUTPUT="${2:-/tmp/tts_whatsapp.ogg}"

export GOOGLE_API_KEY="REDACTED_GOOGLE_API_KEY"
cd ~/.openclaw/skills/google-speech

python3 hebrew_speech.py tts "$TEXT" -o /tmp/tts_temp.mp3 --voice he-IL-Wavenet-A 2>/dev/null

ffmpeg -i /tmp/tts_temp.mp3 -c:a libopus -b:a 32k -application voip "$OUTPUT" -y 2>/dev/null

echo "$OUTPUT"
