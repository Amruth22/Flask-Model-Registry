"""
Metrics Collector
Collect and aggregate metrics
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collect metrics from model predictions
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize metrics collector
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Metrics collector initialized")
    
    def collect_metric(self, model_name, version, metric_name, metric_value):
        """
        Collect a single metric
        
        Args:
            model_name: Model name
            version: Model version
            metric_name: Metric name
            metric_value: Metric value
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            logger.warning(f"Version not found: {model_name} v{version}")
            return
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (version_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (version_id, metric_name, metric_value))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Metric collected: {metric_name}={metric_value}")
    
    def get_recent_metrics(self, model_name, version, metric_name, limit=100):
        """
        Get recent metrics
        
        Args:
            model_name: Model name
            version: Model version
            metric_name: Metric name
            limit: Number of records
            
        Returns:
            List of metric values
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            return []
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric_value, timestamp
            FROM metrics
            WHERE version_id = ? AND metric_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (version_id, metric_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_aggregated_metrics(self, model_name, version):
        """
        Get aggregated metrics
        
        Args:
            model_name: Model name
            version: Model version
            
        Returns:
            Dictionary with aggregated metrics
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            return None
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get all metric types
        cursor.execute('''
            SELECT DISTINCT metric_name
            FROM metrics
            WHERE version_id = ?
        ''', (version_id,))
        
        metric_names = [row['metric_name'] for row in cursor.fetchall()]
        
        aggregated = {}
        
        for metric_name in metric_names:
            cursor.execute('''
                SELECT 
                    COUNT(*) as count,
                    AVG(metric_value) as avg,
                    MIN(metric_value) as min,
                    MAX(metric_value) as max,
                    SUM(metric_value) as sum
                FROM metrics
                WHERE version_id = ? AND metric_name = ?
            ''', (version_id, metric_name))
            
            stats = cursor.fetchone()
            
            aggregated[metric_name] = {
                'count': stats['count'],
                'avg': round(stats['avg'] or 0, 3),
                'min': round(stats['min'] or 0, 3),
                'max': round(stats['max'] or 0, 3),
                'sum': round(stats['sum'] or 0, 3)
            }
        
        conn.close()
        
        return aggregated
    
    def _get_version_id(self, model_name, version):
        """Get version ID"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND v.version = ?
        ''', (model_name, version))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['id'] if result else None
