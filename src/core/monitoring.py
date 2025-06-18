"""
Production Monitoring and Error Tracking
Integrates with Sentry, DataDog, and custom metrics
"""

import logging
import time
import os
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
import traceback
from pathlib import Path

# Try to import monitoring services
try:
    import sentry_sdk
    from sentry_sdk import capture_exception, set_context
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and tracks application metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
        self.metrics_file = Path("logs/metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        
    def increment(self, metric: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        key = f"{metric}:{json.dumps(tags or {})}"
        if key not in self.metrics:
            self.metrics[key] = {
                "name": metric,
                "type": "counter",
                "value": 0,
                "tags": tags or {},
                "last_updated": datetime.now().isoformat()
            }
        self.metrics[key]["value"] += value
        self.metrics[key]["last_updated"] = datetime.now().isoformat()
        self._save_metrics()
    
    def gauge(self, metric: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        key = f"{metric}:{json.dumps(tags or {})}"
        self.metrics[key] = {
            "name": metric,
            "type": "gauge", 
            "value": value,
            "tags": tags or {},
            "last_updated": datetime.now().isoformat()
        }
        self._save_metrics()
    
    def timing(self, metric: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timing metric"""
        key = f"{metric}:{json.dumps(tags or {})}"
        if key not in self.metrics:
            self.metrics[key] = {
                "name": metric,
                "type": "timing",
                "values": [],
                "tags": tags or {},
                "last_updated": datetime.now().isoformat()
            }
        self.metrics[key]["values"].append(duration_ms)
        # Keep only last 1000 values
        if len(self.metrics[key]["values"]) > 1000:
            self.metrics[key]["values"] = self.metrics[key]["values"][-1000:]
        self.metrics[key]["last_updated"] = datetime.now().isoformat()
        self._save_metrics()
    
    def _save_metrics(self):
        """Persist metrics to disk"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {
            "uptime_seconds": time.time() - self.start_time,
            "metrics": {}
        }
        
        for key, metric in self.metrics.items():
            name = metric["name"]
            if name not in summary["metrics"]:
                summary["metrics"][name] = []
            
            if metric["type"] == "timing" and metric.get("values"):
                avg_time = sum(metric["values"]) / len(metric["values"])
                metric["average"] = avg_time
                metric["min"] = min(metric["values"])
                metric["max"] = max(metric["values"])
                metric.pop("values", None)  # Don't include all values in summary
            
            summary["metrics"][name].append(metric)
        
        return summary

# Global metrics collector
metrics = MetricsCollector()

def track_performance(metric_name: str = None):
    """Decorator to track function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error_occurred = False
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                track_error(e, context={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                name = metric_name or f"function.{func.__name__}"
                
                metrics.timing(name, duration_ms, tags={
                    "status": "error" if error_occurred else "success"
                })
                
                if duration_ms > 5000:  # Log slow operations
                    logger.warning(f"Slow operation: {name} took {duration_ms:.0f}ms")
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            error_occurred = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                track_error(e, context={
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                })
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                name = metric_name or f"function.{func.__name__}"
                
                metrics.timing(name, duration_ms, tags={
                    "status": "error" if error_occurred else "success"
                })
                
                if duration_ms > 5000:  # Log slow operations
                    logger.warning(f"Slow operation: {name} took {duration_ms:.0f}ms")
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator

def track_error(error: Exception, context: Dict[str, Any] = None):
    """Track an error with context"""
    error_type = type(error).__name__
    error_message = str(error)
    
    # Log the error
    logger.error(f"{error_type}: {error_message}", exc_info=True)
    
    # Track in metrics
    metrics.increment("errors", tags={"type": error_type})
    
    # Send to Sentry if available
    if SENTRY_AVAILABLE:
        if context:
            for key, value in context.items():
                set_context(key, value)
        capture_exception(error)
    
    # Save error details
    error_log = {
        "timestamp": datetime.now().isoformat(),
        "type": error_type,
        "message": error_message,
        "traceback": traceback.format_exc(),
        "context": context or {}
    }
    
    error_file = Path("logs/errors.json")
    error_file.parent.mkdir(exist_ok=True)
    
    try:
        errors = []
        if error_file.exists():
            with open(error_file, 'r') as f:
                errors = json.load(f)
        
        errors.append(error_log)
        # Keep only last 1000 errors
        if len(errors) > 1000:
            errors = errors[-1000:]
        
        with open(error_file, 'w') as f:
            json.dump(errors, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save error log: {e}")

def init_monitoring():
    """Initialize monitoring services"""
    # Initialize Sentry
    if SENTRY_AVAILABLE and os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            environment=os.getenv("ENVIRONMENT", "production"),
            traces_sample_rate=0.1,
            attach_stacktrace=True,
            send_default_pii=False
        )
        logger.info("Sentry error tracking initialized")
    
    # Log startup
    logger.info("Monitoring system initialized")
    metrics.increment("app.startup")

# Health check endpoint data
class HealthChecker:
    """System health monitoring"""
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get current system health status"""
        from ..database import DatabaseManager
        
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check database
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                conn.execute("SELECT 1")
            health["checks"]["database"] = {"status": "ok"}
        except Exception as e:
            health["checks"]["database"] = {"status": "error", "message": str(e)}
            health["status"] = "unhealthy"
        
        # Check disk space
        try:
            import shutil
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)
            health["checks"]["disk"] = {
                "status": "ok" if free_gb > 1 else "warning",
                "free_gb": round(free_gb, 2)
            }
        except:
            health["checks"]["disk"] = {"status": "unknown"}
        
        # Check memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            health["checks"]["memory"] = {
                "status": "ok" if memory.percent < 90 else "warning",
                "percent_used": memory.percent
            }
        except:
            health["checks"]["memory"] = {"status": "unknown"}
        
        # Add metrics summary
        health["metrics"] = metrics.get_summary()
        
        return health

# Import asyncio for async support
import asyncio 