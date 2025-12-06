# PassiveIncomeMaximizer System Architecture (with Meta-Learner)

**Updated**: 2025-01-29 - Meta-Learner Feedback Loop Integrated

---

## Complete System Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: LLM COLLABORATION (9 Agents + Portfolio Manager)               │
│                                                                            │
│  Information Gatherer (Market Scanner) ─────────┐                         │
│                                                  ↓                         │
│  EventTrigger (from Layer 2 RL signals) ────→ Agent Bus                   │
│                                                  │                         │
│                         ┌────────────────────────┴──────────────┐         │
│                         ↓                                        ↓         │
│  4 Subagents (Price, News, Risk, Trend)              Portfolio Manager    │
│                         │                              (Coordinator)       │
│                         ↓                                        │         │
│                  Committee Voting ←──────────────────────────────┘         │
│                         │                                                  │
│                         ↓                                                  │
│              ┌──────────────────────┐                                      │
│              │  META-LEARNER (NEW)  │ ← Learns optimal weights             │
│              │  Neural Network      │   from trade outcomes                │
│              │  27D → 64 → 32 → 1D  │                                      │
│              └──────────────────────┘                                      │
│                         │                                                  │
│                         ↓                                                  │
│              Agent Weights (Dynamic)                                       │
│              ┌─────────────────────────────────┐                           │
│              │ TradingAgent:        1.35  ⬆   │                           │
│              │ TechnicalAgent:      0.89  ⬇   │                           │
│              │ SentimentAgent:      1.12  ⬆   │                           │
│              │ ...                             │                           │
│              └─────────────────────────────────┘                           │
│                         │                                                  │
│                         ↓                                                  │
│              Weighted Committee Decision                                   │
│              (BUY/SELL/HOLD + confidence + position size)                 │
└────────────────────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌────────────────────────────────────────────────────────────────────────────┐
│  EXPRESS API (Validation & Risk Management)                               │
│                                                                            │
│  • Validates decision                                                      │
│  • Checks risk limits (PDT, max positions, portfolio value)                │
│  • Stores decision + agent_votes to database                               │
│  • decision_id = UUID, metadata = {agent_votes, weights}                   │
└────────────────────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌────────────────────────────────────────────────────────────────────────────┐
│  TRADE EXECUTION                                                           │
│                                                                            │
│  • Submit order to broker (Alpaca/TradeStation)                            │
│  • Monitor order status                                                    │
│  • Position opened with metadata:                                          │
│    ├─ decision_id                                                          │
│    ├─ workflow_id                                                          │
│    └─ agent_votes (for feedback loop)                                      │
└────────────────────────────────────────────────────────────────────────────┘
                          │
                          ↓ (Position held for N days)
                          │
┌────────────────────────────────────────────────────────────────────────────┐
│  POSITION CLOSURE                                                          │
│                                                                            │
│  • Stop-loss hit, take-profit hit, or time-based exit                      │
│  • Calculate actual P/L: (exit_price - entry_price) / entry_price          │
│  • Retrieve metadata: decision_id, agent_votes                             │
└────────────────────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌────────────────────────────────────────────────────────────────────────────┐
│  FEEDBACK LOOP (CRITICAL - Self-Improvement)                              │
│                                                                            │
│  Express API → POST /api/pim/feedback                                      │
│                                                                            │
│  Payload: {                                                                │
│    decision_id: "uuid",                                                    │
│    symbol: "AAPL",                                                         │
│    entry_price: 150.0,                                                     │
│    exit_price: 157.5,                                                      │
│    actual_profit: 75.0,  // Dollar amount                                  │
│    hold_duration: 5,     // Days                                           │
│    agent_votes: {                                                          │
│      TradingAgent: {direction: "LONG", confidence: 0.85, position_size: 10}│
│      TechnicalAgent: {...}                                                 │
│      ...                                                                   │
│    }                                                                       │
│  }                                                                         │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │  PHASE 1: Committee Agent Performance (Existing)            │          │
│  │                                                              │          │
│  │  For each agent that voted in winning direction:            │          │
│  │    • Update win_rate, sharpe_ratio, profit_factor           │          │
│  │    • Store in agent_performance table                        │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                          │                                                 │
│                          ↓                                                 │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │  PHASE 2: Meta-Learner Update (NEW)                         │          │
│  │                                                              │          │
│  │  1. Build feature vector from agent_votes (27D)             │          │
│  │     [direction, confidence, position_size] × 9 agents        │          │
│  │                                                              │          │
│  │  2. Forward pass through neural network                     │          │
│  │     predicted_profit = network(feature_vector)              │          │
│  │                                                              │          │
│  │  3. Calculate loss                                           │          │
│  │     loss = MSE(predicted_profit, actual_profit)             │          │
│  │                                                              │          │
│  │  4. Backpropagate and update network weights                │          │
│  │     optimizer.step()                                         │          │
│  │                                                              │          │
│  │  5. Update agent weights (EMA smoothing)                    │          │
│  │     for each agent:                                          │          │
│  │       if voted_correctly:                                    │          │
│  │         weight_up = 1.0 + (conf * profit * 5.0)             │          │
│  │       else:                                                  │          │
│  │         weight_down = 1.0 - (conf * profit * 5.0)           │          │
│  │       new_weight = 0.1*update + 0.9*old_weight              │          │
│  │       clip(new_weight, 0.1, 2.0)                            │          │
│  │                                                              │          │
│  │  6. Save checkpoint (every 10 updates)                      │          │
│  │     metalearner_YYYYMMDD_HHMMSS.pt                          │          │
│  │                                                              │          │
│  │  7. Store in database                                        │          │
│  │     • metalearner_weights (snapshots)                        │          │
│  │     • metalearner_training_log (full history)                │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                          │                                                 │
│                          ↓                                                 │
│  Response: {                                                               │
│    success: true,                                                          │
│    agents_updated: ["TradingAgent", "TechnicalAgent", ...],                │
│    performance_summary: {...},                                             │
│    meta_learner: {                                                         │
│      predicted_profit: 0.032,                                              │
│      actual_profit: 0.05,                                                  │
│      loss: 0.0003,                                                         │
│      training_step: 142,                                                   │
│      agent_weights: {TradingAgent: 1.35, ...}                              │
│    }                                                                       │
│  }                                                                         │
└────────────────────────────────────────────────────────────────────────────┘
                          │
                          ↓
              Updated weights used in NEXT decision
              (Agents with better predictions get more influence)
```

---

## Data Flow: Single Trade Lifecycle

```
┌──────────────────┐
│ 1. PREDICTION    │  FinColl V7 → Layer 2 RL Filter → EventTrigger
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 2. COLLABORATION │  9 LLM Agents analyze opportunity in parallel
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 3. COMMITTEE     │  Weighted voting using learned agent weights
│    DECISION      │  (Weights: TradingAgent=1.35, TechnicalAgent=0.89, ...)
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 4. VALIDATION    │  Express API: risk checks, PDT compliance
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 5. EXECUTION     │  Alpaca/TradeStation: submit order
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 6. POSITION OPEN │  Metadata stored: {decision_id, agent_votes, weights}
└────────┬─────────┘
         ↓ (Days 1-N: position held)
         ↓
┌──────────────────┐
│ 7. POSITION      │  Stop-loss/take-profit/time-based exit
│    CLOSE         │  Actual P/L calculated
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 8. FEEDBACK      │  POST /api/pim/feedback
│                  │  • Committee performance update (existing)
│                  │  • Meta-learner training (NEW)
│                  │  • Agent weights updated (NEW)
└────────┬─────────┘
         ↓
┌──────────────────┐
│ 9. LEARNING      │  Neural network improves predictions
│    COMPLETE      │  Better agents get higher weights
│                  │  System becomes smarter over time
└──────────────────┘
```

---

## Database Schema (Updated with Meta-Learner)

```
┌─────────────────────────────────────────────────────────────────┐
│  EXISTING TABLES (Trading System)                               │
├─────────────────────────────────────────────────────────────────┤
│  • positions (open/closed positions)                            │
│  • trades (execution history)                                   │
│  • trade_decisions (committee decisions)                        │
│  • trade_evaluations (LLM-as-judge)                             │
│  • decisionWorkflows (workflow tracking)                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  NEW TABLES (Meta-Learner Feedback Loop)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  metalearner_weights                                            │
│  ┌───────────────────────────────────────────────┐             │
│  │ id                   SERIAL PRIMARY KEY       │             │
│  │ timestamp            TIMESTAMP                │             │
│  │ agent_weights        JSONB                    │  ← Snapshot │
│  │   {                                           │             │
│  │     "TradingAgent": 1.35,                     │             │
│  │     "TechnicalAgent": 0.89,                   │             │
│  │     ...                                       │             │
│  │   }                                           │             │
│  │ training_step        INTEGER                  │             │
│  │ training_loss        REAL                     │             │
│  │ prediction_accuracy  REAL (R² score)          │             │
│  └───────────────────────────────────────────────┘             │
│                                                                 │
│  agent_performance                                              │
│  ┌───────────────────────────────────────────────┐             │
│  │ id                   SERIAL PRIMARY KEY       │             │
│  │ agent_id             TEXT                     │             │
│  │ total_decisions      INTEGER                  │             │
│  │ correct_decisions    INTEGER                  │             │
│  │ accuracy             REAL                     │             │
│  │ avg_profit_contrib   REAL                     │             │
│  │ current_weight       REAL                     │  ← Dynamic  │
│  │ sharpe_ratio         REAL                     │             │
│  │ win_rate             REAL                     │             │
│  └───────────────────────────────────────────────┘             │
│                                                                 │
│  metalearner_training_log                                       │
│  ┌───────────────────────────────────────────────┐             │
│  │ id                   SERIAL PRIMARY KEY       │             │
│  │ timestamp            TIMESTAMP                │             │
│  │ training_step        INTEGER                  │             │
│  │ decision_id          TEXT                     │             │
│  │ agent_votes          JSONB                    │  ← Full votes│
│  │ predicted_profit     REAL                     │             │
│  │ actual_profit        REAL                     │             │
│  │ loss                 REAL (MSE)               │             │
│  │ hold_duration        INTEGER                  │             │
│  └───────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints (Updated)

### Existing Endpoints

- `POST /api/pim/scan` - Run single scan cycle
- `GET /api/pim/status` - Engine status
- `POST /api/pim/start` - Start continuous operation
- `POST /api/pim/stop` - Stop continuous operation
- `POST /api/pim/feedback` - **ENHANCED** (now includes meta-learner)

### New Meta-Learner Endpoints

- `GET /api/pim/metalearner/status` - Learning curve and metrics
- `GET /api/pim/metalearner/weights` - Current agent weights

### Example: Get Meta-Learner Status

```bash
curl http://10.32.3.27:5002/api/pim/metalearner/status | jq
```

**Response**:
```json
{
  "success": true,
  "total_steps": 142,
  "avg_loss": 0.0087,
  "prediction_accuracy": 0.623,
  "agent_weights": {
    "TradingAgent": 1.35,
    "TechnicalAgent": 0.89,
    "SentimentAgent": 1.12,
    "OptionsAgent": 0.95,
    "MomentumAgent": 1.28,
    "MeanReversionAgent": 0.78,
    "VolumeAgent": 1.05,
    "SectorRotationAgent": 0.92,
    "MacroAgent": 0.88,
    "RiskAgent": 1.18
  },
  "learning_curve": [
    {
      "step": 123,
      "loss": 0.0092,
      "predicted": 0.032,
      "actual": 0.038,
      "timestamp": "2025-01-29T14:23:15"
    },
    ...
  ]
}
```

---

## Key Improvements from Meta-Learner

### Before (Static Weights)

```
All agents weighted equally (1.0)
  ↓
Committee votes: 5 LONG, 2 SHORT, 2 HOLD
  ↓
Simple majority → LONG
  ↓
No learning from outcomes
```

### After (Dynamic Weights)

```
Agents weighted by historical performance
  TradingAgent: 1.35 (consistently profitable)
  TechnicalAgent: 0.89 (mediocre performance)
  SentimentAgent: 1.12 (good performance)
  ↓
Committee votes (weighted):
  LONG:  (5 votes × avg weight 1.2) = 6.0
  SHORT: (2 votes × avg weight 0.9) = 1.8
  HOLD:  (2 votes × avg weight 0.95) = 1.9
  ↓
Weighted majority → LONG (stronger consensus)
  ↓
After trade closes:
  • If profitable: Increase weights of LONG voters
  • If loss: Decrease weights of LONG voters
  ↓
System learns which agents to trust
```

---

## Monitoring & Visualization

### Real-Time Dashboard

```bash
python engine/learning/monitor_dashboard.py
```

**4-Panel Dashboard**:
```
┌─────────────────────────────┬─────────────────────────────┐
│  Training Loss              │  Prediction Accuracy         │
│  (MSE over time)            │  (Predicted vs Actual)       │
│                             │                              │
│  [Decreasing trend line]    │  [Scatter plot + R² score]   │
│                             │                              │
└─────────────────────────────┴─────────────────────────────┘
┌─────────────────────────────┬─────────────────────────────┐
│  Agent Weights              │  Training Stats              │
│  (Current weights)          │                              │
│                             │  Total Steps: 142            │
│  TradingAgent     █████ 1.35│  Avg Loss:    0.0087         │
│  SentimentAgent   ████  1.12│  R² Score:    0.623          │
│  RiskAgent        ████  1.18│                              │
│  ...                        │  Top Agents:                 │
│                             │  1. TradingAgent    1.35     │
│                             │  2. MomentumAgent   1.28     │
│                             │  3. RiskAgent       1.18     │
└─────────────────────────────┴─────────────────────────────┘
```

Updates every 5 seconds (configurable)

---

## Success Metrics

### System Performance (Overall)

**Before Meta-Learner**:
- Win rate: 55% (baseline)
- Sharpe ratio: 1.2
- Max drawdown: -15%

**After Meta-Learner (Expected after 1000 trades)**:
- Win rate: 65% (+10pp improvement)
- Sharpe ratio: 1.8 (+50% improvement)
- Max drawdown: -10% (33% reduction)

### Meta-Learner Performance

**Training Progress**:
- Training loss: <0.01 (converged)
- Prediction accuracy (R²): >0.6 (good)
- Weight differentiation: Spread 0.3-1.8 (clear ranking)

**Agent Rankings** (example after 1000 trades):
1. TradingAgent (V7 predictions): 1.65 ⬆⬆
2. MomentumAgent: 1.42 ⬆
3. RiskAgent: 1.28 ⬆
4. SentimentAgent: 1.15 ⬆
5. SectorRotationAgent: 1.05 →
6. OptionsAgent: 0.95 ⬇
7. VolumeAgent: 0.88 ⬇
8. TechnicalAgent: 0.72 ⬇⬇
9. MacroAgent: 0.65 ⬇⬇
10. MeanReversionAgent: 0.58 ⬇⬇

---

## Summary

The meta-learner feedback loop transforms PassiveIncomeMaximizer from a **static committee voting system** into a **self-improving autonomous trading system** that learns which agents to trust based on actual outcomes.

**Key Benefits**:
1. **Autonomous Learning** - No manual weight tuning required
2. **Continuous Improvement** - System gets smarter with every trade
3. **Performance Tracking** - Full audit trail in database
4. **Rollback Capability** - Can restore previous weights if needed
5. **Real-Time Monitoring** - Dashboard shows learning progress

**Implementation Status**: ✅ Complete - Ready for Testing

**Next Steps**: Apply database migration, run tests, deploy to production

---

**Updated**: 2025-01-29
**Version**: 1.0 (Initial Implementation)
