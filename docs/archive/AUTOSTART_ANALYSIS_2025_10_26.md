# Autostart Services Analysis - 2025-10-26

**Question**: What services should auto-start on WSL restart?

---

## ✅ SERVICES THAT AUTO-START (Currently Configured)

### 1. finvec-trading.service - **ENABLED & RUNNING**

**Status**: ✅ Auto-starts on WSL boot
**Service File**: `/etc/systemd/system/finvec-trading.service`
**Current State**: Active (running) since 21:16:53, PID 395
**Memory**: 2.4GB (peak: 2.6GB)

**What it does**:
- Continuous market monitoring 24/7
- Token refresh every 10 minutes (TradeStation OAuth)
- Market data updates every 5 minutes (during market hours)
- Signal generation every 15 minutes (paper trading)
- Model evaluation every hour
- Health check every minute
- Log cleanup daily at 2 AM

**Restart Policy**: `Restart=always`, `RestartSec=10`
**Dependencies**: `After=network.target`

**Command**:
```bash
sudo systemctl status finvec-trading
sudo journalctl -u finvec-trading -f  # Live logs
```

---

## 📅 CRON JOBS (Scheduled Tasks)

**Crontab for user `rford`**:

### 1. Automated Training/Validation
**Schedule**: 7:30 AM daily (Mon-Fri) - Phoenix time / 10:30 AM EST
**Command**:
```bash
cd /home/rford/caelum/ss/finvec &&
source .venv/bin/activate &&
python3 scripts/automated_training_validation.py >> logs/cron_auto_train.log 2>&1
```
**Purpose**: Daily model retraining 1 hour after market open
**Status**: ✅ ACTIVE

### 2. Overnight Model Improvement
**Schedule**: 10:00 PM daily (8-hour run)
**Status**: ⏸️ **DISABLED** (commented out)
**Reason**: Likely disabled during V4 development
**Command** (when enabled):
```bash
cd /home/rford/caelum/ss/finvec &&
source .venv/bin/activate &&
python3 scripts/overnight_improvement.py --hours 8 >> logs/cron_overnight.log 2>&1
```

### 3. Paper Trading Validation (Old V2)
**Schedule**: 1:30 PM Phoenix / 4:30 PM EST
**Status**: ⏸️ **DISABLED** - marked as OLD_V2
**Purpose**: Market close validation

---

## ❌ SERVICES THAT SHOULD AUTO-START (But Don't)

### 1. MongoDB - NOT CONFIGURED
**Expected Port**: 27017 on 10.32.3.27
**Current Status**: ❌ Not running
**Impact**: PassiveIncomeMaximizer Phase 2 cannot function
**Auto-start**: None configured

**Should this auto-start?** YES (if PIM Phase 2 is production)

**How to enable auto-start**:
```bash
# Option A: System MongoDB service (if installed)
sudo systemctl enable mongodb
sudo systemctl start mongodb

# Option B: Docker container with restart policy
docker run -d \
  --name caelum-mongodb \
  --restart always \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=adminroderick \
  -e MONGO_INITDB_ROOT_PASSWORD=SFKgEUbidQ38bpK12ofc \
  -v mongodb-data:/data/db \
  mongo:latest
```

### 2. Redis - NOT CONFIGURED
**Expected Port**: 6379 on 10.32.3.27
**Current Status**: ❌ Unknown (not checked)
**Impact**: Caelum caching layer unavailable
**Auto-start**: None configured

**Should this auto-start?** YES (if Caelum is production)

**How to enable auto-start**:
```bash
docker run -d \
  --name caelum-redis \
  --restart always \
  -p 6379:6379 \
  redis:alpine
```

### 3. PassiveIncomeMaximizer - NOT CONFIGURED
**Expected**: PIM server/orchestrator
**Current Status**: ❌ No systemd service found
**Impact**: PIM agents not running autonomously
**Auto-start**: None configured

**Should this auto-start?** DEPENDS
- If PIM is production → YES
- If PIM is development/testing → NO (manual start)

**How to enable auto-start** (if needed):
```bash
# Create systemd service
sudo nano /etc/systemd/system/pim-orchestrator.service

[Unit]
Description=PassiveIncomeMaximizer Trading Orchestrator
After=network.target postgresql.service

[Service]
Type=simple
User=rford
Group=rford
WorkingDirectory=/home/rford/caelum/ss/PassiveIncomeMaximizer
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npx tsx server/index.ts
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable pim-orchestrator
sudo systemctl start pim-orchestrator
```

### 4. Caelum-Unified MCP Servers - MANUAL START ONLY
**Current Status**: Running (PIDs 2300, 2318, 2325)
**Started by**: Claude Code session (manual)
**Auto-start**: None configured (intentional - development mode)

**Should this auto-start?** NO (currently in development)
- MCP servers are session-specific
- Started by Claude Code when needed
- Not intended as always-on services (yet)

### 5. Docker Containers (Windows Host)
**Expected**:
- caelum-prometheus (monitoring)
- caelum-nginx (reverse proxy)
- caelum-mongodb (database)
- caelum-redis (cache)

**Current Status**: ❓ Unknown (Docker not accessible from WSL)
**Location**: Windows host (not WSL)
**Auto-start**: Depends on Docker Desktop auto-start + container restart policies

**How to check from Windows**:
```powershell
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

**How to enable auto-start**:
```powershell
# Set containers to auto-restart
docker update --restart=always caelum-prometheus
docker update --restart=always caelum-nginx
docker update --restart=always caelum-mongodb
docker update --restart=always caelum-redis
```

---

## 🔍 SERVICES FOUND BUT NOT INSTALLED

### 1. `/home/rford/caelum/ss/caelum/systemd/caelum-worker.service`
**Status**: Service file exists but not installed
**Purpose**: Unknown - Caelum worker process

### 2. `/home/rford/caelum/ss/caelum/opportunity-discovery-server/scripts/caelum-system.service`
**Status**: Service file exists but not installed
**Purpose**: Caelum system service (opportunity discovery)

**Should these be installed?** MAYBE
- Depends on Caelum deployment status
- Check with user before enabling

---

## 🚨 THINGS THAT GOT SHUT OFF (Interrupted)

### 1. FinVec V4 Data Generation
**Status**: Was running, now stopped (41% complete)
**PID**: No longer running
**Last Log**: `generate_v4_seq300_part1.log` stopped at 24/59 symbols
**Cause**: Likely system reboot or manual termination
**Auto-restart**: ❌ NO - This is a one-time batch job

**How to restart**:
```bash
cd /home/rford/caelum/ss/finvec
.venv/bin/python scripts/generate_training_data_v4.py \
  --seq-len 300 \
  --output data/training/timing_training_data_v4_seq300.pt &
```

### 2. MongoDB (if it was running)
**Status**: ❌ Not running
**Auto-restart**: ❌ NO (never configured)
**Need**: Configure auto-start if production

### 3. Redis (if it was running)
**Status**: ❌ Unknown
**Auto-restart**: ❌ NO (never configured)
**Need**: Configure auto-start if production

### 4. Docker Containers on Windows
**Status**: ❓ Unknown
**Auto-restart**: Depends on `--restart` policy
**Check**: Need to verify from Windows PowerShell

---

## 📋 AUTO-START SUMMARY TABLE

| Service | Auto-Start? | Status | Should Auto-Start? | Action Needed |
|---------|------------|--------|-------------------|---------------|
| **finvec-trading.service** | ✅ YES | ✅ Running | ✅ YES | None - working correctly |
| **Cron: Daily training** | ✅ YES | ✅ Scheduled | ✅ YES | None - working correctly |
| **MongoDB** | ❌ NO | ❌ Stopped | ✅ YES (if prod) | Configure systemd or Docker |
| **Redis** | ❌ NO | ❓ Unknown | ✅ YES (if prod) | Configure systemd or Docker |
| **PIM Orchestrator** | ❌ NO | ❌ Not running | ⚠️ MAYBE | Depends on production status |
| **Caelum MCP Servers** | ❌ NO | ✅ Running | ❌ NO | Manual start OK (dev mode) |
| **V4 Data Generation** | ❌ NO | ❌ Stopped | ❌ NO | One-time job - restart manually |
| **Docker Containers** | ⚠️ DEPENDS | ❓ Unknown | ✅ YES (if prod) | Set `--restart=always` |

---

## 🎯 RECOMMENDED AUTO-START CONFIGURATION

### For Production Deployment:

1. **Keep Auto-Starting**:
   - ✅ finvec-trading.service (already enabled)
   - ✅ Cron jobs (already enabled)

2. **Add Auto-Start** (if moving to production):
   - 🔧 MongoDB (via Docker with `--restart=always`)
   - 🔧 Redis (via Docker with `--restart=always`)
   - 🔧 PIM Orchestrator (create systemd service)
   - 🔧 Prometheus/nginx (update Docker restart policy)

3. **Leave Manual Start** (development):
   - 🔧 Caelum MCP servers (session-specific)
   - 🔧 V4 data generation (one-time jobs)
   - 🔧 Training jobs (scheduled or manual)

### For Development:
- Current setup is fine
- Only finvec-trading auto-starts (makes sense - it's production)
- Everything else is manual start (gives control)

---

## 🔧 QUICK REFERENCE: SERVICE COMMANDS

### Check All Services
```bash
# Check finvec-trading
sudo systemctl status finvec-trading

# Check cron jobs
crontab -l

# Check running processes
ps aux | grep -E "finvec|python|node"

# Check listening ports
sudo netstat -tlnp | grep -E ":(5000|8080|27017|6379)"
```

### View Logs
```bash
# finvec-trading service logs
sudo journalctl -u finvec-trading -f

# Cron job logs
tail -f /home/rford/caelum/ss/finvec/logs/cron_auto_train.log

# Service logs
tail -f /home/rford/caelum/ss/finvec/logs/service/finvec_service.log
```

### Restart Services
```bash
# Restart finvec-trading
sudo systemctl restart finvec-trading

# Reload cron after editing
crontab -e  # Edit
# Cron automatically reloads
```

---

## 💡 KEY INSIGHTS

1. **Only FinVec Trading is auto-starting** - This is intentional
   - It's the only production service
   - Everything else is development/manual

2. **V4 data generation is NOT auto-start** - Correct behavior
   - It's a batch job, not a service
   - Should be run manually or via specific workflows

3. **MongoDB/Redis are NOT auto-starting** - Decision needed
   - If PIM Phase 2 is production → Enable auto-start
   - If still in development → Keep manual start

4. **WSL services survive restarts** - `finvec-trading.service` will auto-restart
   - systemd services persist across WSL restarts
   - cron jobs persist across WSL restarts

5. **Docker containers are separate** - Windows host issue
   - Need to check Windows Docker Desktop settings
   - Set `--restart=always` for production containers

---

## 🚀 IMMEDIATE ACTIONS AFTER WSL RESTART

**What auto-starts**:
1. ✅ finvec-trading.service (automatic)
2. ✅ Cron jobs (automatic)

**What you need to manually start**:
1. MongoDB (if needed for PIM Phase 2)
2. Redis (if needed for Caelum)
3. MCP servers (if needed for Claude Code)
4. V4 data generation (if incomplete)
5. PIM orchestrator (if production)

**Quick health check script**:
```bash
#!/bin/bash
echo "=== Service Health Check ==="
echo ""
echo "1. FinVec Trading Service:"
sudo systemctl is-active finvec-trading && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "2. MongoDB:"
timeout 1 bash -c "echo > /dev/tcp/10.32.3.27/27017" 2>/dev/null && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "3. Redis:"
redis-cli -h 10.32.3.27 ping 2>/dev/null || echo "❌ Not accessible"
echo ""
echo "4. PostgreSQL:"
timeout 1 bash -c "echo > /dev/tcp/localhost/15432" 2>/dev/null && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "5. Running processes:"
ps aux | grep -E "finvec|python|node" | grep -v grep | wc -l
echo "processes found"
```

---

**Created**: 2025-10-26 21:30 UTC
**Summary**: Only finvec-trading auto-starts. Everything else is manual (intentional for development).
**Decision Needed**: Should MongoDB, Redis, and PIM be production services with auto-start?
