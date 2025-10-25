"""
Model Loader
Dynamically load models by name and version
"""

import logging
from models.gemini_model import GeminiModel

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Load models dynamically by name and version
    """
    
    def __init__(self):
        """Initialize model loader"""
        self.loaded_models = {}
        logger.info("Model loader initialized")
    
    def load_model(self, model_name, version, config=None):
        """
        Load a model by name and version
        
        Args:
            model_name: Model name
            version: Model version
            config: Optional configuration dictionary
            
        Returns:
            Model instance
        """
        cache_key = f"{model_name}:{version}"
        
        # Check if already loaded
        if cache_key in self.loaded_models:
            logger.info(f"Using cached model: {cache_key}")
            return self.loaded_models[cache_key]
        
        # Load model based on name
        if model_name == "gemini":
            model = GeminiModel(version=version)
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Cache the model
        self.loaded_models[cache_key] = model
        logger.info(f"Loaded model: {cache_key}")
        
        return model
    
    def unload_model(self, model_name, version):
        """
        Unload a model from cache
        
        Args:
            model_name: Model name
            version: Model version
        """
        cache_key = f"{model_name}:{version}"
        
        if cache_key in self.loaded_models:
            del self.loaded_models[cache_key]
            logger.info(f"Unloaded model: {cache_key}")
    
    def list_loaded_models(self):
        """
        List all loaded models
        
        Returns:
            List of loaded model keys
        """
        return list(self.loaded_models.keys())
    
    def clear_cache(self):
        """Clear all loaded models from cache"""
        self.loaded_models.clear()
        logger.info("Model cache cleared")
