# Caelum Ecosystem Deployment Strategy

**Multi-Repository Self-Evolving System - Comprehensive Guide**

---

## Executive Summary

The Caelum AI trading system consists of **4 independent repositories** that need coordinated deployment, version management, and configuration. This document outlines the deployment strategy for achieving:

1. **Independence**: Each repo can version and deploy independently
2. **Coordination**: PIM orchestrates and monitors all services
3. **Self-Evolution**: Automated testing, deployment, and rollback
4. **Multi-Environment**: Dev, test, and production environments
5. **Multi-Host**: Distributed deployment across GPU servers

---

## Quick Decision Matrix

| Scenario | Recommended Approach |
|----------|---------------------|
| **First-time setup** | Docker Compose (all services) |
| **Development** | Native Python/Node (fast iteration) |
| **Production (single host)** | systemd (low overhead) |
| **Production (multi-host)** | Docker Compose + systemd |
| **Self-evolution** | Docker Compose (version management) |
| **Testing new versions** | Docker profiles (parallel testing) |

---

## Architecture Overview

### Service Dependencies

```
┌─────────────────────────────────────────────────┐
│              PIM (Control Plane)                │
│         Configuration + Orchestration           │
└───────┬──────────┬──────────┬──────────────────┘
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌──────┐  ┌──────────┐
   │FinColl  │ │SenVec│  │  FinVec  │
   │(Depends)│ │      │  │ (Training)│
   └────┬────┘ └──────┘  └──────────┘
        │
        ├─► SenVec (sentiment features)
        └─► FinVec (model checkpoints)
```

**Key Insight**: FinColl depends on both SenVec and FinVec, so deployment order matters.

### Resource Requirements

| Service | RAM | GPU | Network | Storage |
|---------|-----|-----|---------|---------|
| PIM | 400MB | No | 5000 | 1GB |
| FinColl | 200MB | Optional | 8001 | 500MB |
| SenVec | 200MB | No | 18000-18004 | 2GB (cache) |
| FinVec | 8GB | **YES** | N/A | 50GB (models) |

**Total**: ~1GB RAM (runtime) + GPU for training

---

## Deployment Options

### Option 1: Unified Docker Compose (Recommended for Self-Evolution)

**Location**: `/home/rford/caelum/ss/docker-compose.ecosystem.yml`

**Profiles**:
- `dev`: All services with hot-reload
- `production`: Optimized containers with auto-restart
- `testing`: Multi-version parallel testing
- `monitoring`: Add Prometheus/Grafana

**Usage**:

```bash
# Development (all services)
cd /home/rford/caelum/ss
docker-compose -f docker-compose.ecosystem.yml --profile dev up

# Production (all services)
docker-compose -f docker-compose.ecosystem.yml --profile production up -d

# Testing new versions (parallel)
FINCOLL_VERSION=v1.0.0 FINCOLL_TEST_VERSION=v2.0.0-beta \
  docker-compose -f docker-compose.ecosystem.yml --profile testing up -d

# Start only specific services
docker-compose -f docker-compose.ecosystem.yml up senvec-aggregator fincoll-production

# Multi-host deployment
DOCKER_HOST=ssh://10.32.3.44 docker-compose -f docker-compose.ecosystem.yml up fincoll-production
```

**Pros**:
- ✅ Single command to start entire ecosystem
- ✅ Version management built-in
- ✅ Easy multi-version testing
- ✅ Network isolation
- ✅ Perfect for autonomous deployment

**Cons**:
- ❌ Container overhead (~100MB per service)
- ❌ Requires Docker on all hosts
- ❌ More complex debugging

### Option 2: Service-Specific Docker Compose

Each repo has its own `docker-compose.yml`:

**FinColl**: `/home/rford/caelum/ss/fincoll/docker-compose.yml`
- Profiles: `dev`, `production`, `testing`
- See: `fincoll/DEPLOYMENT.md`

**SenVec**: `/home/rford/caelum/ss/senvec/docker-compose.yml`
- Microservice architecture (5 services)
- Profiles: `local` (dev), `production`

**PIM**: `/home/rford/caelum/ss/PassiveIncomeMaximizer/docker-compose.yml` (to be created)

**Usage**:

```bash
# Start SenVec
cd /home/rford/caelum/ss/senvec
docker-compose --profile production up -d

# Start FinColl
cd /home/rford/caelum/ss/fincoll
docker-compose --profile production up -d

# Start PIM
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
docker-compose up -d
```

**Pros**:
- ✅ Independent deployment per service
- ✅ Smaller scope (easier debugging)
- ✅Repo independence maintained

**Cons**:
- ❌ Manual coordination required
- ❌ No unified orchestration
- ❌ Must manage dependencies manually

### Option 3: systemd Services (Production - Native)

**FinColl**: Already configured
- Service: `/etc/systemd/system/fincoll.service`
- Docs: `/home/rford/caelum/ss/fincoll/SYSTEMD_SERVICE.md`

**SenVec**: Templated services (to be created)
```bash
# /etc/systemd/system/senvec@.service
sudo systemctl start senvec@sentimentrader
sudo systemctl start senvec@alphavantage
sudo systemctl start senvec@social
sudo systemctl start senvec@news
sudo systemctl start senvec@aggregator
```

**PIM**: PM2 (Node.js)
```bash
pm2 start npm --name pim -- start
pm2 save
```

**Pros**:
- ✅ Native performance (no container overhead)
- ✅ Boot integration
- ✅ Centralized logging (journald)
- ✅ Auto-restart on crash

**Cons**:
- ❌ Manual version management
- ❌ Harder multi-version testing
- ❌ No rollback mechanism

### Option 4: Hybrid (Docker + systemd)

**Best of both worlds**:

```bash
# systemd manages Docker Compose
# /etc/systemd/system/caelum-ecosystem.service
[Unit]
Description=Caelum AI Trading Ecosystem
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/rford/caelum/ss
ExecStart=/usr/bin/docker-compose -f docker-compose.ecosystem.yml --profile production up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.ecosystem.yml down

[Install]
WantedBy=multi-user.target
```

**Usage**:

```bash
sudo systemctl enable caelum-ecosystem
sudo systemctl start caelum-ecosystem
```

**Pros**:
- ✅ Boot integration (systemd)
- ✅ Version management (Docker)
- ✅ Auto-restart (systemd + Docker)

---

## Multi-Host Deployment

### Topology 1: All-in-One (Development)

**Host**: WSL (10.32.3.27)

```
PIM:      10.32.3.27:5000
FinColl:  10.32.3.27:8001
SenVec:   10.32.3.27:18000-18004
FinVec:   Native training
```

### Topology 2: Distributed Production

**WSL (10.32.3.27)**: Control plane
```
PIM:      10.32.3.27:5000 (PM2)
SenVec:   10.32.3.27:18000-18004 (systemd)
```

**GPU Server 1 (10.32.3.44)**: Primary ML
```
FinColl:  10.32.3.44:8001 (Docker)
FinVec:   LLM-5 training
```

**GPU Server 2 (10.32.3.22)**: Secondary ML
```
FinVec:   LLM-3 training
```

**GPU Server 3 (10.32.3.62)**: Testing
```
FinColl:  10.32.3.62:8002 (Docker - test version)
FinVec:   LLM-1 training
```

### Multi-Host Docker Compose

Use Docker contexts:

```bash
# Create contexts
docker context create gpu1 --docker "host=ssh://10.32.3.44"
docker context create gpu2 --docker "host=ssh://10.32.3.22"
docker context create gpu3 --docker "host=ssh://10.32.3.62"

# Deploy to specific host
docker --context gpu1 compose -f docker-compose.ecosystem.yml up fincoll-production -d

# Or use DOCKER_HOST
DOCKER_HOST=ssh://10.32.3.44 docker-compose -f docker-compose.ecosystem.yml up fincoll-production -d
```

---

## Configuration Management (PIM as Control Plane)

### Central Configuration Database

**PIM PostgreSQL** stores configuration for all services:

```sql
-- Service configurations
CREATE TABLE service_configs (
  service_name VARCHAR(50),  -- 'fincoll', 'senvec', 'finvec'
  version VARCHAR(20),
  config_json JSONB,
  environment VARCHAR(20),  -- 'dev', 'test', 'prod'
  host VARCHAR(100),
  port INTEGER,
  enabled BOOLEAN
);

-- Example row
INSERT INTO service_configs VALUES (
  'fincoll',
  'v1.0.0',
  '{"senvec_url": "http://10.32.3.27:18000", "log_level": "INFO"}',
  'prod',
  '10.32.3.44',
  8001,
  true
);
```

### PIM API for Configuration

**Endpoint**: `GET /api/config/:service/:version`

```bash
curl http://10.32.3.27:5000/api/config/fincoll/v1.0.0
```

**Response**:
```json
{
  "service": "fincoll",
  "version": "v1.0.0",
  "config": {
    "senvec_url": "http://10.32.3.27:18000",
    "port": 8001,
    "log_level": "INFO",
    "model_checkpoint_dir": "/home/rford/caelum/ss/finvec/checkpoints"
  },
  "environment": "prod",
  "host": "10.32.3.44"
}
```

### Services Fetch Config on Startup

**FinColl example**:

```python
# fincoll/server.py
import requests
import os

PIM_URL = os.getenv('PIM_URL', 'http://10.32.3.27:5000')
SERVICE_NAME = 'fincoll'
VERSION = os.getenv('FINCOLL_VERSION', 'v1.0.0')

# Fetch config from PIM
config = requests.get(f'{PIM_URL}/api/config/{SERVICE_NAME}/{VERSION}').json()

# Use config
SENVEC_URL = config['config']['senvec_url']
PORT = config['config']['port']
LOG_LEVEL = config['config']['log_level']

app = FastAPI()
# ... rest of server
```

---

## Autonomous Version Management

### Self-Evolution Workflow

```
1. Code Change Detected
   ├─► Git commit (manual or AI-generated)
   └─► Trigger deployment pipeline

2. PIM Orchestration Service
   ├─► Build Docker image: `fincoll:v1.1.0`
   ├─► Start test instance on port 8002
   ├─► Run health checks
   ├─► Run prediction accuracy tests
   └─► Decision:
       ├─► PASS → Promote to production (port 8001)
       └─► FAIL → Rollback + log failure

3. Deployment Logs
   └─► Store in `deployment_history` table
```

### PIM Deployment API

**Endpoint**: `POST /api/deployment/deploy`

```bash
curl -X POST http://10.32.3.27:5000/api/deployment/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "service": "fincoll",
    "version": "v1.1.0",
    "environment": "test",
    "auto_promote": false
  }'
```

**Response**:
```json
{
  "deployment_id": "d12345",
  "service": "fincoll",
  "version": "v1.1.0",
  "status": "testing",
  "test_url": "http://10.32.3.44:8002",
  "health": {
    "status": "healthy",
    "response_time_ms": 45
  },
  "accuracy_tests": {
    "prediction_accuracy": 0.78,
    "sharpe_ratio": 1.45,
    "pass": true
  }
}
```

**Auto-Promote**:

```bash
curl -X POST http://10.32.3.27:5000/api/deployment/promote/d12345
```

**Rollback**:

```bash
curl -X POST http://10.32.3.27:5000/api/deployment/rollback/fincoll
```

---

## Testing Environments

### Development Environment

```bash
# Native execution (fastest iteration)
cd /home/rford/caelum/ss/senvec
source .venv/bin/activate
./start_all_services.sh

cd /home/rford/caelum/ss/fincoll
source .venv/bin/activate
python -m fincoll.server

cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run dev
```

### Test Environment (Parallel Testing)

```bash
# Start production on 8001
docker-compose -f docker-compose.ecosystem.yml up fincoll-production -d

# Start test version on 8002
FINCOLL_TEST_VERSION=v2.0.0-beta \
  docker-compose -f docker-compose.ecosystem.yml up fincoll-test -d

# Compare performance
curl http://10.32.3.27:8001/api/v1/inference/predict/AAPL  # v1.0.0
curl http://10.32.3.27:8002/api/v1/inference/predict/AAPL  # v2.0.0-beta
```

### Production Environment

```bash
# Option A: Docker Compose
docker-compose -f docker-compose.ecosystem.yml --profile production up -d

# Option B: systemd
sudo systemctl start caelum-ecosystem

# Check status
curl http://10.32.3.27:5000/api/system/health
```

---

## Monitoring and Health Checks

### PIM System Health Endpoint

**Endpoint**: `GET /api/system/health`

```json
{
  "status": "healthy",
  "services": {
    "fincoll": {
      "status": "healthy",
      "version": "v1.0.0",
      "url": "http://10.32.3.44:8001",
      "response_time_ms": 45
    },
    "senvec": {
      "status": "healthy",
      "microservices": {
        "aggregator": "healthy",
        "sentimentrader": "healthy",
        "alphavantage": "healthy",
        "social": "degraded",
        "news": "healthy"
      }
    },
    "finvec": {
      "status": "training",
      "current_job": "llm1-tech",
      "progress": "45%"
    }
  }
}
```

### Grafana Dashboards

Start monitoring stack:

```bash
docker-compose -f docker-compose.ecosystem.yml --profile monitoring up -d
```

Access:
- **Grafana**: http://10.32.3.27:3001 (admin/admin)
- **Prometheus**: http://10.32.3.27:9090

---

## Disaster Recovery

### Backup Strategy

**Automated Backups**:

```bash
# Database backups (daily)
0 2 * * * pg_dump -U caelum pim_database > /mnt/d/swdatasci/caelum/backups/pim-$(date +\%Y\%m\%d).sql

# Model checkpoints (weekly)
0 3 * * 0 rsync -av /home/rford/caelum/ss/finvec/checkpoints /mnt/d/swdatasci/caelum/backups/models-$(date +\%Y\%m\%d)/
```

### Rollback Procedures

**FinColl**:

```bash
# Docker
docker-compose -f docker-compose.ecosystem.yml down fincoll-production
VERSION=v1.0.0 docker-compose -f docker-compose.ecosystem.yml up fincoll-production -d

# systemd
cd /home/rford/caelum/ss/fincoll
git checkout v1.0.0
sudo systemctl restart fincoll
```

**Model Rollback** (via PIM API):

```bash
curl -X POST http://10.32.3.27:5000/api/config/fincoll/update \
  -H "Content-Type: application/json" \
  -d '{
    "model_checkpoint_dir": "/home/rford/caelum/ss/finvec/checkpoints/llm1-tech-v1.0.0.pt"
  }'
```

---

## Recommendations

### For Your Use Case

Based on your requirements for **self-evolution**, **multi-host**, and **testing while production runs**:

**Recommended Deployment**:

1. **Production Services** (10.32.3.44):
   - FinColl: Docker Compose (systemd-managed)
   - Allows version management and auto-restart

2. **Control Plane** (10.32.3.27):
   - PIM: PM2 (native Node.js)
   - SenVec: systemd (native Python)
   - Low overhead, fast startup

3. **Testing** (10.32.3.62):
   - Docker Compose with `testing` profile
   - Parallel testing of new versions

4. **Training** (All GPU servers):
   - Native Python (.venv)
   - systemd timers for scheduled retraining

### Implementation Steps

1. ✅ **Complete** - Created `/home/rford/caelum/ss/ECOSYSTEM_ARCHITECTURE.md`
2. ✅ **Complete** - Created `/home/rford/caelum/ss/docker-compose.ecosystem.yml`
3. ⏳ **Next** - Implement PIM deployment API (`/api/deployment/*`)
4. ⏳ **Next** - Create SenVec Dockerfiles for microservices
5. ⏳ **Next** - Create FinVec training Dockerfile
6. ⏳ **Next** - Set up systemd hybrid service
7. ⏳ **Next** - Implement automated testing in deployment pipeline

---

## Quick Start

### Development (All Services - Native)

```bash
# SenVec
cd ~/caelum/ss/senvec && ./start_all_services.sh &

# FinColl
cd ~/caelum/ss/fincoll && source .venv/bin/activate && python -m fincoll.server &

# PIM
cd ~/caelum/ss/PassiveIncomeMaximizer && npm run dev
```

### Production (Docker Compose)

```bash
cd ~/caelum/ss
docker-compose -f docker-compose.ecosystem.yml --profile production up -d
```

### Check Status

```bash
curl http://10.32.3.27:5000/api/system/health
```

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-08
**Next Review**: After implementation of PIM deployment API
