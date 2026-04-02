#!/usr/bin/env python3
"""
Agent Performance Analytics - Core Module
Track and analyze AI agent performance metrics
"""

import time
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import threading

@dataclass
class MetricRecord:
    timestamp: datetime
    operation: str
    model: str
    latency_ms: float
    tokens_input: int
    tokens_output: int
    cost_usd: float
    success: bool
    error_type: Optional[str] = None
    
class AnalyticsCollector:
    """Collects metrics from agent operations"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                operation TEXT,
                model TEXT,
                latency_ms REAL,
                tokens_input INTEGER,
                tokens_output INTEGER,
                cost_usd REAL,
                success INTEGER,
                error_type TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON metrics(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_operation ON metrics(operation)
        ''')
        conn.commit()
        conn.close()
    
    @contextmanager
    def track(self, operation: str, model: str, estimated_cost: float = 0.0):
        """Context manager to track an operation"""
        start_time = time.time()
        record = {
            "operation": operation,
            "model": model,
            "start_time": start_time,
            "estimated_cost": estimated_cost
        }
        self._local.current_record = record
        
        try:
            yield self
            success = True
            error_type = None
        except Exception as e:
            success = False
            error_type = type(e).__name__
            raise
        finally:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Store metric
            self._store_metric(
                operation=operation,
                model=model,
                latency_ms=latency_ms,
                tokens_input=record.get("tokens_input", 0),
                tokens_output=record.get("tokens_output", 0),
                cost_usd=estimated_cost,
                success=success,
                error_type=error_type
            )
    
    def _store_metric(self, **kwargs):
        """Store metric in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics 
            (timestamp, operation, model, latency_ms, tokens_input, tokens_output, cost_usd, success, error_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            kwargs["operation"],
            kwargs["model"],
            kwargs["latency_ms"],
            kwargs["tokens_input"],
            kwargs["tokens_output"],
            kwargs["cost_usd"],
            1 if kwargs["success"] else 0,
            kwargs["error_type"]
        ))
        conn.commit()
        conn.close()
    
    def set_tokens(self, input_tokens: int, output_tokens: int):
        """Set token counts for current operation"""
        if hasattr(self._local, "current_record"):
            self._local.current_record["tokens_input"] = input_tokens
            self._local.current_record["tokens_output"] = output_tokens


class Analytics:
    """Analytics query and reporting"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
    
    def query(self, time_range: str = "24h", operation: Optional[str] = None) -> Dict[str, Any]:
        """Query metrics from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parse time range
        hours = int(time_range.replace("h", ""))
        since = datetime.now() - timedelta(hours=hours)
        
        query = "SELECT * FROM metrics WHERE timestamp > ?"
        params = [since.isoformat()]
        
        if operation:
            query += " AND operation = ?"
            params.append(operation)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return self._process_metrics(rows)
    
    def _process_metrics(self, rows: List) -> Dict[str, Any]:
        """Process raw metrics into summary"""
        if not rows:
            return {"count": 0, "message": "No metrics found"}
        
        latencies = [r[4] for r in rows]
        costs = [r[7] for r in rows]
        successes = [r[8] for r in rows]
        
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        
        return {
            "count": n,
            "latency": {
                "avg_ms": sum(latencies) / n,
                "p50_ms": latencies_sorted[n // 2],
                "p95_ms": latencies_sorted[int(n * 0.95)],
                "p99_ms": latencies_sorted[int(n * 0.99)],
                "min_ms": min(latencies),
                "max_ms": max(latencies)
            },
            "cost": {
                "total_usd": sum(costs),
                "avg_per_request": sum(costs) / n
            },
            "success_rate": sum(successes) / n * 100
        }
    
    def get_insights(self) -> Dict[str, Any]:
        """Generate optimization insights"""
        metrics_24h = self.query("24h")
        metrics_7d = self.query("168h")  # 7 days
        
        insights = {
            "period": "24h",
            "summary": metrics_24h,
            "recommendations": []
        }
        
        if metrics_24h["count"] == 0:
            insights["recommendations"].append({
                "priority": "info",
                "message": "No data collected yet. Start using the collector to see insights."
            })
            return insights
        
        # Check latency
        if metrics_24h["latency"]["p95_ms"] > 2000:
            insights["recommendations"].append({
                "priority": "high",
                "message": f"High P95 latency ({metrics_24h['latency']['p95_ms']:.0f}ms). Consider using a faster model or optimizing prompts."
            })
        
        # Check error rate
        if metrics_24h["success_rate"] < 95:
            insights["recommendations"].append({
                "priority": "high",
                "message": f"Error rate is {(100 - metrics_24h['success_rate']):.1f}%. Investigate failures."
            })
        
        # Cost trends
        daily_cost = metrics_24h["cost"]["total_usd"]
        if daily_cost > 50:
            insights["recommendations"].append({
                "priority": "medium",
                "message": f"High daily cost (${daily_cost:.2f}). Consider enabling cost optimization."
            })
        
        return insights


class MetricQuery:
    """Builder for metric queries"""
    
    def __init__(self):
        self.time_range_val = "24h"
        self.operation_val = None
        self.model_val = None
    
    def time_range(self, range_str: str):
        self.time_range_val = range_str
        return self
    
    def operation(self, op: str):
        self.operation_val = op
        return self
    
    def model(self, m: str):
        self.model_val = m
        return self


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python analytics.py [collect|report|insights]")
        sys.exit(1)
    
    command = sys.argv[1]
    analytics = Analytics()
    
    if command == "report":
        result = analytics.query("24h")
        print(json.dumps(result, indent=2))
    elif command == "insights":
        insights = analytics.get_insights()
        print(json.dumps(insights, indent=2))
    else:
        print(f"Unknown command: {command}")