#!/bin/bash

# BizBooks Backup Scheduler
# This script helps you schedule automatic daily backups at 11:00 AM IST

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_manager.py"
PYTHON_PATH=$(which python3)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}BizBooks Backup Scheduler${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This script is for macOS. For Linux, see setup_linux_cron.sh${NC}"
    exit 1
fi

# Check if python3 is available
if [ -z "$PYTHON_PATH" ]; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3 first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found: $PYTHON_PATH${NC}"

# Load environment variables from config.env if exists
CONFIG_FILE="$SCRIPT_DIR/config.env"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ Loading configuration from config.env${NC}"
    export $(cat "$CONFIG_FILE" | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  config.env not found. Please create it from config.env.example${NC}"
    echo -e "${YELLOW}   Copy: cp config.env.example config.env${NC}"
    echo -e "${YELLOW}   Edit: nano config.env (add your DATABASE_URL)${NC}"
    exit 1
fi

# Create backup directory if it doesn't exist
BACKUP_DIR="${BACKUP_DIR:-/Users/rishjain/Downloads/bizbooks/backup}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup directory: $BACKUP_DIR${NC}"

# Create wrapper script that loads environment
WRAPPER_SCRIPT="$SCRIPT_DIR/run_backup.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Auto-generated wrapper script for BizBooks backup
# Loads environment variables and runs backup

# Load environment variables
export \$(cat "$CONFIG_FILE" | grep -v '^#' | xargs)

# Run backup
$PYTHON_PATH "$BACKUP_SCRIPT"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✅ Created wrapper script: $WRAPPER_SCRIPT${NC}"

# Create LaunchAgent plist for macOS (better than cron)
PLIST_NAME="com.bizbooks.backup"
PLIST_FILE="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

echo ""
echo -e "${BLUE}Creating LaunchAgent for automatic backups...${NC}"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$WRAPPER_SCRIPT</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>11</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$BACKUP_DIR/scheduler.log</string>
    
    <key>StandardErrorPath</key>
    <string>$BACKUP_DIR/scheduler_error.log</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo -e "${GREEN}✅ Created LaunchAgent: $PLIST_FILE${NC}"

# Load the LaunchAgent
launchctl unload "$PLIST_FILE" 2>/dev/null  # Unload if already loaded
launchctl load "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ LaunchAgent loaded successfully!${NC}"
    echo ""
    echo -e "${GREEN}🎉 Backup scheduled successfully!${NC}"
    echo -e "${BLUE}   ⏰ Daily backup at: 11:00 AM IST${NC}"
    echo -e "${BLUE}   📁 Backup location: $BACKUP_DIR${NC}"
    echo -e "${BLUE}   📝 Logs: $BACKUP_DIR/backup.log${NC}"
    echo ""
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo -e "   Test backup now:  $PYTHON_PATH $BACKUP_SCRIPT"
    echo -e "   View logs:        tail -f $BACKUP_DIR/backup.log"
    echo -e "   Unschedule:       launchctl unload $PLIST_FILE"
    echo -e "   Re-schedule:      launchctl load $PLIST_FILE"
    echo ""
else
    echo -e "${RED}❌ Failed to load LaunchAgent${NC}"
    exit 1
fi

echo -e "${BLUE}======================================${NC}"

