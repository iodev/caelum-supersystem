# Trading System Finalization Plan

**Date**: 2025-12-02  
**Objective**: Activate PassiveIncomeMaximizer MVP trading pipeline  
**Current Status**: All components exist but pipeline not running

---

## Executive Summary

The trading system is "super close" because:
- ✅ All architecture, code, and integrations are complete
- ✅ Database schema ready with all MVP tables
- ✅ Services running: pim-server, pim-engine, fincoll, senvec
- ❌ **MVP pipeline components NOT running** (root cause)

**Blocker**: `start-mvp.sh` has never been executed. Three critical components are not running:
1. MVP Recommendation Poller - Fetches FinColl predictions
2. MVP Pipeline Orchestrator - Runs 3-agent decision pipeline
3. Layer 2 RL Service - Filters predictions by confidence

---

## Current System Status (on 10.32.3.27 via PM2)

### Running
- pim-server (port 5000, 8h uptime, 19 restarts)
- pim-engine (port 5002, 9h uptime, 84 restarts)
- fincoll-server (port 8002, 8h uptime)
- senvec-aggregator (port 18000, 3 days uptime)
- All senvec microservices (ports 18001-18004)

### Not Running (Critical)
- MVP Recommendation Poller (TypeScript)
- MVP Pipeline Orchestrator (TypeScript)
- Layer 2 RL Service (Python, port 5003)

### Pipeline Architecture
```
FinColl (8002) 
    ↓ [NOT RUNNING]
MVP Poller → Layer 2 RL (5003) → layer2_recommendations table
    ↓ [NO DATA]
Portfolio Manager V2 (Claude) → portfolio_decisions table
    ↓ [NO DECISIONS]
Risk Manager V2 (GPT-4) → risk_approvals table
    ↓ [NO APPROVALS]
Account Manager V2 (Grok) → TradeStation API / Simulation
```

---

## Implementation Plan

### Phase 1: Activate MVP Pipeline (30 minutes) - CRITICAL

#### Step 1.1: Verify Environment Variables
Location: `PassiveIncomeMaximizer/.env`

Required variables:
- DATABASE_URL
- ANTHROPIC_API_KEY (Claude for Portfolio Manager)
- OPENAI_API_KEY (GPT-4 for Risk Manager)
- XAI_API_KEY (Grok for Account Manager)
- TRADESTATION_CLIENT_ID
- TRADESTATION_CLIENT_SECRET
- TRADESTATION_API_URL=https://sim-api.tradestation.com/v3
- TRADESTATION_ACCOUNT_ID

**Action**: `ssh rford@10.32.3.27` and verify `.env` file has all keys

#### Step 1.2: Verify TradeStation OAuth Token
Location: `~/.tradestation_token.json`

Check token validity:
```bash
cat ~/.tradestation_token.json | jq '.expiry'
curl -H "Authorization: Bearer $(cat ~/.tradestation_token.json | jq -r '.access_token')" \
  https://sim-api.tradestation.com/v3/accounts
```

If expired or 401 error, run: `node PassiveIncomeMaximizer/sync-tradestation-token.cjs`

#### Step 1.3: Start MVP Services
```bash
cd /home/rford/caelum/caelum-supersystem/PassiveIncomeMaximizer
./start-mvp.sh
```

This script starts:
1. **Layer 2 RL Service** (Python) - Port 5003, filters predictions by confidence
2. **MVP Recommendation Poller** (TypeScript) - Polls FinColl every 5 minutes
3. **MVP Pipeline Orchestrator** (TypeScript) - Runs 3-agent pipeline every 1 minute

PIDs saved to: `/tmp/mvp-pids.txt`

#### Step 1.4: Verify Services Started
```bash
# Check processes running
ps aux | grep -E "layer2_service|mvp-poller|mvp-orchestrator" | grep -v grep

# Check Layer 2 RL service health
curl http://localhost:5003/health

# View saved PIDs
cat /tmp/mvp-pids.txt
```

Expected: 3 processes with PIDs

#### Step 1.5: Monitor Pipeline Activation
```bash
# Watch orchestrator log
tail -f /tmp/mvp-orchestrator.log
```

Look for:
- "🤖 Starting MVP Pipeline Orchestrator (continuous mode)..."
- "Checking for pending recommendations..."
- "Step 1: Portfolio Manager analyzing recommendations..."

---

### Phase 2: Verify Data Flow (20 minutes)

#### Step 2.1: Check FinColl Service
```bash
curl http://localhost:8002/health
curl http://localhost:8002/api/v1/inference/velocity/AAPL
```

Expected: Health check passes, AAPL prediction returns with velocities

#### Step 2.2: Monitor MVP Poller
```bash
tail -f /tmp/mvp-poller.log
```

Wait for 5-minute cycle. Look for:
- "Fetching predictions from FinColl..."
- "Sending to Layer 2 RL for filtering..."
- "Inserted N recommendations into database"

#### Step 2.3: Verify Database Population
```bash
psql postgresql://pim_user:pim_password@10.32.3.27:15433/pim_db -c \
  "SELECT COUNT(*) FROM layer2_recommendations WHERE status = 'pending';"

psql postgresql://pim_user:pim_password@10.32.3.27:15433/pim_db -c \
  "SELECT symbol, layer2_score, created_at FROM layer2_recommendations 
   ORDER BY created_at DESC LIMIT 10;"
```

Expected: Recommendations with `layer2_score > 0.6` and `status='pending'`

---

### Phase 3: Verify 3-Agent Pipeline (30 minutes)

#### Step 3.1: Monitor Portfolio Manager (Claude)
Watch `/tmp/mvp-orchestrator.log` for:
- "Step 1: Portfolio Manager analyzing recommendations..."
- "Portfolio Manager decision: BUY/SELL/HOLD for SYMBOL"
- "Reasoning: [Claude's analysis]"

Database check:
```sql
SELECT decision_id, symbol, decision, reasoning 
FROM portfolio_decisions 
WHERE status = 'pending' 
ORDER BY created_at DESC LIMIT 5;
```

Expected: Claude-generated decisions with detailed reasoning

#### Step 3.2: Monitor Risk Manager (GPT-4)
Watch for:
- "Step 2: Risk Manager validating decision..."
- "Risk Manager approval: APPROVED/REJECTED for SYMBOL"
- "Risk notes: [GPT-4 analysis]"

Database check:
```sql
SELECT approval_id, decision_id, approved, risk_notes 
FROM risk_approvals 
WHERE status = 'pending' 
ORDER BY created_at DESC LIMIT 5;
```

Expected: GPT-4 risk validations with approval status

#### Step 3.3: Monitor Account Manager (Grok)
Watch for:
- "Step 3: Account Manager executing approved trade..."
- "Executing trade: BUY/SELL SYMBOL @ PRICE"
- "TradeStation API response" OR "Using simulated execution"

Database check:
```sql
SELECT approval_id, execution_status, execution_details, executed_at 
FROM risk_approvals 
WHERE execution_status IN ('executed', 'failed') 
ORDER BY executed_at DESC LIMIT 5;
```

Expected: Trade executions with status and details

---

### Phase 4: Fix Missing API Endpoints (60 minutes)

**Current 404 Errors** (from Express server logs):
- GET /api/portfolio → 404
- GET /api/positions/active → 404
- GET /api/decisions/recent → 404
- GET /api/decisions/agents/performance → 404
- GET /api/risk/metrics → 404

#### Step 4.1: Create MVP Routes File
File: `PassiveIncomeMaximizer/server/routes/mvp-routes.ts`

```typescript
import { Router } from 'express';
import { storage } from '../storage';

const router = Router();

// Portfolio state from database
router.get('/portfolio', async (req, res) => {
  const decisions = await storage.db.query(`
    SELECT pd.symbol, pd.decision, pd.created_at,
           ra.approved, ra.execution_status
    FROM portfolio_decisions pd
    LEFT JOIN risk_approvals ra ON pd.decision_id = ra.decision_id
    WHERE pd.status = 'active'
    ORDER BY pd.created_at DESC
  `);
  res.json({ success: true, portfolio: decisions.rows });
});

// Active positions
router.get('/positions/active', async (req, res) => {
  const positions = await storage.db.query(`
    SELECT * FROM risk_approvals 
    WHERE execution_status = 'executed' AND status = 'active'
    ORDER BY executed_at DESC
  `);
  res.json({ success: true, positions: positions.rows });
});

// Recent decisions
router.get('/decisions/recent', async (req, res) => {
  const decisions = await storage.db.query(`
    SELECT pd.*, ra.approved, ra.risk_notes
    FROM portfolio_decisions pd
    LEFT JOIN risk_approvals ra ON pd.decision_id = ra.decision_id
    ORDER BY pd.created_at DESC
    LIMIT 50
  `);
  res.json({ success: true, decisions: decisions.rows });
});

// Agent performance
router.get('/agents/performance', async (req, res) => {
  const performance = await storage.db.query(`
    SELECT * FROM mvp_agent_performance 
    ORDER BY created_at DESC
  `);
  res.json({ success: true, performance: performance.rows });
});

export default router;
```

#### Step 4.2: Mount Routes in Server
File: `PassiveIncomeMaximizer/server/server.ts`

Add import:
```typescript
import mvpRoutes from './routes/mvp-routes';
```

Mount routes:
```typescript
app.use('/api/mvp', mvpRoutes);
```

#### Step 4.3: Test Endpoints
```bash
# Restart Express server
ssh rford@10.32.3.27 "pm2 restart pim-server"

# Test endpoints
curl http://10.32.3.27:5000/api/mvp/portfolio
curl http://10.32.3.27:5000/api/mvp/positions/active
curl http://10.32.3.27:5000/api/mvp/decisions/recent
curl http://10.32.3.27:5000/api/mvp/agents/performance
```

Expected: JSON responses with data from MVP tables

---

### Phase 5: End-to-End Integration Test (45 minutes)

#### Step 5.1: Prepare Test Environment
1. Set `useMockExecution = true` in orchestrator (safe testing mode)
2. Clear test data:
```sql
TRUNCATE layer2_recommendations, portfolio_decisions, 
         risk_approvals, mvp_agent_performance;
```

#### Step 5.2: Trigger Test Cycle
Wait for next poller cycle (5 minutes max)

Monitor all logs simultaneously:
```bash
tail -f /tmp/mvp-poller.log /tmp/layer2-service.log /tmp/mvp-orchestrator.log
```

#### Step 5.3: Verify Each Stage
- **Stage 1**: FinColl Fetch → "Fetched N predictions from FinColl"
- **Stage 2**: Layer 2 Filter → Only predictions with score > 0.6 pass
- **Stage 3**: Database Insert → "Inserted N recommendations"
- **Stage 4**: Portfolio Manager → Claude decision with reasoning
- **Stage 5**: Risk Manager → GPT-4 approval with notes
- **Stage 6**: Account Manager → Execution completes (simulated)

#### Step 5.4: Success Criteria
✅ All 6 stages complete without errors  
✅ Data flows through all tables correctly  
✅ Agents generate coherent decisions  
✅ Execution status recorded in database  
✅ No crashes or unhandled exceptions  

---

### Phase 6: TradeStation Live Testing (30 minutes)

**PREREQUISITE**: Phase 5 must be 100% successful with simulated execution

#### Step 6.1: Enable Real TradeStation Execution
File: `PassiveIncomeMaximizer/mvp-start-orchestrator.ts` (created by start-mvp.sh)

Change line:
```typescript
useMockExecution: false,  // CHANGE FROM true TO false
accountType: 'sim',       // KEEP AS SIM for safety
```

Restart: `./stop-mvp.sh && ./start-mvp.sh`

#### Step 6.2: Verify TradeStation Connection
Monitor orchestrator log for:
- "TradeStationService initialized with account: SIM-XXX"
- "TradeStation API connection successful"

If errors:
- "Unauthorized" → Token expired, run sync script
- "Account not found" → Wrong TRADESTATION_ACCOUNT_ID

#### Step 6.3: Execute Test Trade
Wait for next pipeline cycle with approved trade

Monitor for:
- "Placing order via TradeStation API..."
- "TradeStation order ID: XXX"
- "Order status: FILLED/PARTIAL/REJECTED"

#### Step 6.4: Verify on TradeStation
1. Log into https://sim.tradestation.com
2. Navigate to Orders → Recent Orders
3. Verify order appears with correct:
   - Symbol (e.g., AAPL not "buy")
   - Side (BUY/SELL)
   - Quantity
   - Status (FILLED)

---

## Security Blockers (DO NOT DEPLOY TO PRODUCTION YET)

From `PEER_REVIEW_EXECUTIVE_SUMMARY.md`:

🔴 **5 CRITICAL ISSUES** blocking live trading:

1. **No Input Validation** (2 hours to fix)
   - Risk: Invalid symbols, database crashes
   - File: `server/routes/symbol-presets-routes.ts`

2. **No Authentication** (3 hours to fix)
   - Risk: Anyone can modify presets, DoS attacks
   - File: Same as above

3. **No Integration Tests** (4 hours to fix)
   - Risk: Unknown failures in production
   - Location: `tests/` directory

4. **No Migration Rollback Plan** (2 hours to fix)
   - Risk: Cannot recover from failed deployments
   - File: `migrations/005_add_symbol_presets.sql`

5. **Circular Dependency** (1 hour to fix)
   - Risk: Performance degradation (100-200ms slower)
   - File: `server/routes/backtest-routes.ts:240`

**Total Work**: 12 hours minimum (3 working days)

**Recommendation**: Complete Phases 1-6 in SIM account, then fix security issues before live trading

---

## Critical Files Reference

### Configuration
- `PassiveIncomeMaximizer/.env` - All environment variables and API keys
- `PassiveIncomeMaximizer/start-mvp.sh` - MVP startup script (84 lines)
- `PassiveIncomeMaximizer/stop-mvp.sh` - MVP shutdown script
- `~/.tradestation_token.json` - OAuth token (check expiry!)

### MVP Components  
- `mvp-recommendation-poller.ts` - Polls FinColl, filters via Layer 2
- `server/services/mvp-pipeline-orchestrator.ts` - 3-agent continuous pipeline
- `engine/layer2_service.py` - RL confidence filtering (port 5003)

### Agent Implementations
- `server/services/agents/portfolio-manager-v2.ts` - Claude Sonnet 4 decision maker
- `server/services/agents/risk-manager-v2.ts` - GPT-4o risk validator
- `server/services/agents/account-manager-v2.ts` - Grok-3 + TradeStation executor

### Database Tables (PostgreSQL)
- `layer2_recommendations` - FinColl predictions filtered by RL
- `portfolio_decisions` - Portfolio Manager decisions
- `risk_approvals` - Risk Manager approvals + execution results
- `mvp_agent_performance` - Agent accuracy tracking

### Log Files
- `/tmp/mvp-orchestrator.log` - Pipeline execution (primary)
- `/tmp/mvp-poller.log` - FinColl polling
- `/tmp/layer2-service.log` - RL filtering
- `/tmp/mvp-pids.txt` - Process IDs

---

## Recommended Execution Order

### TODAY (if you want to see trades)
**Time**: ~90 minutes total

1. **Phase 1 (30 min)**: Activate MVP pipeline via `start-mvp.sh`
2. **Phase 2 (20 min)**: Verify FinColl → Layer 2 → Database flow
3. **Phase 3 (30 min)**: Verify 3-agent pipeline execution
4. **STOP and OBSERVE**: Let system run for few hours, monitor logs

Expected outcome: Trades executing in simulation mode, full pipeline active

### TOMORROW (once stable)
**Time**: ~2-3 hours total

5. **Phase 4 (60 min)**: Fix 404 API endpoints for frontend visibility
6. **Phase 5 (45 min)**: Formal end-to-end integration test
7. **Phase 6 (30 min)**: Enable real TradeStation SIM account execution

Expected outcome: Real orders on TradeStation SIM account, API working

### NEXT WEEK (for production)
**Time**: ~5-6 days

8. **Phase 7**: Security hardening (12+ hours development)
9. Integration test suite (4 hours)
10. Security review and approval (1 day)
11. Live account deployment (2 hours)

Expected outcome: Production-ready system

---

## Questions for User

Before executing this plan:

1. **Priority**: Do you want to activate the pipeline TODAY to see trades, or review security issues first?

2. **TradeStation**: Do you have the SIM account ID and confirmed the OAuth token is valid?

3. **API Keys**: Are Claude, GPT-4, and Grok API keys funded with sufficient credits for testing?

4. **Execution Mode**: Should we start with `useMockExecution = true` (simulated) or go straight to real SIM trades?

5. **Symbol List**: Which symbols should the poller fetch? Use "MVP Recommendation Poller" preset from database?

6. **404 Errors**: Are these blocking your current work, or can they wait until after pipeline activation?

7. **Monitoring**: Do you want desktop notifications for trades, or just log monitoring?

---

## Next Steps

**If proceeding with activation:**
1. SSH to 10.32.3.27
2. Navigate to PassiveIncomeMaximizer directory
3. Run `./start-mvp.sh`
4. Monitor `/tmp/mvp-orchestrator.log`
5. Wait 5 minutes for first recommendation cycle
6. Watch for Portfolio Manager → Risk Manager → Account Manager flow

**Expected first trade within**: 5-10 minutes of activation (if FinColl has predictions ready)

**Stop anytime with**: `./stop-mvp.sh`

---

**Document Status**: ✅ COMPLETE  
**Ready for Execution**: YES (Phases 1-6)  
**Production Ready**: NO (Security fixes required first)
