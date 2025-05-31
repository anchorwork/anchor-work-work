#!/usr/bin/env python3
"""
Test Script for Unified Logging Dashboard (Step 9)

This script comprehensively tests the dashboard system including:
- Dashboard API endpoints
- Health monitoring
- Metrics collection
- Agent management
- Log searching
- Real-time events
- Web interface

Author: GitHub Copilot
Created: 2024
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any


class DashboardTester:
    """Comprehensive tester for the unified logging dashboard."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results = {}
        
    async def test_all(self):
        """Run all dashboard tests."""
        print("🚀 Starting Unified Logging Dashboard Tests")
        print("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            self.client = client
            
            # Test dashboard API endpoints
            await self.test_dashboard_info()
            await self.test_health_check()
            await self.test_metrics()
            await self.test_status()
            await self.test_agents_summary()
            await self.test_log_search()
            await self.test_real_time_events()
            await self.test_overview()
            await self.test_web_interface()
            
            # Create some test data and retest
            await self.create_test_data()
            await self.test_with_data()
            
            # Test cleanup
            await self.test_cleanup()
        
        # Print final results
        self.print_summary()
    
    async def test_dashboard_info(self):
        """Test basic dashboard info endpoint."""
        print("\n📋 Testing Dashboard Info...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            assert "name" in data["data"]
            assert "endpoints" in data["data"]
            assert "features" in data["data"]
            
            print("✅ Dashboard info endpoint working")
            self.results["dashboard_info"] = "PASS"
            
        except Exception as e:
            print(f"❌ Dashboard info failed: {e}")
            self.results["dashboard_info"] = f"FAIL: {e}"
    
    async def test_health_check(self):
        """Test system health endpoint."""
        print("\n🏥 Testing Health Check...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/health")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            health_data = data["data"]
            
            # Check required health fields
            required_fields = [
                "redis_connected", "redis_streams_active", "redis_stack_available",
                "pinecone_connected", "total_agents", "active_streams",
                "redis_memory_usage", "uptime_hours", "last_updated", "overall_status"
            ]
            
            for field in required_fields:
                assert field in health_data, f"Missing health field: {field}"
            
            print(f"✅ Health check passed - Status: {health_data['overall_status']}")
            print(f"   Redis: {'✅' if health_data['redis_connected'] else '❌'}")
            print(f"   Streams: {'✅' if health_data['redis_streams_active'] else '❌'}")
            print(f"   Redis Stack: {'✅' if health_data['redis_stack_available'] else '❌'}")
            print(f"   Pinecone: {'✅' if health_data['pinecone_connected'] else '❌'}")
            print(f"   Agents: {health_data['total_agents']}")
            print(f"   Memory: {health_data['redis_memory_usage']}")
            print(f"   Uptime: {health_data['uptime_hours']:.1f}h")
            
            self.results["health_check"] = "PASS"
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.results["health_check"] = f"FAIL: {e}"
    
    async def test_metrics(self):
        """Test metrics endpoint."""
        print("\n📊 Testing Metrics Collection...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/metrics?hours=24")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            metrics = data["data"]
            
            # Check required metrics fields
            required_fields = [
                "total_logs_24h", "logs_per_hour", "top_agents", "top_actions",
                "error_rate", "avg_response_time", "redis_hit_rate",
                "stream_throughput", "memory_usage", "time_window_hours"
            ]
            
            for field in required_fields:
                assert field in metrics, f"Missing metrics field: {field}"
            
            print(f"✅ Metrics collection working")
            print(f"   Total logs (24h): {metrics['total_logs_24h']}")
            print(f"   Error rate: {metrics['error_rate']:.1f}%")
            print(f"   Redis hit rate: {metrics['redis_hit_rate']:.1f}%")
            print(f"   Top agents: {len(metrics['top_agents'])}")
            print(f"   Top actions: {len(metrics['top_actions'])}")
            
            self.results["metrics"] = "PASS"
            
        except Exception as e:
            print(f"❌ Metrics test failed: {e}")
            self.results["metrics"] = f"FAIL: {e}"
    
    async def test_status(self):
        """Test quick status endpoint."""
        print("\n⚡ Testing Quick Status...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/status")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            status = data["data"]
            
            # Check required status fields
            required_fields = [
                "status", "redis_connected", "total_agents", "recent_logs",
                "error_rate", "uptime_hours", "last_updated"
            ]
            
            for field in required_fields:
                assert field in status, f"Missing status field: {field}"
            
            print(f"✅ Quick status working - {status['status']}")
            self.results["status"] = "PASS"
            
        except Exception as e:
            print(f"❌ Status test failed: {e}")
            self.results["status"] = f"FAIL: {e}"
    
    async def test_agents_summary(self):
        """Test agents summary endpoint."""
        print("\n👥 Testing Agents Summary...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/agents")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            agents_data = data["data"]
            
            assert "agents" in agents_data
            assert "total_agents" in agents_data
            
            print(f"✅ Agents summary working")
            print(f"   Total agents: {agents_data['total_agents']}")
            
            if agents_data["agents"]:
                agent = agents_data["agents"][0]
                print(f"   Sample agent: {agent['agent_id']}")
                print(f"     Recent logs: {agent['recent_logs']}")
                print(f"     Memory entries: {agent['memory_entries']}")
            
            self.results["agents_summary"] = "PASS"
            
        except Exception as e:
            print(f"❌ Agents summary failed: {e}")
            self.results["agents_summary"] = f"FAIL: {e}"
    
    async def test_log_search(self):
        """Test log search functionality."""
        print("\n🔍 Testing Log Search...")
        
        try:
            # Test basic search
            response = await self.client.get(f"{self.base_url}/dashboard/search?hours=24&limit=10")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            search_data = data["data"]
            
            assert "logs" in search_data
            assert "total_found" in search_data
            assert "filters" in search_data
            
            print(f"✅ Log search working")
            print(f"   Found: {search_data['total_found']} logs")
            
            # Test filtered search
            if search_data["logs"]:
                first_log = search_data["logs"][0]
                agent_id = first_log.get("author")
                
                if agent_id and agent_id != "unknown":
                    response = await self.client.get(
                        f"{self.base_url}/dashboard/search?agent_id={agent_id}&hours=24"
                    )
                    filtered_data = response.json()
                    print(f"   Filtered by {agent_id}: {filtered_data['data']['total_found']} logs")
            
            self.results["log_search"] = "PASS"
            
        except Exception as e:
            print(f"❌ Log search failed: {e}")
            self.results["log_search"] = f"FAIL: {e}"
    
    async def test_real_time_events(self):
        """Test real-time events endpoint."""
        print("\n⚡ Testing Real-time Events...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/events?count=5")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            events_data = data["data"]
            
            assert "events" in events_data
            assert "total_events" in events_data
            
            print(f"✅ Real-time events working")
            print(f"   Found: {events_data['total_events']} recent events")
            
            self.results["real_time_events"] = "PASS"
            
        except Exception as e:
            print(f"❌ Real-time events failed: {e}")
            self.results["real_time_events"] = f"FAIL: {e}"
    
    async def test_overview(self):
        """Test comprehensive overview endpoint."""
        print("\n🌐 Testing Dashboard Overview...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard/overview")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            overview = data["data"]
            
            # Check required overview sections
            required_sections = [
                "system_health", "metrics_summary", "agents_summary",
                "recent_activity", "generated_at"
            ]
            
            for section in required_sections:
                assert section in overview, f"Missing overview section: {section}"
            
            print(f"✅ Dashboard overview working")
            print(f"   System health: {overview['system_health']['overall_status']}")
            print(f"   Total logs (24h): {overview['metrics_summary']['total_logs_24h']}")
            print(f"   Total agents: {overview['agents_summary']['total_agents']}")
            print(f"   Active agents: {overview['agents_summary']['active_agents']}")
            
            self.results["overview"] = "PASS"
            
        except Exception as e:
            print(f"❌ Overview test failed: {e}")
            self.results["overview"] = f"FAIL: {e}"
    
    async def test_web_interface(self):
        """Test web dashboard interface."""
        print("\n🌐 Testing Web Interface...")
        
        try:
            response = await self.client.get(f"{self.base_url}/dashboard")
            
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            
            content = response.text
            assert "Anchorwork Logging Dashboard" in content
            assert "dashboard-grid" in content
            assert "System Health" in content
            
            print(f"✅ Web interface accessible")
            print(f"   Content length: {len(content)} characters")
            
            self.results["web_interface"] = "PASS"
            
        except Exception as e:
            print(f"❌ Web interface failed: {e}")
            self.results["web_interface"] = f"FAIL: {e}"
    
    async def create_test_data(self):
        """Create some test data for more comprehensive testing."""
        print("\n🧪 Creating Test Data...")
        
        try:
            # Create test logs through the save_log API
            test_logs = [
                {
                    "author": "dashboard_tester",
                    "action": "test_dashboard_functionality",
                    "target": "dashboard_system",
                    "content": "Testing dashboard with comprehensive data"
                },
                {
                    "author": "dashboard_tester",
                    "action": "performance_test",
                    "target": "metrics_collection",
                    "content": "Performance testing for dashboard metrics"
                },
                {
                    "author": "test_agent_alpha",
                    "action": "memory_operation",
                    "target": "agent_memory",
                    "content": "Testing agent memory operations"
                }
            ]
            
            for log_data in test_logs:
                response = await self.client.post(f"{self.base_url}/save_log", json=log_data)
                assert response.status_code == 200
            
            print(f"✅ Created {len(test_logs)} test log entries")
            
            # Wait a moment for data to propagate
            await asyncio.sleep(2)
            
            self.results["test_data_creation"] = "PASS"
            
        except Exception as e:
            print(f"❌ Test data creation failed: {e}")
            self.results["test_data_creation"] = f"FAIL: {e}"
    
    async def test_with_data(self):
        """Test dashboard functionality with the created test data."""
        print("\n📊 Testing With Created Data...")
        
        try:
            # Test search for our test data
            response = await self.client.get(
                f"{self.base_url}/dashboard/search?query=dashboard&hours=1&limit=50"
            )
            data = response.json()
            
            assert response.status_code == 200
            found_logs = data["data"]["logs"]
            
            # Should find our test logs
            test_logs_found = [log for log in found_logs if "dashboard" in log.get("content", "").lower()]
            
            print(f"✅ Search with data working")
            print(f"   Found {len(test_logs_found)} test logs")
            
            # Test agent-specific search
            response = await self.client.get(
                f"{self.base_url}/dashboard/search?agent_id=dashboard_tester&hours=1"
            )
            agent_data = response.json()
            agent_logs = agent_data["data"]["logs"]
            
            print(f"   Found {len(agent_logs)} logs for dashboard_tester")
            
            self.results["test_with_data"] = "PASS"
            
        except Exception as e:
            print(f"❌ Testing with data failed: {e}")
            self.results["test_with_data"] = f"FAIL: {e}"
    
    async def test_cleanup(self):
        """Test cleanup functionality."""
        print("\n🧹 Testing Cleanup...")
        
        try:
            # Test cleanup endpoint (but don't actually clean much)
            response = await self.client.post(f"{self.base_url}/dashboard/cleanup?days=30")
            data = response.json()
            
            assert response.status_code == 200
            assert data["status"] == "success"
            cleanup_stats = data["data"]["cleanup_stats"]
            
            print(f"✅ Cleanup functionality working")
            print(f"   Logs removed: {cleanup_stats['logs_removed']}")
            print(f"   Stream entries removed: {cleanup_stats['stream_entries_removed']}")
            print(f"   Errors: {cleanup_stats['errors']}")
            
            self.results["cleanup"] = "PASS"
            
        except Exception as e:
            print(f"❌ Cleanup test failed: {e}")
            self.results["cleanup"] = f"FAIL: {e}"
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("🏁 DASHBOARD TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result}")
            
            if result == "PASS":
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 SUMMARY: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 ALL DASHBOARD TESTS PASSED!")
            print("\n🚀 The Unified Logging Dashboard is fully functional!")
            print("\n📋 You can now:")
            print("   • Access the web dashboard at: http://localhost:8000/dashboard")
            print("   • Use the API endpoints for programmatic access")
            print("   • Monitor system health and performance metrics")
            print("   • Search and analyze logs across all agents")
            print("   • View real-time events and activity")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")


async def main():
    """Run the dashboard test suite."""
    tester = DashboardTester()
    await tester.test_all()


if __name__ == "__main__":
    asyncio.run(main())
