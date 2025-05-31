#!/usr/bin/env python3
"""
migrate_logs_to_redis.py

Migration script to move log files from filesystem to Redis streams
for better performance and real-time access.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from utils.redis_streams import RedisStreamsManager

# NOTE: Google Drive is now used for backup instead of GCS. Remove or update any GCS-specific logic below.

def migrate_log_store_json():
    """Migrate log_store.json to system_logs stream."""
    log_file = "/Users/rebeccamorris/Desktop/anchorwork/logs/log_store.json"
    
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return 0
        
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        redis_manager = RedisStreamsManager()
        migrated_count = 0
        
        for log_entry in logs:
            # Map log entry to system log format
            level = "info"  # Default level for test logs
            message = f"[{log_entry.get('author', 'unknown')}] {log_entry.get('action', 'unknown_action')}"
            details = {
                "target": log_entry.get('target', ''),
                "content": log_entry.get('content', ''),
                "original_timestamp": log_entry.get('timestamp', '')
            }
            
            entry_id = redis_manager.publish_system_log(level, message, details)
            if entry_id:
                migrated_count += 1
        
        print(f"Migrated {migrated_count} entries from log_store.json to system_logs stream")
        return migrated_count
        
    except Exception as e:
        print(f"Error migrating log_store.json: {e}")
        return 0

def migrate_test_agent_logs():
    """Migrate test_agent_log.jsonl to user_interactions stream."""
    log_file = "/Users/rebeccamorris/Desktop/anchorwork/logs/test_agent_log.jsonl"
    
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return 0
        
    try:
        redis_manager = RedisStreamsManager()
        migrated_count = 0
        
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    log_entry = json.loads(line)
                    
                    # Map to user interaction format
                    interaction_data = {
                        "prompt": log_entry.get('prompt', ''),
                        "response": log_entry.get('response', ''),
                        "mood": log_entry.get('mood', ''),
                        "tags": log_entry.get('tags', []),
                        "original_timestamp": log_entry.get('timestamp', '')
                    }
                    
                    entry_id = redis_manager.publish_user_interaction(
                        user_id="test_agent",
                        interaction_type="conversation",
                        data=interaction_data
                    )
                    if entry_id:
                        migrated_count += 1
        
        print(f"Migrated {migrated_count} entries from test_agent_log.jsonl to user_interactions stream")
        return migrated_count
        
    except Exception as e:
        print(f"Error migrating test_agent_log.jsonl: {e}")
        return 0

def migrate_test_streams_agent_logs():
    """Migrate test_streams_agent_log.jsonl to agent_events stream."""
    log_file = "/Users/rebeccamorris/Desktop/anchorwork/logs/test_streams_agent_log.jsonl"
    
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return 0
        
    try:
        redis_manager = RedisStreamsManager()
        migrated_count = 0
        
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    log_entry = json.loads(line)
                    
                    # Map to agent event format
                    event_data = {
                        "prompt": log_entry.get('prompt', ''),
                        "response": log_entry.get('response', ''),
                        "mood": log_entry.get('mood', ''),
                        "tags": log_entry.get('tags', []),
                        "original_timestamp": log_entry.get('timestamp', '')
                    }
                    
                    entry_id = redis_manager.publish_agent_event(
                        agent_id="test_streams_agent",
                        event_type="conversation",
                        data=event_data
                    )
                    if entry_id:
                        migrated_count += 1
        
        print(f"Migrated {migrated_count} entries from test_streams_agent_log.jsonl to agent_events stream")
        return migrated_count
        
    except Exception as e:
        print(f"Error migrating test_streams_agent_log.jsonl: {e}")
        return 0

def backup_files_before_deletion():
    """Create a backup of files before deleting them and copy to redis_uploads/shared."""
    backup_dir = "/Users/rebeccamorris/Desktop/anchorwork/logs/backup"
    shared_dir = "/Users/rebeccamorris/Desktop/anchorwork/redis_uploads/shared"
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(shared_dir, exist_ok=True)
    
    files_to_backup = [
        "log_store.json",
        "test_agent_log.jsonl", 
        "test_streams_agent_log.jsonl",
        "codex.json"
    ]
    
    for filename in files_to_backup:
        source_path = f"/Users/rebeccamorris/Desktop/anchorwork/logs/{filename}"
        backup_path = f"{backup_dir}/{filename}.backup"
        shared_path = f"{shared_dir}/{filename}.backup"
        
        if os.path.exists(source_path):
            try:
                # Create backup in logs/backup
                with open(source_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                print(f"Backed up {filename} to {backup_path}")
                
                # Also copy to redis_uploads/shared for reference
                with open(source_path, 'r') as src, open(shared_path, 'w') as dst:
                    dst.write(src.read())
                print(f"Copied {filename} to redis_uploads/shared/{filename}.backup")
                
            except Exception as e:
                print(f"Error backing up {filename}: {e}")

def main():
    """Main migration function."""
    print("Starting log migration to Redis...")
    print("="*50)
    
    # Debug: Check if we can import Redis
    try:
        redis_manager = RedisStreamsManager()
        print("✓ Redis connection established")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return
    
    # Create backups first
    print("Creating backups...")
    backup_files_before_deletion()
    print()
    
    # Skip GCS backup during testing phase
    print("Skipping GCS backup during testing phase...")
    print("Will enable full backups once Redis migration is confirmed working")
    print()
    
    # Migrate files
    total_migrated = 0
    
    total_migrated += migrate_log_store_json()
    total_migrated += migrate_test_agent_logs() 
    total_migrated += migrate_test_streams_agent_logs()
    
    print()
    print("="*50)
    print(f"Migration complete! Total entries migrated: {total_migrated}")
    print()
    print("Files migrated to Redis streams:")
    print("- log_store.json → system_logs stream")
    print("- test_agent_log.jsonl → user_interactions stream")
    print("- test_streams_agent_log.jsonl → agent_events stream")
    print()
    print("Files to keep as-is:")
    print("- session_log.md (markdown documentation)")
    print("- codex.json (currently empty, will use Redis going forward)")
    print("- crew_history.jsonl (currently empty, will use Redis going forward)")
    print()
    print("Backups created in:")
    print("- logs/backup/ directory")
    print("- redis_uploads/shared/ directory (for shared access)")
    # if GCS_AVAILABLE:
    #     print("- Google Cloud Storage (if configured)")
    # else:
    #     print("- Install google-cloud-storage for GCS backups: pip install google-cloud-storage")

if __name__ == "__main__":
    main()
