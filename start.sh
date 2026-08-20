#!/bin/bash
# Render start wrapper for MARKMWEHEHETOOL bot
# - Unbuffered output so Render ALWAYS sees logs (fixes missing output issue)
# - Exec directly into Python so the Telegram bot PID is PID 1 and receives
#   SIGTERM from Render immediately (no wrapper in between to hide signals)

echo "=== RENDER START WRAPPER BEGIN ==="
echo "Render PORT env: ${PORT:-NOT SET}"
echo "Date: $(date -u)"
echo "=== RENDER START WRAPPER END ==="

# exec replaces this shell with the Python process — clean signal handling,
# no orphaned children, and Render's 143/SIGTERM goes straight to the bot.
exec python3 -u bot.py
