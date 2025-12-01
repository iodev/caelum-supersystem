# Monday Morning Checklist - Market Readiness

**Market Open**: 9:30 AM ET
**Pre-Market Prep**: 6:00 AM - 9:00 AM ET

---

## 🔴 6:00 AM - Automated Readiness Check

**Run**:
```bash
cd /home/rford/caelum/caelum-supersystem/finvec
./scripts/monday_readiness_check.sh
```

This automatically:
- ✅ Finds best velocity checkpoint (~15 epochs from weekend training)
- ✅ Validates checkpoint integrity
- ✅ Starts velocity inference server (port 5001)
- ✅ Tests prediction endpoint
- ✅ Generates readiness report

**Expected Output**: "Status: READY FOR TESTING"

---

## 🟡 6:30 AM - Manual Verification

### 1. Check Training Results
```bash
ssh rford@10.32.3.44
tail -100 /tmp/velocity_training.log | grep "Epoch"
```

**Look for**:
- Final epoch number (target: ~15)
- Final loss value (should be decreasing)
- No CUDA errors or crashes

### 2. Verify All Services Running
```bash
# Velocity server
curl http://localhost:5001/health

# FinColl API
curl http://localhost:8002/health

# PIM Engine
curl http://localhost:5002/api/pim/status

# PIM Express
curl http://localhost:5000/api/health
```

**All should return**: `{"status": "healthy"}` or similar

### 3. Test Full Pipeline
```bash
# Test velocity prediction through FinColl
curl "http://localhost:8002/api/v1/inference/velocity/AAPL"
```

**Expected**: JSON with velocities for 5 timeframes

---

## 🟢 7:00 AM - Quick RL Retraining (Optional)

If velocity predictions look good, optionally retrain RL agents:

```bash
cd /home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine
source .venv/bin/activate

# Quick retraining (30 min)
python scripts/quick_rl_retrain.py --epochs 50 --symbols SPY AAPL MSFT
```

**Or**: Use existing RL checkpoints for initial testing

---

## 🔵 8:00 AM - PIM Integration Test

### 1. Start PIM Services
```bash
# Start PIM Engine (Layer 2 RL + Layer 1 LLM)
cd /home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/engine
source .venv/bin/activate
python pim_service.py &  # Port 5002

# Start Express server (frontend)
cd /home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer
npm run dev &  # Port 5000
```

### 2. Run Test Trades
```bash
# Test PIM decision-making on 5 symbols
curl -X POST http://localhost:5002/api/pim/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["SPY", "AAPL", "MSFT", "GOOGL", "AMZN"]}'
```

**Look for**:
- Layer 2 RL predictions (9 agents voting)
- Layer 1 LLM decisions (9 agents voting)
- Meta-learner weighted output
- Final decision: BUY/SELL/HOLD with confidence

### 3. Verify Decision Quality
- Check confidence scores (>0.7 is good)
- Verify reasoning makes sense
- Ensure no errors in logs

---

## 🟣 8:30 AM - Sim Account Connection

### 1. Configure Sim Account
```bash
# Edit PIM config
vim /home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer/config/trading.json
```

Set:
```json
{
  "mode": "paper",
  "account_type": "sim",
  "max_position_size": 100,
  "max_daily_trades": 10
}
```

### 2. Test Connection
```bash
curl http://localhost:5002/api/pim/account/status
```

**Expected**: Account balance, buying power, positions

---

## ⚪ 9:00 AM - Final Pre-Market Check

### Dashboard Health
- Open: http://localhost:5000 (PIM Dashboard)
- Check: All agents showing green status
- Verify: Market data streaming (pre-market activity)

### Monitoring
- Open: http://localhost:8888 (Training monitor)
- Open: http://10.32.3.27:3002 (Grafana - cost metrics)
- Check: All metrics updating

### Risk Management
- Verify: Max position size limits
- Verify: Stop-loss configured
- Verify: Max daily loss limit

---

## 🟢 9:30 AM - Market Open

### Initial Testing Period (9:30 - 10:00 AM)
- **Mode**: OBSERVE ONLY
- Watch PIM recommendations
- DO NOT execute trades yet
- Validate signals make sense

### If Signals Look Good (10:00 AM+)
- Enable paper trading
- Start with 1-2 small positions
- Monitor closely for first hour
- Check for any errors/anomalies

---

## 🚨 Rollback Plan

If anything fails:

### Emergency Stops
```bash
# Stop all PIM services
pkill -f pim_service
pkill -f "npm.*PassiveIncome"

# Stop velocity server
pkill -f velocity_inference_server
```

### Fallback Options
1. Use FinColl V6/V7 direct features (skip velocity)
2. Use existing RL checkpoints (skip retraining)
3. Manual trading only (disable PIM automation)

---

## 📊 Success Criteria

**Minimum for "GO"**:
- ✅ Velocity server responding (even if predictions not perfect)
- ✅ FinColl API working
- ✅ PIM Engine making decisions
- ✅ No critical errors in logs
- ✅ Sim account connected

**Ideal for "FULL GO"**:
- ✅ All above PLUS
- ✅ RL agents retrained with V7
- ✅ Meta-learner showing good confidence
- ✅ Backtests show positive expected value
- ✅ All monitoring dashboards healthy

---

## 📝 Contacts & Resources

**Logs**:
- Training: `/tmp/velocity_training.log`
- Velocity server: `/tmp/velocity_server_monday.log`
- PIM Engine: Check `pim_service.py` output
- Monday readiness: `/tmp/monday_readiness_*.log`

**Monitoring**:
- Training: http://localhost:8888
- Grafana: http://10.32.3.27:3002
- PIM Dashboard: http://localhost:5000

**Emergency**: Stop everything, assess, decide whether to postpone live testing

---

**Last Updated**: 2025-11-29 (Session continuation)
