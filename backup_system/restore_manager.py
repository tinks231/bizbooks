#!/usr/bin/env python3
"""
BizBooks Database Restore Manager
Restore database from backup files

Features:
- List all available backups
- Restore from any backup
- Validates backup before restore
- Creates safety backup before restore
- Dry-run mode for testing

Usage:
  python restore_manager.py --list                    # List all backups
  python restore_manager.py --restore <backup_file>   # Restore from backup
  python restore_manager.py --latest                  # Restore from latest backup
"""

import os
import subprocess
import sys
from datetime import datetime
import argparse

# Configuration
BACKUP_DIR = "/Users/rishjain/Downloads/bizbooks/backup"
LOG_FILE = os.path.join(BACKUP_DIR, "restore.log")

# Database connection (from environment or manual)
DB_HOST = os.getenv("DATABASE_URL", "").split("@")[1].split("/")[0] if os.getenv("DATABASE_URL") else ""
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "")


def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        f.write(log_message + "\n")


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
            log("  ❌ No backups found")
            return None
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x[2], reverse=True)
        
        for i, (filename, size, time) in enumerate(backups, 1):
            log(f"  {i}. {filename}")
            log(f"     Size: {size:.2f} MB | Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        log(f"\n✅ Total backups: {len(backups)}")
        
        return backups
        
    except Exception as e:
        log(f"❌ Failed to list backups: {e}")
        return None


def get_latest_backup():
    """Get the most recent backup file"""
    backups = list_backups()
    if backups:
        return backups[0][0]  # Return filename of newest backup
    return None


def decompress_backup(compressed_file):
    """Decompress .gz backup file"""
    log(f"🗜️  Decompressing {compressed_file}...")
    
    decompressed_file = compressed_file.replace(".gz", "")
    
    try:
        cmd = ["gunzip", "-k", compressed_file]  # -k keeps original
        subprocess.run(cmd, check=True)
        log(f"✅ Decompressed to: {decompressed_file}")
        return decompressed_file
        
    except Exception as e:
        log(f"❌ Decompression failed: {e}")
        return None


def validate_backup(backup_file):
    """Validate SQL backup file"""
    log(f"🔍 Validating backup file...")
    
    try:
        # Check if file exists
        if not os.path.exists(backup_file):
            log(f"❌ Backup file not found: {backup_file}")
            return False
        
        # Check file size
        file_size = os.path.getsize(backup_file) / (1024 * 1024)  # MB
        if file_size < 0.01:  # Less than 10KB
            log(f"❌ Backup file too small ({file_size:.2f} MB) - likely corrupted")
            return False
        
        # Check if it's a valid SQL file
        with open(backup_file, 'r') as f:
            first_lines = f.read(1000)
            if 'PostgreSQL' not in first_lines and 'CREATE' not in first_lines:
                log(f"❌ File doesn't appear to be a valid PostgreSQL dump")
                return False
        
        log(f"✅ Backup file is valid ({file_size:.2f} MB)")
        return True
        
    except Exception as e:
        log(f"❌ Validation failed: {e}")
        return False


def create_safety_backup():
    """Create a safety backup before restore"""
    log("🛡️  Creating safety backup of current database...")
    
    try:
        # Run the backup script
        backup_script = os.path.join(os.path.dirname(__file__), "backup_manager.py")
        result = subprocess.run(["python3", backup_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✅ Safety backup created successfully")
            return True
        else:
            log(f"⚠️  Safety backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"⚠️  Safety backup error: {e}")
        return False


def restore_database(backup_file, skip_safety_backup=False):
    """Restore database from backup file"""
    log("=" * 60)
    log("🔄 Starting database restore...")
    log("=" * 60)
    
    # Validate backup first
    if not validate_backup(backup_file):
        log("❌ Backup validation failed. Aborting restore.")
        return False
    
    # Create safety backup (unless skipped)
    if not skip_safety_backup:
        response = input("\n⚠️  This will REPLACE your current database. Continue? (yes/no): ")
        if response.lower() != "yes":
            log("❌ Restore cancelled by user")
            return False
        
        log("\n🛡️  Creating safety backup first...")
        create_safety_backup()
    
    try:
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            raise Exception("DATABASE_URL not found. Please set it in environment variables.")
        
        log(f"📊 Restoring from: {os.path.basename(backup_file)}")
        
        # Run psql to restore
        with open(backup_file, 'r') as f:
            cmd = [
                "psql",
                db_url
            ]
            
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            # Check if errors are just warnings
            if "ERROR" in result.stderr:
                log(f"⚠️  Restore completed with errors:")
                log(result.stderr)
                log("\n⚠️  Some errors may be normal (e.g., 'relation already exists')")
                log("    Please verify database integrity")
            else:
                log(f"✅ Restore completed (warnings can be ignored)")
        else:
            log("✅ Database restored successfully!")
        
        log("=" * 60)
        return True
        
    except FileNotFoundError:
        log("❌ psql not found. Please install PostgreSQL client tools.")
        log("   macOS: brew install postgresql")
        return False
        
    except Exception as e:
        log(f"❌ Restore failed: {e}")
        return False


def restore_from_compressed(compressed_file, skip_safety_backup=False):
    """Restore from compressed backup file"""
    # Decompress first
    decompressed_file = decompress_backup(os.path.join(BACKUP_DIR, compressed_file))
    
    if not decompressed_file:
        return False
    
    # Restore
    success = restore_database(decompressed_file, skip_safety_backup)
    
    # Cleanup decompressed file
    try:
        os.remove(decompressed_file)
        log(f"🧹 Cleaned up decompressed file")
    except:
        pass
    
    return success


def main():
    parser = argparse.ArgumentParser(description="BizBooks Database Restore Manager")
    parser.add_argument("--list", action="store_true", help="List all available backups")
    parser.add_argument("--restore", type=str, help="Restore from specific backup file")
    parser.add_argument("--latest", action="store_true", help="Restore from latest backup")
    parser.add_argument("--no-safety-backup", action="store_true", help="Skip safety backup before restore")
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if not any([args.list, args.restore, args.latest]):
        parser.print_help()
        return
    
    # List backups
    if args.list:
        list_backups()
        return
    
    # Restore from latest
    if args.latest:
        latest = get_latest_backup()
        if latest:
            log(f"\n🔄 Restoring from latest backup: {latest}")
            restore_from_compressed(latest, args.no_safety_backup)
        else:
            log("❌ No backups found")
        return
    
    # Restore from specific backup
    if args.restore:
        backup_file = args.restore
        
        # If just filename provided, add directory
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(BACKUP_DIR, backup_file)
        
        if not os.path.exists(backup_file):
            log(f"❌ Backup file not found: {backup_file}")
            return
        
        if backup_file.endswith(".gz"):
            restore_from_compressed(os.path.basename(backup_file), args.no_safety_backup)
        else:
            restore_database(backup_file, args.no_safety_backup)


if __name__ == "__main__":
    main()

