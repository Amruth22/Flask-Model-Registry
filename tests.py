"""
Comprehensive Unit Tests for Model Registry
Tests registration, versioning, deployment, rollback, and tracking

TESTING APPROACH:
- test_10_health_checks: MOCKED (prevents quota exhaustion)
- All other tests: No API calls or mocked internally
- Handles free API tier limits (10 requests/minute)
"""

import unittest
import os
from unittest.mock import patch, Mock
from dotenv import load_dotenv

from storage.database import init_database
from models.gemini_model import GeminiModel
from registry.model_registry import ModelRegistry
from registry.version_manager import VersionManager
from registry.metadata_store import MetadataStore
from deployment.deployment_manager import DeploymentManager
from rollback.rollback_manager import RollbackManager
from rollback.snapshot_manager import SnapshotManager
from tracking.performance_tracker import PerformanceTracker
from deployment.health_checker import HealthChecker

# Load environment variables
load_dotenv()


class ModelRegistryTestCase(unittest.TestCase):
    """Unit tests for Model Registry"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration"""
        print("\n" + "=" * 60)
        print("Model Registry - Unit Test Suite")
        print("=" * 60)
        print("Testing: Registry, Versioning, Deployment, Rollback, Tracking")
        print("=" * 60 + "\n")
        
        # Use test database
        cls.db_path = 'test_registry.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        
        init_database(cls.db_path)
        
        # Check for API key
        cls.has_api_key = bool(os.getenv('GEMINI_API_KEY'))
        if not cls.has_api_key:
            print("Warning: GEMINI_API_KEY not found. Some tests will be skipped.\n")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
    
    # Test 1: Model Registration
    def test_01_model_registration(self):
        """Test model registration"""
        print("\n1. Testing model registration...")
        
        registry = ModelRegistry(self.db_path)
        
        # Register model
        model_id = registry.register_model('gemini', 'Google Gemini LLM')
        self.assertIsNotNone(model_id)
        print(f"   Model registered: ID {model_id}")
        
        # Get model
        model = registry.get_model('gemini')
        self.assertIsNotNone(model)
        self.assertEqual(model['name'], 'gemini')
        print(f"   Model retrieved: {model['name']}")
        
        # List models
        models = registry.list_models()
        self.assertGreaterEqual(len(models), 1)
        print(f"   Total models: {len(models)}")
    
    # Test 2: Version Management
    def test_02_version_management(self):
        """Test version registration and listing"""
        print("\n2. Testing version management...")
        
        registry = ModelRegistry(self.db_path)
        
        # Register versions
        v1_id = registry.register_version('gemini', '1.0.0', 'stable')
        v2_id = registry.register_version('gemini', '1.1.0', 'stable')
        v3_id = registry.register_version('gemini', '2.0.0', 'beta')
        
        self.assertIsNotNone(v1_id)
        self.assertIsNotNone(v2_id)
        self.assertIsNotNone(v3_id)
        
        print(f"   Versions registered: v1.0.0, v1.1.0, v2.0.0")
        
        # List versions
        versions = registry.list_versions('gemini')
        self.assertEqual(len(versions), 3)
        print(f"   Total versions: {len(versions)}")
        
        # Get specific version
        version = registry.get_version('gemini', '1.0.0')
        self.assertIsNotNone(version)
        self.assertEqual(version['version'], '1.0.0')
        print(f"   Retrieved version: {version['version']}")
    
    # Test 3: Version Comparison
    def test_03_version_comparison(self):
        """Test version comparison logic"""
        print("\n3. Testing version comparison...")
        
        version_manager = VersionManager()
        
        # Test is_newer
        self.assertTrue(version_manager.is_newer('1.1.0', '1.0.0'))
        self.assertTrue(version_manager.is_newer('2.0.0', '1.1.0'))
        self.assertFalse(version_manager.is_newer('1.0.0', '1.1.0'))
        print("   Version comparison: OK")
        
        # Test is_compatible
        self.assertTrue(version_manager.is_compatible('1.0.0', '1.1.0'))
        self.assertFalse(version_manager.is_compatible('1.1.0', '2.0.0'))
        print("   Compatibility check: OK")
        
        # Test get_latest_version
        versions = ['1.0.0', '1.1.0', '2.0.0', '1.2.0']
        latest = version_manager.get_latest_version(versions)
        self.assertEqual(latest, '2.0.0')
        print(f"   Latest version: {latest}")
    
    # Test 4: Deployment
    def test_04_deployment(self):
        """Test model deployment"""
        print("\n4. Testing deployment...")
        
        deployment_manager = DeploymentManager(self.db_path)
        
        # Deploy with direct strategy
        deployment_id = deployment_manager.deploy('gemini', '1.0.0', 'direct')
        self.assertIsNotNone(deployment_id)
        print(f"   Deployment ID: {deployment_id}")
        
        # Get deployment
        deployment = deployment_manager.get_deployment(deployment_id)
        self.assertIsNotNone(deployment)
        self.assertEqual(deployment['strategy'], 'direct')
        self.assertEqual(deployment['status'], 'completed')
        print(f"   Deployment status: {deployment['status']}")
    
    # Test 5: Blue-Green Deployment
    def test_05_blue_green_deployment(self):
        """Test blue-green deployment strategy"""
        print("\n5. Testing blue-green deployment...")
        
        deployment_manager = DeploymentManager(self.db_path)
        
        # Deploy with blue-green strategy
        deployment_id = deployment_manager.deploy('gemini', '1.1.0', 'blue-green')
        self.assertIsNotNone(deployment_id)
        print(f"   Blue-green deployment ID: {deployment_id}")
        
        # Verify deployment
        deployment = deployment_manager.get_deployment(deployment_id)
        self.assertEqual(deployment['strategy'], 'blue-green')
        self.assertEqual(deployment['status'], 'completed')
        print("   Blue-green deployment: Successful")
    
    # Test 6: Canary Deployment
    def test_06_canary_deployment(self):
        """Test canary deployment strategy"""
        print("\n6. Testing canary deployment...")
        
        deployment_manager = DeploymentManager(self.db_path)
        
        # Deploy with canary strategy
        deployment_id = deployment_manager.deploy('gemini', '2.0.0', 'canary')
        self.assertIsNotNone(deployment_id)
        print(f"   Canary deployment ID: {deployment_id}")
        
        # Verify deployment
        deployment = deployment_manager.get_deployment(deployment_id)
        self.assertEqual(deployment['strategy'], 'canary')
        self.assertEqual(deployment['status'], 'completed')
        print("   Canary deployment: Successful")
    
    # Test 7: Rollback
    def test_07_rollback(self):
        """Test rollback mechanism"""
        print("\n7. Testing rollback...")
        
        rollback_manager = RollbackManager(self.db_path)
        
        # Rollback to previous version
        previous_version = rollback_manager.rollback_to_previous('gemini')
        self.assertIsNotNone(previous_version)
        print(f"   Rolled back to: v{previous_version}")
        
        # Rollback to specific version
        success = rollback_manager.rollback_to_version('gemini', '1.0.0')
        self.assertTrue(success)
        print("   Rollback to v1.0.0: Successful")
    
    # Test 8: Snapshot Management
    def test_08_snapshot_management(self):
        """Test snapshot creation and restoration"""
        print("\n8. Testing snapshot management...")
        
        snapshot_manager = SnapshotManager(self.db_path)
        
        # Get a deployment ID
        deployment_manager = DeploymentManager(self.db_path)
        deployments = deployment_manager.list_deployments(limit=1)
        
        if deployments:
            deployment_id = deployments[0]['id']
            
            # Create snapshot
            snapshot_id = snapshot_manager.create_snapshot(deployment_id)
            self.assertIsNotNone(snapshot_id)
            print(f"   Snapshot created: ID {snapshot_id}")
            
            # List snapshots
            snapshots = snapshot_manager.list_snapshots(deployment_id)
            self.assertGreaterEqual(len(snapshots), 1)
            print(f"   Total snapshots: {len(snapshots)}")
            
            # Restore snapshot
            success = snapshot_manager.restore_snapshot(snapshot_id)
            self.assertTrue(success)
            print("   Snapshot restored: Successful")
        else:
            print("   Skipped (no deployments)")
    
    # Test 9: Performance Tracking
    def test_09_performance_tracking(self):
        """Test performance tracking"""
        print("\n9. Testing performance tracking...")
        
        if not self.has_api_key:
            print("   Skipped (no API key)")
            self.skipTest("No API key available")
        
        tracker = PerformanceTracker(self.db_path)
        
        # Create model and make predictions
        model = GeminiModel(version="1.0.0")
        
        # Track predictions
        for i in range(3):
            result = model.predict("Test", max_tokens=10)
            tracker.track_prediction(
                'gemini',
                '1.0.0',
                result['latency'],
                result['tokens']
            )
        
        # Get metrics
        metrics = tracker.get_metrics('gemini', '1.0.0')
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['total_requests'], 3)
        
        print(f"   Tracked predictions: {metrics['total_requests']}")
        print(f"   Avg latency: {metrics['avg_latency']:.3f}s")
        print(f"   Success rate: {metrics['success_rate']:.1f}%")
    
    # Test 10: Health Checks
    def test_10_health_checks(self):
        """Test health checking (MOCKED to prevent quota exhaustion)"""
        print("\n10. Testing health checks (mocked)...")

        # Mock the model prediction to prevent API calls
        with patch('models.gemini_model.GeminiModel.predict') as mock_predict:
            # Setup mock response
            mock_predict.return_value = {
                'prediction': 'test output',
                'latency': 0.5,
                'tokens': 50,
                'version': '1.0.0'
            }

            health_checker = HealthChecker()
            model = GeminiModel(version="1.0.0")

            # Check availability (mocked)
            available = health_checker.check_availability(model)
            self.assertTrue(available)
            print("   Availability check: Passed (mocked)")

            # Check response time (mocked)
            response_time_ok = health_checker.check_response_time(model)
            self.assertTrue(response_time_ok)
            print("   Response time check: Passed (mocked)")

            # Comprehensive check (mocked)
            results = health_checker.comprehensive_check(model)
            self.assertTrue(results['overall_healthy'])
            print("   Comprehensive check: Passed (mocked)")


def run_tests():
    """Run all unit tests"""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(ModelRegistryTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\nALL TESTS PASSED!")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Model Registry - Unit Test Suite")
    print("=" * 60)
    
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
