"""
Health Checker
Check model health and availability
"""

import logging
import time

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Check model health
    """
    
    def __init__(self):
        """Initialize health checker"""
        logger.info("Health checker initialized")
    
    def check_availability(self, model, timeout=5):
        """
        Check if model is available
        
        Args:
            model: Model instance
            timeout: Timeout in seconds
            
        Returns:
            True if available
        """
        try:
            start_time = time.time()
            
            # Try a simple prediction
            result = model.predict("health check", max_tokens=10)
            
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                logger.warning(f"Health check timeout: {elapsed:.2f}s")
                return False
            
            logger.info(f"Health check passed: {elapsed:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def check_response_time(self, model, threshold=2.0):
        """
        Check if response time is acceptable
        
        Args:
            model: Model instance
            threshold: Maximum acceptable latency in seconds
            
        Returns:
            True if response time is acceptable
        """
        try:
            result = model.predict("test", max_tokens=10)
            latency = result.get('latency', 0)
            
            if latency > threshold:
                logger.warning(f"Response time too high: {latency:.2f}s")
                return False
            
            logger.info(f"Response time OK: {latency:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Response time check failed: {e}")
            return False
    
    def check_error_rate(self, model, num_requests=5, max_errors=1):
        """
        Check error rate
        
        Args:
            model: Model instance
            num_requests: Number of test requests
            max_errors: Maximum acceptable errors
            
        Returns:
            True if error rate is acceptable
        """
        errors = 0
        
        for i in range(num_requests):
            try:
                model.predict(f"test {i}", max_tokens=10)
            except Exception as e:
                errors += 1
                logger.warning(f"Request {i} failed: {e}")
        
        error_rate = (errors / num_requests) * 100
        
        if errors > max_errors:
            logger.warning(f"Error rate too high: {error_rate:.1f}%")
            return False
        
        logger.info(f"Error rate OK: {error_rate:.1f}%")
        return True
    
    def comprehensive_check(self, model):
        """
        Run comprehensive health check
        
        Args:
            model: Model instance
            
        Returns:
            Dictionary with check results
        """
        results = {
            'available': self.check_availability(model),
            'response_time_ok': self.check_response_time(model),
            'error_rate_ok': self.check_error_rate(model),
            'overall_healthy': False
        }
        
        # Overall health is true if all checks pass
        results['overall_healthy'] = all([
            results['available'],
            results['response_time_ok'],
            results['error_rate_ok']
        ])
        
        return results
