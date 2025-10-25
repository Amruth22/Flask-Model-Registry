# Model Registry - MCQ Questions

Multiple choice questions to test understanding of model registry, version control, deployment strategies, rollback mechanisms, and performance tracking concepts.

---

## Section 1: Model Registry (Easy)

### Question 1: Model Registry Purpose
What is the primary purpose of a model registry?

a) To train AI models  
b) To centrally manage and track AI models and versions  
c) To store training data  
d) To generate predictions  

**Answer: b) To centrally manage and track AI models and versions**

**Explanation:** A model registry serves as a central repository for managing AI models, their versions, metadata, and deployment history. It provides a single source of truth for all models in an organization, enabling version control, deployment tracking, and model discovery.

---

### Question 2: Semantic Versioning Format
What does the version number "2.1.3" represent in semantic versioning?

a) 2 = minor, 1 = major, 3 = patch  
b) 2 = major, 1 = minor, 3 = patch  
c) 2 = patch, 1 = minor, 3 = major  
d) 2 = year, 1 = month, 3 = day  

**Answer: b) 2 = major, 1 = minor, 3 = patch**

**Explanation:** Semantic versioning follows the format MAJOR.MINOR.PATCH where MAJOR indicates breaking changes, MINOR indicates new features (backward compatible), and PATCH indicates bug fixes. This standard helps communicate the nature of changes between versions.

---

### Question 3: Version Compatibility
Which versions are compatible according to semantic versioning?

a) 1.0.0 and 2.0.0  
b) 1.0.0 and 1.1.0  
c) 2.0.0 and 3.0.0  
d) 1.5.0 and 2.5.0  

**Answer: b) 1.0.0 and 1.1.0**

**Explanation:** Versions with the same major number are considered compatible. Version 1.1.0 adds new features to 1.0.0 but maintains backward compatibility. Different major versions (1.x.x vs 2.x.x) indicate breaking changes and are not compatible.

---

## Section 2: Deployment Strategies (Medium)

### Question 4: Direct Deployment
What is the main characteristic of direct deployment?

a) Zero downtime  
b) Gradual rollout  
c) Immediate replacement with potential downtime  
d) Requires two environments  

**Answer: c) Immediate replacement with potential downtime**

**Explanation:** Direct deployment immediately replaces the old version with the new version. It's the simplest strategy but may cause downtime during the switch. It's suitable for development environments or non-critical services where brief downtime is acceptable.

---

### Question 5: Blue-Green Deployment
How does blue-green deployment achieve zero downtime?

a) By deploying gradually  
b) By maintaining two identical environments and switching traffic  
c) By using multiple servers  
d) By caching responses  

**Answer: b) By maintaining two identical environments and switching traffic**

**Explanation:** Blue-green deployment maintains two identical environments (blue and green). The new version is deployed to the inactive environment, tested, and then traffic is instantly switched. This provides zero downtime and instant rollback capability by switching back if issues arise.

---

### Question 6: Canary Deployment
What is the typical traffic progression in canary deployment?

a) 0% → 100% immediately  
b) 50% → 100%  
c) 10% → 50% → 100% gradually  
d) 100% → 0%  

**Answer: c) 10% → 50% → 100% gradually**

**Explanation:** Canary deployment gradually increases traffic to the new version (e.g., 10% → 50% → 100%), monitoring for issues at each stage. This minimizes risk by exposing only a small percentage of users to potential problems initially, allowing for early detection and rollback if needed.

---

## Section 3: Rollback Mechanisms (Medium)

### Question 7: Rollback Purpose
When should you trigger a rollback?

a) Only on weekends  
b) When error rate exceeds threshold or performance degrades  
c) Every hour  
d) Never, always move forward  

**Answer: b) When error rate exceeds threshold or performance degrades**

**Explanation:** Rollback should be triggered when the new version shows problems such as high error rates, increased latency, or failed health checks. Automatic rollback based on metrics ensures quick recovery and minimizes impact on users.

---

### Question 8: Snapshot Management
What is the purpose of creating snapshots before deployment?

a) To backup training data  
b) To enable point-in-time recovery and safe rollback  
c) To improve performance  
d) To reduce costs  

**Answer: b) To enable point-in-time recovery and safe rollback**

**Explanation:** Snapshots capture the complete state of a deployment including configuration, traffic routing, and metadata. They enable safe rollback to a known good state if the new deployment fails, ensuring service continuity and data consistency.

---

### Question 9: Automatic vs Manual Rollback
When is automatic rollback preferred over manual rollback?

a) Never, manual is always better  
b) When error rates exceed thresholds and immediate action is needed  
c) Only during business hours  
d) When deploying to development  

**Answer: b) When error rates exceed thresholds and immediate action is needed**

**Explanation:** Automatic rollback is crucial for production systems where immediate response to issues is necessary. It monitors metrics in real-time and triggers rollback when thresholds are exceeded, minimizing downtime and user impact without waiting for human intervention.

---

## Section 4: Performance Tracking (Hard)

### Question 10: Key Performance Metrics
Which metrics are most important for tracking model performance?

a) Only latency  
b) Only error rate  
c) Latency, error rate, success rate, and token usage  
d) Only cost  

**Answer: c) Latency, error rate, success rate, and token usage**

**Explanation:** Comprehensive performance tracking requires monitoring multiple metrics: latency (response time), error rate (failures), success rate (successful predictions), and token usage (cost). Together, these provide a complete picture of model health and performance.

---

### Question 11: Performance Degradation Detection
How do you detect performance degradation between versions?

a) By guessing  
b) By comparing metrics like latency and error rate between versions  
c) By user complaints only  
d) By checking once a month  

**Answer: b) By comparing metrics like latency and error rate between versions**

**Explanation:** Performance degradation is detected by comparing key metrics between the current and previous versions. If the new version shows significantly higher latency, error rate, or lower success rate, it indicates degradation and may trigger alerts or automatic rollback.

---

### Question 12: Alerting Thresholds
What should trigger a performance alert?

a) Any change in metrics  
b) Metrics exceeding predefined thresholds (e.g., latency > 2s)  
c) Only complete failures  
d) Random intervals  

**Answer: b) Metrics exceeding predefined thresholds (e.g., latency > 2s)**

**Explanation:** Alerts should be triggered when metrics exceed predefined thresholds that indicate problems. For example, average latency > 2 seconds or error rate > 10%. Thresholds should be set based on service requirements and historical performance data.

---

## Section 5: MLOps Practices (Hard)

### Question 13: Model Lifecycle Management
What are the key stages in model lifecycle management?

a) Train only  
b) Train, deploy, forget  
c) Register, version, deploy, monitor, rollback  
d) Deploy and hope  

**Answer: c) Register, version, deploy, monitor, rollback**

**Explanation:** Complete model lifecycle management includes: registering models in a central registry, versioning for tracking changes, deploying with appropriate strategies, monitoring performance in production, and having rollback mechanisms for safety. This ensures reliable and maintainable ML systems.

---

### Question 14: Health Checks
What should a comprehensive health check validate?

a) Only if the service is running  
b) Availability, response time, and error rate  
c) Only during deployment  
d) Nothing, trust the deployment  

**Answer: b) Availability, response time, and error rate**

**Explanation:** Comprehensive health checks validate multiple aspects: availability (can the model respond), response time (is latency acceptable), and error rate (are predictions succeeding). These checks ensure the deployed model is functioning correctly before routing production traffic.

---

### Question 15: Production Best Practices
Which is NOT a production best practice for model deployment?

a) Always create snapshots before deployment  
b) Monitor metrics continuously  
c) Deploy directly to production without testing  
d) Have rollback plans ready  

**Answer: c) Deploy directly to production without testing**

**Explanation:** Deploying directly to production without testing is dangerous and violates best practices. Production deployments should follow proper procedures: test in staging, use appropriate deployment strategies (blue-green or canary), monitor metrics, and have rollback plans ready.

---

## Scoring Guide

- **13-15 correct:** Excellent understanding of MLOps and model registry
- **10-12 correct:** Good grasp of core concepts
- **7-9 correct:** Basic understanding, review key topics
- **Below 7:** Review the documentation and code examples

## Key Takeaways

1. **Model Registry:** Central management for all models and versions
2. **Semantic Versioning:** Standard format for version communication
3. **Deployment Strategies:** Choose based on risk and requirements
4. **Blue-Green:** Zero downtime, instant rollback
5. **Canary:** Gradual rollout, risk mitigation
6. **Rollback Safety:** Always have a way back
7. **Snapshots:** Enable point-in-time recovery
8. **Performance Tracking:** Monitor continuously
9. **Alerting:** Proactive issue detection
10. **MLOps:** Complete lifecycle management

## Further Learning

- Study the code examples in main.py
- Run the tests to see concepts in action
- Experiment with the Flask API
- Try different deployment strategies
- Implement custom health checks
- Add more performance metrics
- Create monitoring dashboards
- Practice rollback scenarios

---

**Good luck with your learning journey!**
