#!/bin/bash
# Start attendance app and tunnel in screen session
# You can disconnect terminal after running this!

echo "🚀 Starting Attendance App in Screen Session"
echo "=============================================="

# Check if screen session already exists
if screen -list | grep -q "attendance_app"; then
    echo "⚠️  Session 'attendance_app' already exists!"
    echo "Options:"
    echo "  1. Reattach: screen -r attendance_app"
    echo "  2. Kill old: screen -X -S attendance_app quit"
    exit 1
fi

# Start new screen session
screen -dmS attendance_app bash -c "
    cd /Users/rishjain/Downloads/attendence_app/modular_app
    source ../venv/bin/activate
    
    echo '🔷 Starting Flask App...'
    python3 app.py > app.log 2>&1 &
    APP_PID=\$!
    
    echo '⏳ Waiting for app to start...'
    sleep 5
    
    echo '🌍 Starting Cloudflare Tunnel...'
    python3 start_fixed_tunnel.py
    
    # If tunnel stops, stop app too
    kill \$APP_PID 2>/dev/null
"

sleep 3

echo ""
echo "✅ Started in background!"
echo ""
echo "📋 Useful Commands:"
echo "  • View running sessions: screen -ls"
echo "  • Attach to session:     screen -r attendance_app"
echo "  • Detach from session:   Press Ctrl+A then D"
echo "  • Stop everything:       screen -X -S attendance_app quit"
echo ""
echo "🔍 Checking tunnel URL..."
sleep 8

if [ -f current_tunnel_url.txt ]; then
    echo ""
    echo "🌍 PUBLIC URL:"
    cat current_tunnel_url.txt
else
    echo "⏳ URL file not created yet. Wait a few seconds and check:"
    echo "   cat /Users/rishjain/Downloads/attendence_app/modular_app/current_tunnel_url.txt"
fi

echo ""
echo "✨ You can now close this terminal - everything keeps running!"

