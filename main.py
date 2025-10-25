"""
Model Registry - Main Demonstration
Shows examples of all model registry features
"""

import os
import time
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

# Load environment variables
load_dotenv()


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_model_registration():
    """Demonstrate model registration"""
    print_section("1. Model Registration")
    
    try:
        db_path = 'demo.db'
        registry = ModelRegistry(db_path)
        
        # Register model
        print("\nRegistering model: gemini")
        model_id = registry.register_model('gemini', 'Google Gemini LLM')
        print(f"   Model registered with ID: {model_id}")
        
        # Register versions
        print("\nRegistering versions:")
        v1_id = registry.register_version('gemini', '1.0.0', 'stable')
        print(f"   v1.0.0 registered (ID: {v1_id})")
        
        v2_id = registry.register_version('gemini', '1.1.0', 'stable')
        print(f"   v1.1.0 registered (ID: {v2_id})")
        
        v3_id = registry.register_version('gemini', '2.0.0', 'beta')
        print(f"   v2.0.0 registered (ID: {v3_id})")
        
        # List models
        models = registry.list_models()
        print(f"\nTotal models registered: {len(models)}")
        
        # List versions
        versions = registry.list_versions('gemini')
        print(f"\nVersions for gemini:")
        for v in versions:
            print(f"   - v{v['version']} ({v['status']})")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_version_management():
    """Demonstrate version management"""
    print_section("2. Version Management")
    
    try:
        version_manager = VersionManager()
        
        # Version comparison
        print("\nVersion Comparison:")
        v1 = "1.0.0"
        v2 = "1.1.0"
        v3 = "2.0.0"
        
        print(f"   Is {v2} newer than {v1}? {version_manager.is_newer(v2, v1)}")
        print(f"   Is {v3} newer than {v2}? {version_manager.is_newer(v3, v2)}")
        
        # Compatibility check
        print(f"\n   Are {v1} and {v2} compatible? {version_manager.is_compatible(v1, v2)}")
        print(f"   Are {v2} and {v3} compatible? {version_manager.is_compatible(v2, v3)}")
        
        # Get latest version
        versions = ["1.0.0", "1.1.0", "2.0.0", "1.2.0"]
        latest = version_manager.get_latest_version(versions)
        print(f"\n   Latest version from {versions}: {latest}")
        
        # Increment version
        print(f"\n   Increment {v1} patch: {version_manager.increment_version(v1, 'patch')}")
        print(f"   Increment {v1} minor: {version_manager.increment_version(v1, 'minor')}")
        print(f"   Increment {v1} major: {version_manager.increment_version(v1, 'major')}")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_deployment():
    """Demonstrate direct deployment"""
    print_section("3. Direct Deployment")
    
    try:
        db_path = 'demo.db'
        deployment_manager = DeploymentManager(db_path)
        
        print("\nDeploying gemini v1.0.0 with direct strategy...")
        deployment_id = deployment_manager.deploy('gemini', '1.0.0', 'direct')
        
        print(f"   Deployment ID: {deployment_id}")
        
        # Get deployment details
        deployment = deployment_manager.get_deployment(deployment_id)
        print(f"\n   Deployment details:")
        print(f"      Model: {deployment['model_name']}")
        print(f"      Version: {deployment['version']}")
        print(f"      Strategy: {deployment['strategy']}")
        print(f"      Status: {deployment['status']}")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_blue_green_deployment():
    """Demonstrate blue-green deployment"""
    print_section("4. Blue-Green Deployment")
    
    try:
        db_path = 'demo.db'
        deployment_manager = DeploymentManager(db_path)
        
        print("\nDeploying gemini v1.1.0 with blue-green strategy...")
        print("   Phase 1: Deploy to green environment (0% traffic)")
        print("   Phase 2: Run health checks")
        print("   Phase 3: Switch traffic to green (100%)")
        
        deployment_id = deployment_manager.deploy('gemini', '1.1.0', 'blue-green')
        
        print(f"\n   Deployment completed: ID {deployment_id}")
        print("   Zero-downtime deployment achieved!")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_canary_deployment():
    """Demonstrate canary deployment"""
    print_section("5. Canary Deployment")
    
    try:
        db_path = 'demo.db'
        deployment_manager = DeploymentManager(db_path)
        
        print("\nDeploying gemini v2.0.0 with canary strategy...")
        print("   Gradual rollout:")
        print("      Stage 1: 10% traffic")
        print("      Stage 2: 50% traffic")
        print("      Stage 3: 100% traffic")
        
        deployment_id = deployment_manager.deploy('gemini', '2.0.0', 'canary')
        
        print(f"\n   Canary deployment completed: ID {deployment_id}")
        print("   Gradual rollout successful!")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_rollback():
    """Demonstrate rollback mechanism"""
    print_section("6. Rollback Mechanism")
    
    try:
        db_path = 'demo.db'
        rollback_manager = RollbackManager(db_path)
        
        print("\nSimulating performance issue with v2.0.0...")
        print("   Detecting high error rate...")
        print("   Triggering automatic rollback...")
        
        # Rollback to previous version
        previous_version = rollback_manager.rollback_to_previous('gemini')
        
        if previous_version:
            print(f"\n   Rolled back to v{previous_version}")
            print("   Service restored successfully!")
        else:
            print("\n   No previous version available")
        
        # Demonstrate rollback to specific version
        print("\n   Rolling back to specific version (v1.0.0)...")
        success = rollback_manager.rollback_to_version('gemini', '1.0.0')
        
        if success:
            print("   Rollback to v1.0.0 successful!")
        
    except Exception as e:
        print(f"\nError: {e}")


def demo_performance_tracking():
    """Demonstrate performance tracking"""
    print_section("7. Performance Tracking")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("\nSkipping (no API key)")
        print("Set GEMINI_API_KEY in .env to run this demo")
        return
    
    try:
        db_path = 'demo.db'
        tracker = PerformanceTracker(db_path)
        
        # Simulate predictions for different versions
        print("\nSimulating predictions for version comparison...")
        
        # Create models
        model_v1 = GeminiModel(version="1.0.0")
        model_v2 = GeminiModel(version="1.1.0")
        
        # Track predictions for v1.0.0
        print("\n   Testing v1.0.0...")
        for i in range(3):
            result = model_v1.predict("Test prompt", max_tokens=20)
            tracker.track_prediction(
                'gemini',
                '1.0.0',
                result['latency'],
                result['tokens']
            )
        
        # Track predictions for v1.1.0
        print("   Testing v1.1.0...")
        for i in range(3):
            result = model_v2.predict("Test prompt", max_tokens=20)
            tracker.track_prediction(
                'gemini',
                '1.1.0',
                result['latency'],
                result['tokens']
            )
        
        # Get metrics
        print("\n   Performance Metrics:")
        
        metrics_v1 = tracker.get_metrics('gemini', '1.0.0')
        print(f"\n   v1.0.0:")
        print(f"      Avg latency: {metrics_v1['avg_latency']:.3f}s")
        print(f"      Avg tokens: {metrics_v1['avg_tokens']:.1f}")
        print(f"      Total requests: {metrics_v1['total_requests']}")
        print(f"      Success rate: {metrics_v1['success_rate']:.1f}%")
        
        metrics_v2 = tracker.get_metrics('gemini', '1.1.0')
        print(f"\n   v1.1.0:")
        print(f"      Avg latency: {metrics_v2['avg_latency']:.3f}s")
        print(f"      Avg tokens: {metrics_v2['avg_tokens']:.1f}")
        print(f"      Total requests: {metrics_v2['total_requests']}")
        print(f"      Success rate: {metrics_v2['success_rate']:.1f}%")
        
        # Compare versions
        comparison = tracker.compare_versions('gemini', '1.0.0', '1.1.0')
        print(f"\n   Comparison (v1.1.0 vs v1.0.0):")
        print(f"      Latency diff: {comparison['latency_diff']:.3f}s")
        print(f"      Tokens diff: {comparison['tokens_diff']:.1f}")
        
    except Exception as e:
        print(f"\nError: {e}")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  Model Registry - Demonstration")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\nWarning: GEMINI_API_KEY not found in environment!")
        print("Some demos will be skipped.")
        print("Create a .env file with your API key to run all demos.")
    
    try:
        # Clean up old database
        db_path = 'demo.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        
        init_database(db_path)
        
        # Run demonstrations
        demo_model_registration()
        demo_version_management()
        demo_deployment()
        demo_blue_green_deployment()
        demo_canary_deployment()
        demo_rollback()
        demo_performance_tracking()
        
        print("\n" + "=" * 70)
        print("  All Demonstrations Completed!")
        print("=" * 70)
        print("\nKey Concepts Demonstrated:")
        print("  1. Model Registration - Register models and versions")
        print("  2. Version Management - Semantic versioning")
        print("  3. Direct Deployment - Immediate replacement")
        print("  4. Blue-Green Deployment - Zero-downtime switch")
        print("  5. Canary Deployment - Gradual rollout")
        print("  6. Rollback Mechanism - Safe recovery")
        print("  7. Performance Tracking - Monitor metrics")
        print("\nTo run Flask API:")
        print("  python api/app.py")
        print("\nTo run tests:")
        print("  python tests.py")
        print()
        
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        
    except KeyboardInterrupt:
        print("\n\nDemonstration interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
