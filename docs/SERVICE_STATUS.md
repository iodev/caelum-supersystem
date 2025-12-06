# PIM Service Status Summary

**Last Updated**: 2025-12-02 22:15 MST
**Machine**: 10.32.3.27 (primary server)

---

## ✅ Currently Running Services

### Infrastructure (Docker Containers)

| Service | Container | Port | Status | Notes |
|---------|-----------|------|--------|-------|
| PostgreSQL | pim-postgres | 15433 | ✅ Healthy | Contains months of trading data - DO NOT recreate |
| MongoDB | pim-mongodb | 27117 | ✅ Running | External memory storage (fresh container - no data yet) |

### PIM Application Services

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| Express API | 5000 | ✅ Running | Backend API + React frontend |
| Vue3 UI | 5500 | ⚠️ Not started | Run with `npm run vue` (runs on 10.32.3.27:5500) |
| PIM Engine | 5002 | ⚠️ Running (idle) | Process healthy; scheduler has 0 tasks so no scans yet |

### External Caelum Services (on 10.32.3.27)

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| FinColl API | 8002 | ✅ Production | Running locally via finvec `uvicorn`, model `v2.0-factorial` (copied checkpoint) |
| SenVec API | 18000 | ✅ Running | Managed by PM2 on 10.32.3.27 (senvec-aggregator) |
| Redis | 6379 | ✅ Running | Managed by caelum-unified on 10.32.3.27 |

---

## 🔍 Quick Health Check Commands

### Infrastructure
```bash
# PostgreSQL
docker ps | grep pim-postgres
# Should show: Up X minutes (healthy)

# MongoDB
docker ps | grep pim-mongodb
# Should show: Up X minutes

# Test PostgreSQL connection
docker exec pim-postgres psql -U pim_user -d pim_database -c "SELECT version();"
```

### Application Services
```bash
# Express API (comprehensive health)
curl http://10.32.3.27:5000/api/health | jq

# PIM Engine
curl http://10.32.3.27:5002/api/pim/status

# Vue3 UI (on 10.32.3.27)
curl http://10.32.3.27:5500/
```

### External Services
```bash
# FinColl (on 10.32.3.27)
curl http://10.32.3.27:8002/health | jq

# SenVec
curl http://10.32.3.27:18000/health
# OR
curl http://10.32.3.27:18000/health

# Redis
redis-cli -h 10.32.3.27 ping
```

---

## 🛠 Recent Remediation

1. Created `/tmp/paper_trading_bot_status.json` with `{ "running": true }` to keep trading loop enabled after restarts.
2. Created `/tmp/trading_bot_config.json` with confidence thresholds (`min_confidence: 0.65`) for prediction loop alignment.
3. Copied production checkpoint from `~/caelum/sxx/finvec/checkpoints/checkpoint_step_50000.pt` to `~/caelum/ss/finvec/checkpoints/final_model_diversified.pt`.
4. Updated `finvec/api/main.py` to load checkpoints with `weights_only=False`, infer horizons `[1,5,20]`, and wrap the inference engine for factorial vector output.
5. Verified FinColl health at `http://10.32.3.27:8002/health` returns `mode: "production"` with `model_version: "v2.0-factorial"`.

---

## 📋 Known Issues

None currently documented.

---

## ✨ What's Working

1. **PostgreSQL Database** - Healthy, password issue resolved (`pim_secure_2025!`)
2. **MongoDB** - Running (fresh container, no data loss risk)
3. **Express API** - Running and serving requests
4. **FinColl API** - Available on 10.32.3.27:8002, managed by PM2
5. **SenVec API** - Running on 10.32.3.27:18000, managed by PM2 (senvec-aggregator)
6. **Redis** - Running on 10.32.3.27:6379, managed by caelum-unified

---

## 🚀 Next Actions

To resume automated trading:

1. **Re-register Scheduler Tasks** – Restart Express server or call scheduler API to create `continuous-learning` task.
2. **Validate FinColl Outputs** – Compare live predictions against backtest benchmarks to ensure velocity/confidence values are non-zero.
3. **Run E2E workflow** – After tasks are active, execute `./tests/e2e/run-e2e-tests.sh` for integration validation.

---

## 📝 Important Notes

- **DO NOT recreate pim-postgres container** - See CRITICAL_DO_NOT_CHANGE.md
- **MongoDB is fresh** - No historical data yet, safe to recreate if needed
- **FinColl/SenVec live in finvec repo** - Start from `~/caelum/ss/finvec` (FinColl) and `~/caelum/ss/senvec`
- **Vue3 UI runs on 10.32.3.27** - Not on current workstation

---

**For automated startup**: Use `./scripts/start-all-services.sh`
**For manual startup**: See `STARTUP_PROCEDURE.md`
