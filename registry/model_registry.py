"""
Model Registry
Central registry for managing AI models
"""

import logging
import json
from storage.database import get_connection

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Central registry for AI models
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize model registry
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Model registry initialized")
    
    def register_model(self, name, description=""):
        """
        Register a new model
        
        Args:
            name: Model name
            description: Model description
            
        Returns:
            Model ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO models (name, description)
                VALUES (?, ?)
            ''', (name, description))
            
            model_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Model registered: {name} (ID: {model_id})")
            return model_id
            
        except sqlite3.IntegrityError:
            # Model already exists
            cursor.execute('SELECT id FROM models WHERE name = ?', (name,))
            model_id = cursor.fetchone()['id']
            logger.info(f"Model already exists: {name} (ID: {model_id})")
            return model_id
            
        finally:
            conn.close()
    
    def register_version(self, model_name, version, status='active', metadata=None):
        """
        Register a model version
        
        Args:
            model_name: Model name
            version: Version string
            status: Version status (active, deprecated, beta)
            metadata: Optional metadata dictionary
            
        Returns:
            Version ID
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        # Get model ID
        cursor.execute('SELECT id FROM models WHERE name = ?', (model_name,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise ValueError(f"Model not found: {model_name}")
        
        model_id = result['id']
        
        # Convert metadata to JSON
        metadata_json = json.dumps(metadata) if metadata else None
        
        try:
            cursor.execute('''
                INSERT INTO versions (model_id, version, status, metadata)
                VALUES (?, ?, ?, ?)
            ''', (model_id, version, status, metadata_json))
            
            version_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Version registered: {model_name} v{version} (ID: {version_id})")
            return version_id
            
        except Exception as e:
            logger.error(f"Error registering version: {e}")
            raise
            
        finally:
            conn.close()
    
    def get_model(self, name):
        """
        Get model by name
        
        Args:
            name: Model name
            
        Returns:
            Model dictionary or None
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM models WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_version(self, model_name, version):
        """
        Get specific model version
        
        Args:
            model_name: Model name
            version: Version string
            
        Returns:
            Version dictionary or None
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.* FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND v.version = ?
        ''', (model_name, version))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            version_dict = dict(result)
            # Parse metadata JSON
            if version_dict.get('metadata'):
                version_dict['metadata'] = json.loads(version_dict['metadata'])
            return version_dict
        return None
    
    def list_models(self):
        """
        List all registered models
        
        Returns:
            List of model dictionaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM models ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def list_versions(self, model_name):
        """
        List all versions for a model
        
        Args:
            model_name: Model name
            
        Returns:
            List of version dictionaries
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.* FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ?
            ORDER BY v.created_at DESC
        ''', (model_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        versions = []
        for row in results:
            version_dict = dict(row)
            if version_dict.get('metadata'):
                version_dict['metadata'] = json.loads(version_dict['metadata'])
            versions.append(version_dict)
        
        return versions
    
    def update_version_status(self, model_name, version, status):
        """
        Update version status
        
        Args:
            model_name: Model name
            version: Version string
            status: New status
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE versions
            SET status = ?
            WHERE id IN (
                SELECT v.id FROM versions v
                JOIN models m ON v.model_id = m.id
                WHERE m.name = ? AND v.version = ?
            )
        ''', (status, model_name, version))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Version status updated: {model_name} v{version} -> {status}")


import sqlite3
