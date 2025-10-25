"""
Rollback Manager
Manage model rollbacks
"""

import logging
from storage.database import get_connection
from rollback.snapshot_manager import SnapshotManager

logger = logging.getLogger(__name__)


class RollbackManager:
    """
    Manage model rollbacks
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize rollback manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.snapshot_manager = SnapshotManager(db_path)
        logger.info("Rollback manager initialized")
    
    def rollback_to_previous(self, model_name):
        """
        Rollback to previous version
        
        Args:
            model_name: Model name
            
        Returns:
            Previous version string or None
        """
        # Get current and previous deployments
        deployments = self._get_recent_deployments(model_name, limit=2)
        
        if len(deployments) < 2:
            logger.warning(f"No previous deployment found for {model_name}")
            return None
        
        current = deployments[0]
        previous = deployments[1]
        
        logger.info(f"Rolling back {model_name}: v{current['version']} -> v{previous['version']}")
        
        # Restore previous version traffic
        self._set_traffic(model_name, previous['version'], 100)
        
        # Set current version traffic to 0
        self._set_traffic(model_name, current['version'], 0)
        
        logger.info(f"Rollback completed: {model_name} v{previous['version']}")
        return previous['version']
    
    def rollback_to_version(self, model_name, version):
        """
        Rollback to specific version
        
        Args:
            model_name: Model name
            version: Target version
            
        Returns:
            True if successful
        """
        # Check if version exists
        if not self._version_exists(model_name, version):
            logger.error(f"Version not found: {model_name} v{version}")
            return False
        
        logger.info(f"Rolling back {model_name} to v{version}")
        
        # Set target version traffic to 100%
        self._set_traffic(model_name, version, 100)
        
        # Set all other versions to 0%
        self._clear_other_traffic(model_name, version)
        
        logger.info(f"Rollback completed: {model_name} v{version}")
        return True
    
    def rollback_from_snapshot(self, snapshot_id):
        """
        Rollback from snapshot
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            True if successful
        """
        logger.info(f"Rolling back from snapshot: {snapshot_id}")
        
        # Restore snapshot
        success = self.snapshot_manager.restore_snapshot(snapshot_id)
        
        if success:
            logger.info(f"Rollback from snapshot completed: {snapshot_id}")
        else:
            logger.error(f"Rollback from snapshot failed: {snapshot_id}")
        
        return success
    
    def auto_rollback_on_error(self, model_name, error_threshold=0.1):
        """
        Automatically rollback if error rate exceeds threshold
        
        Args:
            model_name: Model name
            error_threshold: Error rate threshold (0.0 to 1.0)
            
        Returns:
            True if rollback was triggered
        """
        # Get current deployment
        current = self._get_current_deployment(model_name)
        
        if not current:
            return False
        
        # Check error rate (simplified - would use real metrics in production)
        error_rate = self._get_error_rate(model_name, current['version'])
        
        if error_rate > error_threshold:
            logger.warning(f"Error rate {error_rate:.2%} exceeds threshold {error_threshold:.2%}")
            logger.info(f"Triggering automatic rollback for {model_name}")
            
            # Rollback to previous version
            previous_version = self.rollback_to_previous(model_name)
            
            if previous_version:
                logger.info(f"Automatic rollback completed: {model_name} v{previous_version}")
                return True
        
        return False
    
    def _get_recent_deployments(self, model_name, limit=2):
        """Get recent deployments"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, v.version
            FROM deployments d
            JOIN versions v ON d.version_id = v.id
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND d.status = 'completed'
            ORDER BY d.deployed_at DESC
            LIMIT ?
        ''', (model_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def _get_current_deployment(self, model_name):
        """Get current deployment"""
        deployments = self._get_recent_deployments(model_name, limit=1)
        return deployments[0] if deployments else None
    
    def _version_exists(self, model_name, version):
        """Check if version exists"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND v.version = ?
        ''', (model_name, version))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] > 0
    
    def _set_traffic(self, model_name, version, percentage):
        """Set traffic percentage"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND v.version = ?
        ''', (model_name, version))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        version_id = result['id']
        
        cursor.execute('''
            INSERT OR REPLACE INTO traffic (version_id, percentage)
            VALUES (?, ?)
        ''', (version_id, percentage))
        
        conn.commit()
        conn.close()
    
    def _clear_other_traffic(self, model_name, keep_version):
        """Clear traffic for all versions except one"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE traffic
            SET percentage = 0
            WHERE version_id IN (
                SELECT v.id FROM versions v
                JOIN models m ON v.model_id = m.id
                WHERE m.name = ? AND v.version != ?
            )
        ''', (model_name, keep_version))
        
        conn.commit()
        conn.close()
    
    def _get_error_rate(self, model_name, version):
        """Get error rate for version (simplified)"""
        # In production, this would query real metrics
        # For demo, return a low error rate
        return 0.01
