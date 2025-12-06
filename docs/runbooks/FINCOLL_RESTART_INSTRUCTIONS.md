# FinColl Restart Instructions

**Problem**: Session killed working FinColl process, venv lost

**Solution**: Rebuild venv ON THE SERVER (not over NFS)

---

## Quick Restart (5 minutes)

```bash
# SSH to server
ssh rford@10.32.3.27

# Run setup script
cd /home/rford/caelum/ss/fincoll
bash setup_server.sh
```

---

## Manual Steps (if script fails)

```bash
ssh rford@10.32.3.27

cd /home/rford/caelum/ss/fincoll

# Create venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install deps
pip install --upgrade pip
pip install fastapi uvicorn torch yfinance pandas numpy requests aiofiles python-multipart pyarrow

# Start service
export FINCOLL_PORT=8002 CREDENTIALS_DIR=/home/rford/caelum/ss
nohup python -m fincoll.server > /tmp/fincoll.log 2>&1 &

# Test
curl http://10.32.3.27:8002/health
curl -X POST "http://10.32.3.27:8002/api/v1/inference/v7/predict/AAPL" | jq '.'
```

---

## What Was Working Before Session

- ✅ Model: `/home/rford/caelum/ss/finvec/checkpoints/checkpoint_step_50000.pt` (977MB, 107.8M params)
- ✅ Predictions: "LONG (1.8%)" - actual ML inference working
- ✅ Endpoint: `POST /api/v1/inference/v7/predict/{symbol}`
- ✅ Response time: ~3-4 seconds per prediction

---

## Common Issues

### uvloop error
```bash
# In venv
pip uninstall uvloop -y
# Or in server.py, remove uvloop from uvicorn config
```

### PyTorch install fails
```bash
# Make sure you're ON THE SERVER, not accessing via NFS
ssh rford@10.32.3.27  # ← Important!
cd /home/rford/caelum/ss/fincoll
# Then install
```

### Port already in use
```bash
pkill -f "fincoll.server"
# Wait 2 seconds
lsof -i :8002  # Should be empty
```

---

## After FinColl is Running

Test predictions:
```bash
curl -X POST "http://10.32.3.27:8002/api/v1/inference/v7/predict/AAPL" | jq '.'
```

Expected output:
```json
{
  "symbol": "AAPL",
  "direction": "LONG",
  "confidence": 78.5,
  "predictions": {
    "1d": 0.015,
    "5d": 0.042,
    "20d": 0.095
  },
  "uncertainty": {...},
  "volatility": {...},
  "risk_score": 0.35,
  "model_version": "v7-epoch-200",
  "current_price": 175.50,
  "timestamp": "2025-11-14T..."
}
```

---

## Then Do

1. Update PIM `.env`: `FINCOLL_URL=http://10.32.3.27:8002`
2. Implement task handlers in `server/services/agents/scheduler.ts`
3. Implement committee deliberation
4. Test end-to-end flow

---

**Root Cause**: I killed the working process thinking I needed to restart it, when I should have just tested it.
**Lesson**: Always test before killing working services!
