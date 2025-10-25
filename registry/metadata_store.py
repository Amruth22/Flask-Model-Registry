"""
Metadata Store
Store and retrieve model metadata
"""

import logging
import json
from storage.database import get_connection

logger = logging.getLogger(__name__)


class MetadataStore:
    """
    Store model metadata
    """
    
    def __init__(self, db_path='model_registry.db'):
        """
        Initialize metadata store
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        logger.info("Metadata store initialized")
    
    def store_metadata(self, model_name, version, metadata):
        """
        Store metadata for a model version
        
        Args:
            model_name: Model name
            version: Version string
            metadata: Metadata dictionary
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata)
        
        cursor.execute('''
            UPDATE versions
            SET metadata = ?
            WHERE id IN (
                SELECT v.id FROM versions v
                JOIN models m ON v.model_id = m.id
                WHERE m.name = ? AND v.version = ?
            )
        ''', (metadata_json, model_name, version))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Metadata stored: {model_name} v{version}")
    
    def get_metadata(self, model_name, version):
        """
        Get metadata for a model version
        
        Args:
            model_name: Model name
            version: Version string
            
        Returns:
            Metadata dictionary or None
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.metadata FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ? AND v.version = ?
        ''', (model_name, version))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result['metadata']:
            return json.loads(result['metadata'])
        return None
    
    def update_metadata(self, model_name, version, updates):
        """
        Update metadata fields
        
        Args:
            model_name: Model name
            version: Version string
            updates: Dictionary of fields to update
        """
        # Get current metadata
        current = self.get_metadata(model_name, version) or {}
        
        # Merge updates
        current.update(updates)
        
        # Store updated metadata
        self.store_metadata(model_name, version, current)
        
        logger.info(f"Metadata updated: {model_name} v{version}")
    
    def add_tag(self, model_name, version, tag):
        """
        Add tag to model version
        
        Args:
            model_name: Model name
            version: Version string
            tag: Tag to add
        """
        metadata = self.get_metadata(model_name, version) or {}
        
        tags = metadata.get('tags', [])
        if tag not in tags:
            tags.append(tag)
            metadata['tags'] = tags
            self.store_metadata(model_name, version, metadata)
            logger.info(f"Tag added: {model_name} v{version} -> {tag}")
    
    def remove_tag(self, model_name, version, tag):
        """
        Remove tag from model version
        
        Args:
            model_name: Model name
            version: Version string
            tag: Tag to remove
        """
        metadata = self.get_metadata(model_name, version) or {}
        
        tags = metadata.get('tags', [])
        if tag in tags:
            tags.remove(tag)
            metadata['tags'] = tags
            self.store_metadata(model_name, version, metadata)
            logger.info(f"Tag removed: {model_name} v{version} -> {tag}")
    
    def get_versions_by_tag(self, model_name, tag):
        """
        Get versions with specific tag
        
        Args:
            model_name: Model name
            tag: Tag to search for
            
        Returns:
            List of version strings
        """
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.version, v.metadata FROM versions v
            JOIN models m ON v.model_id = m.id
            WHERE m.name = ?
        ''', (model_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        versions = []
        for row in results:
            if row['metadata']:
                metadata = json.loads(row['metadata'])
                if tag in metadata.get('tags', []):
                    versions.append(row['version'])
        
        return versions
