#!/bin/bash
# Stop the attendance app and tunnel

echo "🛑 Stopping Attendance App & Tunnel"
echo "===================================="

# Stop screen session
if screen -list | grep -q "attendance_app"; then
    screen -X -S attendance_app quit
    echo "✅ Screen session 'attendance_app' stopped"
else
    echo "⚠️  No screen session found"
fi

# Stop any running Flask app on port 5001
echo "🔍 Stopping Flask app on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null
echo "✅ Flask app stopped"

# Stop any cloudflared processes
echo "🔍 Stopping Cloudflare tunnels..."
pkill -f cloudflared 2>/dev/null
echo "✅ Cloudflare tunnel stopped"

echo ""
echo "✨ All services stopped!"

