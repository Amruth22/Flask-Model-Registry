"""
Snapshot Manager
Create and restore deployment snapshots
"""

import logging
import json
from storage.database import get_connection

logger = logging.getLogger(__name__)


class SnapshotManager:
    """
    Manage deployment snapshots
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize snapshot manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Snapshot manager initialized")
    
    def create_snapshot(self, deployment_id):
        """
        Create snapshot of deployment
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Snapshot ID
        """
        # Get deployment details
        deployment = self._get_deployment(deployment_id)
        
        if not deployment:
            logger.error(f"Deployment not found: {deployment_id}")
            return None
        
        # Get traffic configuration
        traffic = self._get_traffic_config(deployment['version_id'])
        
        # Create snapshot data
        snapshot_data = {
            'deployment_id': deployment_id,
            'version_id': deployment['version_id'],
            'version': deployment['version'],
            'model_name': deployment['model_name'],
            'strategy': deployment['strategy'],
            'traffic': traffic
        }
        
        # Store snapshot
        snapshot_id = self._store_snapshot(deployment_id, snapshot_data)
        
        logger.info(f"Snapshot created: {snapshot_id} for deployment {deployment_id}")
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id):
        """
        Restore from snapshot
        
        Args:
            snapshot_id: Snapshot ID
            
        Returns:
            True if successful
        """
        # Get snapshot data
        snapshot = self._get_snapshot(snapshot_id)
        
        if not snapshot:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return False
        
        snapshot_data = json.loads(snapshot['snapshot_data'])
        
        logger.info(f"Restoring snapshot: {snapshot_id}")
        
        # Restore traffic configuration
        self._restore_traffic(snapshot_data['version_id'], snapshot_data['traffic'])
        
        logger.info(f"Snapshot restored: {snapshot_id}")
        return True
    
    def list_snapshots(self, deployment_id=None, limit=10):
        """
        List snapshots
        
        Args:
            deployment_id: Optional deployment ID filter
            limit: Number of records
            
        Returns:
            List of snapshot dictionaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        if deployment_id:
            cursor.execute('''
                SELECT * FROM snapshots
                WHERE deployment_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (deployment_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM snapshots
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        snapshots = []
        for row in results:
            snapshot = dict(row)
            snapshot['snapshot_data'] = json.loads(snapshot['snapshot_data'])
            snapshots.append(snapshot)
        
        return snapshots
    
    def delete_snapshot(self, snapshot_id):
        """
        Delete snapshot
        
        Args:
            snapshot_id: Snapshot ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM snapshots WHERE id = ?', (snapshot_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Snapshot deleted: {snapshot_id}")
    
    def _get_deployment(self, deployment_id):
        """Get deployment details"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, v.version, m.name as model_name
            FROM deployments d
            JOIN versions v ON d.version_id = v.id
            JOIN models m ON v.model_id = m.id
            WHERE d.id = ?
        ''', (deployment_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def _get_traffic_config(self, version_id):
        """Get traffic configuration"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT percentage FROM traffic
            WHERE version_id = ?
        ''', (version_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['percentage'] if result else 0
    
    def _store_snapshot(self, deployment_id, snapshot_data):
        """Store snapshot in database"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        snapshot_json = json.dumps(snapshot_data)
        
        cursor.execute('''
            INSERT INTO snapshots (deployment_id, snapshot_data)
            VALUES (?, ?)
        ''', (deployment_id, snapshot_json))
        
        snapshot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return snapshot_id
    
    def _get_snapshot(self, snapshot_id):
        """Get snapshot from database"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM snapshots WHERE id = ?', (snapshot_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def _restore_traffic(self, version_id, percentage):
        """Restore traffic configuration"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO traffic (version_id, percentage)
            VALUES (?, ?)
        ''', (version_id, percentage))
        
        conn.commit()
        conn.close()
