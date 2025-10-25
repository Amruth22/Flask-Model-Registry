"""
Flask API for Model Registry
Provides REST API for model management, deployment, and monitoring
"""

from flask import Flask, request, jsonify
import logging
import os
from dotenv import load_dotenv

from storage.database import init_database
from models.gemini_model import GeminiModel
from models.model_loader import ModelLoader
from registry.model_registry import ModelRegistry
from registry.version_manager import VersionManager
from registry.metadata_store import MetadataStore
from deployment.deployment_manager import DeploymentManager
from deployment.health_checker import HealthChecker
from rollback.rollback_manager import RollbackManager
from rollback.snapshot_manager import SnapshotManager
from tracking.performance_tracker import PerformanceTracker
from tracking.metrics_collector import MetricsCollector
from tracking.alerting import AlertingSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize database
db_path = os.getenv('DATABASE_PATH', 'model_registry.db')
init_database(db_path)

# Initialize components
model_registry = ModelRegistry(db_path)
version_manager = VersionManager()
metadata_store = MetadataStore(db_path)
deployment_manager = DeploymentManager(db_path)
health_checker = HealthChecker()
rollback_manager = RollbackManager(db_path)
snapshot_manager = SnapshotManager(db_path)
performance_tracker = PerformanceTracker(db_path)
metrics_collector = MetricsCollector(db_path)
alerting_system = AlertingSystem(db_path)
model_loader = ModelLoader()


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Model Registry API',
        'version': '1.0.0',
        'features': [
            'Model Registry',
            'Version Control',
            'Deployment Automation',
            'Rollback Mechanisms',
            'Performance Tracking'
        ],
        'endpoints': {
            'models': '/api/models',
            'versions': '/api/models/{name}/versions',
            'deploy': '/api/models/{name}/deploy',
            'rollback': '/api/models/{name}/rollback',
            'metrics': '/api/models/{name}/metrics'
        }
    })


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})


@app.route('/api/models/register', methods=['POST'])
def register_model():
    """Register a new model"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Model name required'}), 400
    
    try:
        model_id = model_registry.register_model(
            data['name'],
            data.get('description', '')
        )
        
        return jsonify({
            'status': 'success',
            'model_id': model_id,
            'name': data['name']
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering model: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models', methods=['GET'])
def list_models():
    """List all models"""
    try:
        models = model_registry.list_models()
        return jsonify({
            'status': 'success',
            'models': models,
            'count': len(models)
        })
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/versions/register', methods=['POST'])
def register_version(model_name):
    """Register a model version"""
    data = request.get_json()
    
    if not data or 'version' not in data:
        return jsonify({'error': 'Version required'}), 400
    
    try:
        version_id = model_registry.register_version(
            model_name,
            data['version'],
            data.get('status', 'active'),
            data.get('metadata')
        )
        
        return jsonify({
            'status': 'success',
            'version_id': version_id,
            'model': model_name,
            'version': data['version']
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering version: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/versions', methods=['GET'])
def list_versions(model_name):
    """List all versions for a model"""
    try:
        versions = model_registry.list_versions(model_name)
        return jsonify({
            'status': 'success',
            'model': model_name,
            'versions': versions,
            'count': len(versions)
        })
    except Exception as e:
        logger.error(f"Error listing versions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/deploy', methods=['POST'])
def deploy_model(model_name):
    """Deploy a model version"""
    data = request.get_json()
    
    if not data or 'version' not in data:
        return jsonify({'error': 'Version required'}), 400
    
    try:
        deployment_id = deployment_manager.deploy(
            model_name,
            data['version'],
            data.get('strategy', 'direct')
        )
        
        # Create snapshot
        snapshot_id = snapshot_manager.create_snapshot(deployment_id)
        
        return jsonify({
            'status': 'success',
            'deployment_id': deployment_id,
            'snapshot_id': snapshot_id,
            'model': model_name,
            'version': data['version'],
            'strategy': data.get('strategy', 'direct')
        })
        
    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/predict', methods=['POST'])
def predict(model_name):
    """Make prediction with model"""
    data = request.get_json()
    
    if not data or 'input' not in data:
        return jsonify({'error': 'Input required'}), 400
    
    try:
        # Get active deployment
        deployment = deployment_manager.get_active_deployment(model_name)
        
        if not deployment:
            return jsonify({'error': 'No active deployment'}), 404
        
        version = deployment['version']
        
        # Load model
        model = model_loader.load_model(model_name, version)
        
        # Make prediction
        result = model.predict(data['input'])
        
        # Track performance
        performance_tracker.track_prediction(
            model_name,
            version,
            result['latency'],
            result['tokens']
        )
        
        return jsonify({
            'status': 'success',
            'prediction': result['prediction'],
            'version': version,
            'latency': result['latency'],
            'tokens': result['tokens']
        })
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/rollback', methods=['POST'])
def rollback_model(model_name):
    """Rollback model to previous version"""
    data = request.get_json() or {}
    
    try:
        if 'version' in data:
            # Rollback to specific version
            success = rollback_manager.rollback_to_version(model_name, data['version'])
            version = data['version']
        else:
            # Rollback to previous version
            version = rollback_manager.rollback_to_previous(model_name)
            success = version is not None
        
        if success:
            return jsonify({
                'status': 'success',
                'model': model_name,
                'version': version,
                'message': f'Rolled back to v{version}'
            })
        else:
            return jsonify({'error': 'Rollback failed'}), 500
        
    except Exception as e:
        logger.error(f"Error rolling back: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/metrics', methods=['GET'])
def get_metrics(model_name):
    """Get performance metrics"""
    version = request.args.get('version')
    
    if not version:
        return jsonify({'error': 'Version parameter required'}), 400
    
    try:
        metrics = performance_tracker.get_metrics(model_name, version)
        
        if not metrics:
            return jsonify({'error': 'Metrics not found'}), 404
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/models/<model_name>/compare', methods=['GET'])
def compare_versions(model_name):
    """Compare two versions"""
    version1 = request.args.get('version1')
    version2 = request.args.get('version2')
    
    if not version1 or not version2:
        return jsonify({'error': 'Both version1 and version2 required'}), 400
    
    try:
        comparison = performance_tracker.compare_versions(model_name, version1, version2)
        
        if not comparison:
            return jsonify({'error': 'Comparison failed'}), 404
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        })
        
    except Exception as e:
        logger.error(f"Error comparing versions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/deployments', methods=['GET'])
def list_deployments():
    """List deployments"""
    model_name = request.args.get('model')
    limit = int(request.args.get('limit', 10))
    
    try:
        deployments = deployment_manager.list_deployments(model_name, limit)
        
        return jsonify({
            'status': 'success',
            'deployments': deployments,
            'count': len(deployments)
        })
        
    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts"""
    model_name = request.args.get('model')
    version = request.args.get('version')
    severity = request.args.get('severity')
    limit = int(request.args.get('limit', 10))
    
    try:
        alerts = alerting_system.get_alerts(model_name, version, severity, limit)
        
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("Model Registry - Flask API")
    print("=" * 60)
    print(f"Starting on port {port}")
    print("Features:")
    print("  - Model Registry")
    print("  - Version Control")
    print("  - Deployment Automation")
    print("  - Rollback Mechanisms")
    print("  - Performance Tracking")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
