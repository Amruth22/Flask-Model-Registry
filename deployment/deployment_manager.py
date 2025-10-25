"""
Deployment Manager
Manage model deployments with different strategies
"""

import logging
from datetime import datetime
from storage.database import get_connection
from deployment.deployment_strategy import DirectDeployment, BlueGreenDeployment, CanaryDeployment

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Manage model deployments
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize deployment manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.strategies = {
            'direct': DirectDeployment(),
            'blue-green': BlueGreenDeployment(),
            'canary': CanaryDeployment()
        }
        logger.info("Deployment manager initialized")
    
    def deploy(self, model_name, version, strategy='direct'):
        """
        Deploy a model version
        
        Args:
            model_name: Model name
            version: Version to deploy
            strategy: Deployment strategy ('direct', 'blue-green', 'canary')
            
        Returns:
            Deployment ID
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Get version ID
        version_id = self._get_version_id(model_name, version)
        if not version_id:
            raise ValueError(f"Version not found: {model_name} v{version}")
        
        # Create deployment record
        deployment_id = self._create_deployment(version_id, strategy)
        
        # Execute deployment strategy
        deployment_strategy = self.strategies[strategy]
        success = deployment_strategy.deploy(model_name, version, deployment_id, self.db_path)
        
        # Update deployment status
        if success:
            self._update_deployment_status(deployment_id, 'completed')
            logger.info(f"Deployment completed: {model_name} v{version} ({strategy})")
        else:
            self._update_deployment_status(deployment_id, 'failed')
            logger.error(f"Deployment failed: {model_name} v{version}")
        
        return deployment_id
    
    def _get_version_id(self, model_name, version):
        """Get version ID from database"""
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
    
    def _create_deployment(self, version_id, strategy):
        """Create deployment record"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deployments (version_id, strategy, status)
            VALUES (?, ?, 'pending')
        ''', (version_id, strategy))
        
        deployment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return deployment_id
    
    def _update_deployment_status(self, deployment_id, status):
        """Update deployment status"""
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE deployments
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, deployment_id))
        
        conn.commit()
        conn.close()
    
    def get_deployment(self, deployment_id):
        """
        Get deployment details
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Deployment dictionary
        """
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
    
    def list_deployments(self, model_name=None, limit=10):
        """
        List deployments
        
        Args:
            model_name: Optional model name filter
            limit: Number of records
            
        Returns:
            List of deployment dictionaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        if model_name:
            cursor.execute('''
                SELECT d.*, v.version, m.name as model_name
                FROM deployments d
                JOIN versions v ON d.version_id = v.id
                JOIN models m ON v.model_id = m.id
                WHERE m.name = ?
                ORDER BY d.deployed_at DESC
                LIMIT ?
            ''', (model_name, limit))
        else:
            cursor.execute('''
                SELECT d.*, v.version, m.name as model_name
                FROM deployments d
                JOIN versions v ON d.version_id = v.id
                JOIN models m ON v.model_id = m.id
                ORDER BY d.deployed_at DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_active_deployment(self, model_name):
        """
        Get currently active deployment
        
        Args:
            model_name: Model name
            
        Returns:
            Active deployment dictionary or None
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, v.version
            FROM deployments d
            JOIN versions v ON d.version_id = v.id
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND d.status = 'completed'
            ORDER BY d.deployed_at DESC
            LIMIT 1
        ''', (model_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
