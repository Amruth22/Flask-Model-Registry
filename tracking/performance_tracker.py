"""
Performance Tracker
Track model performance metrics
"""

import logging
from storage.database import get_connection

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Track model performance metrics
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Performance tracker initialized")
    
    def track_prediction(self, model_name, version, latency, tokens, success=True):
        """
        Track a prediction
        
        Args:
            model_name: Model name
            version: Model version
            latency: Prediction latency in seconds
            tokens: Token count
            success: Whether prediction was successful
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            logger.warning(f"Version not found: {model_name} v{version}")
            return
        
        # Track latency
        self._track_metric(version_id, 'latency', latency)
        
        # Track tokens
        self._track_metric(version_id, 'tokens', tokens)
        
        # Track success/failure
        self._track_metric(version_id, 'success', 1 if success else 0)
        
        logger.debug(f"Tracked prediction: {model_name} v{version}")
    
    def get_metrics(self, model_name, version):
        """
        Get metrics for a model version
        
        Args:
            model_name: Model name
            version: Model version
            
        Returns:
            Dictionary with metrics
        """
        version_id = self._get_version_id(model_name, version)
        
        if not version_id:
            return None
        
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get latency metrics
        cursor.execute('''
            SELECT 
                AVG(metric_value) as avg_latency,
                MIN(metric_value) as min_latency,
                MAX(metric_value) as max_latency
            FROM metrics
            WHERE version_id = ? AND metric_name = 'latency'
        ''', (version_id,))
        
        latency_stats = cursor.fetchone()
        
        # Get token metrics
        cursor.execute('''
            SELECT 
                AVG(metric_value) as avg_tokens,
                SUM(metric_value) as total_tokens
            FROM metrics
            WHERE version_id = ? AND metric_name = 'tokens'
        ''', (version_id,))
        
        token_stats = cursor.fetchone()
        
        # Get success rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total_requests,
                SUM(metric_value) as successful_requests
            FROM metrics
            WHERE version_id = ? AND metric_name = 'success'
        ''', (version_id,))
        
        success_stats = cursor.fetchone()
        
        conn.close()
        
        # Calculate success rate
        success_rate = 0.0
        if success_stats['total_requests'] > 0:
            success_rate = (success_stats['successful_requests'] / success_stats['total_requests']) * 100
        
        return {
            'model_name': model_name,
            'version': version,
            'avg_latency': round(latency_stats['avg_latency'] or 0, 3),
            'min_latency': round(latency_stats['min_latency'] or 0, 3),
            'max_latency': round(latency_stats['max_latency'] or 0, 3),
            'avg_tokens': round(token_stats['avg_tokens'] or 0, 1),
            'total_tokens': int(token_stats['total_tokens'] or 0),
            'total_requests': success_stats['total_requests'],
            'success_rate': round(success_rate, 2)
        }
    
    def compare_versions(self, model_name, version1, version2):
        """
        Compare two versions
        
        Args:
            model_name: Model name
            version1: First version
            version2: Second version
            
        Returns:
            Comparison dictionary
        """
        metrics1 = self.get_metrics(model_name, version1)
        metrics2 = self.get_metrics(model_name, version2)
        
        if not metrics1 or not metrics2:
            return None
        
        return {
            'version1': metrics1,
            'version2': metrics2,
            'latency_diff': metrics2['avg_latency'] - metrics1['avg_latency'],
            'tokens_diff': metrics2['avg_tokens'] - metrics1['avg_tokens'],
            'success_rate_diff': metrics2['success_rate'] - metrics1['success_rate']
        }
    
    def get_version_ranking(self, model_name):
        """
        Rank versions by performance
        
        Args:
            model_name: Model name
            
        Returns:
            List of versions ranked by performance
        """
        # Get all versions
        versions = self._get_all_versions(model_name)
        
        # Get metrics for each version
        version_metrics = []
        for version in versions:
            metrics = self.get_metrics(model_name, version)
            if metrics and metrics['total_requests'] > 0:
                # Calculate performance score (lower latency + higher success rate = better)
                score = (1 / metrics['avg_latency']) * (metrics['success_rate'] / 100)
                metrics['performance_score'] = round(score, 3)
                version_metrics.append(metrics)
        
        # Sort by performance score
        version_metrics.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return version_metrics
    
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
    
    def _track_metric(self, version_id, metric_name, metric_value):
        """Track a metric"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (version_id, metric_name, metric_value)
            VALUES (?, ?, ?)
        ''', (version_id, metric_name, metric_value))
        
        conn.commit()
        conn.close()
    
    def _get_all_versions(self, model_name):
        """Get all versions for a model"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.version FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ?
        ''', (model_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [row['version'] for row in results]
