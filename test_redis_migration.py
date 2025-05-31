#!/usr/bin/env python3
"""
test_redis_migration.py

Test script to verify that the log migration to Redis streams was successful
and that the data can be properly read back.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from utils.redis_streams import RedisStreamsManager

def test_system_logs():
    """Test reading from system_logs stream."""
    print("🔍 Testing system_logs stream...")
    redis_manager = RedisStreamsManager()
    
    try:
        # Read recent entries from system logs
        entries = redis_manager.read_stream("system_logs", count=5)
        
        print(f"✓ Found {len(entries)} entries in system_logs stream")
        
        if entries:
            print("📋 Sample entry:")
            latest_entry = entries[0]
            print(f"  ID: {latest_entry['id']}")
            print(f"  Level: {latest_entry.get('level', 'N/A')}")
            print(f"  Message: {latest_entry.get('message', 'N/A')[:50]}...")
        
        return len(entries)
        
    except Exception as e:
        print(f"✗ Error reading system_logs: {e}")
        return 0

def test_user_interactions():
    """Test reading from user_interactions stream."""
    print("\n🔍 Testing user_interactions stream...")
    redis_manager = RedisStreamsManager()
    
    try:
        # Read recent entries from user interactions
        entries = redis_manager.read_stream("user_interactions", count=5)
        
        print(f"✓ Found {len(entries)} entries in user_interactions stream")
        
        if entries:
            print("📋 Sample entry:")
            latest_entry = entries[0]
            print(f"  ID: {latest_entry['id']}")
            print(f"  User ID: {latest_entry.get('user_id', 'N/A')}")
            print(f"  Type: {latest_entry.get('interaction_type', 'N/A')}")
        
        return len(entries)
        
    except Exception as e:
        print(f"✗ Error reading user_interactions: {e}")
        return 0

def test_agent_events():
    """Test reading from agent_events stream."""
    print("\n🔍 Testing agent_events stream...")
    redis_manager = RedisStreamsManager()
    
    try:
        # Read recent entries from agent events
        entries = redis_manager.read_stream("agent_events", count=5)
        
        print(f"✓ Found {len(entries)} entries in agent_events stream")
        
        if entries:
            print("📋 Sample entry:")
            latest_entry = entries[0]
            print(f"  ID: {latest_entry['id']}")
            print(f"  Agent: {latest_entry.get('agent_id', 'N/A')}")
            print(f"  Event: {latest_entry.get('event_type', 'N/A')}")
        
        return len(entries)
        
    except Exception as e:
        print(f"✗ Error reading agent_events: {e}")
        return 0

def test_redis_connection():
    """Test basic Redis connection."""
    print("🔗 Testing Redis connection...")
    redis_manager = RedisStreamsManager()
    
    try:
        # Test basic Redis connection
        redis_manager.redis_client.ping()
        print("✓ Redis connection successful")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False

def test_stream_publishing():
    """Test publishing new events to streams."""
    print("\n📝 Testing stream publishing...")
    redis_manager = RedisStreamsManager()
    
    try:
        # Test publishing system log
        system_id = redis_manager.publish_system_log(
            level="info",
            message="Test migration verification",
            details={"test": True, "timestamp": "2025-05-27T23:59:59Z"}
        )
        print(f"✓ Successfully published test system log: {system_id}")
        
        # Test publishing user interaction
        user_id = redis_manager.publish_user_interaction(
            user_id="test_user",
            interaction_type="test",
            data={"action": "migration_test", "success": True}
        )
        print(f"✓ Successfully published test user interaction: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Stream publishing failed: {e}")
        return False

def main():
    """Run all migration tests."""
    print("🧪 Redis Migration Test Suite")
    print("=" * 50)
    
    # Test Redis connection first
    if not test_redis_connection():
        print("❌ Redis connection failed - aborting tests")
        return False
    
    # Test reading from migrated streams
    system_count = test_system_logs()
    user_count = test_user_interactions()
    agent_count = test_agent_events()
    
    print("\n" + "=" * 50)
    
    # Test publishing new events
    publishing_works = test_stream_publishing()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"  System logs entries: {system_count}")
    print(f"  User interaction entries: {user_count}")
    print(f"  Agent event entries: {agent_count}")
    print(f"  New publishing: {'✓ Working' if publishing_works else '✗ Failed'}")
    
    # Determine overall success
    total_entries = system_count + user_count + agent_count
    if total_entries > 0 and publishing_works:
        print("\n✅ Migration test PASSED - Redis streams are working correctly!")
        print("   You can now safely remove the original log files if desired.")
        return True
    else:
        print("\n❌ Migration test FAILED - No data found in streams.")
        print("   Check if migration completed successfully.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
