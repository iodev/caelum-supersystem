# PassiveIncomeMaximizer Auto-Start & Health Monitoring Setup

## 🚨 CRITICAL: Position Management During Reboots

**Problem**: If the system reboots while positions are active, they could be left unmanaged.

**Solution**: Auto-start + Health Monitoring + Position Recovery

---

## Quick Setup (5 minutes)

```bash
cd /home/rford/caelum/ss

# 1. Run the auto-start setup script
./setup-auto-start.sh

# 2. When prompted, run the sudo command shown

# 3. Verify it's working
pm2 list

# 4. Test health monitoring
./health-monitor.sh
```

---

## What Gets Auto-Started

### Critical Services (Auto-restart on failure)

1. **pim-server** (Port 5000)
   - PIM core server with agent swarm
   - Manages active positions
   - **Auto-restart**: Immediate (2s delay)
   - **Max restarts**: 50 (active positions are critical!)

2. **fincoll-server** (Port 8002)
   - ML inference API (V7 model: checkpoint_step_50000.pt)
   - **Auto-restart**: 5s delay
   - **Max restarts**: 10
   - **Note**: Port changed from 8001 to 8002 (2025-11-15)

3. **senvec-aggregator** (Port 18000)
   - Sentiment analysis aggregator (49D active, 72D potential)
   - **Auto-restart**: 5s delay
   - **Max restarts**: 10

4. **senvec-alphavantage** (Port 18002)
   - Alpha Vantage sentiment (18D cross-asset signals)

5. **senvec-social** (Port 18003)
   - Social media sentiment (23D)

6. **senvec-news** (Port 18004)
   - News sentiment (8D)

---

## PM2 Configuration

All services are configured in: `/home/rford/caelum/ss/pm2-ecosystem.config.js`

### Key Features:
- ✅ Auto-restart on crash
- ✅ Memory limits (prevents runaway processes)
- ✅ Centralized logging
- ✅ Wait for dependencies before starting
- ✅ Immediate restart for critical services

### PM2 Commands:

```bash
# View all processes
pm2 list

# View logs (all services)
pm2 logs

# View logs (specific service)
pm2 logs pim-server

# Restart a service
pm2 restart pim-server

# Stop a service
pm2 stop pim-server

# Start a service
pm2 start pim-server

# Restart all
pm2 restart all

# Save current state
pm2 save

# Restore saved state
pm2 resurrect
```

---

## Health Monitoring

### Automatic Checks (Every 5 minutes)

The health monitor (`/home/rford/caelum/ss/health-monitor.sh`) checks:

1. **PIM Server** (CRITICAL)
   - PM2 process status
   - HTTP health endpoint
   - **Action on failure**: Alert + Auto-restart

2. **FinVec Inference**
   - PM2 process status
   - **Action on failure**: Alert + Auto-restart

3. **FinColl**
   - PM2 process status
   - HTTP health endpoint
   - **Action on failure**: Alert + Auto-restart

4. **SenVec**
   - PM2 process status
   - HTTP health endpoint
   - **Action on failure**: Log warning (non-critical)

5. **Infrastructure**
   - Redis connectivity (10.32.3.27:6379)
   - Qdrant connectivity (10.32.3.27:6333)
   - **Action on failure**: Alert

6. **Active Positions Check** (CRITICAL)
   - Queries `/api/positions` endpoint
   - If positions exist AND system has failures → CRITICAL ALERT

### Manual Health Check:

```bash
# Run health check manually
/home/rford/caelum/ss/health-monitor.sh

# View health monitor logs
tail -f /home/rford/caelum/ss/logs/health-monitor.log

# Check PIM health endpoint
curl http://10.32.3.27:5000/api/health | jq

# Quick status
curl http://10.32.3.27:5000/api/health/check
```

---

## Position Recovery

**Location**: `PassiveIncomeMaximizer/server/services/position-recovery.ts`

### What It Does (On PIM Startup):

1. ✅ Fetches current positions from Alpaca
2. ✅ Checks which positions are tracked in database
3. ✅ Creates trade records for any unmanaged positions
4. ✅ Updates tracked positions with current broker data
5. ✅ Logs recovery summary
6. ✅ Sends CRITICAL alert if unmanaged positions found

### How to Integrate:

Add to `PassiveIncomeMaximizer/server/initializer.ts`:

```typescript
import { createPositionRecoveryService } from './services/position-recovery';

// In initializeSystem(), after alpacaClient is initialized:
const positionRecovery = createPositionRecoveryService(alpacaClient, storage);
const recoveryResult = await positionRecovery.recoverPositions();

logger.info('Position Recovery Result:', recoveryResult);

if (recoveryResult.unmanagedPositions > 0) {
  logger.error(`ALERT: ${recoveryResult.unmanagedPositions} unmanaged positions found!`);
  // TODO: Send notification
}
```

---

## Alerting (Optional Enhancement)

### Email Alerts:

Set in environment or health-monitor.sh:
```bash
export ALERT_EMAIL="your-email@example.com"
```

### Slack Alerts:

Set webhook URL:
```bash
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

## Testing Auto-Start

### Test 1: Manual Restart
```bash
# Stop all PM2 processes
pm2 stop all

# Resurrect from saved state
pm2 resurrect

# Verify all started
pm2 list
```

### Test 2: Reboot Test
```bash
# Save current PM2 state
pm2 save

# Reboot the system
sudo reboot

# After reboot, check PM2
pm2 list

# Should show all services running
```

### Test 3: Position Recovery
```bash
# Check recovery status endpoint (add to routes)
curl http://10.32.3.27:5000/api/position-recovery/status | jq
```

---

## Log Locations

- **PM2 Logs**: `/home/rford/.pm2/logs/`
- **PIM Server**: `/home/rford/caelum/ss/PassiveIncomeMaximizer/logs/`
- **FinVec**: `/home/rford/caelum/ss/finvec/logs/`
- **FinColl**: `/home/rford/caelum/ss/fincoll/logs/`
- **SenVec**: `/home/rford/caelum/ss/senvec/logs/`
- **Health Monitor**: `/home/rford/caelum/ss/logs/health-monitor.log`

---

## Troubleshooting

### PM2 not auto-starting on reboot?
```bash
# Re-run startup config
pm2 startup
# Copy/paste the sudo command
# Save state
pm2 save
```

### Service won't start?
```bash
# Check PM2 logs
pm2 logs <service-name> --lines 100

# Check if port is in use
ss -tlnp | grep <port>

# Try starting manually
cd /home/rford/caelum/ss/<service-directory>
# Run the start command from pm2-ecosystem.config.js
```

### Health monitor not running?
```bash
# Check cron jobs
crontab -l

# Add manually if missing
crontab -e
# Add: */5 * * * * /home/rford/caelum/ss/health-monitor.sh >> /home/rford/caelum/ss/logs/health-monitor.log 2>&1
```

---

## Next Steps

1. ✅ Run `./setup-auto-start.sh`
2. ✅ Verify all services: `pm2 list`
3. ✅ Test health monitor: `./health-monitor.sh`
4. ✅ Add position recovery to initializer.ts
5. ✅ Configure alerting (email/Slack)
6. ✅ Test with system reboot
7. ✅ Monitor logs for first 24 hours

---

## Status Before vs After

### BEFORE ❌
- No auto-start mechanism
- No health monitoring
- No position recovery
- System reboot = unmanaged positions = RISK

### AFTER ✅
- PM2 auto-starts all services on reboot
- Health checks every 5 minutes
- Auto-restart failed services
- Position recovery on startup
- Active position alerts if failures detected
- System reboot = auto-recovery = SAFE

---

## Emergency Commands

```bash
# Stop everything immediately
pm2 stop all

# Restart everything
pm2 restart all

# View real-time logs
pm2 logs --lines 1000

# Check system health
curl http://10.32.3.27:5000/api/health | jq

# Check active positions
curl http://10.32.3.27:5000/api/positions | jq
```
