"""
redis_managers.py
Unified Redis managers for Anchorwork: connection, streams, and stack modules.
"""
import os
import redis
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# --- Redis Client Singleton ---
class AnchorworkRedisClient:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.password = os.getenv("REDIS_PASSWORD")
        self.ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            ssl=self.ssl,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        try:
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def __getattr__(self, name):
        return getattr(self.client, name)

_redis_client: Optional[AnchorworkRedisClient] = None

def get_redis_client() -> AnchorworkRedisClient:
    global _redis_client
    if _redis_client is None:
        _redis_client = AnchorworkRedisClient()
    return _redis_client

# --- Redis Streams Manager ---
class RedisStreamsManager:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.streams = {
            "agent_events": "agent:events",
            "system_logs": "system:logs",
            "user_interactions": "user:interactions",
            "memory_updates": "memory:updates"
        }
        self._init_consumer_groups()

    def _init_consumer_groups(self):
        for stream_key, stream_name in self.streams.items():
            try:
                self.redis_client.xgroup_create(
                    stream_name,
                    f"{stream_key}_group",
                    id="0",
                    mkstream=True
                )
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.warning(f"Could not create consumer group for {stream_name}: {e}")

    def publish_agent_event(self, agent_id: str, event_type: str, data: Dict[str, Any]) -> str:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "event_type": event_type,
            "data": json.dumps(data) if isinstance(data, dict) else str(data)
        }
        try:
            entry_id = self.redis_client.xadd(
                self.streams["agent_events"],
                event,
                maxlen=10000
            )
            logger.debug(f"Published agent event {entry_id} for {agent_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Failed to publish agent event: {e}")
            return None

    def publish_system_log(self, level: str, message: str, details: Optional[Dict] = None) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "details": json.dumps(details) if details else ""
        }
        try:
            entry_id = self.redis_client.xadd(
                self.streams["system_logs"],
                log_entry,
                maxlen=10000
            )
            logger.debug(f"Published system log {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Failed to publish system log: {e}")
            return None

    def publish_user_interaction(self, user_id: str, interaction_type: str, data: Dict[str, Any]) -> str:
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "interaction_type": interaction_type,
            "data": json.dumps(data) if isinstance(data, dict) else str(data)
        }
        try:
            entry_id = self.redis_client.xadd(
                self.streams["user_interactions"],
                interaction,
                maxlen=2000
            )
            logger.debug(f"Published user interaction {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Failed to publish user interaction: {e}")
            return None

    def publish_memory_update(self, agent_id: str, update_type: str, data: Dict[str, Any]) -> str:
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "update_type": update_type,
            "data": json.dumps(data) if isinstance(data, dict) else str(data)
        }
        try:
            entry_id = self.redis_client.xadd(
                self.streams["memory_updates"],
                update,
                maxlen=3000
            )
            logger.debug(f"Published memory update {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Failed to publish memory update: {e}")
            return None

    def read_stream(self, stream_key: str, count: int = 10, consumer_group: Optional[str] = None, consumer_name: Optional[str] = None) -> List[Dict]:
        if stream_key not in self.streams:
            logger.error(f"Unknown stream key: {stream_key}")
            return []
        stream_name = self.streams[stream_key]
        try:
            if consumer_group and consumer_name:
                result = self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {stream_name: ">"},
                    count=count,
                    block=0
                )
            else:
                result = self.redis_client.xread(
                    {stream_name: "0"},
                    count=count,
                    block=None
                )
            entries = []
            for stream, messages in result:
                for message_id, fields in messages:
                    entry = {
                        "id": message_id.decode() if isinstance(message_id, bytes) else message_id,
                        "stream": stream.decode() if isinstance(stream, bytes) else stream
                    }
                    for key, value in fields.items():
                        key_str = key.decode() if isinstance(key, bytes) else key
                        value_str = value.decode() if isinstance(value, bytes) else value
                        if key_str in ["data", "details"]:
                            try:
                                entry[key_str] = json.loads(value_str)
                            except:
                                entry[key_str] = value_str
                        else:
                            entry[key_str] = value_str
                    entries.append(entry)
            return entries
        except Exception as e:
            logger.error(f"Failed to read from stream {stream_key}: {e}")
            return []

    def get_recent_events(self, stream_key: str, minutes: int = 10) -> List[Dict]:
        if stream_key not in self.streams:
            return []
        stream_name = self.streams[stream_key]
        cutoff_time = int((time.time() - (minutes * 60)) * 1000)
        try:
            result = self.redis_client.xrange(
                stream_name,
                min=cutoff_time,
                max="+",
                count=1000
            )
            entries = []
            for message_id, fields in result:
                entry = {"id": message_id.decode() if isinstance(message_id, bytes) else message_id}
                for key, value in fields.items():
                    key_str = key.decode() if isinstance(key, bytes) else key
                    value_str = value.decode() if isinstance(value, bytes) else value
                    if key_str in ["data", "details"]:
                        try:
                            entry[key_str] = json.loads(value_str)
                        except:
                            entry[key_str] = value_str
                    else:
                        entry[key_str] = value_str
                entries.append(entry)
            return entries
        except Exception as e:
            logger.error(f"Failed to get recent events from {stream_key}: {e}")
            return []

    def acknowledge_message(self, stream_key: str, consumer_group: str, message_id: str) -> bool:
        if stream_key not in self.streams:
            return False
        stream_name = self.streams[stream_key]
        try:
            result = self.redis_client.xack(stream_name, consumer_group, message_id)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
            return False

    def get_stream_info(self, stream_key: str) -> Dict:
        if stream_key not in self.streams:
            return {}
        stream_name = self.streams[stream_key]
        try:
            info = self.redis_client.xinfo_stream(stream_name)
            result = {}
            for key, value in info.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                val = value.decode() if isinstance(value, bytes) else value
                result[key_str] = val
            return result
        except Exception as e:
            logger.error(f"Failed to get stream info for {stream_key}: {e}")
            return {}

# --- Redis Stack Manager (Bloom, TimeSeries, JSON) ---
class RedisStackManager:
    def __init__(self):
        self.redis_client = get_redis_client()
        self._check_redis_stack_support()

    def _check_redis_stack_support(self):
        try:
            self.redis_client.bf_reserve("test_bloom", 0.01, 1000)
            self.redis_client.delete("test_bloom")
            self.bloom_available = True
        except Exception:
            self.bloom_available = False
            logger.warning("RedisBloom module not available - Bloom filter features disabled")
        try:
            self.redis_client.ts_create("test_ts")
            self.redis_client.delete("test_ts")
            self.timeseries_available = True
        except Exception:
            self.timeseries_available = False
            logger.warning("RedisTimeSeries module not available - TimeSeries features disabled")
        try:
            self.redis_client.json_set("test_json", ".", {"test": True})
            self.redis_client.delete("test_json")
            self.json_available = True
        except Exception:
            self.json_available = False
            logger.warning("RedisJSON module not available - enhanced JSON features disabled")

    # Bloom Filter Operations
    def create_bloom_filter(self, key: str, error_rate: float = 0.01, capacity: int = 10000) -> bool:
        if not self.bloom_available:
            logger.warning("Bloom filters not available")
            return False
        try:
            self.redis_client.bf_reserve(key, error_rate, capacity)
            logger.info(f"Created Bloom filter {key} with {capacity} capacity and {error_rate} error rate")
            return True
        except Exception as e:
            logger.error(f"Failed to create Bloom filter {key}: {e}")
            return False

    def add_to_bloom_filter(self, key: str, item: str) -> bool:
        if not self.bloom_available:
            return False
        try:
            result = self.redis_client.bf_add(key, item)
            return result == 1
        except Exception as e:
            logger.error(f"Failed to add item to Bloom filter {key}: {e}")
            return False

    def check_bloom_filter(self, key: str, item: str) -> bool:
        if not self.bloom_available:
            return False
        try:
            result = self.redis_client.bf_exists(key, item)
            return result == 1
        except Exception as e:
            logger.error(f"Failed to check Bloom filter {key}: {e}")
            return False

    def get_bloom_filter_info(self, key: str) -> Dict:
        if not self.bloom_available:
            return {}
        try:
            info = self.redis_client.bf_info(key)
            return {
                "capacity": info[1],
                "size": info[3],
                "number_of_filters": info[5],
                "number_of_inserted_items": info[7],
                "expansion_rate": info[9]
            }
        except Exception as e:
            logger.error(f"Failed to get Bloom filter info for {key}: {e}")
            return {}

    # TimeSeries Operations
    def create_timeseries(self, key: str, retention_ms: Optional[int] = None, labels: Optional[Dict[str, str]] = None) -> bool:
        if not self.timeseries_available:
            logger.warning("TimeSeries not available")
            return False
        try:
            args = [key]
            if retention_ms:
                args.extend(["RETENTION", retention_ms])
            if labels:
                args.append("LABELS")
                for k, v in labels.items():
                    args.extend([k, v])
            self.redis_client.execute_command("TS.CREATE", *args)
            logger.info(f"Created TimeSeries {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to create TimeSeries {key}: {e}")
            return False

    def add_timeseries_point(self, key: str, value: float, timestamp: Optional[int] = None) -> bool:
        if not self.timeseries_available:
            return False
        try:
            ts = timestamp or int(time.time() * 1000)
            self.redis_client.ts_add(key, ts, value)
            return True
        except Exception as e:
            logger.error(f"Failed to add point to TimeSeries {key}: {e}")
            return False

    def get_timeseries_range(self, key: str, from_time: int = 0, to_time: int = -1) -> List[tuple]:
        if not self.timeseries_available:
            return []
        try:
            result = self.redis_client.ts_range(key, from_time, to_time)
            return [(ts, float(value)) for ts, value in result]
        except Exception as e:
            logger.error(f"Failed to get TimeSeries range for {key}: {e}")
            return []

    def get_timeseries_last(self, key: str) -> Optional[tuple]:
        if not self.timeseries_available:
            return None
        try:
            result = self.redis_client.ts_get(key)
            if result:
                return (result[0], float(result[1]))
            return None
        except Exception as e:
            logger.error(f"Failed to get last TimeSeries point for {key}: {e}")
            return None

    def get_timeseries_info(self, key: str) -> Dict:
        if not self.timeseries_available:
            return {}
        try:
            info = self.redis_client.ts_info(key)
            result = {}
            for i in range(0, len(info), 2):
                key_name = info[i].decode() if isinstance(info[i], bytes) else info[i]
                value = info[i + 1]
                if isinstance(value, bytes):
                    value = value.decode()
                result[key_name] = value
            return result
        except Exception as e:
            logger.error(f"Failed to get TimeSeries info for {key}: {e}")
            return {}

    # Enhanced JSON Operations
    def json_set_with_index(self, key: str, path: str, data: Any, create_index: bool = False, index_fields: Optional[List[str]] = None) -> bool:
        if not self.json_available:
            try:
                self.redis_client.set(key, json.dumps(data))
                return True
            except Exception as e:
                logger.error(f"Failed to set JSON data for {key}: {e}")
                return False
        try:
            self.redis_client.json_set(key, path, data)
            if create_index and index_fields:
                self._create_json_index(key, index_fields)
            return True
        except Exception as e:
            logger.error(f"Failed to set JSON data for {key}: {e}")
            return False

    def json_get_enhanced(self, key: str, path: str = ".") -> Any:
        if not self.json_available:
            try:
                data = self.redis_client.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Failed to get JSON data for {key}: {e}")
                return None
        try:
            return self.redis_client.json_get(key, path)
        except Exception as e:
            logger.error(f"Failed to get JSON data for {key}: {e}")
            return None

    def _create_json_index(self, key_pattern: str, fields: List[str]):
        try:
            index_name = f"idx_{key_pattern.replace('*', 'all')}"
            logger.info(f"Index creation placeholder for {index_name}")
        except Exception as e:
            logger.warning(f"Could not create search index: {e}")

class LoggingMetrics:
    def __init__(self):
        self.stack = RedisStackManager()
        self.metrics_prefix = "metrics:"
        self.bloom_prefix = "bloom:"
        self._init_standard_metrics()

    def _init_standard_metrics(self):
        base_time = int(time.time() * 1000)
        metrics = [
            "log_count",
            "error_rate",
            "response_time",
            "memory_usage",
            "agent_activity"
        ]
        for metric in metrics:
            key = f"{self.metrics_prefix}{metric}"
            self.stack.create_timeseries(
                key,
                retention_ms=7 * 24 * 60 * 60 * 1000,
                labels={"metric_type": metric, "system": "anchorwork"}
            )
        bloom_filters = [
            "duplicate_logs",
            "processed_events",
            "user_sessions"
        ]
        for bloom_filter in bloom_filters:
            key = f"{self.bloom_prefix}{bloom_filter}"
            self.stack.create_bloom_filter(key, error_rate=0.01, capacity=100000)

    def record_log_event(self, event_type: str = "general"):
        key = f"{self.metrics_prefix}log_count"
        self.stack.add_timeseries_point(key, 1.0)
        type_key = f"{self.metrics_prefix}log_count_{event_type}"
        self.stack.add_timeseries_point(type_key, 1.0)

    def record_error(self, error_type: str = "general"):
        key = f"{self.metrics_prefix}error_rate"
        self.stack.add_timeseries_point(key, 1.0)
        type_key = f"{self.metrics_prefix}error_{error_type}"
        self.stack.add_timeseries_point(type_key, 1.0)

    def record_response_time(self, duration_ms: float):
        key = f"{self.metrics_prefix}response_time"
        self.stack.add_timeseries_point(key, duration_ms)

    def record_agent_activity(self, agent_id: str):
        key = f"{self.metrics_prefix}agent_activity"
        self.stack.add_timeseries_point(key, 1.0)
        agent_key = f"{self.metrics_prefix}agent_{agent_id}_activity"
        self.stack.add_timeseries_point(agent_key, 1.0)

    def check_duplicate_log(self, log_signature: str) -> bool:
        key = f"{self.bloom_prefix}duplicate_logs"
        if self.stack.check_bloom_filter(key, log_signature):
            return True
        self.stack.add_to_bloom_filter(key, log_signature)
        return False

    def get_metrics_summary(self, hours_back: int = 1) -> Dict:
        end_time = int(time.time() * 1000)
        start_time = end_time - (hours_back * 60 * 60 * 1000)
        summary = {
            "time_range_hours": hours_back,
            "metrics": {}
        }
        metrics = ["log_count", "error_rate", "response_time", "agent_activity"]
        for metric in metrics:
            key = f"{self.metrics_prefix}{metric}"
            data = self.stack.get_timeseries_range(key, start_time, end_time)
            if data:
                values = [point[1] for point in data]
                summary["metrics"][metric] = {
                    "count": len(values),
                    "total": sum(values),
                    "average": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "latest": values[-1] if values else 0
                }
            else:
                summary["metrics"][metric] = {
                    "count": 0, "total": 0, "average": 0,
                    "min": 0, "max": 0, "latest": 0
                }
        return summary

# Global instances
_stack_manager = None
_metrics_manager = None

def get_stack_manager() -> RedisStackManager:
    global _stack_manager
    if _stack_manager is None:
        _stack_manager = RedisStackManager()
    return _stack_manager

def get_metrics_manager() -> LoggingMetrics:
    global _metrics_manager
    if _metrics_manager is None:
        _metrics_manager = LoggingMetrics()
    return _metrics_manager
