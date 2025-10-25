"""
Model Store
Store and retrieve model artifacts
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


class ModelStore:
    """
    Store model artifacts and configurations
    """
    
    def __init__(self, store_path='./model_store'):
        """
        Initialize model store
        
        Args:
            store_path: Path to model storage directory
        """
        self.store_path = store_path
        
        # Create store directory if it doesn't exist
        if not os.path.exists(store_path):
            os.makedirs(store_path)
            logger.info(f"Created model store: {store_path}")
    
    def save_model_config(self, model_name, version, config):
        """
        Save model configuration
        
        Args:
            model_name: Model name
            version: Model version
            config: Configuration dictionary
            
        Returns:
            Path to saved config
        """
        model_dir = os.path.join(self.store_path, model_name, version)
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        config_path = os.path.join(model_dir, 'config.json')
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved config: {config_path}")
        return config_path
    
    def load_model_config(self, model_name, version):
        """
        Load model configuration
        
        Args:
            model_name: Model name
            version: Model version
            
        Returns:
            Configuration dictionary or None
        """
        config_path = os.path.join(self.store_path, model_name, version, 'config.json')
        
        if not os.path.exists(config_path):
            logger.warning(f"Config not found: {config_path}")
            return None
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded config: {config_path}")
        return config
    
    def delete_model_version(self, model_name, version):
        """
        Delete model version artifacts
        
        Args:
            model_name: Model name
            version: Model version
        """
        model_dir = os.path.join(self.store_path, model_name, version)
        
        if os.path.exists(model_dir):
            import shutil
            shutil.rmtree(model_dir)
            logger.info(f"Deleted model version: {model_dir}")
    
    def list_model_versions(self, model_name):
        """
        List all versions for a model
        
        Args:
            model_name: Model name
            
        Returns:
            List of version strings
        """
        model_dir = os.path.join(self.store_path, model_name)
        
        if not os.path.exists(model_dir):
            return []
        
        versions = [d for d in os.listdir(model_dir) 
                   if os.path.isdir(os.path.join(model_dir, d))]
        
        return sorted(versions)
