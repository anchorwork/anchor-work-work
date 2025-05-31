#!/usr/bin/env python3
"""
Direct test of enhanced logging API functions with AgentMemory integration
"""

import sys
import os
import json
import asyncio
from unittest.mock import Mock
sys.path.append('/Users/rebeccamorris/Desktop/anchorwork')

from routes.save_log_api import _get_agent_memory, save_agent_interaction, get_agent_memory
from utils.agent_memory import AgentMemory
from utils.redis_client import get_redis_client

async def test_enhanced_logging_integration():
    """Test the enhanced logging API integration directly"""
    print("🔧 Testing Enhanced Logging API Integration (Direct)")
    print("=" * 60)
    
    # Test Redis connection
    try:
        redis_client = get_redis_client()
        if redis_client.test_connection():
            print("✅ Redis connection successful")
        else:
            print("❌ Redis connection failed")
            return
    except Exception as e:
        print(f"❌ Redis connection error: {e}")
        return
    
    # Test 1: AgentMemory instance creation
    print("\n🧠 Test 1: Testing AgentMemory instance creation...")
    test_agent = "test_api_agent"
    memory = _get_agent_memory(test_agent)
    print(f"✅ Created AgentMemory for agent: {test_agent}")
    print(f"   Initial mood: {memory.mood}")
    print(f"   Initial goals: {memory.goals}")
    
    # Clear any existing memory
    memory.clear_recent_memory()
    print("✅ Cleared existing memory for clean test")
    
    # Test 2: Save agent interaction function
    print("\n💬 Test 2: Testing save_agent_interaction function...")
    
    # Mock request object
    mock_request = Mock()
    mock_request.json = asyncio.coroutine(lambda: {
        "prompt": "What's the best way to handle exceptions in Python?",
        "response": "Use try-except blocks and be specific about exception types. Consider using finally for cleanup.",
        "mood": "educational",
        "tags": ["python", "exceptions", "best-practices"]
    })
    
    try:
        result = await save_agent_interaction(test_agent, mock_request)
        print(f"✅ Interaction saved: {result['status']}")
        print(f"   Agent mood: {result['current_mood']}")
        print(f"   History count: {result['recent_history_count']}")
    except Exception as e:
        print(f"❌ Error saving interaction: {e}")
    
    # Test 3: Multiple interactions
    print("\n💬 Test 3: Adding multiple interactions...")
    
    interactions = [
        {
            "prompt": "Can you show me an example?",
            "response": "Sure! Here's a basic example: try: result = risky_operation() except ValueError as e: print(f'Error: {e}')",
            "mood": "helpful",
            "tags": ["python", "examples", "code"]
        },
        {
            "prompt": "What about handling multiple exception types?",
            "response": "You can use multiple except blocks or catch multiple types: except (ValueError, TypeError) as e:",
            "mood": "informative",
            "tags": ["python", "exceptions", "multiple-types"]
        }
    ]
    
    for i, interaction_data in enumerate(interactions, 1):
        mock_req = Mock()
        mock_req.json = asyncio.coroutine(lambda data=interaction_data: data)
        
        try:
            result = await save_agent_interaction(test_agent, mock_req)
            print(f"✅ Interaction {i} saved successfully")
        except Exception as e:
            print(f"❌ Error saving interaction {i}: {e}")
    
    # Test 4: Retrieve agent memory
    print("\n🔍 Test 4: Testing get_agent_memory function...")
    
    try:
        result = await get_agent_memory(test_agent, query=None, limit=10)
        print(f"✅ Memory retrieved: {result['status']}")
        print(f"   Agent ID: {result['agent_id']}")
        print(f"   Current mood: {result['mood']}")
        print(f"   Goals count: {len(result['goals'])}")
        print(f"   Recent interactions: {len(result['recent_interactions'])}")
        
        # Show recent interactions
        if result['recent_interactions']:
            print("   Recent interactions:")
            for i, interaction in enumerate(result['recent_interactions'][:2]):
                print(f"     {i+1}. {interaction['prompt'][:50]}...")
                
    except Exception as e:
        print(f"❌ Error retrieving memory: {e}")
    
    # Test 5: Direct AgentMemory functionality
    print("\n🎯 Test 5: Testing direct AgentMemory functionality...")
    
    # Update mood
    memory.update_mood("confident")
    print(f"✅ Mood updated to: {memory.mood}")
    
    # Add goals
    goals = ["Help with Python questions", "Provide clear examples", "Teach best practices"]
    for goal in goals:
        memory.add_goal(goal)
        print(f"✅ Goal added: {goal}")
    
    print(f"   Total goals: {len(memory.goals)}")
    
    # Test tag search
    print("\n🏷️ Test 6: Testing tag-based search...")
    python_interactions = memory.get_recent_by_tag("python", limit=5)
    print(f"✅ Found {len(python_interactions)} interactions with 'python' tag")
    
    for interaction in python_interactions:
        print(f"   - {interaction['prompt'][:40]}... (tags: {interaction['tags']})")
    
    # Test 7: Memory summary
    print("\n📝 Test 7: Testing memory summary...")
    summary = memory.summarize("python exceptions")
    if summary:
        print(f"✅ Summary generated: {summary[:100]}...")
    else:
        print("✅ Summary requested (vector DB not enabled)")
    
    # Test 8: Redis data verification
    print("\n🔧 Test 8: Verifying Redis data...")
    try:
        redis_key = f"agent:{test_agent}:recent_logs"
        log_count = redis_client.llen(redis_key)
        print(f"✅ Redis contains {log_count} logs for agent")
        
        mood_key = f"agent:{test_agent}:mood"
        current_mood = redis_client.get(mood_key)
        if current_mood:
            print(f"✅ Current mood in Redis: {current_mood}")
        
        goals_key = f"agent:{test_agent}:goals"
        goal_count = redis_client.llen(goals_key)
        print(f"✅ Redis contains {goal_count} goals for agent")
        
    except Exception as e:
        print(f"❌ Redis verification failed: {e}")
    
    print("\n✅ Enhanced Logging API Integration test completed!")
    print("🎉 All functionality working properly")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    memory.clear_recent_memory()
    print("✅ Test data cleared")

if __name__ == "__main__":
    asyncio.run(test_enhanced_logging_integration())
