"""
Alerting
Alert on performance issues
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class AlertingSystem:
    """
    Alert on performance degradation
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize alerting system
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Alerting system initialized")
    
    def check_latency_threshold(self, model_name, version, threshold=2.0):
        """
        Check if latency exceeds threshold
        
        Args:
            model_name: Model name
            version: Model version
            threshold: Latency threshold in seconds
            
        Returns:
            True if alert triggered
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            return False
        
        # Get recent average latency
        avg_latency = self._get_avg_metric(version_id, 'latency', limit=10)
        
        if avg_latency > threshold:
            self._create_alert(
                version_id,
                'latency_high',
                f"Average latency {avg_latency:.2f}s exceeds threshold {threshold}s",
                'warning'
            )
            logger.warning(f"Latency alert: {model_name} v{version} - {avg_latency:.2f}s")
            return True
        
        return False
    
    def check_error_rate_threshold(self, model_name, version, threshold=0.1):
        """
        Check if error rate exceeds threshold
        
        Args:
            model_name: Model name
            version: Model version
            threshold: Error rate threshold (0.0 to 1.0)
            
        Returns:
            True if alert triggered
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            return False
        
        # Calculate error rate
        error_rate = self._get_error_rate(version_id)
        
        if error_rate > threshold:
            self._create_alert(
                version_id,
                'error_rate_high',
                f"Error rate {error_rate:.2%} exceeds threshold {threshold:.2%}",
                'critical'
            )
            logger.error(f"Error rate alert: {model_name} v{version} - {error_rate:.2%}")
            return True
        
        return False
    
    def check_performance_degradation(self, model_name, current_version, previous_version, threshold=0.2):
        """
        Check if performance degraded compared to previous version
        
        Args:
            model_name: Model name
            current_version: Current version
            previous_version: Previous version
            threshold: Degradation threshold (0.0 to 1.0)
            
        Returns:
            True if alert triggered
        """
        current_id = self._get_version_id(model_name, current_version)
        previous_id = self._get_version_id(model_name, previous_version)
        
        if not current_id or not previous_id:
            return False
        
        # Compare latencies
        current_latency = self._get_avg_metric(current_id, 'latency')
        previous_latency = self._get_avg_metric(previous_id, 'latency')
        
        if previous_latency > 0:
            degradation = (current_latency - previous_latency) / previous_latency
            
            if degradation > threshold:
                self._create_alert(
                    current_id,
                    'performance_degradation',
                    f"Performance degraded by {degradation:.1%} compared to v{previous_version}",
                    'warning'
                )
                logger.warning(f"Performance degradation: {model_name} v{current_version}")
                return True
        
        return False
    
    def get_alerts(self, model_name=None, version=None, severity=None, limit=10):
        """
        Get alerts
        
        Args:
            model_name: Optional model name filter
            version: Optional version filter
            severity: Optional severity filter
            limit: Number of records
            
        Returns:
            List of alert dictionaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT a.*, v.version, m.name as model_name
            FROM alerts a
            JOIN versions v ON a.version_id = v.id
            JOIN models m ON v.model_id = m.id
            WHERE 1=1
        '''
        params = []
        
        if model_name:
            query += ' AND m.name = ?'
            params.append(model_name)
        
        if version:
            query += ' AND v.version = ?'
            params.append(version)
        
        if severity:
            query += ' AND a.severity = ?'
            params.append(severity)
        
        query += ' ORDER BY a.timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
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
    
    def _get_avg_metric(self, version_id, metric_name, limit=100):
        """Get average metric value"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(metric_value) as avg
            FROM (
                SELECT metric_value
                FROM metrics
                WHERE version_id = ? AND metric_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            )
        ''', (version_id, metric_name, limit))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['avg'] or 0.0
    
    def _get_error_rate(self, version_id):
        """Calculate error rate"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(metric_value) as successes
            FROM metrics
            WHERE version_id = ? AND metric_name = 'success'
        ''', (version_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result['total'] > 0:
            return 1.0 - (result['successes'] / result['total'])
        return 0.0
    
    def _create_alert(self, version_id, alert_type, message, severity):
        """Create alert"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (version_id, alert_type, message, severity)
            VALUES (?, ?, ?, ?)
        ''', (version_id, alert_type, message, severity))
        
        conn.commit()
        conn.close()
