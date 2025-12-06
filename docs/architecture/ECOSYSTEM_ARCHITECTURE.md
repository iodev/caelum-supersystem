# Caelum AI Trading Ecosystem Architecture

**Multi-Repository Self-Evolving System**

---

## Overview

The Caelum trading system consists of **4 independent repositories** working together:

| Repository | Language | Purpose | Port(s) | Resource Usage |
|------------|----------|---------|---------|----------------|
| **PIM** | Node.js/React | Control plane, UI, orchestration | 5000 | ~400MB RAM |
| **FinColl** | Python/FastAPI | ML inference API | 8001 | ~100MB RAM |
| **SenVec** | Python/FastAPI | Sentiment features (72D) | 18000-18004 | ~200MB RAM |
| **FinVec** | Python/PyTorch | ML training (LLM) | N/A (batch jobs) | GPU-heavy |

**Total RAM (all services)**: ~700MB
**GPU Requirements**: 1-3 GPUs for FinVec training
**NFS Share**: `/home/rford/caelum/ss` (shared across all hosts)

---

## Service Dependencies

```
┌─────────────────────────────────────────────────────────┐
│                    PIM (Port 5000)                      │
│              Control Plane + Web UI                     │
│  - Service orchestration                                │
│  - Configuration management                             │
│  - Health monitoring                                    │
│  - Trading dashboard                                    │
└────────────┬──────────────┬──────────────┬──────────────┘
             │              │              │
             ▼              ▼              ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│ FinColl (8001)  │  │ SenVec       │  │ FinVec (Training)│
│  ML Predictions │  │ (18000-18004)│  │  GPU Workloads   │
│                 │  │ Sentiment    │  │                  │
│  Depends on:    │  │ Features     │  │  Runs on:        │
│  • SenVec ────────►│              │  │  • 10.32.3.27    │
│  • FinVec ──────────────────────────►│  • 10.32.3.22    │
│    (models)     │  │              │  │  • 10.32.3.44    │
└─────────────────┘  └──────────────┘  └──────────────────┘
```

### Dependency Matrix

| Service | Depends On | Optional? | Fallback |
|---------|-----------|-----------|----------|
| **PIM** | FinColl | No | Show "unavailable" |
| **FinColl** | SenVec | Yes | Zeros for 72D features |
| **FinColl** | FinVec (models) | No | Cannot start without model |
| **FinColl** | TradeStation/AlphaVantage | No | Data source required |
| **SenVec** | None | - | Standalone |
| **FinVec** | TradeStation/AlphaVantage | No | Training requires data |

---

## Multi-Host Deployment Topology

### Option 1: All-in-One (Development)

**Host**: WSL (10.32.3.27)

```bash
# All services on one machine
PIM:      10.32.3.27:5000
FinColl:  10.32.3.27:8001
SenVec:   10.32.3.27:18000-18004
FinVec:   Native .venv training
```

**Pros**: Simple, fast iteration
**Cons**: Resource contention, no GPU specialization

### Option 2: Distributed (Production)

**WSL (10.32.3.27)**: Control plane
```bash
PIM:      10.32.3.27:5000
SenVec:   10.32.3.27:18000-18004
```

**GPU Server 1 (10.32.3.44)**: Primary ML
```bash
FinColl:  10.32.3.44:8001
FinVec:   GPU training (LLM-5)
```

**GPU Server 2 (10.32.3.22)**: Secondary ML
```bash
FinVec:   GPU training (LLM-3)
```

**GPU Server 3 (10.32.3.62)**: Testing
```bash
FinColl:  10.32.3.62:8002  (test version)
FinVec:   GPU training (LLM-1)
```

### Option 3: Hybrid Testing

**Production** (systemd):
```bash
FinColl v1.0:  10.32.3.44:8001
SenVec:        10.32.3.27:18000
```

**Testing** (Docker):
```bash
FinColl v2.0:  10.32.3.44:8002  (parallel testing)
FinColl v2.1:  10.32.3.62:8001  (canary testing)
```

---

## Deployment Methods by Service

### PIM (Node.js)

| Method | Use Case | Command |
|--------|----------|---------|
| **Native** | Development | `npm run dev` |
| **PM2** | Production (native) | `pm2 start npm --name pim -- start` |
| **Docker** | Autonomous deployment | `docker-compose --profile production up` |

**Recommendation**: PM2 for production, Docker for testing

### FinColl (Python FastAPI)

| Method | Use Case | Command |
|--------|----------|---------|
| **Native** | Development | `python -m fincoll.server` |
| **systemd** | Production (single version) | `sudo systemctl start fincoll` |
| **Docker Compose** | Multi-version testing | `docker-compose --profile testing up` |
| **Hybrid** | Autonomous + boot integration | systemd manages Docker |

**Recommendation**: Docker Compose (best for self-evolution)

See: `/home/rford/caelum/ss/fincoll/DEPLOYMENT.md`

### SenVec (Python FastAPI Microservices)

| Method | Use Case | Command |
|--------|----------|---------|
| **Native** | Development | `./start_senvec_services.sh` |
| **systemd** | Production | `sudo systemctl start senvec@*` |
| **Docker Compose** | Containerized | `docker-compose --profile production up` |

**Recommendation**: systemd with templated services

See: `/home/rford/caelum/ss/senvec/DEPLOYMENT.md` (to be created)

### FinVec (PyTorch Training)

| Method | Use Case | Command |
|--------|----------|---------|
| **Native** | Development/Production | `python train_production.py` |
| **systemd (timer)** | Scheduled retraining | `systemctl start finvec-train@llm1` |
| **Kubernetes Job** | Cloud training | `kubectl apply -f training-job.yaml` |

**Recommendation**: Native with systemd timers for automation

**GPU Assignment**:
- LLM-1 (Tech stocks): 10.32.3.27 or 10.32.3.62
- LLM-3 (YIELDMAX): 10.32.3.22
- LLM-5 (Volatility): 10.32.3.44

---

## Configuration Management

### Central Configuration (PIM)

PIM acts as the **configuration control plane** for all services:

**Database**: `pim_database` (PostgreSQL)

```sql
CREATE TABLE service_configs (
  id SERIAL PRIMARY KEY,
  service_name VARCHAR(50) NOT NULL,  -- 'fincoll', 'senvec', 'finvec'
  version VARCHAR(20) NOT NULL,       -- 'v1.0.0', 'v2.0.0-beta'
  config_json JSONB NOT NULL,         -- Service-specific config
  environment VARCHAR(20) NOT NULL,   -- 'dev', 'test', 'prod'
  host VARCHAR(100),                  -- '10.32.3.44', '10.32.3.27'
  port INTEGER,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE service_health (
  id SERIAL PRIMARY KEY,
  service_name VARCHAR(50) NOT NULL,
  version VARCHAR(20),
  status VARCHAR(20),  -- 'healthy', 'degraded', 'down'
  last_check TIMESTAMP DEFAULT NOW(),
  response_time_ms INTEGER,
  metadata JSONB
);

CREATE TABLE deployment_history (
  id SERIAL PRIMARY KEY,
  service_name VARCHAR(50) NOT NULL,
  version VARCHAR(20) NOT NULL,
  action VARCHAR(20),  -- 'deploy', 'rollback', 'test', 'promote'
  host VARCHAR(100),
  status VARCHAR(20),  -- 'success', 'failed', 'in_progress'
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  logs TEXT
);
```

### Configuration Distribution

**Method 1: Environment Variables** (current)

PIM generates `.env` files and deploys them to each service:

```bash
# FinColl .env (generated by PIM)
FINCOLL_PORT=8001
SENVEC_API_URL=http://10.32.3.27:18000
CREDENTIALS_DIR=/home/rford/caelum/ss
LOG_LEVEL=INFO
```

**Method 2: API-based Configuration** (future)

Services fetch config from PIM on startup:

```python
# In fincoll/server.py
import requests

config = requests.get('http://10.32.3.27:5000/api/config/fincoll/v1.0.0').json()
SENVEC_URL = config['senvec_url']
PORT = config['port']
```

**Method 3: Service Discovery** (advanced)

Use Consul or etcd for dynamic service discovery.

---

## Autonomous Version Management

### Self-Evolution Workflow

```
1. PIM detects new code version (git pull or self-generated)
2. PIM builds Docker image with version tag
3. PIM deploys to test environment (separate port)
4. PIM runs health checks + prediction accuracy tests
5. If tests pass → promote to production
6. If tests fail → rollback, log failure, notify
```

### Version Management Strategy

#### FinColl Versioning

```bash
# Production
fincoll:v1.0.0 → 10.32.3.44:8001 (systemd or Docker)

# Testing (parallel)
fincoll:v1.1.0-beta → 10.32.3.44:8002 (Docker)

# Canary
fincoll:v2.0.0-rc → 10.32.3.62:8001 (Docker, 10% traffic)
```

**Deployment Script** (PIM-controlled):

```python
# server/services/deployment-manager.ts
async function deployNewVersion(service: string, version: string) {
  // 1. Build image
  await buildDockerImage(service, version);

  // 2. Start test instance
  const testPort = await startTestInstance(service, version);

  // 3. Run health checks
  const healthy = await runHealthChecks(testPort);

  // 4. Run prediction accuracy tests (for FinColl)
  const accurate = await runAccuracyTests(service, testPort);

  if (healthy && accurate) {
    // 5. Promote to production
    await promoteToProduction(service, version);
    await stopTestInstance(service, version);
    return { success: true, version };
  } else {
    // 6. Rollback
    await rollback(service);
    await logFailure(service, version, { healthy, accurate });
    return { success: false, version, reason: 'Tests failed' };
  }
}
```

#### SenVec Versioning

SenVec has **5 microservices** that can version independently:

```yaml
# docker-compose.yml (SenVec)
services:
  sentimentrader:
    image: senvec-sentimentrader:${ST_VERSION:-v1.0.0}
    ports: ["18001:18001"]

  alphavantage:
    image: senvec-alphavantage:${AV_VERSION:-v1.0.0}
    ports: ["18002:18002"]

  social:
    image: senvec-social:${SOCIAL_VERSION:-v1.0.0}
    ports: ["18003:18003"]

  news:
    image: senvec-news:${NEWS_VERSION:-v1.0.0}
    ports: ["18004:18004"]

  aggregator:
    image: senvec-aggregator:${AGG_VERSION:-v1.0.0}
    ports: ["18000:18000"]
    depends_on: [sentimentrader, alphavantage, social, news]
```

**Rolling Update**: Update one microservice at a time without downtime.

#### FinVec Versioning

**Model Versioning** (not service versioning):

```bash
/home/rford/caelum/ss/finvec/checkpoints/
  ├── llm1-tech-v1.0.0.pt
  ├── llm1-tech-v1.1.0.pt (← new version after retraining)
  ├── llm3-yieldmax-v1.0.0.pt
  └── llm5-volatility-v1.0.0.pt
```

**FinColl References Models**:

```python
# In fincoll/config.py
MODEL_REGISTRY = {
  'llm1': '/home/rford/caelum/ss/finvec/checkpoints/llm1-tech-v1.1.0.pt',
  'llm3': '/home/rford/caelum/ss/finvec/checkpoints/llm3-yieldmax-v1.0.0.pt',
  'llm5': '/home/rford/caelum/ss/finvec/checkpoints/llm5-volatility-v1.0.0.pt'
}
```

**Automated Model Updates**:
1. FinVec completes training → saves new checkpoint
2. FinVec runs validation tests on new model
3. If validation passes → update `MODEL_REGISTRY` in FinColl config
4. FinColl hot-reloads new model (no downtime)
5. If model performs worse → automatic rollback

---

## Testing Environments

### Development
- **Host**: WSL (10.32.3.27)
- **Method**: Native Python, `npm run dev`
- **Database**: Local PostgreSQL (port 15433)
- **Data**: Demo/sample data

### Staging
- **Host**: 10.32.3.62
- **Method**: Docker Compose
- **Database**: Shared Caelum PostgreSQL
- **Data**: Production data (read-only)

### Production
- **Hosts**: 10.32.3.27 (PIM/SenVec), 10.32.3.44 (FinColl), 10.32.3.22 (Training)
- **Method**: systemd (PIM/SenVec), Docker (FinColl)
- **Database**: Caelum PostgreSQL (10.255.255.254)
- **Data**: Live market data

---

## Monitoring and Health Checks

### PIM Monitors All Services

**Endpoint**: `GET /api/system/health`

```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T...",
  "services": {
    "fincoll": {
      "status": "healthy",
      "version": "v1.0.0",
      "url": "http://10.32.3.44:8001",
      "response_time_ms": 45,
      "last_prediction": "2025-11-08T14:30:00Z"
    },
    "senvec": {
      "status": "healthy",
      "version": "v1.0.0",
      "url": "http://10.32.3.27:18000",
      "microservices": {
        "sentimentrader": "healthy",
        "alphavantage": "healthy",
        "social": "degraded",
        "news": "healthy",
        "aggregator": "healthy"
      }
    },
    "finvec": {
      "status": "training",
      "current_job": "llm1-tech",
      "progress": "45%",
      "eta": "2025-11-08T18:00:00Z",
      "gpu_usage": {
        "10.32.3.27": "85%",
        "10.32.3.22": "90%",
        "10.32.3.44": "idle"
      }
    }
  }
}
```

### Health Check Intervals

| Service | Check Interval | Timeout | Retries |
|---------|---------------|---------|---------|
| FinColl | 60s (production) | 5s | 3 |
| SenVec | 30s | 3s | 2 |
| FinVec | N/A (batch jobs) | - | - |

---

## Resource Allocation

### Memory Requirements

| Service | Min RAM | Recommended | Max (containerized) |
|---------|---------|-------------|---------------------|
| PIM | 200MB | 400MB | 1GB |
| FinColl | 100MB | 200MB | 2GB (Docker limit) |
| SenVec (all) | 150MB | 200MB | 1GB |
| FinVec Training | 2GB | 8GB | 32GB (GPU memory) |

### GPU Allocation

| GPU Server | GPU | Current Usage | Available For |
|------------|-----|---------------|---------------|
| 10.32.3.27 | RTX 3080 | LLM-1 training | Testing |
| 10.32.3.22 | RTX 3080 | LLM-3 training | Production |
| 10.32.3.44 | RTX 3080 | LLM-5 training | FinColl inference |
| 10.32.3.62 | RTX 3080 | Idle | Staging/Testing |

**GPU Training Schedule**:
- **LLM-1**: Daily retraining (2-4 hours)
- **LLM-3**: Weekly retraining (4-6 hours)
- **LLM-5**: On-demand retraining

---

## Security and Credentials

### Shared Credentials (NFS)

```bash
/home/rford/caelum/ss/
  ├── .alpha_vantage_credentials.json
  ├── .tradestation_token.json
  ├── .sentimentrader_credentials.json
  └── .pim_database_credentials.json
```

**Access**: All services read from same location (NFS-mounted).

**Security**: File permissions 600 (rford:rford only).

### Environment-Specific Secrets

Docker secrets or systemd EnvironmentFile:

```bash
# /etc/systemd/system/fincoll.env
CREDENTIALS_DIR=/home/rford/caelum/ss
DATABASE_URL=postgresql://pim_user:***@10.255.255.254:5432/pim_database
SENVEC_API_URL=http://10.32.3.27:18000
```

---

## Disaster Recovery

### Backup Strategy

**Database**:
- Daily automated backups to `/mnt/d/swdatasci/caelum/backups/`
- Retention: 30 days

**Model Checkpoints**:
- Keep last 5 versions per model
- Archive to S3/Backblaze weekly

**Configuration**:
- Git-tracked in respective repos
- PIM database backed up daily

### Rollback Procedures

**FinColl**:
```bash
# Docker
docker-compose --profile production down
VERSION=v1.0.0 docker-compose --profile production up -d

# systemd
git checkout v1.0.0
sudo systemctl restart fincoll
```

**Model Rollback**:
```python
# PIM triggers FinColl config update
update_fincoll_config({
  'model_registry': {
    'llm1': '/path/to/llm1-tech-v1.0.0.pt'  # Previous version
  }
})
```

---

## Next Steps

1. **Create SenVec deployment docs** (similar to FinColl)
2. **Implement PIM orchestration API** (`/api/deployment/*`)
3. **Create unified `docker-compose.ecosystem.yml`** (all services)
4. **Add automated testing to deployment pipeline**
5. **Implement model A/B testing framework**
6. **Create Grafana dashboards for system monitoring**

---

## Quick Reference Commands

### Start Entire Ecosystem (Development)

```bash
# Terminal 1: SenVec
cd ~/caelum/ss/senvec && ./start_all_services.sh

# Terminal 2: FinColl
cd ~/caelum/ss/fincoll && source .venv/bin/activate && python -m fincoll.server

# Terminal 3: PIM
cd ~/caelum/ss/PassiveIncomeMaximizer && npm run dev

# Check all services
curl http://10.32.3.27:18000/health  # SenVec
curl http://10.32.3.27:8001/health   # FinColl
curl http://10.32.3.27:5000/api/trading-bot/fincoll-status  # PIM
```

### Start Entire Ecosystem (Production - Multi-Host)

```bash
# On WSL (10.32.3.27)
sudo systemctl start senvec@*  # All SenVec microservices
pm2 start pim                  # PIM

# On GPU Server (10.32.3.44)
sudo systemctl start fincoll   # FinColl

# Verify
curl http://10.32.3.27:5000/api/system/health
```

### Deploy New Version (Autonomous)

```bash
# PIM triggers this automatically, or manually:
curl -X POST http://10.32.3.27:5000/api/deployment/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "service": "fincoll",
    "version": "v1.1.0",
    "environment": "test"
  }'
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintained By**: PIM Orchestration System
