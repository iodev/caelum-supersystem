# FinVec ↔ PassiveIncomeMaximizer Integration Analysis

**Date**: 2025-10-24
**Context**: Understanding how two projects integrate and relate to Caelum ecosystem

---

## 🎯 Executive Summary

**Two Distinct But Integrated Projects:**

1. **FinVec** (`/home/rford/caelum/ss/finvec`)
   - **Role**: AI Research & Model Development
   - **Technology**: Python, PyTorch, Custom LLM Architecture
   - **Output**: Stock prediction models (V3, V4 in development)
   - **Team**: ML/AI researchers building novel architecture
   - **Status**: V4 in Phase 3 (data generation 3h+ in progress)

2. **PassiveIncomeMaximizer (PIM)** (`/home/rford/caelum/ss/PassiveIncomeMaximizer`)
   - **Role**: Production Trading System
   - **Technology**: TypeScript, Node.js, LangGraph, Multi-Agent System
   - **Input**: FinVec predictions + 9 specialized AI agents
   - **Output**: Live trades on TradeStation (simulation account)
   - **Status**: Integrated with FinVec v2, awaiting v4 models

---

## 📊 The Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  PIM Web Dashboard (React) - http://10.32.3.27:3000              │
│  - Portfolio view, agent status, predictions, P/L tracking      │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              PASSIVE INCOME MAXIMIZER (PIM)                      │
│  Multi-Agent Trading System (TypeScript/Node.js)                │
│                                                                  │
│  9 Specialized Agents (LangGraph):                              │
│  ├─ Portfolio Manager - Overall strategy                        │
│  ├─ Price Analyzer - Technical analysis                         │
│  ├─ News Processor - Sentiment analysis                         │
│  ├─ Risk Manager - Position sizing                              │
│  ├─ Trend Analyzer - Market regime detection                    │
│  ├─ Metrics Evaluator - Performance tracking                    │
│  ├─ Event Trigger - Alert system                                │
│  ├─ Web Search - Real-time research                             │
│  └─ Information Gatherer - Data collection                      │
│                                                                  │
│  Plus: FinVec Agent (NEW)                                       │
│  └─ Calls FinVec API for AI predictions                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ REST API (http://10.32.3.27:5000)
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FINVEC API SERVER                           │
│  Python FastAPI serving trained models                          │
│                                                                  │
│  Endpoints:                                                      │
│  - POST /predict - Get predictions for symbol                   │
│  - GET /health - System health                                  │
│  - POST /retrain - Trigger model update                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FINVEC CORE (Python)                          │
│  Custom Financial LLM Implementation                             │
│                                                                  │
│  Components:                                                     │
│  ├─ Financial Tokenizer - OHLC → Tokens                         │
│  ├─ Financial Embeddings - Temporal + Asset embeddings          │
│  ├─ Transformer Architecture - Multi-head attention             │
│  ├─ Prediction Heads - Multi-horizon forecasting                │
│  └─ Profit-Aware Trainer - Optimizes for profitability          │
│                                                                  │
│  Current Models:                                                 │
│  ├─ V3 FINAL: 50D features, 64.6% win rate, +1.34% avg profit   │
│  └─ V4: 81D features (velocity+acceleration+jerk) IN TRAINING   │
└─────────────────────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                   MARKET DATA SOURCES                            │
│  ├─ TradeStation API (primary) - Real-time & historical         │
│  ├─ Alpaca API (backup) - Market data                           │
│  └─ Technical Indicators - RSI, MACD, Bollinger Bands           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. **Model Training Flow** (FinVec Standalone)

```
Market Data (TradeStation/Alpaca)
    ↓
FinVec Data Generator (scripts/generate_training_data_v4.py)
    ↓ [RUNNING NOW - 3h+ elapsed]
Training Data Files (timing_training_data_v4_seq{300,500,800}.pt)
    ↓ [NEXT: Auto-launches GPU training]
GPU Training on 3 machines (8-12 hours)
    ↓
Trained Models (checkpoints/timing_v4_seq300/best_model.pt)
    ↓
Backtesting & Validation
    ↓
Production Model (deployed to API server)
```

### 2. **Live Trading Flow** (PIM + FinVec Integration)

```
Every 5 minutes (pipelineInterval):

1. PIM → TradeStation API
   "Get latest bars for AAPL, MSFT, GOOGL, TSLA, NVDA"

2. PIM → Format data for FinVec
   OHLC + Volume + Technical Indicators → JSON

3. PIM → FinVec API (POST /predict)
   Request: { symbol, bars, indicators }
   Response: { hour1: +1.5%, day1: +2.8%, days5: +4.2%, confidence: 0.85 }

4. PIM Signal Generation
   IF hour1 > 1.0 AND day1 > 2.0 AND days5 > 3.0:
      → BUY signal (confidence 85%)

5. PIM Risk Manager
   Check: maxPositionSize ($5k), minConfidence (70%), maxOpenPositions (3)
   → Approved

6. PIM → TradeStation Execute
   Place order: BUY AAPL $5000 @ market
   Set stop loss: -2%
   Set take profit: +4%

7. PIM → Database
   Store: prediction, trade, ongoing P/L tracking

8. Every hour (learningInterval):
   IF 100+ closed trades AND accuracy declining:
      → Trigger FinVec retraining with actual outcomes
```

---

## 💾 Database Schema

### PIM PostgreSQL (`pim_prod`)

**FinVec-Specific Tables:**
```sql
finvec_predictions       -- AI predictions with horizons
trade_executions         -- Executed trades
trade_outcomes          -- P/L tracking
finvec_learning_data    -- Retraining dataset
finvec_retraining_log   -- Model update history
finvec_learning_metrics -- Accuracy by horizon
finvec_market_data      -- Market data cache
```

**Agent System Tables:**
```sql
agents                   -- 9 + 1 FinVec agent
agent_configs           -- Agent settings
agent_decisions         -- Decision history
agent_insights          -- Analysis results
agent_performance       -- Metrics tracking
```

---

## 🏗️ Integration Points

### Current Integration (FinVec v2)

**Status**: ✅ Operational on production

1. **FinVec Agent** (`server/services/agents/finvec-prediction-agent.ts`)
   - Integrated into LangGraph workflow
   - Calls FinVec API for predictions
   - Converts predictions to trading signals

2. **Orchestrator** (`server/services/finvec/orchestrator.ts`)
   - Coordinates: Data Pipeline → Predictions → Execution → Tracking → Learning
   - Runs as background service

3. **Configuration** (`finvec-config.json`)
   - Account: SIM1137629M (TradeStation simulation)
   - Symbols: 5 (AAPL, MSFT, GOOGL, TSLA, NVDA)
   - Risk limits: Max $5k/position, 70% min confidence, 3 max positions

### Upcoming Integration (FinVec v4)

**Status**: ⏳ Models training (Phase 4 pending)

**Expected Improvements:**
- META: -0.32% → **+0.50-1.00%** (first time profitable!)
- MU: +2.51% → **+3.00-3.50%**
- AMD: +3.48% → **+4.00-4.50%**
- Overall: +1.34% → **+1.75-2.00%** (+30-50% improvement)

**New Features (81D):**
- Acceleration features (2nd derivative)
- Jerk features (3rd derivative)
- Regime detection (plateau, compression, breakout)
- Pre-move pattern indicators

---

## 🎯 Design Philosophy Differences

### FinVec: Research-First

**Goal**: Push boundaries of financial ML
**Approach**: Novel architecture (financial tokenization, profit-aware loss)
**Team Issues**: "Ironing out requirements, architecture, design"
**Iterations**: V1 → V2 → V3 → V4 (continuous improvement)
**Output**: Trained models as API endpoints

### PIM: Production-First

**Goal**: Make money reliably
**Approach**: Multi-agent orchestration with proven tools
**Tech Stack**: Enterprise (TypeScript, PostgreSQL, LangGraph, multi-LLM)
**Integration**: Consumes FinVec as one of 10 agents
**Output**: Live trades on broker account

---

## 🔧 Swarm Architecture Fit

### Current: PIM as Internal Village

**PIM is already a "swarm":**
- 9 specialized agents + FinVec agent
- Agent-to-agent communication via LangGraph
- Shared memory (PostgreSQL)
- Autonomous decision-making
- Continuous learning

**Dashboard Interface:**
- Web UI for monitoring/configuration
- No direct LLM interaction needed
- Settings changes via web forms
- Reports via UI/API

### How This Fits Caelum-Unified Vision

```
┌─────────────────────────────────────────────────────────────┐
│  Caelum-Unified External API (10-20 high-level tools)       │
│  - analyze_project                                          │
│  - execute_complex_workflow ← PIM COULD BE THIS             │
│  - manage_infrastructure                                    │
│  - optimize_trading_strategy ← NEW TOOL                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  Business Intelligence Supervisor (Internal)                │
│  - Spawns Claude/Ollama session                            │
│  - Has access to PIM orchestration tools                   │
│  - Calls: pim_analyze_opportunity                          │
│  - Calls: pim_execute_trade                                │
│  - Calls: pim_get_performance                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────────┐
│  PassiveIncomeMaximizer (Autonomous Village)                │
│  - 10 agents working internally                            │
│  - FinVec integration                                       │
│  - Only reports results upward                             │
│  - Receives high-level instructions downward               │
└─────────────────────────────────────────────────────────────┘
```

### Proposed Integration

**External Tool (Caelum-Unified):**
```typescript
async function optimize_trading_strategy(params: {
  symbols: string[];
  riskProfile: 'conservative' | 'moderate' | 'aggressive';
  budget: number;
}): Promise<TradingStrategy> {
  // Supervisor spawns Ollama/Claude session
  // Uses PIM tools internally
  // Returns consolidated trading strategy
}
```

**Supervisor Uses PIM Tools:**
```typescript
// These run inside supervisor's Claude session
const opportunities = await pim_scan_market({ sectors: ['tech', 'healthcare'] });
const predictions = await pim_get_finvec_predictions({ symbols: opportunities });
const positions = await pim_analyze_portfolio({ account: 'SIM1137629M' });
const strategy = await pim_generate_strategy({ predictions, positions, risk });

// Returns to external Claude
return strategy;
```

**PIM Stays Autonomous:**
- Runs its 10-agent swarm internally
- Web dashboard for human oversight
- Reports upward when asked
- Executes strategies when instructed
- Learns continuously from outcomes

---

## 🎬 Current State Summary

### FinVec Project
- **V3 Models**: Production-ready, 64.6% win rate
- **V4 Models**: Data generation 80% complete (~1h remaining)
- **GPU Training**: Will auto-start on 3 GPUs when data ready
- **Expected V4**: 30-50% performance improvement over V3
- **API Server**: FastAPI running on 10.32.3.27:5000

### PIM Project
- **Status**: Operational with FinVec v2 integration
- **Account**: TradeStation SIM1137629M (simulation)
- **Agents**: 9 specialized + 1 FinVec agent
- **Trading**: 5 symbols, $5k max position, 2:1 R:R
- **Database**: PostgreSQL on 10.32.3.27:15432
- **Recent Work**: OAuth setup, node-postgres migration

### Integration Status
- ✅ PIM calls FinVec v2 API successfully
- ✅ Predictions → Signals → Execution working
- ✅ Continuous learning framework in place
- ⏳ Awaiting FinVec v4 models (8-12h training ahead)
- ⏳ Need to test v4 integration when models ready

---

## 🚀 Recommendations

### Immediate (Next 24 hours)

1. **Monitor V4 Training**
   - Data generation completes (~1h)
   - GPU training auto-starts
   - Monitor logs: `tail -f logs/train_seq{300,500,800}.log`

2. **Document PIM as Autonomous Village**
   - Create: `PIM_AS_CAELUM_VILLAGE.md`
   - Define PIM supervisor tools for Caelum
   - Map external API surface

### Short-Term (Next Week)

3. **Integrate V4 Models into PIM**
   - Replace v2 model checkpoints with v4
   - Test 81D feature predictions
   - Validate 30-50% improvement claim

4. **Create Caelum-PIM Bridge**
   - Design supervisor tools: `pim_*`
   - Implement in Business Intelligence Supervisor
   - Test hierarchical workflow

### Long-Term (Next Month)

5. **Expand PIM Symbol Universe**
   - Currently: 5 symbols
   - Target: 30-100 symbols (from FinVec backtests)
   - Use Caelum to manage symbol selection

6. **Production Deployment**
   - Move from SIM account to live (when profitable)
   - Implement safety rails via Caelum oversight
   - Real-money risk management

---

## 📋 Key Takeaways

1. **FinVec is the ML Engine** - Research-driven, continuously improving
2. **PIM is the Trading System** - Production-ready, multi-agent orchestration
3. **Integration is Clean** - FinVec predictions → PIM execution → Learning loop
4. **Both are "Villages"** - Autonomous internal complexity, simple external interface
5. **Caelum Vision Fits** - PIM becomes a supervisor's tool in larger ecosystem

**The relationship:**
- FinVec builds better prediction models
- PIM uses those models to make profitable trades
- Both feed data back for continuous improvement
- Caelum orchestrates at the meta level

---

*Document created: 2025-10-24*
*Projects: FinVec (ML) + PassiveIncomeMaximizer (Trading)*
*Integration: Clean API boundary, autonomous operation, hierarchical coordination*
