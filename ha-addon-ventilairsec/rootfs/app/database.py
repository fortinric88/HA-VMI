"""
Database Management - SQLite for data storage and history
"""

import sqlite3
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for storing sensor readings and history"""
    
    def __init__(self, db_path):
        """
        Initialize database
        
        Args:
            db_path: Path to database directory
        """
        self.db_path = Path(db_path) / 'ventilairsec.db'
        self.connection = None
    
    def initialize(self):
        """Initialize database and create tables"""
        try:
            self._create_connection()
            self._create_tables()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_connection(self):
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=10
            )
            self.connection.row_factory = sqlite3.Row
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Readings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    device_type TEXT,
                    device_name TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_unit TEXT,
                    raw_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_device_timestamp
                ON readings(device_id, timestamp DESC)
            ''')
            
            # Devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    last_seen DATETIME,
                    status TEXT
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            self.connection.commit()
            logger.debug("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_reading(self, parsed_data):
        """
        Insert a new reading into the database
        
        Args:
            parsed_data: Dictionary with parsed sensor data
        """
        try:
            if not parsed_data or not isinstance(parsed_data, dict):
                return False
            
            device_id = parsed_data.get('device_id')
            device_type = parsed_data.get('device_type')
            device_name = parsed_data.get('device_name')
            
            cursor = self.connection.cursor()
            
            # Update device status
            cursor.execute('''
                INSERT OR REPLACE INTO devices (id, name, type, last_seen, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (device_id, device_name, device_type, datetime.now(), 'online'))
            
            # Insert metrics from data
            timestamp = parsed_data.get('timestamp', datetime.now().isoformat())
            raw_data = parsed_data.get('raw_data', '')
            
            # Extract and insert all numeric metrics
            for key, value in parsed_data.items():
                if key not in ['device_id', 'device_type', 'device_name', 'timestamp', 'raw_data']:
                    if isinstance(value, (int, float)):
                        cursor.execute('''
                            INSERT INTO readings
                            (device_id, device_type, device_name, metric_name, metric_value, timestamp, raw_data)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (device_id, device_type, device_name, key, value, timestamp, raw_data))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting reading: {e}")
            return False
    
    def get_latest_readings(self):
        """
        Get the latest reading for each device
        
        Returns:
            Dictionary with latest readings per device
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT DISTINCT device_id, device_name, device_type, 
                       MAX(timestamp) as last_update
                FROM readings
                GROUP BY device_id
            ''')
            
            devices = {}
            for row in cursor.fetchall():
                device_id = row['device_id']
                device_name = row['device_name']
                device_type = row['device_type']
                last_update = row['last_update']
                
                # Get latest metrics for this device
                cursor.execute('''
                    SELECT metric_name, metric_value, metric_unit
                    FROM readings
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (device_id,))
                
                metrics = {}
                for metric in cursor.fetchall():
                    metric_name = metric['metric_name']
                    metric_value = metric['metric_value']
                    
                    # Keep only the latest value for each metric
                    if metric_name not in metrics:
                        metrics[metric_name] = metric_value
                
                devices[device_id] = {
                    'name': device_name,
                    'type': device_type,
                    'last_update': last_update,
                    'metrics': metrics
                }
            
            return devices
            
        except Exception as e:
            logger.error(f"Error getting latest readings: {e}")
            return {}
    
    def get_readings_history(self, device_id, hours=24):
        """
        Get historical readings for a device
        
        Args:
            device_id: Device identifier
            hours: Number of hours to retrieve
        
        Returns:
            List of readings
        """
        try:
            cursor = self.connection.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, metric_name, metric_value, metric_unit
                FROM readings
                WHERE device_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (device_id, start_time.isoformat()))
            
            readings = []
            for row in cursor.fetchall():
                readings.append({
                    'timestamp': row['timestamp'],
                    'metric': row['metric_name'],
                    'value': row['metric_value'],
                    'unit': row['metric_unit']
                })
            
            return readings
            
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []
    
    def get_metric_history(self, device_id, metric_name, hours=24):
        """
        Get historical data for a specific metric
        
        Args:
            device_id: Device identifier
            metric_name: Name of the metric
            hours: Number of hours to retrieve
        
        Returns:
            List of metric values with timestamps
        """
        try:
            cursor = self.connection.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT timestamp, metric_value
                FROM readings
                WHERE device_id = ? AND metric_name = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (device_id, metric_name, start_time.isoformat()))
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'timestamp': row['timestamp'],
                    'value': row['metric_value']
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting metric history: {e}")
            return []
    
    def cleanup_old_data(self, days=30):
        """
        Remove readings older than specified days
        
        Args:
            days: Number of days to keep
        """
        try:
            cursor = self.connection.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute(
                'DELETE FROM readings WHERE timestamp < ?',
                (cutoff_date.isoformat(),)
            )
            
            self.connection.commit()
            deleted_count = cursor.rowcount
            
            logger.info(f"Cleaned up {deleted_count} old readings")
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
    
    def get_statistics(self, device_id, metric_name, hours=24):
        """
        Get statistics for a metric
        
        Args:
            device_id: Device identifier
            metric_name: Name of the metric
            hours: Number of hours to analyze
        
        Returns:
            Dictionary with min, max, avg values
        """
        try:
            cursor = self.connection.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    MIN(metric_value) as min_value,
                    MAX(metric_value) as max_value,
                    AVG(metric_value) as avg_value,
                    COUNT(*) as count
                FROM readings
                WHERE device_id = ? AND metric_name = ? AND timestamp >= ?
            ''', (device_id, metric_name, start_time.isoformat()))
            
            result = cursor.fetchone()
            
            return {
                'min': result['min_value'],
                'max': result['max_value'],
                'average': result['avg_value'],
                'count': result['count']
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                logger.debug("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
