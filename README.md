# Model Registry

Educational Flask application demonstrating **AI model registry**, **version control**, **deployment automation** with blue-green and canary strategies, **rollback mechanisms**, and **performance tracking** with **SQLite storage**.

## Features

### Model Registry
- **Model Registration** - Register AI models centrally
- **Version Management** - Semantic versioning (MAJOR.MINOR.PATCH)
- **Metadata Storage** - Store model metadata and tags
- **Model Discovery** - List and search models
- **Version History** - Track all model versions

### Version Control
- **Semantic Versioning** - Standard version format
- **Version Comparison** - Compare version numbers
- **Compatibility Checking** - Check version compatibility
- **Latest Version** - Get latest version automatically
- **Version Tagging** - Tag versions (stable, beta, experimental)

### Deployment Automation
- **Direct Deployment** - Immediate replacement
- **Blue-Green Deployment** - Zero-downtime switch
- **Canary Deployment** - Gradual rollout (10% → 50% → 100%)
- **Deployment History** - Track all deployments
- **Health Checks** - Automatic health validation

### Rollback Mechanisms
- **Automatic Rollback** - Rollback on errors
- **Manual Rollback** - Rollback to specific version
- **Snapshot Management** - Create and restore snapshots
- **Rollback History** - Track rollback operations
- **Safe Recovery** - Ensure service continuity

### Performance Tracking
- **Latency Monitoring** - Track response times
- **Success Rate** - Monitor prediction success
- **Token Usage** - Track token consumption
- **Version Comparison** - Compare version performance
- **Alerting** - Alert on performance degradation

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Amruth22/Flask-Model-Registry.git
cd Flask-Model-Registry
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get API key from: https://makersuite.google.com/app/apikey
```

### 5. Run Demonstrations
```bash
python main.py
```

### 6. Run Flask API
```bash
python api/app.py
```

### 7. Run Tests
```bash
python tests.py
```

## Project Structure

```
Flask-Model-Registry/
│
├── models/
│   ├── base_model.py           # Base model interface
│   ├── gemini_model.py         # Gemini integration
│   └── model_loader.py         # Dynamic model loading
│
├── registry/
│   ├── model_registry.py       # Model registration
│   ├── version_manager.py      # Version control
│   └── metadata_store.py       # Metadata management
│
├── deployment/
│   ├── deployment_manager.py   # Deployment orchestration
│   ├── deployment_strategy.py  # Deployment strategies
│   └── health_checker.py       # Health checks
│
├── rollback/
│   ├── rollback_manager.py     # Rollback management
│   └── snapshot_manager.py     # Snapshot operations
│
├── tracking/
│   ├── performance_tracker.py  # Performance metrics
│   ├── metrics_collector.py    # Metrics collection
│   └── alerting.py             # Alerting system
│
├── storage/
│   ├── database.py             # SQLite setup
│   └── model_store.py          # Model artifacts
│
├── api/
│   └── app.py                  # Flask REST API
│
├── main.py                     # Demonstrations
├── tests.py                    # 10 unit tests
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Usage Examples

### Model Registration

```python
from registry.model_registry import ModelRegistry

# Initialize registry
registry = ModelRegistry()

# Register model
model_id = registry.register_model('gemini', 'Google Gemini LLM')

# Register version
version_id = registry.register_version('gemini', '1.0.0', 'stable')

# List versions
versions = registry.list_versions('gemini')
```

### Version Management

```python
from registry.version_manager import VersionManager

manager = VersionManager()

# Compare versions
is_newer = manager.is_newer('1.1.0', '1.0.0')  # True

# Check compatibility
compatible = manager.is_compatible('1.0.0', '1.1.0')  # True (same major)

# Get latest version
latest = manager.get_latest_version(['1.0.0', '1.1.0', '2.0.0'])  # '2.0.0'

# Increment version
new_version = manager.increment_version('1.0.0', 'minor')  # '1.1.0'
```

### Deployment

```python
from deployment.deployment_manager import DeploymentManager

manager = DeploymentManager()

# Direct deployment
deployment_id = manager.deploy('gemini', '1.0.0', 'direct')

# Blue-green deployment
deployment_id = manager.deploy('gemini', '1.1.0', 'blue-green')

# Canary deployment
deployment_id = manager.deploy('gemini', '2.0.0', 'canary')
```

### Rollback

```python
from rollback.rollback_manager import RollbackManager

manager = RollbackManager()

# Rollback to previous version
previous_version = manager.rollback_to_previous('gemini')

# Rollback to specific version
success = manager.rollback_to_version('gemini', '1.0.0')

# Automatic rollback on errors
triggered = manager.auto_rollback_on_error('gemini', error_threshold=0.1)
```

### Performance Tracking

```python
from tracking.performance_tracker import PerformanceTracker

tracker = PerformanceTracker()

# Track prediction
tracker.track_prediction('gemini', '1.0.0', latency=1.5, tokens=100)

# Get metrics
metrics = tracker.get_metrics('gemini', '1.0.0')
print(f"Avg latency: {metrics['avg_latency']:.3f}s")
print(f"Success rate: {metrics['success_rate']:.1f}%")

# Compare versions
comparison = tracker.compare_versions('gemini', '1.0.0', '1.1.0')
```

## Flask API Endpoints

### Model Operations
- `POST /api/models/register` - Register new model
- `GET /api/models` - List all models
- `POST /api/models/{name}/versions/register` - Register version
- `GET /api/models/{name}/versions` - List versions

### Deployment Operations
- `POST /api/models/{name}/deploy` - Deploy model
- `GET /api/deployments` - List deployments
- `POST /api/models/{name}/predict` - Make prediction

### Rollback Operations
- `POST /api/models/{name}/rollback` - Rollback model

### Monitoring Operations
- `GET /api/models/{name}/metrics` - Get metrics
- `GET /api/models/{name}/compare` - Compare versions
- `GET /api/alerts` - Get alerts

## API Examples

### Register Model
```bash
curl -X POST http://localhost:5000/api/models/register \
  -H "Content-Type: application/json" \
  -d '{"name": "gemini", "description": "Google Gemini LLM"}'
```

### Register Version
```bash
curl -X POST http://localhost:5000/api/models/gemini/versions/register \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0", "status": "stable"}'
```

### Deploy Model
```bash
curl -X POST http://localhost:5000/api/models/gemini/deploy \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0", "strategy": "blue-green"}'
```

### Make Prediction
```bash
curl -X POST http://localhost:5000/api/models/gemini/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "Explain AI in one sentence"}'
```

### Rollback
```bash
curl -X POST http://localhost:5000/api/models/gemini/rollback \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0"}'
```

## Testing

Run the comprehensive test suite:

```bash
python tests.py
```

### Test Coverage (10 Tests)

1. **Model Registration** - Test model registration
2. **Version Management** - Test version registration
3. **Version Comparison** - Test version logic
4. **Deployment** - Test direct deployment
5. **Blue-Green Deployment** - Test blue-green strategy
6. **Canary Deployment** - Test canary strategy
7. **Rollback** - Test rollback mechanism
8. **Snapshot Management** - Test snapshots
9. **Performance Tracking** - Test metrics
10. **Health Checks** - Test health validation

## Deployment Strategies

### Direct Deployment
```
Old Version → New Version (immediate)
```
- Simplest strategy
- Immediate replacement
- Potential downtime
- Use for: Development, non-critical services

### Blue-Green Deployment
```
Blue (old) ← 100% traffic
Green (new) ← 0% traffic
↓ (health check)
Blue (old) ← 0% traffic
Green (new) ← 100% traffic
```
- Zero-downtime deployment
- Instant rollback capability
- Requires 2x resources
- Use for: Production, critical services

### Canary Deployment
```
Old ← 90% traffic, New ← 10% traffic
↓ (monitor)
Old ← 50% traffic, New ← 50% traffic
↓ (monitor)
Old ← 0% traffic, New ← 100% traffic
```
- Gradual rollout
- Risk mitigation
- Real-world testing
- Use for: High-risk changes, new features

## Educational Notes

### 1. Semantic Versioning

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (1.0.0 → 1.0.1)

### 2. Model Registry Benefits

- **Centralized Management**: Single source of truth
- **Version Control**: Track all model versions
- **Deployment History**: Audit trail
- **Rollback Safety**: Quick recovery
- **Performance Tracking**: Data-driven decisions

### 3. Deployment Best Practices

- **Always test** before deploying
- **Use health checks** to validate deployments
- **Create snapshots** before major changes
- **Monitor metrics** during rollout
- **Have rollback plan** ready

### 4. Performance Monitoring

Track these metrics:
- **Latency**: Response time (p50, p95, p99)
- **Throughput**: Requests per second
- **Error Rate**: Failed predictions
- **Success Rate**: Successful predictions
- **Token Usage**: Cost tracking

### 5. Rollback Triggers

Rollback when:
- Error rate exceeds threshold
- Latency increases significantly
- Success rate drops
- Health checks fail
- Manual intervention needed

## Production Considerations

For production use:

1. **Database:**
   - Use PostgreSQL instead of SQLite
   - Implement connection pooling
   - Add database migrations

2. **Model Storage:**
   - Use S3 or cloud storage
   - Version model artifacts
   - Implement artifact cleanup

3. **Monitoring:**
   - Add Prometheus metrics
   - Create Grafana dashboards
   - Set up alerting (PagerDuty, Slack)

4. **Security:**
   - Add authentication
   - Implement authorization
   - Encrypt sensitive data
   - Audit logging

5. **Scalability:**
   - Horizontal scaling
   - Load balancing
   - Caching layer (Redis)
   - Async processing

## Dependencies

- **Flask 3.0.0** - Web framework
- **google-genai 0.2.0** - Gemini API client
- **python-dotenv 1.0.0** - Environment variables
- **pytest 7.4.3** - Testing framework
- **requests 2.31.0** - HTTP client
- **packaging 23.2** - Version parsing

## Real-World Applications

This pattern is used in:
- **ML Platforms**: Model deployment systems
- **API Management**: Version control for APIs
- **Microservices**: Service deployment
- **Feature Flags**: Gradual feature rollout
- **A/B Testing**: Traffic splitting
- **CI/CD Pipelines**: Automated deployment

## Learning Path

1. **Start with Registry** - Understand model registration
2. **Add Versioning** - Implement version control
3. **Deploy Models** - Try different strategies
4. **Implement Rollback** - Safe recovery mechanisms
5. **Track Performance** - Monitor metrics
6. **Build API** - Expose via REST
7. **Write Tests** - Ensure quality
8. **Optimize** - Improve performance

## Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not found
Solution: Create .env file with your API key
```

### Import Errors
```
Error: No module named 'packaging'
Solution: pip install -r requirements.txt
```

### Database Errors
```
Error: Database locked
Solution: Close other connections or delete .db file
```

## Contributing

This is an educational project. Feel free to:
- Add new deployment strategies
- Improve health checks
- Add more metrics
- Enhance monitoring
- Write more tests

## License

This project is for educational purposes. Feel free to use and modify as needed.

---

**Happy Learning!**
