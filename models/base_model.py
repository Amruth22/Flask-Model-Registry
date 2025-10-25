"""
Base Model
Abstract base class for all AI models
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for AI models with version support
    """
    
    def __init__(self, name, version, description=""):
        """
        Initialize base model
        
        Args:
            name: Model name
            version: Model version (semantic versioning)
            description: Model description
        """
        self.name = name
        self.version = version
        self.description = description
        logger.info(f"Model initialized: {name} v{version}")
    
    @abstractmethod
    def predict(self, input_data, **kwargs):
        """
        Make prediction
        
        Args:
            input_data: Input data for prediction
            **kwargs: Additional parameters
            
        Returns:
            Prediction result
        """
        pass
    
    def get_version(self):
        """
        Get model version
        
        Returns:
            Version string
        """
        return self.version
    
    def get_metadata(self):
        """
        Get model metadata
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description
        }
    
    def validate_input(self, input_data):
        """
        Validate input data
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        return input_data is not None
