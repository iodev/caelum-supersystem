# MVP 3-Agent Trading System

**Created**: 2025-11-30
**Deadline**: 12 hours (sim trading launch)
**Status**: ✅ READY FOR TESTING

---

## What Was Built

A simplified 3-agent autonomous trading pipeline that replaces the original 12+ agent system:

### Architecture

```
Layer 2 RL Recommendations (9 RL agents filter predictions)
          ↓
Portfolio Manager V2 (Claude Sonnet 4.5) - Makes trading decisions
          ↓
Risk Manager V2 (GPT-4o) - Validates risk and PDT compliance
          ↓
Account Manager V2 (Gemini 2.0) - Executes trades
          ↓
TradeStation Execution (simulated for MVP)
```

### Key Features

**Multi-Provider LLM Reasoning**:
- Portfolio Manager: Claude Sonnet 4.5 (Anthropic)
- Risk Manager: GPT-4o (OpenAI)
- Account Manager: Gemini 2.0 Flash (Google)
- Each agent uses a different LLM provider for independent analysis

**Shared Memory Tables**:
- `layer2_recommendations` - Filtered predictions from RL agents
- `portfolio_decisions` - Portfolio Manager trading decisions
- `risk_approvals` - Risk Manager approval/rejection decisions
- `mvp_agent_performance` - Performance tracking per agent

**Velocity-Driven Trading Philosophy**:
- Exit when profit velocity turns negative ($/hour tracking)
- "Let winners run" - no artificial profit caps
- Self-adjustment based on recent performance
- Confidence-scaled position sizing

---

## File Structure

```
PassiveIncomeMaximizer/
├── shared/
│   ├── schema-mvp-agents.ts         # Database schema for 3-agent pipeline
│   └── schema.ts                     # Updated to export MVP schema
│
├── server/services/agents/
│   ├── portfolio-manager-v2.ts       # Claude Sonnet 4.5 decision maker (426 lines)
│   ├── risk-manager-v2.ts            # GPT-4o risk validator (563 lines)
│   └── account-manager-v2.ts         # Gemini 2.0 executor (526 lines)
│
├── server/services/
│   └── mvp-pipeline-orchestrator.ts  # Coordinates all 3 agents (258 lines)
│
└── MVP_3_AGENT_README.md             # This file
```

---

## Prerequisites

### 1. Database

Ensure PostgreSQL is running with PIM database:

```bash
# Check database
docker ps | grep pim-postgres

# Start if needed
docker start pim-postgres
```

### 2. API Keys

Required environment variables:

```bash
# In .env file
ANTHROPIC_API_KEY=sk-ant-...         # For Portfolio Manager (Claude)
OPENAI_API_KEY=sk-...                # For Risk Manager (GPT-4o)
GOOGLE_GENERATIVE_AI_API_KEY=...    # For Account Manager (Gemini)

# Optional
TRADESTATION_API_KEY=...             # For live trading (not required for sim)
```

### 3. Database Migration

Apply the new MVP schema:

```bash
cd PassiveIncomeMaximizer

# Generate migration
npm run db:generate

# Apply migration (creates layer2_recommendations, portfolio_decisions, risk_approvals, mvp_agent_performance)
npm run db:push
```

**Expected tables**:
- `layer2_recommendations` ✅
- `portfolio_decisions` ✅
- `risk_approvals` ✅
- `mvp_agent_performance` ✅

---

## How to Run the Pipeline

### Option 1: Programmatic (Recommended for Testing)

Create a test script to run the orchestrator:

```typescript
// test-mvp-pipeline.ts
import { createMVPPipelineOrchestrator } from './server/services/mvp-pipeline-orchestrator';

const orchestrator = createMVPPipelineOrchestrator({
  anthropicApiKey: process.env.ANTHROPIC_API_KEY!,
  openaiApiKey: process.env.OPENAI_API_KEY!,
  geminiApiKey: process.env.GOOGLE_GENERATIVE_AI_API_KEY!,
  accountBalance: 100000,      // $100k sim account
  maxTradeAmount: 10000,       // Max $10k per trade
  riskPercentage: 2.0,         // 2% risk per trade
  accountId: 'SIM123456',      // Sim account ID
  accountType: 'sim',          // 'sim' or 'live'
  pollingInterval: 60000,      // 1 minute polling
  maxRecommendationsPerRun: 10
});

// Run once for testing
const result = await orchestrator.runOnce();
console.log('Pipeline result:', result);

// Or run continuously
await orchestrator.start();
// Pipeline runs every 1 minute...
// await orchestrator.stop();
```

### Option 2: Express API Endpoint

Add to Express API routes:

```typescript
// server/routes/mvp.ts
import { Router } from 'express';
import { createMVPPipelineOrchestrator } from '../services/mvp-pipeline-orchestrator';

const router = Router();
let orchestrator: any = null;

// POST /api/mvp/start - Start pipeline
router.post('/start', async (req, res) => {
  if (orchestrator?.getStatus().isRunning) {
    return res.status(400).json({ error: 'Pipeline already running' });
  }

  orchestrator = createMVPPipelineOrchestrator({
    anthropicApiKey: process.env.ANTHROPIC_API_KEY!,
    openaiApiKey: process.env.OPENAI_API_KEY!,
    geminiApiKey: process.env.GOOGLE_GENERATIVE_AI_API_KEY!,
    accountBalance: req.body.accountBalance || 100000,
    maxTradeAmount: req.body.maxTradeAmount || 10000,
    riskPercentage: req.body.riskPercentage || 2.0,
    accountId: req.body.accountId || 'SIM123456',
    accountType: req.body.accountType || 'sim',
    pollingInterval: req.body.pollingInterval || 60000,
    maxRecommendationsPerRun: 10
  });

  await orchestrator.start();
  res.json({ status: 'started', ...orchestrator.getStatus() });
});

// POST /api/mvp/stop - Stop pipeline
router.post('/stop', async (req, res) => {
  if (!orchestrator) {
    return res.status(400).json({ error: 'Pipeline not started' });
  }

  await orchestrator.stop();
  res.json({ status: 'stopped' });
});

// GET /api/mvp/status - Get pipeline status
router.get('/status', (req, res) => {
  if (!orchestrator) {
    return res.json({ isRunning: false });
  }

  res.json(orchestrator.getStatus());
});

// GET /api/mvp/stats - Get performance stats
router.get('/stats', async (req, res) => {
  if (!orchestrator) {
    return res.status(400).json({ error: 'Pipeline not started' });
  }

  const stats = await orchestrator.getPerformanceStats();
  res.json(stats);
});

export default router;
```

Then add to `server/index.ts`:

```typescript
import mvpRoutes from './routes/mvp';
app.use('/api/mvp', mvpRoutes);
```

---

## Testing the Pipeline

### Step 1: Insert Test Layer 2 Recommendations

Manually insert test recommendations to trigger the pipeline:

```sql
-- Insert a test Layer 2 recommendation (simulates RL agents filtering a prediction)
INSERT INTO layer2_recommendations (
  recommendation_id,
  symbol,
  direction,
  rl_average_confidence,
  rl_agent_scores,
  rl_passed_agents,
  fincoll_prediction_id,
  fincoll_confidence,
  fincoll_velocity,
  status
) VALUES (
  gen_random_uuid(),
  'TSLA',
  'LONG',
  0.85,
  '{
    "MomentumAgent": 0.92,
    "TechnicalAgent": 0.88,
    "SentimentAgent": 0.75,
    "VolumeAgent": 0.89,
    "RiskAgent": 0.78,
    "MacroAgent": 0.81,
    "OptionsAgent": 0.86,
    "SectorRotationAgent": 0.84,
    "MeanReversionAgent": 0.72
  }'::jsonb,
  9,
  'fincoll-pred-12345',
  0.92,
  125.50,
  'pending'
);
```

### Step 2: Run Pipeline

```bash
# Option A: Run once
npx tsx test-mvp-pipeline.ts

# Option B: Start continuous loop via API
curl -X POST http://10.32.3.27:5000/api/mvp/start \
  -H "Content-Type: application/json" \
  -d '{
    "accountBalance": 100000,
    "accountType": "sim"
  }'
```

### Step 3: Watch Logs

Watch the pipeline process the recommendation:

```
[Portfolio Manager V2] Processing 1 pending recommendations
[Portfolio Manager V2] Analyzing TSLA (LONG)
[Portfolio Manager V2] Decision made for TSLA: BUY (ID: abc-123)

[Risk Manager V2] Processing 1 pending decisions
[Risk Manager V2] Validating TSLA BUY
[Risk Manager V2] Decision for TSLA: APPROVED (ID: def-456)

[Account Manager V2] Processing 1 approved trades
[Account Manager V2] Executing TSLA BUY (100 shares)
[Account Manager V2] SIMULATED: BUY 100 TSLA @ $245.67 (Order: SIM-1701234567-TSLA)
[Account Manager V2] Trade executed: TSLA BUY - Order ID: SIM-1701234567-TSLA

[MVP Pipeline] === PIPELINE RUN COMPLETE (3456ms) ===
[MVP Pipeline] Summary: 1 recs → 1 decisions → 1 approved → 1 executed
```

### Step 4: Verify Database

Check that all tables were updated:

```sql
-- Check Layer 2 recommendation was marked as reviewed
SELECT * FROM layer2_recommendations WHERE symbol = 'TSLA';
-- Expected: status = 'reviewed', reviewed_by_portfolio_manager = true

-- Check Portfolio Manager decision
SELECT * FROM portfolio_decisions WHERE symbol = 'TSLA';
-- Expected: action = 'BUY', status = 'risk_approved', llm_provider = 'claude'

-- Check Risk Manager approval
SELECT * FROM risk_approvals WHERE symbol = 'TSLA';
-- Expected: decision = 'APPROVED', status = 'executed', llm_provider = 'gpt4'

-- Check execution details
SELECT
  symbol,
  action,
  quantity,
  execution_price,
  execution_order_id,
  execution_timestamp
FROM risk_approvals
WHERE symbol = 'TSLA';
-- Expected: execution_order_id = 'SIM-...', execution_price ≈ $245.67
```

### Step 5: Check Performance Stats

```bash
curl http://10.32.3.27:5000/api/mvp/stats | jq
```

Expected output:

```json
{
  "portfolioManager": {
    "totalDecisions": 1,
    "buyCount": 1,
    "sellCount": 0,
    "holdCount": 0,
    "waitCount": 0,
    "avgConfidence": 0.85
  },
  "riskManager": {
    "totalDecisions": 1,
    "approvedCount": 1,
    "rejectedCount": 0,
    "approvalRate": 100,
    "avgConfidence": 0.9
  },
  "accountManager": {
    "totalExecutions": 1,
    "successCount": 1,
    "failedCount": 0,
    "avgExecutionTime": 0.123,
    "avgSlippage": 0.05
  }
}
```

---

## Testing Different Scenarios

### Scenario 1: High-Confidence Buy (Should Approve)

```sql
INSERT INTO layer2_recommendations (
  recommendation_id, symbol, direction, rl_average_confidence,
  rl_passed_agents, status
) VALUES (
  gen_random_uuid(), 'NVDA', 'LONG', 0.92, 9, 'pending'
);
```

**Expected**: BUY → APPROVED → EXECUTED

---

### Scenario 2: Low-Confidence Prediction (Should Reject or WAIT)

```sql
INSERT INTO layer2_recommendations (
  recommendation_id, symbol, direction, rl_average_confidence,
  rl_passed_agents, status
) VALUES (
  gen_random_uuid(), 'AMD', 'LONG', 0.65, 5, 'pending'
);
```

**Expected**: WAIT or BUY → REJECTED (low confidence)

---

### Scenario 3: PDT Violation (Should Reject)

1. Create 3+ executed trades in last 5 days (to trigger PDT rule)
2. Insert new recommendation with margin account
3. **Expected**: BUY → REJECTED (PDT violation)

```sql
-- Simulate 3 recent trades (PDT threshold)
INSERT INTO risk_approvals (
  approval_id, portfolio_decision_id, symbol, action, decision, status, execution_timestamp
)
SELECT
  gen_random_uuid(), gen_random_uuid(), 'TEST' || i, 'BUY', 'APPROVED', 'executed', NOW() - INTERVAL '1 day'
FROM generate_series(1, 3) AS i;

-- Now try to execute 4th trade (should trigger PDT rejection)
INSERT INTO layer2_recommendations (
  recommendation_id, symbol, direction, rl_average_confidence, rl_passed_agents, status
) VALUES (
  gen_random_uuid(), 'AAPL', 'LONG', 0.88, 9, 'pending'
);
```

**Expected**: BUY → REJECTED (PDT rule - >3 day trades with account <$25k)

---

## Production Deployment

### Connecting to Real Layer 2 RL

The pipeline is designed to read from `layer2_recommendations` table. To connect to actual RL agents:

1. **Python RL Service** - Create a service that:
   - Fetches FinColl predictions
   - Runs 9 RL agents (from `./trained_agents_*/`)
   - Filters by confidence threshold
   - Inserts high-confidence recs into `layer2_recommendations`

2. **Example Python Integration**:

```python
# layer2_rl_service.py
import asyncio
from pim.data.fincoll_client import FinCollClient
from pim.agents.rl_agents import load_all_rl_agents
from db import insert_layer2_recommendation

async def poll_and_filter():
    fincoll = FinCollClient()
    rl_agents = load_all_rl_agents()  # Load 9 trained RL checkpoints

    while True:
        # 1. Fetch FinColl predictions
        predictions = await fincoll.get_predictions()

        for pred in predictions:
            # 2. Score with RL agents
            rl_scores = {}
            for agent_name, agent in rl_agents.items():
                score = agent.evaluate(pred)
                rl_scores[agent_name] = score

            # 3. Calculate average confidence
            avg_confidence = sum(rl_scores.values()) / len(rl_scores)
            passed_agents = sum(1 for s in rl_scores.values() if s > 0.7)

            # 4. Filter: Only high-confidence signals
            if avg_confidence > 0.75 and passed_agents >= 6:
                # 5. Insert into layer2_recommendations
                await insert_layer2_recommendation({
                    'symbol': pred.symbol,
                    'direction': 'LONG' if pred.direction > 0 else 'SHORT',
                    'rl_average_confidence': avg_confidence,
                    'rl_agent_scores': rl_scores,
                    'rl_passed_agents': passed_agents,
                    'fincoll_prediction_id': pred.id,
                    'fincoll_confidence': pred.confidence,
                    'fincoll_velocity': pred.velocity,
                    'status': 'pending'
                })

        await asyncio.sleep(300)  # Poll every 5 minutes
```

### TradeStation Integration

For live trading, replace simulated execution in `account-manager-v2.ts`:

```typescript
// In AccountManagerV2.submitOrder()
if (this.accountType === 'live') {
  // Call TradeStation API
  const tradeStationClient = new TradeStationClient(this.tradeStationApiKey);
  const order = await tradeStationClient.placeOrder({
    symbol,
    action,
    quantity,
    orderType,
    timeInForce,
    limitPrice
  });

  return {
    orderId: order.OrderID,
    fillPrice: order.FilledPrice,
    fillTimestamp: new Date(order.FilledTime),
    fillStatus: order.Status
  };
}
```

---

## Monitoring and Debugging

### Check Pipeline Status

```bash
# Is pipeline running?
curl http://10.32.3.27:5000/api/mvp/status

# Performance stats
curl http://10.32.3.27:5000/api/mvp/stats

# Recent decisions
psql -U pim_user -d pim_db -c "SELECT * FROM portfolio_decisions ORDER BY created_at DESC LIMIT 10;"

# Recent approvals
psql -U pim_user -d pim_db -c "SELECT * FROM risk_approvals ORDER BY created_at DESC LIMIT 10;"
```

### Common Issues

**Issue**: No recommendations processed

```bash
# Check for pending recommendations
psql -U pim_user -d pim_db -c "SELECT COUNT(*) FROM layer2_recommendations WHERE status = 'pending';"

# If 0: Insert test recommendation (see Testing section)
```

**Issue**: Decisions made but not approved

```bash
# Check pending decisions
psql -U pim_user -d pim_db -c "SELECT * FROM portfolio_decisions WHERE status = 'pending';"

# Check Risk Manager logs for rejection reasons
grep "Risk Manager" pim-server.log | tail -20
```

**Issue**: Approved but not executed

```bash
# Check pending approvals
psql -U pim_user -d pim_db -c "SELECT * FROM risk_approvals WHERE status = 'pending' AND decision = 'APPROVED';"

# Check Account Manager logs
grep "Account Manager" pim-server.log | tail -20
```

---

## Next Steps

### MVP Complete ✅

- [x] Database schema (4 tables)
- [x] Portfolio Manager V2 (Claude)
- [x] Risk Manager V2 (GPT-4o)
- [x] Account Manager V2 (Gemini)
- [x] Pipeline orchestrator
- [x] Testing guide
- [x] Deployment guide

### Future Enhancements

1. **Real Layer 2 Integration**
   - Connect to Python RL service
   - Load 27 trained RL checkpoints
   - Real-time RL filtering

2. **TradeStation API**
   - OAuth token management
   - Live order submission
   - Order status monitoring
   - Fill notifications

3. **Performance Tracking**
   - Agent performance dashboard
   - Win rate by LLM provider
   - Execution quality metrics
   - Meta-learning feedback loop

4. **Risk Enhancements**
   - Real-time portfolio value tracking
   - Sector concentration enforcement
   - Volatility-adjusted position sizing
   - Dynamic PDT management

5. **Monitoring**
   - Real-time pipeline dashboard
   - Alert system for rejections
   - Slack/Discord notifications
   - Performance anomaly detection

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                   LAYER 2: RL FILTERING (Python)                    │
│                                                                       │
│  FinColl Predictions → 9 RL Agents → Filter by Confidence (>0.75)   │
│                                 ↓                                     │
│                    layer2_recommendations table                      │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│               LAYER 1: 3-AGENT LLM PIPELINE (TypeScript)            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  PORTFOLIO MANAGER V2 (Claude Sonnet 4.5)                   │   │
│  │  • Reads: layer2_recommendations (status = 'pending')       │   │
│  │  • Analyzes RL scores + confidence                          │   │
│  │  • Makes decision: BUY/SELL/HOLD/WAIT                       │   │
│  │  • Calculates position size (confidence-scaled)             │   │
│  │  • Writes: portfolio_decisions table                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                ↓                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RISK MANAGER V2 (GPT-4o)                                   │   │
│  │  • Reads: portfolio_decisions (status = 'pending')          │   │
│  │  • Validates PDT compliance                                 │   │
│  │  • Checks position size limits                              │   │
│  │  • Verifies sector concentration                            │   │
│  │  • Independent risk assessment                              │   │
│  │  • Decision: APPROVED / REJECTED                            │   │
│  │  • Writes: risk_approvals table                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                ↓                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ACCOUNT MANAGER V2 (Gemini 2.0 Flash)                      │   │
│  │  • Reads: risk_approvals (decision = 'APPROVED')            │   │
│  │  • Determines execution strategy (order type, timing)       │   │
│  │  • Submits order to TradeStation (or simulates)             │   │
│  │  • Monitors order fill status                               │   │
│  │  • Updates: risk_approvals (execution details)              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  EXECUTION: TradeStation API                         │
│                    (Simulated for MVP)                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

✅ **MVP 3-Agent System Complete**

- 4 new database tables for shared memory
- 3 LLM agents (Claude + GPT-4 + Gemini) for independent reasoning
- Pipeline orchestrator for continuous operation
- Simulated execution for testing
- Comprehensive testing and deployment guide

**Ready for sim trading launch!** 🚀

