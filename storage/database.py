"""
Database Module
Initialize and manage SQLite database for model registry
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


def init_database(db_path='model_registry.db'):
    """
    Initialize SQLite database with all required tables
    
    Args:
        db_path: Path to database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Models table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Versions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            version TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models(id),
            UNIQUE(model_id, version)
        )
    ''')
    
    # Deployments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL,
            strategy TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            traffic_percentage INTEGER DEFAULT 0,
            deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (version_id) REFERENCES versions(id)
        )
    ''')
    
    # Snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deployment_id INTEGER NOT NULL,
            snapshot_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deployment_id) REFERENCES deployments(id)
        )
    ''')
    
    # Metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (version_id) REFERENCES versions(id)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT,
            severity TEXT DEFAULT 'info',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (version_id) REFERENCES versions(id)
        )
    ''')
    
    # Traffic table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL,
            percentage INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (version_id) REFERENCES versions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database initialized: {db_path}")


def get_connection(db_path='model_registry.db'):
    """
    Get database connection
    
    Args:
        db_path: Path to database file
        
    Returns:
        SQLite connection
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
