#!/bin/bash
# Bizbooks.co.in Management Script
# Quick commands to start/stop/restart your application

case "$1" in
    start)
        echo "🚀 Starting BizBooks..."
        
        # Start Flask app
        cd /Users/rishjain/Downloads/attendence_app/modular_app
        source ../venv/bin/activate
        python3 app.py > app.log 2>&1 &
        echo "✅ Flask app started (port 5001)"
        
        # Wait for app to start
        sleep 3
        
        # Start Cloudflare tunnel
        cloudflared tunnel run bizbooks-attendance > /tmp/bizbooks-tunnel.log 2>&1 &
        echo "✅ Cloudflare tunnel started"
        
        sleep 3
        echo ""
        echo "🌐 Your URLs are live:"
        echo "   https://bizbooks.co.in"
        echo "   https://bizbooks.co.in/attendance"
        echo "   https://bizbooks.co.in/admin/login"
        ;;
    
    stop)
        echo "🛑 Stopping BizBooks..."
        
        # Stop Flask app
        lsof -ti:5001 | xargs kill -9 2>/dev/null
        echo "✅ Flask app stopped"
        
        # Stop Cloudflare tunnel
        pkill -f "cloudflared tunnel run bizbooks-attendance"
        echo "✅ Cloudflare tunnel stopped"
        ;;
    
    restart)
        echo "🔄 Restarting BizBooks..."
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        echo "📊 BizBooks Status:"
        echo ""
        
        # Check Flask app
        if lsof -ti:5001 > /dev/null 2>&1; then
            echo "✅ Flask app: RUNNING (port 5001)"
        else
            echo "❌ Flask app: STOPPED"
        fi
        
        # Check Cloudflare tunnel
        if pgrep -f "cloudflared tunnel run bizbooks-attendance" > /dev/null 2>&1; then
            echo "✅ Cloudflare tunnel: RUNNING"
            echo ""
            echo "🌐 Live URLs:"
            echo "   https://bizbooks.co.in"
            echo "   https://bizbooks.co.in/attendance"
            echo "   https://bizbooks.co.in/admin/login"
        else
            echo "❌ Cloudflare tunnel: STOPPED"
        fi
        
        echo ""
        echo "📋 Recent app logs:"
        tail -5 /Users/rishjain/Downloads/attendence_app/modular_app/app.log 2>/dev/null || echo "   No logs found"
        ;;
    
    logs)
        echo "📋 Viewing BizBooks Logs (Ctrl+C to exit)..."
        echo ""
        tail -f /Users/rishjain/Downloads/attendence_app/modular_app/app.log
        ;;
    
    tunnel-logs)
        echo "📋 Viewing Cloudflare Tunnel Logs (Ctrl+C to exit)..."
        echo ""
        tail -f /tmp/bizbooks-tunnel.log
        ;;
    
    urls)
        echo "🌐 BizBooks URLs:"
        echo ""
        echo "👥 Employee Attendance:"
        echo "   https://bizbooks.co.in/attendance"
        echo ""
        echo "👤 Admin Dashboard:"
        echo "   https://bizbooks.co.in/admin/login"
        echo "   (Username: admin, Password: admin123)"
        echo ""
        echo "📦 Inventory:"
        echo "   https://bizbooks.co.in/admin/inventory"
        echo ""
        echo "🏠 Main Site:"
        echo "   https://bizbooks.co.in"
        ;;
    
    *)
        echo "🎯 BizBooks Management Commands:"
        echo ""
        echo "  ./manage_bizbooks.sh start         - Start all services"
        echo "  ./manage_bizbooks.sh stop          - Stop all services"
        echo "  ./manage_bizbooks.sh restart       - Restart all services"
        echo "  ./manage_bizbooks.sh status        - Check service status"
        echo "  ./manage_bizbooks.sh logs          - View app logs"
        echo "  ./manage_bizbooks.sh tunnel-logs   - View tunnel logs"
        echo "  ./manage_bizbooks.sh urls          - Show all URLs"
        echo ""
        echo "Example: ./manage_bizbooks.sh start"
        ;;
esac

