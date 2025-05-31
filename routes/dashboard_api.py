"""
Dashboard API Routes

FastAPI routes for the unified logging dashboard system.
Provides comprehensive monitoring and management endpoints for the hybrid logging system.

Author: GitHub Copilot
Created: 2024
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging

from utils.logging_dashboard import (
    get_dashboard, 
    get_system_status, 
    search_recent_activity,
    SystemHealth,
    LoggingMetrics,
    AgentSummary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/health", response_model=Dict[str, Any])
async def get_health():
    """Get comprehensive system health status."""
    try:
        dashboard = await get_dashboard()
        health = await dashboard.get_system_health()
        return {
            "status": "success",
            "data": {
                "redis_connected": health.redis_connected,
                "redis_streams_active": health.redis_streams_active,
                "redis_stack_available": health.redis_stack_available,
                "pinecone_connected": health.pinecone_connected,
                "total_agents": health.total_agents,
                "active_streams": health.active_streams,
                "redis_memory_usage": health.redis_memory_usage,
                "uptime_hours": health.uptime_hours,
                "last_updated": health.last_updated,
                "overall_status": "healthy" if health.redis_connected else "degraded"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back for metrics")
):
    """Get comprehensive logging system metrics."""
    try:
        dashboard = await get_dashboard()
        metrics = await dashboard.get_logging_metrics(hours=hours)
        return {
            "status": "success",
            "data": {
                "total_logs_24h": metrics.total_logs_24h,
                "logs_per_hour": metrics.logs_per_hour,
                "top_agents": metrics.top_agents,
                "top_actions": metrics.top_actions,
                "error_rate": metrics.error_rate,
                "avg_response_time": metrics.avg_response_time,
                "redis_hit_rate": metrics.redis_hit_rate,
                "stream_throughput": metrics.stream_throughput,
                "memory_usage": metrics.memory_usage,
                "time_window_hours": hours
            }
        }
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_quick_status():
    """Get a quick system status overview."""
    try:
        status = await get_system_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/agents", response_model=Dict[str, Any])
async def get_all_agents():
    """Get summary information for all agents."""
    try:
        dashboard = await get_dashboard()
        agents = await dashboard.get_all_agents_summary()
        return {
            "status": "success",
            "data": {
                "agents": [
                    {
                        "agent_id": agent.agent_id,
                        "identity_loaded": agent.identity_loaded,
                        "recent_logs": agent.recent_logs,
                        "memory_entries": agent.memory_entries,
                        "last_active": agent.last_active,
                        "current_mood": agent.current_mood,
                        "active_goals": agent.active_goals,
                        "vector_memories": agent.vector_memories
                    }
                    for agent in agents
                ],
                "total_agents": len(agents)
            }
        }
    except Exception as e:
        logger.error(f"Agents summary failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agents summary failed: {str(e)}")


@router.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent_details(agent_id: str):
    """Get detailed information for a specific agent."""
    try:
        dashboard = await get_dashboard()
        agent = await dashboard.get_agent_summary(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "status": "success",
            "data": {
                "agent_id": agent.agent_id,
                "identity_loaded": agent.identity_loaded,
                "recent_logs": agent.recent_logs,
                "memory_entries": agent.memory_entries,
                "last_active": agent.last_active,
                "current_mood": agent.current_mood,
                "active_goals": agent.active_goals,
                "vector_memories": agent.vector_memories
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent details failed for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent details failed: {str(e)}")


@router.get("/search", response_model=Dict[str, Any])
async def search_logs(
    query: Optional[str] = Query(None, description="Text search query"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results")
):
    """Search logs with various filters."""
    try:
        dashboard = await get_dashboard()
        logs = await dashboard.search_logs(
            query=query or "",
            agent_id=agent_id,
            action=action,
            hours=hours,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "logs": logs,
                "total_found": len(logs),
                "filters": {
                    "query": query,
                    "agent_id": agent_id,
                    "action": action,
                    "hours": hours,
                    "limit": limit
                }
            }
        }
    except Exception as e:
        logger.error(f"Log search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Log search failed: {str(e)}")


@router.get("/events", response_model=Dict[str, Any])
async def get_real_time_events(
    stream_name: Optional[str] = Query(None, description="Specific stream name"),
    count: int = Query(10, ge=1, le=100, description="Number of events to retrieve")
):
    """Get recent real-time events from Redis Streams."""
    try:
        dashboard = await get_dashboard()
        events = await dashboard.get_real_time_events(
            stream_name=stream_name,
            count=count
        )
        
        return {
            "status": "success",
            "data": {
                "events": events,
                "total_events": len(events),
                "stream_filter": stream_name,
                "count_requested": count
            }
        }
    except Exception as e:
        logger.error(f"Real-time events failed: {e}")
        raise HTTPException(status_code=500, detail=f"Real-time events failed: {str(e)}")


@router.get("/activity", response_model=Dict[str, Any])
async def get_recent_activity(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    hours: int = Query(1, ge=1, le=24, description="Time window in hours")
):
    """Get recent activity summary for monitoring."""
    try:
        activity = await search_recent_activity(agent_id=agent_id, hours=hours)
        return {
            "status": "success",
            "data": activity
        }
    except Exception as e:
        logger.error(f"Recent activity failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recent activity failed: {str(e)}")


@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_old_data(
    days: int = Query(7, ge=1, le=30, description="Age threshold in days")
):
    """Clean up old data from the logging system."""
    try:
        dashboard = await get_dashboard()
        cleanup_stats = await dashboard.cleanup_old_data(days=days)
        
        return {
            "status": "success",
            "data": {
                "cleanup_stats": cleanup_stats,
                "days_threshold": days,
                "message": f"Cleanup completed: removed {cleanup_stats['logs_removed']} logs and {cleanup_stats['stream_entries_removed']} stream entries"
            }
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview():
    """Get a comprehensive dashboard overview with all key metrics."""
    try:
        dashboard = await get_dashboard()
        
        # Get all the key information
        health = await dashboard.get_system_health()
        metrics = await dashboard.get_logging_metrics(hours=24)
        agents = await dashboard.get_all_agents_summary()
        recent_events = await dashboard.get_real_time_events(count=5)
        
        # Get top active agents (last 24 hours)
        top_agents = []
        for agent_name, count in metrics.top_agents[:5]:
            agent_summary = await dashboard.get_agent_summary(agent_name)
            if agent_summary:
                top_agents.append({
                    "agent_id": agent_name,
                    "log_count": count,
                    "last_active": agent_summary.last_active,
                    "memory_entries": agent_summary.memory_entries
                })
        
        return {
            "status": "success",
            "data": {
                "system_health": {
                    "overall_status": "healthy" if health.redis_connected else "degraded",
                    "redis_connected": health.redis_connected,
                    "streams_active": health.redis_streams_active,
                    "stack_available": health.redis_stack_available,
                    "pinecone_connected": health.pinecone_connected,
                    "uptime_hours": health.uptime_hours
                },
                "metrics_summary": {
                    "total_logs_24h": metrics.total_logs_24h,
                    "error_rate": metrics.error_rate,
                    "redis_hit_rate": metrics.redis_hit_rate,
                    "active_streams": health.active_streams,
                    "memory_usage": health.redis_memory_usage
                },
                "agents_summary": {
                    "total_agents": len(agents),
                    "active_agents": len([a for a in agents if a.recent_logs > 0]),
                    "top_agents": top_agents
                },
                "recent_activity": {
                    "latest_events": recent_events,
                    "event_count": len(recent_events)
                },
                "generated_at": health.last_updated
            }
        }
    except Exception as e:
        logger.error(f"Dashboard overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard overview failed: {str(e)}")


@router.get("/", response_model=Dict[str, Any])
async def get_dashboard_info():
    """Get basic dashboard information and available endpoints."""
    return {
        "status": "success",
        "data": {
            "name": "Anchorwork Unified Logging Dashboard",
            "version": "1.0.0",
            "description": "Comprehensive monitoring and management for the hybrid logging system",
            "endpoints": {
                "health": "GET /dashboard/health - System health status",
                "metrics": "GET /dashboard/metrics - Logging metrics and performance",
                "status": "GET /dashboard/status - Quick status overview",
                "agents": "GET /dashboard/agents - All agents summary",
                "agent_details": "GET /dashboard/agents/{agent_id} - Specific agent details",
                "search": "GET /dashboard/search - Search logs with filters",
                "events": "GET /dashboard/events - Real-time events from streams",
                "activity": "GET /dashboard/activity - Recent activity summary",
                "cleanup": "POST /dashboard/cleanup - Clean up old data",
                "overview": "GET /dashboard/overview - Comprehensive overview"
            },
            "features": [
                "Redis short-term log storage with TTL",
                "Redis Streams real-time event monitoring",
                "Redis Stack advanced features (Bloom filters, TimeSeries)",
                "Pinecone long-term vector memory",
                "Agent memory and identity management",
                "Performance metrics and health monitoring",
                "Log search and filtering",
                "Automated cleanup capabilities"
            ]
        }
    }
