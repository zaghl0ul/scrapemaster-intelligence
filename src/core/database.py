"""
Enhanced Database Manager with Connection Pooling and Async Support
Implements thread-safe operations, query optimization, and caching
"""

import sqlite3
import asyncio
import threading
from contextlib import contextmanager, asynccontextmanager
from typing import List, Dict, Optional, Any, Tuple
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import aiosqlite
from functools import lru_cache
import time

from .models import ScrapingTarget, ScrapedData, Client, PlanType, TargetStatus
from .config import get_config

logger = logging.getLogger(__name__)

class ConnectionPool:
    """Thread-safe SQLite connection pool with size management"""
    
    def __init__(self, db_path: Path, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._in_use = set()
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        
    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized SQLite connection"""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Performance optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL") 
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        
        return conn    
    def get_connection(self):
        """Acquire connection from pool"""
        with self._condition:
            # Wait if all connections are in use
            while len(self._connections) == 0 and len(self._in_use) >= self.max_connections:
                self._condition.wait()
                
            # Get existing connection or create new one
            if self._connections:
                conn = self._connections.pop()
            else:
                conn = self._create_connection()
                
            self._in_use.add(conn)
            return conn
            
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        with self._condition:
            self._in_use.discard(conn)
            if len(self._connections) < self.max_connections:
                self._connections.append(conn)
            else:
                conn.close()
            self._condition.notify()
            
    def close_all(self):
        """Close all connections"""
        with self._lock:
            for conn in self._connections:
                conn.close()
            for conn in self._in_use:
                conn.close()
            self._connections.clear()
            self._in_use.clear()

class DatabaseManager:
    """Enhanced database manager with async support and query optimization"""
    
    def __init__(self, db_path: Optional[Path] = None):
        config = get_config()
        self.db_path = db_path or config.database.path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connection pool for sync operations
        self.pool = ConnectionPool(self.db_path, config.database.max_connections)
        
        # Cache for frequently accessed data
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 60  # seconds
        
        # Initialize database
        self.init_database()
        
        # Async connection string
        self.async_db_path = f"file:{self.db_path}?mode=rw"
        
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        conn = self.pool.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.return_connection(conn)
            
    @asynccontextmanager
    async def get_async_connection(self):
        """Get async connection for concurrent operations"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            await conn.execute("PRAGMA cache_size=10000")
            await conn.execute("PRAGMA temp_store=MEMORY")
            conn.row_factory = aiosqlite.Row
            yield conn    
    def init_database(self):
        """Initialize database schema with optimized indexes and views"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enhanced scraping targets table with additional indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_targets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    selectors TEXT NOT NULL,
                    frequency_hours INTEGER NOT NULL CHECK(frequency_hours BETWEEN 1 AND 168),
                    client_id TEXT NOT NULL,
                    price_per_month REAL NOT NULL CHECK(price_per_month >= 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scraped TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    status TEXT DEFAULT 'active',
                    success_rate REAL DEFAULT 100.0,
                    error_count INTEGER DEFAULT 0,
                    consecutive_errors INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    headers TEXT DEFAULT '{}',
                    cookies TEXT DEFAULT '{}'
                )
            ''')
            
            # Enhanced scraped data table with partitioning consideration
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL,
                    raw_html TEXT,
                    change_detected BOOLEAN DEFAULT FALSE,
                    changes TEXT DEFAULT '{}',
                    hash_signature TEXT NOT NULL,
                    response_time_ms INTEGER DEFAULT 0,
                    status_code INTEGER DEFAULT 200,
                    content_length INTEGER DEFAULT 0,
                    extraction_success_rate REAL DEFAULT 100.0,
                    errors TEXT DEFAULT '[]',
                    warnings TEXT DEFAULT '[]',
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (target_id) REFERENCES scraping_targets (id) ON DELETE CASCADE
                )
            ''')
            
            # Enhanced clients table with CRM features
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    company TEXT,
                    phone TEXT,
                    plan_type TEXT NOT NULL DEFAULT 'starter',
                    monthly_value REAL NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    satisfaction_score REAL DEFAULT 5.0 CHECK(satisfaction_score BETWEEN 0 AND 5),
                    lifetime_value REAL DEFAULT 0,
                    notes TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # Revenue tracking with enhanced analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS revenue_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    target_id TEXT,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    billing_period TEXT NOT NULL,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    payment_method TEXT,
                    transaction_id TEXT UNIQUE,
                    notes TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
                )
            ''')
            
            # Notification queue for async processing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            ''')
            
            # Create optimized indexes
            indexes = [
                # Target indexes
                "CREATE INDEX IF NOT EXISTS idx_target_active_freq ON scraping_targets(is_active, frequency_hours, last_scraped)",
                "CREATE INDEX IF NOT EXISTS idx_target_client ON scraping_targets(client_id, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_target_status ON scraping_targets(status, is_active)",
                
                # Scraped data indexes
                "CREATE INDEX IF NOT EXISTS idx_scraped_target_time ON scraped_data(target_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_scraped_changes ON scraped_data(change_detected, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_scraped_hash ON scraped_data(target_id, hash_signature)",
                
                # Client indexes
                "CREATE INDEX IF NOT EXISTS idx_client_email ON clients(email)",
                "CREATE INDEX IF NOT EXISTS idx_client_active_plan ON clients(is_active, plan_type)",
                
                # Revenue indexes
                "CREATE INDEX IF NOT EXISTS idx_revenue_client_date ON revenue_tracking(client_id, payment_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_revenue_status ON revenue_tracking(status, payment_date DESC)",
                
                # Notification indexes
                "CREATE INDEX IF NOT EXISTS idx_notif_status_priority ON notification_queue(status, priority DESC)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            # Create materialized views for performance
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_active_targets_summary AS
                SELECT 
                    t.id, t.name, t.url, t.frequency_hours,
                    t.last_scraped, t.success_rate, t.status,
                    c.name as client_name, c.email as client_email,
                    c.plan_type, c.monthly_value,
                    COUNT(DISTINCT sd.id) as total_scrapes,
                    SUM(CASE WHEN sd.change_detected THEN 1 ELSE 0 END) as changes_detected,
                    AVG(sd.response_time_ms) as avg_response_time,
                    MAX(sd.timestamp) as last_data_timestamp
                FROM scraping_targets t
                LEFT JOIN clients c ON t.client_id = c.id
                LEFT JOIN scraped_data sd ON t.id = sd.target_id
                WHERE t.is_active = TRUE
                GROUP BY t.id
            ''')
            
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_client_analytics AS
                SELECT 
                    c.*,
                    COUNT(DISTINCT t.id) as active_targets,
                    COUNT(DISTINCT CASE WHEN t.status = 'error' THEN t.id END) as error_targets,
                    AVG(t.success_rate) as avg_target_success_rate,
                    SUM(t.price_per_month) as total_monthly_revenue,
                    MAX(t.last_scraped) as last_activity_timestamp
                FROM clients c
                LEFT JOIN scraping_targets t ON c.id = t.client_id AND t.is_active = TRUE
                WHERE c.is_active = TRUE
                GROUP BY c.id
            ''')
            
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_revenue_dashboard AS
                SELECT 
                    DATE(payment_date) as date,
                    COUNT(DISTINCT client_id) as unique_clients,
                    COUNT(*) as transaction_count,
                    SUM(amount) as daily_revenue,
                    AVG(amount) as avg_transaction_value
                FROM revenue_tracking
                WHERE status = 'active'
                GROUP BY DATE(payment_date)
                ORDER BY date DESC
            ''')
            
            logger.info("Database initialized successfully with optimized schema")    
    def add_target(self, target: ScrapingTarget) -> bool:
        """Add scraping target with duplicate detection and client validation"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Validate client exists and can add targets
                cursor.execute("""
                    SELECT c.id, c.plan_type, 
                           COUNT(t.id) as current_targets
                    FROM clients c
                    LEFT JOIN scraping_targets t ON c.id = t.client_id AND t.is_active = TRUE
                    WHERE c.id = ? AND c.is_active = TRUE
                    GROUP BY c.id, c.plan_type
                """, (target.client_id,))
                
                client_data = cursor.fetchone()
                if not client_data:
                    logger.error(f"Client {target.client_id} not found or inactive")
                    return False
                
                # Check plan limits
                plan_type = PlanType(client_data['plan_type'])
                if client_data['current_targets'] >= plan_type.max_targets:
                    logger.warning(f"Client {target.client_id} has reached plan limit")
                    return False
                
                # Check for duplicate URLs for the same client
                cursor.execute("""
                    SELECT id FROM scraping_targets 
                    WHERE url = ? AND client_id = ? AND is_active = TRUE
                """, (target.url, target.client_id))
                
                if cursor.fetchone():
                    logger.warning(f"Duplicate URL {target.url} for client {target.client_id}")
                    return False
                
                # Insert target
                cursor.execute("""
                    INSERT INTO scraping_targets 
                    (id, name, url, selectors, frequency_hours, client_id, 
                     price_per_month, status, metadata, headers, cookies)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    target.id, target.name, target.url,
                    json.dumps(target.selectors), target.frequency_hours,
                    target.client_id, target.price_per_month,
                    target.status.value, json.dumps(target.metadata),
                    json.dumps(target.headers), json.dumps(target.cookies)
                ))
                
                # Update client's last activity
                cursor.execute("""
                    UPDATE clients 
                    SET last_activity = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (target.client_id,))
                
                # Clear cache
                self._invalidate_cache('active_targets')
                
                logger.info(f"Added target {target.name} for client {target.client_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding target: {e}")
            return False
    
    def get_active_targets(self, force_refresh: bool = False) -> List[ScrapingTarget]:
        """Get active targets with intelligent caching"""
        cache_key = 'active_targets'
        
        # Check cache
        if not force_refresh and self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM v_active_targets_summary
                    ORDER BY 
                        CASE 
                            WHEN last_scraped IS NULL THEN 0
                            ELSE (julianday('now') - julianday(last_scraped)) * 24
                        END DESC,
                        success_rate ASC
                """)
                
                targets = []
                for row in cursor.fetchall():
                    target = ScrapingTarget(
                        id=row['id'],
                        name=row['name'],
                        url=row['url'],
                        selectors=json.loads(cursor.execute(
                            "SELECT selectors FROM scraping_targets WHERE id = ?",
                            (row['id'],)
                        ).fetchone()['selectors']),
                        frequency_hours=row['frequency_hours'],
                        client_id=cursor.execute(
                            "SELECT client_id FROM scraping_targets WHERE id = ?",
                            (row['id'],)
                        ).fetchone()['client_id'],
                        price_per_month=cursor.execute(
                            "SELECT price_per_month FROM scraping_targets WHERE id = ?",
                            (row['id'],)
                        ).fetchone()['price_per_month'],
                        last_scraped=datetime.fromisoformat(row['last_scraped']) if row['last_scraped'] else None,
                        status=TargetStatus(row['status']),
                        success_rate=row['success_rate']
                    )
                    targets.append(target)
                
                # Update cache
                self._cache[cache_key] = targets
                self._cache_timestamps[cache_key] = time.time()
                
                return targets
                
        except Exception as e:
            logger.error(f"Error getting active targets: {e}")
            return []
    
    async def get_active_targets_async(self) -> List[ScrapingTarget]:
        """Async version for concurrent operations"""
        async with self.get_async_connection() as conn:
            cursor = await conn.execute("""
                SELECT t.*, c.plan_type
                FROM scraping_targets t
                JOIN clients c ON t.client_id = c.id
                WHERE t.is_active = TRUE AND c.is_active = TRUE
                ORDER BY t.last_scraped ASC NULLS FIRST
            """)
            
            rows = await cursor.fetchall()
            targets = []
            
            for row in rows:
                target = ScrapingTarget(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    selectors=json.loads(row['selectors']),
                    frequency_hours=row['frequency_hours'],
                    client_id=row['client_id'],
                    price_per_month=row['price_per_month'],
                    last_scraped=datetime.fromisoformat(row['last_scraped']) if row['last_scraped'] else None,
                    status=TargetStatus(row['status']),
                    success_rate=row['success_rate'],
                    consecutive_errors=row['consecutive_errors'],
                    metadata=json.loads(row['metadata']),
                    headers=json.loads(row['headers']),
                    cookies=json.loads(row['cookies'])
                )
                targets.append(target)
                
            return targets    
    def store_scraped_data(self, data: ScrapedData) -> bool:
        """Store scraped data with change detection and performance metrics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get previous data for comparison
                cursor.execute("""
                    SELECT data, hash_signature 
                    FROM scraped_data 
                    WHERE target_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (data.target_id,))
                
                previous = cursor.fetchone()
                
                # Detect changes
                if previous:
                    previous_data = json.loads(previous['data'])
                    changes = data.compare_with(ScrapedData(
                        data=previous_data,
                        hash_signature=previous['hash_signature']
                    ))
                    data.changes = changes
                    data.change_detected = bool(changes)
                
                # Insert scraped data
                cursor.execute("""
                    INSERT INTO scraped_data 
                    (target_id, data, raw_html, change_detected, changes, hash_signature,
                     response_time_ms, status_code, content_length, extraction_success_rate,
                     errors, warnings, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.target_id, json.dumps(data.data), data.raw_html,
                    data.change_detected, json.dumps(data.changes), data.hash_signature,
                    data.response_time_ms, data.status_code, data.content_length,
                    data.extraction_success_rate, json.dumps(data.errors),
                    json.dumps(data.warnings), json.dumps(data.metadata)
                ))
                
                # Update target statistics
                if data.status_code == 200:
                    cursor.execute("""
                        UPDATE scraping_targets 
                        SET last_scraped = CURRENT_TIMESTAMP,
                            success_rate = MIN(100, success_rate * 0.95 + 5.0),
                            consecutive_errors = 0,
                            status = 'active'
                        WHERE id = ?
                    """, (data.target_id,))
                else:
                    cursor.execute("""
                        UPDATE scraping_targets 
                        SET last_scraped = CURRENT_TIMESTAMP,
                            success_rate = MAX(0, success_rate * 0.95),
                            error_count = error_count + 1,
                            consecutive_errors = consecutive_errors + 1,
                            status = CASE 
                                WHEN consecutive_errors >= 3 THEN 'error'
                                ELSE status
                            END
                        WHERE id = ?
                    """, (data.target_id,))
                
                # Queue notifications if needed
                if data.change_detected:
                    cursor.execute("""
                        INSERT INTO notification_queue 
                        (target_id, client_id, notification_type, priority, payload)
                        SELECT t.id, t.client_id, 'change_detected', 8, ?
                        FROM scraping_targets t
                        WHERE t.id = ?
                    """, (json.dumps({
                        'changes': data.changes,
                        'timestamp': data.timestamp.isoformat()
                    }), data.target_id))
                
                # Clear relevant caches
                self._invalidate_cache('active_targets')
                
                return True
                
        except Exception as e:
            logger.error(f"Error storing scraped data: {e}")
            return False
    
    def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get comprehensive revenue analytics with caching"""
        cache_key = 'revenue_analytics'
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try:
            with self.get_connection() as conn:
                # Current MRR
                mrr_result = conn.execute("""
                    SELECT SUM(price_per_month) as mrr
                    FROM scraping_targets
                    WHERE is_active = TRUE
                """).fetchone()
                
                # Client metrics
                client_metrics = conn.execute("""
                    SELECT 
                        COUNT(DISTINCT c.id) as client_count,
                        COUNT(DISTINCT CASE WHEN c.plan_type = 'enterprise' THEN c.id END) as enterprise_clients,
                        AVG(c.satisfaction_score) as avg_satisfaction
                    FROM clients c
                    WHERE c.is_active = TRUE
                """).fetchone()
                
                # Target metrics
                target_metrics = conn.execute("""
                    SELECT 
                        COUNT(*) as target_count,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_targets,
                        AVG(success_rate) as avg_success_rate,
                        SUM(CASE WHEN last_scraped > datetime('now', '-24 hours') THEN 1 ELSE 0 END) as recent_scrapes
                    FROM scraping_targets
                    WHERE is_active = TRUE
                """).fetchone()
                
                # Revenue trend (last 30 days)
                revenue_trend = pd.read_sql_query("""
                    SELECT 
                        DATE(payment_date) as date,
                        SUM(amount) as revenue
                    FROM revenue_tracking
                    WHERE payment_date > datetime('now', '-30 days')
                        AND status = 'active'
                    GROUP BY DATE(payment_date)
                    ORDER BY date
                """, conn)
                
                # Churn risk analysis
                churn_risk = conn.execute("""
                    SELECT 
                        COUNT(CASE WHEN satisfaction_score < 3 THEN 1 END) as high_risk_clients,
                        COUNT(CASE WHEN last_activity < datetime('now', '-30 days') THEN 1 END) as inactive_clients
                    FROM clients
                    WHERE is_active = TRUE
                """).fetchone()
                
                analytics = {
                    'mrr': float(mrr_result['mrr'] or 0),
                    'client_count': int(client_metrics['client_count'] or 0),
                    'enterprise_clients': int(client_metrics['enterprise_clients'] or 0),
                    'avg_satisfaction': float(client_metrics['avg_satisfaction'] or 5.0),
                    'target_count': int(target_metrics['target_count'] or 0),
                    'active_targets': int(target_metrics['active_targets'] or 0),
                    'avg_success_rate': float(target_metrics['avg_success_rate'] or 100.0),
                    'recent_scrapes': int(target_metrics['recent_scrapes'] or 0),
                    'revenue_trend': revenue_trend.to_dict('records'),
                    'high_risk_clients': int(churn_risk['high_risk_clients'] or 0),
                    'inactive_clients': int(churn_risk['inactive_clients'] or 0),
                    'growth_rate': self._calculate_growth_rate(conn)
                }
                
                # Cache results
                self._cache[cache_key] = analytics
                self._cache_timestamps[cache_key] = time.time()
                
                return analytics
                
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {e}")
            return {
                'mrr': 0, 'client_count': 0, 'target_count': 0,
                'revenue_trend': [], 'growth_rate': 0
            }
    
    def _calculate_growth_rate(self, conn) -> float:
        """Calculate month-over-month growth rate"""
        try:
            result = conn.execute("""
                SELECT 
                    SUM(CASE WHEN payment_date > datetime('now', '-30 days') THEN amount ELSE 0 END) as current_month,
                    SUM(CASE WHEN payment_date > datetime('now', '-60 days') 
                             AND payment_date <= datetime('now', '-30 days') THEN amount ELSE 0 END) as previous_month
                FROM revenue_tracking
                WHERE status = 'active'
            """).fetchone()
            
            if result['previous_month'] and result['previous_month'] > 0:
                return ((result['current_month'] - result['previous_month']) / result['previous_month']) * 100
            return 0.0
            
        except:
            return 0.0
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache or key not in self._cache_timestamps:
            return False
        
        age = time.time() - self._cache_timestamps[key]
        return age < self._cache_ttl
    
    def _invalidate_cache(self, key: Optional[str] = None):
        """Invalidate cache entries"""
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
    
    def add_client(self, client: Client) -> bool:
        """Add new client with validation"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO clients 
                    (id, name, email, company, phone, plan_type, monthly_value, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    client.id, client.name, client.email, client.company,
                    client.phone, client.plan_type.value, client.monthly_value,
                    json.dumps(client.metadata)
                ))
                
                self._invalidate_cache()
                logger.info(f"Added client {client.name}")
                return True
                
        except sqlite3.IntegrityError:
            logger.error(f"Client with email {client.email} already exists")
            return False
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            return False
    
    def get_recent_changes(self, limit: int = 50) -> pd.DataFrame:
        """Get recent content changes for monitoring"""
        with self.get_connection() as conn:
            return pd.read_sql_query("""
                SELECT 
                    sd.timestamp,
                    t.name as target_name,
                    t.url,
                    c.name as client_name,
                    sd.changes,
                    sd.response_time_ms
                FROM scraped_data sd
                JOIN scraping_targets t ON sd.target_id = t.id
                JOIN clients c ON t.client_id = c.id
                WHERE sd.change_detected = TRUE
                ORDER BY sd.timestamp DESC
                LIMIT ?
            """, conn, params=(limit,))
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old scraped data to manage database size"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Keep at least one record per target
                cursor.execute("""
                    DELETE FROM scraped_data
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                    AND id NOT IN (
                        SELECT MAX(id)
                        FROM scraped_data
                        GROUP BY target_id
                    )
                """, (days_to_keep,))
                
                deleted = cursor.rowcount
                
                # Vacuum to reclaim space
                cursor.execute("VACUUM")
                
                logger.info(f"Cleaned up {deleted} old records")
                return deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    def close(self):
        """Close all connections and cleanup"""
        self.pool.close_all()
        self._cache.clear()
        logger.info("Database manager closed")