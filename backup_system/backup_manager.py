#!/usr/bin/env python3
"""
BizBooks Database Backup Manager
Automatically backs up PostgreSQL database from Supabase to local system

Features:
- Full database dump
- Compression (saves space)
- Keeps last 30 days of backups
- Logs every operation
- Email alerts on failure (optional)

Schedule: Daily at 11:00 AM IST
Location: /Users/rishjain/Downloads/bizbooks/backup
"""

import os
import subprocess
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Configuration
BACKUP_DIR = "/Users/rishjain/Downloads/bizbooks/backup"
LOG_FILE = os.path.join(BACKUP_DIR, "backup.log")
RETENTION_DAYS = 30  # Keep backups for 30 days

# Supabase Database Connection (from your environment variables)
DB_HOST = os.getenv("DATABASE_URL", "").split("@")[1].split("/")[0] if os.getenv("DATABASE_URL") else ""
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")  # You'll need to set this

# Email alerts (optional)
SEND_EMAIL_ALERTS = False  # Set to True to enable email alerts
ALERT_EMAIL = "rishi.jain@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"


def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")


def send_alert_email(subject, body):
    """Send email alert on backup failure"""
    if not SEND_EMAIL_ALERTS:
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = f"BizBooks Backup: {subject}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        log("✅ Alert email sent successfully")
    except Exception as e:
        log(f"⚠️  Failed to send alert email: {e}")


def get_db_connection_string():
    """Get database connection string from environment or construct it"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Extract from DATABASE_URL
        return database_url
    else:
        # Construct from individual parts
        return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


def create_backup():
    """Create database backup using pg_dump"""
    log("🔄 Starting backup process...")
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"bizbooks_backup_{timestamp}.sql"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    compressed_path = f"{backup_path}.gz"
    
    try:
        # Get database connection details
        db_url = get_db_connection_string()
        
        if not db_url:
            raise Exception("DATABASE_URL not found. Please set it in environment variables.")
        
        log(f"📊 Creating backup: {backup_filename}")
        
        # Run pg_dump command
        # Option 1: If DATABASE_URL is available
        if os.getenv("DATABASE_URL"):
            cmd = [
                "pg_dump",
                "--no-owner",
                "--no-acl",
                "--clean",
                "--if-exists",
                db_url
            ]
        else:
            # Option 2: If using individual connection details
            cmd = [
                "pg_dump",
                "--host", DB_HOST,
                "--port", "5432",
                "--username", DB_USER,
                "--dbname", DB_NAME,
                "--no-owner",
                "--no-acl",
                "--clean",
                "--if-exists"
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = DB_PASSWORD
        
        # Execute pg_dump
        with open(backup_path, "w") as f:
            if os.getenv("DATABASE_URL"):
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            else:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env)
        
        if result.returncode != 0:
            raise Exception(f"pg_dump failed: {result.stderr}")
        
        # Get file size
        file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
        log(f"✅ Backup created: {backup_filename} ({file_size:.2f} MB)")
        
        # Compress the backup
        log("🗜️  Compressing backup...")
        compress_cmd = ["gzip", backup_path]
        subprocess.run(compress_cmd, check=True)
        
        compressed_size = os.path.getsize(compressed_path) / (1024 * 1024)  # MB
        compression_ratio = (1 - compressed_size / file_size) * 100
        log(f"✅ Backup compressed: {compressed_size:.2f} MB (saved {compression_ratio:.1f}%)")
        
        # Cleanup old backups
        cleanup_old_backups()
        
        log("✅ Backup process completed successfully!")
        return True
        
    except FileNotFoundError:
        error_msg = "❌ pg_dump not found. Please install PostgreSQL client tools."
        log(error_msg)
        log("   Install with: brew install postgresql (macOS)")
        send_alert_email("Backup Failed", error_msg)
        return False
        
    except Exception as e:
        error_msg = f"❌ Backup failed: {str(e)}"
        log(error_msg)
        send_alert_email("Backup Failed", error_msg)
        return False


def cleanup_old_backups():
    """Remove backups older than RETENTION_DAYS"""
    log(f"🧹 Cleaning up backups older than {RETENTION_DAYS} days...")
    
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_count = 0
    
    try:
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("bizbooks_backup_") and filename.endswith(".sql.gz"):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
                    log(f"  🗑️  Deleted old backup: {filename}")
        
        if deleted_count > 0:
            log(f"✅ Cleaned up {deleted_count} old backup(s)")
        else:
            log("✅ No old backups to clean up")
            
    except Exception as e:
        log(f"⚠️  Cleanup warning: {e}")


def list_backups():
    """List all available backups"""
    log("\n📋 Available backups:")
    
    try:
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("bizbooks_backup_") and filename.endswith(".sql.gz"):
                file_path = os.path.join(BACKUP_DIR, filename)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                backups.append((filename, file_size, file_time))
        
        if not backups:
            log("  No backups found")
            return
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x[2], reverse=True)
        
        for filename, size, time in backups:
            log(f"  📦 {filename} - {size:.2f} MB - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        log(f"\n✅ Total backups: {len(backups)}")
        
    except Exception as e:
        log(f"❌ Failed to list backups: {e}")


def check_prerequisites():
    """Check if all required tools are installed"""
    log("🔍 Checking prerequisites...")
    
    # Check if pg_dump is available
    try:
        result = subprocess.run(["pg_dump", "--version"], capture_output=True, text=True)
        log(f"✅ PostgreSQL client found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        log("❌ pg_dump not found!")
        log("   Please install PostgreSQL client:")
        log("   macOS: brew install postgresql")
        log("   Ubuntu: sudo apt-get install postgresql-client")
        log("   Windows: Download from https://www.postgresql.org/download/")
        return False


if __name__ == "__main__":
    log("=" * 60)
    log("🚀 BizBooks Database Backup Manager")
    log("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Run backup
    success = create_backup()
    
    # List all backups
    list_backups()
    
    log("=" * 60)
    
    sys.exit(0 if success else 1)

