"""
Gemini Model
Google Gemini LLM integration with version support
"""

import os
import logging
import time
from google import genai
from google.genai import types
from models.base_model import BaseModel

logger = logging.getLogger(__name__)


class GeminiModel(BaseModel):
    """
    Google Gemini model implementation with versioning
    """
    
    def __init__(self, version="1.0.0", model_name="gemini-2.0-flash", api_key=None):
        """
        Initialize Gemini model
        
        Args:
            version: Model version for registry
            model_name: Gemini model name
            api_key: Gemini API key (if None, reads from environment)
        """
        super().__init__(
            name="gemini",
            version=version,
            description=f"Google Gemini LLM {model_name}"
        )
        
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        
        logger.info(f"Gemini model initialized: {model_name} v{version}")
    
    def predict(self, input_data, temperature=1.0, max_tokens=1000, **kwargs):
        """
        Make prediction using Gemini
        
        Args:
            input_data: Input prompt text
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with prediction result and metrics
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        try:
            start_time = time.time()
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=input_data)]
                )
            ]
            
            generate_content_config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generate_content_config
            )
            
            latency = time.time() - start_time
            response_text = response.text
            
            # Simple token counting
            tokens = len(input_data.split()) + len(response_text.split())
            
            logger.info(f"Prediction completed: {tokens} tokens, {latency:.2f}s")
            
            return {
                'prediction': response_text,
                'tokens': tokens,
                'latency': latency,
                'version': self.version,
                'model': self.model_name
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def get_metadata(self):
        """
        Get model metadata
        
        Returns:
            Dictionary with model metadata
        """
        metadata = super().get_metadata()
        metadata.update({
            'model_name': self.model_name,
            'provider': 'Google',
            'type': 'LLM'
        })
        return metadata
