# Caelum SuperSystem - Roadmap

**Focus: PassiveIncomeMaximizer as the PRIMARY goal**

---

## Current Status (2025-11-24)

### What's DONE (Integration Complete)

| Component | Status | Evidence |
|-----------|--------|----------|
| Layer 1 (PIM Engine) → Trading | **CONNECTED** | `pimClient.analyze()` in prediction-loop.ts:292 |
| Layer 2 (RL Filtering) → PIM | **CONNECTED** | `layer2Client.filter()` in prediction-loop.ts:210 |
| Learning Feedback Loop | **CODE EXISTS** | feedback-retry-worker.ts, outcome-tracker.ts |
| Workflow Tracking | **CONNECTED** | decisionWorkflows table updates |
| FinColl V7 Predictions | **CONNECTED** | finCollClient.predict() working |

**Note**: PIM CLAUDE.md says "Integration in progress" but code shows it's **complete**. Documentation needs updating.

---

## Near-Term Goals

### 1. Self-Evolution for Trading Strategies

**Trigger**: Exploration finds improvement that is NOT symbol/quarter/year dependent

**Architecture**:
```
Trade Outcomes (continuous)
        │
        ▼
Performance Monitor
├── Track: Win rate, Sharpe, drawdown by strategy
├── Detect: Performance degradation patterns
└── Key: Changes NOT correlated to specific symbols/time
        │
        ▼
Strategy Evolution Trigger
├── When: Strategy underperforms baseline for N trades
├── How: Generate strategy variations
├── Test: Paper trade variations in parallel
└── Learn: Keep improvements, discard failures
        │
        ▼
Meta-Learner Update
└── Adjust agent weights based on strategy performance
```

**What triggers evolution** (NOT time/symbol dependent):
1. **Regime-independent underperformance**: Strategy loses edge across multiple regimes
2. **Cross-symbol pattern**: Same failure pattern across diverse symbols
3. **Structural market change**: New patterns not in training data
4. **Agent consensus drift**: Agents increasingly disagree without resolution

**What does NOT trigger evolution**:
- Single quarter bad performance (could be market regime)
- Single symbol failure (could be company-specific)
- Seasonal patterns (expected, not failure)

### 2. Reduce Anthropic Dependence (Ollama First)

**Goal**: Become less dependent on commercial LLM providers

**Strategy**: Ollama for routine tasks, Anthropic for complex reasoning

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM ROUTING STRATEGY                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Task Classification                                         │
│  ├── Simple (Ollama): Pattern matching, data extraction     │
│  ├── Medium (Ollama): Technical analysis, sentiment parse   │
│  └── Complex (Anthropic): Multi-factor reasoning, edge cases│
│                                                              │
│  Agent Mapping                                               │
│  ├── Price Analyzer     → Ollama (llama3.1:70b)            │
│  ├── News Processor     → Ollama (llama3.1:70b)            │
│  ├── Trend Analyzer     → Ollama (llama3.1:70b)            │
│  ├── Risk Manager       → Anthropic (complex reasoning)     │
│  ├── Portfolio Manager  → Anthropic (final decisions)       │
│  └── Metrics Evaluator  → Ollama (data analysis)           │
│                                                              │
│  Fallback                                                    │
│  └── If Ollama fails/slow → Route to Anthropic              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Steps**:
1. Add Ollama client to PIM Engine
2. Create task complexity classifier
3. Route simple/medium tasks to Ollama
4. Keep complex reasoning on Anthropic
5. Track cost savings and quality metrics
6. Gradually increase Ollama usage as confidence grows

**Future**: Tier-0 LLM (custom trained) for maximum independence

### 3. Knowledge Sharing (PIM-Centric)

**Goal**: PIM learns from all components, shares insights back

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│              PIM KNOWLEDGE HUB (PostgreSQL + Qdrant)         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PIM Receives From:                                          │
│  ├── FinVec                                                  │
│  │   ├── Cluster assignments (which stocks similar?)        │
│  │   ├── Feature importance (what predicts well?)           │
│  │   └── Confidence calibration (when to trust?)            │
│  │                                                           │
│  ├── Trade Outcomes (self)                                   │
│  │   ├── Actual P/L per trade                               │
│  │   ├── Agent accuracy over time                           │
│  │   └── Strategy performance by regime                     │
│  │                                                           │
│  └── Market Data                                             │
│      ├── Regime transitions                                  │
│      ├── Correlation changes                                 │
│      └── Volatility patterns                                 │
│                                                              │
│  PIM Shares Back To:                                         │
│  ├── FinVec → Trade outcomes for profit-aware retraining    │
│  ├── Agents → Updated weights from meta-learner             │
│  └── Dashboard → Performance metrics, insights              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Database Schema** (in caelum-unified PostgreSQL):

```sql
-- Trade outcomes for learning
CREATE TABLE trade_outcomes (
  id SERIAL PRIMARY KEY,
  decision_id UUID REFERENCES decision_workflows(workflow_id),
  symbol VARCHAR(10),
  entry_price DECIMAL,
  exit_price DECIMAL,
  profit_loss DECIMAL,
  holding_period_days INT,
  agent_votes JSONB,
  meta_learner_weights JSONB,
  market_regime VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent performance tracking
CREATE TABLE agent_performance (
  id SERIAL PRIMARY KEY,
  agent_name VARCHAR(50),
  period_start DATE,
  period_end DATE,
  total_decisions INT,
  correct_decisions INT,
  accuracy DECIMAL,
  profit_contribution DECIMAL,
  avg_confidence DECIMAL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Strategy evolution log
CREATE TABLE strategy_evolution (
  id SERIAL PRIMARY KEY,
  trigger_reason TEXT,
  old_strategy JSONB,
  new_strategy JSONB,
  backtest_results JSONB,
  deployed BOOLEAN DEFAULT FALSE,
  performance_delta DECIMAL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- FinVec cluster insights
CREATE TABLE finvec_clusters (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10),
  cluster_id INT,
  cluster_centroid VECTOR(336),
  similarity_score DECIMAL,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Qdrant Collections** (vector storage):

```
- trade_embeddings: Vectorized trade patterns for similarity search
- agent_reasoning: Embedded agent reasoning for context retrieval
- market_patterns: Vectorized market conditions for regime detection
```

---

## Implementation Priority

### Phase 1: Ollama Integration (1-2 weeks)
1. [ ] Add Ollama client to PIM Engine
2. [ ] Create task router (simple→Ollama, complex→Anthropic)
3. [ ] Test with Price Analyzer agent
4. [ ] Measure cost savings
5. [ ] Expand to more agents

### Phase 2: Knowledge Sharing Schema (1 week)
1. [ ] Add tables to caelum-unified PostgreSQL
2. [ ] Implement trade outcome recording
3. [ ] Connect FinVec cluster data
4. [ ] Create agent performance tracking

### Phase 3: Self-Evolution Triggers (2 weeks)
1. [ ] Build performance monitoring
2. [ ] Implement regime-independent detection
3. [ ] Create strategy variation generator
4. [ ] Build parallel paper trading for variants
5. [ ] Automate meta-learner updates

### Phase 4: Feedback Loop Verification (1 week)
1. [ ] Verify feedback-retry-worker is running
2. [ ] Confirm meta-learner weight updates
3. [ ] Test full cycle: trade → outcome → learning
4. [ ] Update PIM CLAUDE.md to reflect complete integration

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Anthropic API cost | 100% | <40% (Ollama handling 60%+) |
| Learning feedback active | Unknown | Verified working |
| Strategy evolution | Manual | Automated triggers |
| Cross-component data flow | Partial | Full PIM ↔ FinVec |
| Agent weight updates | Code exists | Verified running |

---

## Questions to Resolve

1. **Ollama model size**: llama3.1:70b vs llama3.1:8b - quality vs speed tradeoff?
2. **Evolution frequency**: How many trades before considering strategy change?
3. **Regime detection**: Use FinVec clusters or separate model?
4. **Tier-0 timeline**: When to invest in custom LLM training?

---

**Last Updated**: 2025-11-24
