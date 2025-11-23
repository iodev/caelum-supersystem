# Caelum Swarm Intelligence Architecture

**A Self-Evolving, Multi-Agent Trading Strategy System**

---

## Core Philosophy

This is **NOT** a collection of independent microservices.

This is **ONE UNIFIED STRATEGY** implemented as a **swarm intelligence** where:
- Every component is an **autonomous agent** (sub-brain)
- All agents **collaborate** through a central nervous system (Agent Bus + Caelum MCP)
- The **entire system** is the strategy - incomplete without any one part
- The system **self-evolves** by monitoring itself and adapting to user goals
- **One strategy, customizable per user/account**, not multiple strategies

---

## The Actual Architecture

### System as Organism

```
┌─────────────────────────────────────────────────────────────────┐
│                   THE STRATEGY (Organism)                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Central Nervous System                      │   │
│  │  ┌────────────────────┬────────────────────────────┐    │   │
│  │  │   Agent Bus        │  Caelum MCP (TCP :8090)   │    │   │
│  │  │  (Event-Driven)    │  (Cross-Device Swarm)     │    │   │
│  │  └────────────────────┴────────────────────────────┘    │   │
│  │         ▲                        ▲                       │   │
│  │         │  All agents communicate via bus & MCP         │   │
│  │         │  Shared state, coordination, learning          │   │
│  └─────────┼────────────────────────┼───────────────────────┘   │
│            │                        │                            │
│  ┌─────────┴────────────────────────┴─────────────────────┐    │
│  │                    Sub-Brains (Agents)                  │    │
│  │                                                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │ PIM Agent    │  │FinColl Agent │  │SenVec Agent │  │    │
│  │  │ (Orchestr.)  │  │ (Predictor)  │  │ (Sensor)    │  │    │
│  │  │              │  │              │  │             │  │    │
│  │  │ • UI         │  │ • ML Model   │  │ • Sentiment │  │    │
│  │  │ • Account    │  │ • Inference  │  │ • News      │  │    │
│  │  │ • Config     │  │ • Features   │  │ • Social    │  │    │
│  │  │ • Decisions  │  │ • Training   │  │ • Market    │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │    │
│  │         │                  │                  │          │    │
│  │  ┌──────┴──────┐  ┌───────┴──────┐  ┌───────┴──────┐  │    │
│  │  │FinVec Agent │  │Trading Agent │  │Monitor Agent │  │    │
│  │  │ (Learner)   │  │ (Executor)   │  │ (Observer)   │  │    │
│  │  │             │  │              │  │              │  │    │
│  │  │ • GPU Train │  │ • Orders     │  │ • Health     │  │    │
│  │  │ • Checkpts  │  │ • Positions  │  │ • Metrics    │  │    │
│  │  │ • Evolve    │  │ • Risk       │  │ • Feedback   │  │    │
│  │  └─────────────┘  └──────────────┘  └──────────────┘  │    │
│  │                                                          │    │
│  │  All agents access SHARED state via Agent Bus:          │    │
│  │  - User goals & risk tolerance                          │    │
│  │  - Account configurations                               │    │
│  │  - Market observations                                   │    │
│  │  - Model performance metrics                            │    │
│  │  - Trading history & outcomes                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               Shared Memory (State)                      │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │ PostgreSQL: User config, goals, history, metrics   │ │   │
│  │  │ Redis: Real-time observations, predictions, cache  │ │   │
│  │  │ NFS: Model checkpoints, credentials, code          │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  The Strategy = PIM + FinColl + SenVec + FinVec + Caelum       │
│                                                                  │
│  Note: Trading execution is part of PIM Agent (orchestrator)    │
│        Monitoring is distributed across all agents via          │
│        Agent Bus events + SystemHealthService                   │
│                                                                  │
│  All components monitor each other, share learnings, evolve    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Principles

### 1. **One Strategy, Not Multiple Services**

**WRONG VIEW** (Microservices):
```
PIM is a service → calls FinColl service → calls SenVec service
(Independent, loosely coupled, replaceable)
```

**CORRECT VIEW** (Swarm Intelligence):
```
The Strategy = {PIM + FinColl + SenVec + FinVec + Caelum}
- PIM provides user interface and orchestration brain
- FinColl provides prediction brain
- SenVec provides sensory perception
- FinVec provides learning and evolution brain
- Caelum MCP provides distributed coordination brain

ALL collaborate through Agent Bus to execute ONE strategy.
Remove any component → strategy breaks.
```

### 2. **Swarm Communication via Agent Bus + Caelum MCP**

**Agent Bus** (`server/services/agent-bus.ts`) - **✅ IMPLEMENTED**:

**Current Implementation**:
- **Architecture**: EventEmitter-based pub/sub (Node.js)
- **Scope**: Single-process, in-memory (multi-host via Caelum MCP planned)
- **Agent Registration**: Factory pattern with capability discovery
- **Message Routing**: Direct dispatch and broadcast pub/sub
- **Coordination Tasks**: Priority queue with consensus mechanism

**Technical Specifications**:
```typescript
// Agent identification format
const agentKey = `${agentType}:${agentId}`; // Example: "fincoll:fincoll_1731100000000"

// Agent Registry Structure
interface AgentRegistration {
  agentId: string;
  agentType: string;
  lastActive: number; // Unix timestamp
  capabilities: string[]; // ['trade:execute', 'prediction:create', ...]
  metadata?: Record<string, any>;
}

// Message Structure
interface AgentMessage {
  action: string; // e.g., 'prediction:updated', 'trade:execute'
  agentId?: string; // Source agent
  targetAgentId?: string; // Target agent (for direct dispatch)
  data: any; // Payload
}

// Coordination Task Structure
interface CoordinationTask {
  taskId: string;
  type: string; // 'trade_execution', 'risk_assessment', etc.
  priority: 'low' | 'medium' | 'high';
  agents: string[]; // Agent IDs participating
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  data: any;
  results?: any;
}
```

**Agent Bus Core Methods** (already implemented):
```typescript
class AgentBus {
  // Agent lifecycle
  registerAgent(agentType: string, agent: any): string
  unregisterAgent(agentId: string): void
  getAgentsByType(agentType: string): any[]
  getAllAgents(): any[]

  // Message routing
  publish(topic: string, data: any): void
  subscribe(topic: string, callback: Function): void
  dispatchToAgent(agentId: string, message: AgentMessage): Promise<any>

  // Coordination
  createCoordinationTask(task: CoordinationTask): Promise<string>
  processCoordinationTask(taskId: string): Promise<void>
  getTaskStatus(taskId: string): CoordinationTask | undefined

  // Monitoring
  getStats(): { agentCount: number; taskCount: number; ... }
}
```

**Event Topics** (standardized naming):
```typescript
// Pattern: {domain}:{event_type}

// Agent lifecycle events
'agent:registered'
'agent:unregistered'
'agent:message'
'agent:error'

// Market events
'market:open'
'market:close'
'market:regime_change'

// Prediction events
'prediction:ready'
'prediction:updated'
'pattern:discovered'

// Trading events
'trade:executed'
'trade:completed'
'trade:rejected'
'risk:threshold_breach'

// Model evolution events
'performance:degraded'
'model:updated'
'model:retraining_started'

// Sentiment events
'sentiment:updated'
```

**Health Monitoring Integration** (already implemented):
- **SystemHealthService**: Monitors all agents every 60s
- **Health Status**: `HEALTHY | DEGRADED | UNHEALTHY`
- **Agent Tracking**: `lastActive` timestamp updated on every message
- **Event Emission**: `componentUnhealthy`, `componentDegraded` events

**Agent Pool Management** (already implemented):
- **Auto-scaling**: Max 5 agents per type
- **Job Queue**: Priority-based task assignment
- **Idle Cleanup**: Removes unused agents after 5 minutes
- **Metrics Tracking**: Processing time, jobs per agent type

**Performance Characteristics** (current implementation):
- **Throughput**: EventEmitter-based, >10,000 messages/sec (local)
- **Latency**: <1ms for in-process message delivery
- **Scalability**: Single-process only (limited by Node.js event loop)
- **Future**: Distributed Agent Bus via Redis Pub/Sub or Caelum MCP for cross-host

**Caelum MCP** (TCP localhost:8090) - **🔄 PARTIAL**:

**What's Documented** (from architecture):
- Cross-device agent coordination
- LLM routing (local processing → commercial LLMs)
- Profile and preference management
- Distributed swarm intelligence

**What's Implemented** (MCP tools available):
```typescript
// Available via caelum-unified MCP server
mcp__caelum-unified__get_user_profile
mcp__caelum-unified__update_user_preferences
mcp__caelum-unified__analyze_project
mcp__caelum-unified__send_notification
mcp__caelum-unified__analyze_opportunity
mcp__caelum-unified__list_devices
mcp__caelum-unified__switch_context
```

**Integration Point**:
- PIM Agent connects to Caelum MCP for user profile management
- Cost optimization routing (local first, LLM API fallback)
- Future: Distributed agent coordination across hosts

**Example Swarm Interaction**:
```typescript
// FinColl Agent discovers new pattern
finCollAgent.publish('pattern:discovered', {
  symbol: 'AAPL',
  pattern: 'bullish_divergence',
  confidence: 0.85
});

// Trading Agent receives and evaluates
tradingAgent.subscribe('pattern:discovered', async (msg) => {
  const riskAssessment = await riskAgent.assess(msg);
  const accountFit = await accountAgent.checkRiskTolerance(msg);

  if (accountFit && riskAssessment.acceptable) {
    await tradingAgent.executeTrade(msg);
  }
});

// Monitor Agent logs outcome
monitorAgent.subscribe('trade:executed', async (trade) => {
  await monitorAgent.logOutcome(trade);

  // Feed back to FinVec for learning
  await finVecAgent.recordTrainingExample(trade);
});

// FinVec Agent evolves the model
finVecAgent.subscribe('performance:degraded', async (metrics) => {
  await finVecAgent.scheduleRetraining();
  await finVecAgent.notifySwarm('model:updating', { eta: '2h' });
});
```

### 3. **Shared State = Swarm Memory**

All agents read/write to shared state:

**PostgreSQL** (Persistent Memory):
```sql
-- User configuration (strategy parameters per account)
user_goals: { account_id, risk_tolerance, profit_target, ... }

-- Trading history (collective experience)
trade_history: { symbol, entry, exit, outcome, model_version, ... }

-- Model performance (learning metrics)
model_metrics: { version, sharpe_ratio, win_rate, max_drawdown, ... }

-- Agent coordination (swarm orchestration)
coordination_tasks: { task_id, agents[], status, results, ... }
```

**Redis** (Short-term Memory):
```
# Real-time observations
market:observations:{symbol} → {price, volume, sentiment}

# Predictions cache
predictions:{symbol}:{model} → {confidence, direction, targets}

# Agent health
agent:health:{agent_id} → {status, last_seen, metrics}

# Swarm coordination
swarm:tasks:active → [task_ids...]
```

**NFS Shared Filesystem** (Long-term Knowledge):
```
/home/rford/caelum/ss/
  ├── finvec/checkpoints/  # Evolved neural networks
  ├── .credentials.json    # Shared API access
  ├── training_data/       # Collective experience
  └── configs/             # Strategy parameters
```

### 4. **Self-Evolution Through Feedback Loops**

The system monitors itself and adapts:

```typescript
// Continuous Monitoring Loop
class StrategyEvolutionAgent {
  async monitorAndEvolve() {
    // 1. Observe current performance
    const performance = await this.getPerformanceMetrics();

    // 2. Compare against user goals
    const userGoals = await this.getUserGoals();
    const gap = this.calculateGoalGap(performance, userGoals);

    // 3. If underperforming, trigger evolution
    if (gap.sharpeRatio < userGoals.minSharpeRatio) {
      // Option A: Retrain ML model with recent data
      await this.bus.dispatch('finvec', {
        action: 'retrain',
        data: {
          recent_trades: performance.recentTrades,
          focus: 'sharpe_optimization'
        }
      });

      // Option B: Adjust trading thresholds
      await this.bus.dispatch('trading', {
        action: 'update_thresholds',
        data: {
          confidence_min: 0.80, // Increase from 0.75
          position_size_multiplier: 0.8 // Reduce risk
        }
      });

      // Option C: Expand data sources
      await this.bus.dispatch('senvec', {
        action: 'enable_source',
        data: { source: 'options_flow' } // Add new signal
      });
    }

    // 4. Log evolution decision for future learning
    await this.logEvolutionDecision(gap, actions);
  }
}
```

### 5. **Customization Per User, Not Per Instance**

**WRONG**: Deploy separate instances for each user
```
User A → PIM-A + FinColl-A + SenVec-A
User B → PIM-B + FinColl-B + SenVec-B
```

**CORRECT**: One swarm, customized strategy per account
```
ONE Swarm:
  PIM + FinColl + SenVec + FinVec + Caelum

User A's account: { risk: 'conservative', goal: 'income' }
  → Strategy parameterizes: confidence_threshold=0.85, position_size=5%

User B's account: { risk: 'aggressive', goal: 'growth' }
  → Strategy parameterizes: confidence_threshold=0.70, position_size=15%

SAME models, SAME predictions, DIFFERENT execution based on account config
```

---

## Dependency Map (Swarm Connections)

```
┌──────────────────────────────────────────────────────────┐
│                   Swarm Dependencies                     │
└──────────────────────────────────────────────────────────┘

PIM Agent (Orchestrator)
  ├─ REQUIRES → Agent Bus (cannot coordinate without it)
  ├─ REQUIRES → Caelum MCP (cost optimization, LLM brains)
  ├─ REQUIRES → FinColl (cannot make trading decisions)
  ├─ REQUIRES → PostgreSQL (user config, history)
  └─ MONITORS → All other agents (health, performance)

FinColl Agent (Predictor)
  ├─ REQUIRES → SenVec (72D sentiment features)
  ├─ REQUIRES → FinVec (trained model checkpoints)
  ├─ REQUIRES → TradeStation/AlphaVantage (market data)
  ├─ PUBLISHES → predictions to Agent Bus
  └─ SUBSCRIBES → feedback from Trading Agent

SenVec Agent (Sensor)
  ├─ REQUIRES → None (data collector, leaf node)
  ├─ PUBLISHES → sentiment features to Agent Bus
  └─ CONSUMES → External APIs (Twitter, Reddit, News)

FinVec Agent (Learner)
  ├─ REQUIRES → Training data from shared NFS
  ├─ REQUIRES → GPU resources
  ├─ PUBLISHES → new model checkpoints to NFS
  ├─ SUBSCRIBES → performance feedback from Monitor Agent
  └─ TRIGGERS → FinColl reload when model improves

Trading Agent (Executor)
  ├─ REQUIRES → FinColl predictions
  ├─ REQUIRES → User risk tolerance from PIM
  ├─ REQUIRES → Brokerage API (TradeStation)
  ├─ PUBLISHES → trade executions to Agent Bus
  └─ PROVIDES → feedback to FinVec for learning

Monitor Agent (Observer)
  ├─ SUBSCRIBES → All agent events
  ├─ COMPUTES → Performance metrics
  ├─ PUBLISHES → health status, alerts
  └─ TRIGGERS → Evolution when performance degrades

Caelum MCP (Distributed Swarm Brain)
  ├─ COORDINATES → Cross-device agents
  ├─ PROVIDES → LLM reasoning (Claude, GPT) as sub-brains
  ├─ MANAGES → User profiles, preferences
  └─ OPTIMIZES → Cost (local processing > commercial LLMs)
```

---

## What Must Stay Together vs. What Can Be Sold Separately

### Core Strategy (Cannot Be Separated)

**The Swarm Brain** (must deploy together):
```
PIM + FinColl + SenVec + FinVec + Agent Bus + Shared State
```

If you sell the system, the buyer gets ALL of these. The strategy only works as a complete organism.

### Separable for Commercial Licensing

#### 1. **Caelum MCP** (Swarm Coordination Infrastructure)
- **Purpose**: Distributed agent coordination, cross-device communication
- **Can be sold to**: Other AI/agent developers
- **Revenue model**: Per-device licensing, or SaaS API
- **Example**: "Caelum Swarm" product for building multi-agent systems

#### 2. **SenVec** (Sentiment-as-a-Service)
- **Purpose**: 72D sentiment features API
- **Can be sold to**: Algo traders, quant funds
- **Revenue model**: API subscriptions (as already documented)
- **Independence**: Can run standalone, provides features to ANY consumer

#### 3. **FinVec Training Infrastructure** (ML Training Pipeline)
- **Purpose**: Financial LLM training pipeline
- **Can be sold to**: ML researchers, hedge funds
- **Revenue model**: Training-as-a-service, or licensed software
- **Independence**: Can train models for any financial application

#### 4. **Commercial LLM Sub-Brains** (via Caelum MCP)
- **What it means**: Claude/GPT are ALREADY "sub-brains" accessed via Caelum
- **Your strategy uses commercial LLMs for**:
  - Analyzing news → SenVec agent calls Claude for sentiment
  - Generating trade explanations → PIM calls Claude for UI
  - Optimizing hyperparameters → FinVec calls Claude for AutoML
- **Cost optimization**: Caelum MCP routes to local processing FIRST, LLMs second

### Resources That Must Be Duplicated for Sale

When you sell the system to another user, they get their own:

**DUPLICATED** (Isolated per customer):
- PostgreSQL database (their accounts, history, config)
- Redis instance (their real-time state)
- Credentials (their API keys for TradeStation, etc.)
- Deployment (their servers/cloud)
- UI branding (white-label PIM interface)

**SHARED** (Your infrastructure):
- Caelum MCP swarm coordination (multi-tenant)
- SenVec sentiment API (multi-tenant, they pay per use)
- FinVec model checkpoints (they license, you train and update)

**SOLD AS PRODUCT** (One-time or subscription):
- Source code repositories (PIM, FinColl, FinVec)
- Docker orchestration configs
- Documentation and setup guides
- Model architecture (but not latest weights)

---

## Deployment Strategy for Swarm

### Development (Single Organism, One Host)

```bash
# Start the entire swarm locally
cd /home/rford/caelum/ss

# Terminal 1: Caelum MCP (swarm coordinator)
# (Assuming already running on :8090)

# Terminal 2: Shared infrastructure
docker-compose -f docker-compose.ecosystem.yml up postgres redis -d

# Terminal 3: SenVec Agent (sensors)
cd senvec && ./start_all_services.sh

# Terminal 4: FinColl Agent (predictor)
cd fincoll && source .venv/bin/activate && python -m fincoll.server

# Terminal 5: PIM Agent (orchestrator + UI)
cd PassiveIncomeMaximizer && npm run dev

# All agents auto-discover each other via Agent Bus
# All agents connect to Caelum MCP for swarm coordination
```

### Production (Distributed Swarm, Multi-Host)

```bash
# WSL (10.32.3.27): Central nervous system + UI
Caelum MCP:    localhost:8090 (TCP)
PostgreSQL:    localhost:15432 (shared state)
Redis:         localhost:16379 (short-term memory)
PIM Agent:     localhost:5000 (orchestrator + UI)
SenVec Agent:  localhost:18000-18004 (sensors)

# GPU Server 1 (10.32.3.44): Prediction brain
FinColl Agent: 10.32.3.44:8001 (inference)
FinVec Agent:  (GPU training model V5)

# GPU Server 2 (10.32.3.22): Learning brain
FinVec Agent:  (GPU training model V3)

# All agents connect to Caelum MCP via TCP for swarm coordination
# All agents register with PIM's Agent Bus via HTTP events
```

### Multi-Tenant Deployment (Selling to Customers)

```bash
# YOUR Infrastructure (Shared):
Caelum MCP:    caelum.yourdomain.com:8090 (multi-tenant)
SenVec API:    senvec.yourdomain.com (multi-tenant, usage billing)
Model Registry: models.yourdomain.com (versioned checkpoints)

# Customer A Deployment (Isolated):
PIM Agent:     customer-a.yourdomain.com:5000 (their UI)
FinColl Agent: customer-a.yourdomain.com:8001 (their predictions)
PostgreSQL:    customer-a-db (their accounts, history)
Redis:         customer-a-redis (their state)

# Customer A's agents connect to:
- YOUR Caelum MCP (swarm coordination)
- YOUR SenVec API (sentiment features)
- YOUR Model Registry (licensed models)
- THEIR PostgreSQL/Redis (isolated data)
- THEIR brokerage accounts (TradeStation)
```

---

## Self-Evolution Feedback Loops

### Loop 1: Trading Performance → Model Retraining

```
Monitor Agent observes: Sharpe ratio dropped from 1.8 to 1.2
  ↓
Monitor Agent publishes: 'performance:degraded'
  ↓
FinVec Agent subscribes and triggers: retrain with recent data
  ↓
FinVec Agent trains new model: llm1-tech-v1.2.0
  ↓
FinVec Agent publishes: 'model:updated'
  ↓
FinColl Agent subscribes and hot-reloads: new model checkpoint
  ↓
Monitor Agent tracks: Does Sharpe ratio improve?
  ↓
If YES: FinColl promotes v1.2.0 to production
If NO: FinColl rollbacks to v1.1.0, FinVec tries different approach
```

### Loop 2: User Goal Changes → Strategy Adaptation

```
User updates goal via PIM UI: "I want higher income, less risk"
  ↓
PIM Agent updates PostgreSQL: user_goals table
  ↓
PIM Agent publishes: 'user:goal_changed'
  ↓
Trading Agent subscribes and adjusts:
  - confidence_threshold: 0.75 → 0.85 (less risk)
  - position_size: 10% → 7% (less risk)
  - target_symbols: growth stocks → dividend stocks (income)
  ↓
Monitor Agent tracks: Are new goals being met?
  ↓
If NO: PIM Agent publishes 'strategy:optimization_needed'
  ↓
FinVec Agent retrains: with emphasis on dividend-paying stocks
```

### Loop 3: Market Regime Change → Strategy Evolution

```
SenVec Agent detects: VIX spike, yield curve inversion
  ↓
SenVec Agent publishes: 'market:regime_change' (high volatility)
  ↓
FinColl Agent subscribes and adjusts: prediction thresholds
  ↓
Trading Agent subscribes and adjusts: reduce position sizes
  ↓
FinVec Agent subscribes and triggers: retrain with volatility emphasis
  ↓
Monitor Agent logs: How did strategy perform in new regime?
  ↓
FinVec learns: "In high VIX, reduce confidence threshold"
```

---

## Communication Protocols

### Agent Bus (Intra-Host Swarm)

**Event Topics**:
```typescript
// Pattern: {domain}:{event_type}
'agent:registered'
'agent:unregistered'
'agent:message'
'agent:completed'

'pattern:discovered'
'prediction:updated'
'trade:executed'
'trade:completed'

'performance:degraded'
'model:updated'
'market:regime_change'
'user:goal_changed'

'strategy:optimization_needed'
```

**Message Format**:
```typescript
{
  agentId: 'fincoll-001',
  action: 'prediction:updated',
  data: {
    symbol: 'AAPL',
    confidence: 0.87,
    direction: 'bullish',
    targets: { t1: 185, t2: 190 }
  },
  timestamp: '2025-11-08T...'
}
```

### Caelum MCP (Cross-Host Swarm)

**TCP Port**: 8090
**Protocol**: JSON-RPC over TCP

**Example MCP Call**:
```typescript
// PIM Agent queries user profile from Caelum
const profile = await caelumMCP.call({
  method: 'get_user_profile',
  params: { userId: 'roderick_ford' }
});

// Result includes risk tolerance, preferences
// Used to parameterize trading decisions
```

**MCP as LLM Sub-Brain Router**:
```typescript
// PIM Agent needs sentiment analysis for news
const sentiment = await caelumMCP.call({
  method: 'analyze_text',
  params: {
    text: newsArticle,
    context: 'financial_sentiment',
    prefer_local: true // Try local processing first for cost optimization
  }
});

// Caelum MCP routes (cost optimization strategy):
// 1. Try local sentiment model (FinBERT) first
// 2. If confidence < 0.7, escalate to Claude API
// 3. Cache result for future use
// Goal: >80% of requests handled locally to maximize profitability
```

---

## Monitoring Dashboard Design

### Overview

**Purpose**: Real-time visibility into swarm health, agent coordination, and trading performance

**Current State**: Basic monitoring exists via SystemHealthService and PerformanceMonitor
**Goal**: Comprehensive dashboard for swarm intelligence visualization

### Dashboard Sections

#### 1. **Swarm Health Overview**

**Metrics Displayed**:
```typescript
// Real-time swarm status
interface SwarmHealthMetrics {
  overallStatus: 'HEALTHY' | 'DEGRADED' | 'UNHEALTHY';
  activeAgents: number;
  totalAgentTypes: number;
  agentsByStatus: {
    healthy: number;
    degraded: number;
    unhealthy: number;
  };
  lastHealthCheck: Date;
  uptime: number; // milliseconds
}
```

**Visual Components**:
- **Status Badge**: Large, color-coded (Green/Yellow/Red) overall health indicator
- **Agent Grid**: Visual cards for each agent type showing status
- **Timeline**: Health history over last 24 hours (line chart)
- **Alerts Panel**: Recent warnings and errors

#### 2. **Agent Bus Activity**

**Metrics Tracked** (via existing Agent Bus):
```typescript
interface AgentBusMetrics {
  messagesPerSecond: number;
  messagesByTopic: Record<string, number>; // 'trade:executed': 42
  agentCommunicationMatrix: {
    from: string; // Agent ID
    to: string;
    messageCount: number;
  }[];
  queueDepth: number; // Coordination tasks pending
  averageLatency: number; // ms
}
```

**Visual Components**:
- **Throughput Graph**: Real-time message rate (last 60 seconds)
- **Topic Distribution**: Pie chart of messages by topic
- **Communication Network**: Node graph showing agent connections
- **Queue Monitor**: Gauge showing coordination task queue depth

#### 3. **Trading Performance**

**Metrics** (from existing PerformanceMonitor):
```typescript
interface TradingMetrics {
  sharpeRatio: number;
  totalTrades: number;
  winRate: number; // 0.0 - 1.0
  profitLoss: {
    daily: number;
    weekly: number;
    monthly: number;
  };
  maxDrawdown: number;
  activePositions: number;
  failedTrades: number;
}
```

**Visual Components**:
- **P/L Chart**: Cumulative profit/loss over time
- **Win Rate Gauge**: Circular gauge (target: >55%)
- **Sharpe Ratio**: Large number display with trend indicator
- **Recent Trades Table**: Last 10 trades with outcomes
- **Position Monitor**: Active positions by symbol

#### 4. **Prediction Analytics**

**Metrics**:
```typescript
interface PredictionMetrics {
  totalPredictions: number;
  predictionsByDirection: {
    bullish: number;
    bearish: number;
    neutral: number;
  };
  averageConfidence: number;
  accuracyRate: number; // How many predictions were correct
  latency: number; // Time from data → prediction
}
```

**Visual Components**:
- **Accuracy Trend**: Line chart of prediction accuracy over time
- **Confidence Distribution**: Histogram of prediction confidence levels
- **Symbol Heatmap**: Grid showing which symbols have most predictions
- **Latency Graph**: Prediction generation time (target: <5s)

#### 5. **Model Evolution Tracking**

**Metrics**:
```typescript
interface ModelMetrics {
  currentVersion: string; // 'llm1-tech-v1.2.3'
  trainedOn: Date;
  performanceTrend: {
    version: string;
    sharpeRatio: number;
    winRate: number;
    deployedAt: Date;
  }[];
  lastRetraining: Date;
  nextScheduledTraining: Date;
}
```

**Visual Components**:
- **Version Timeline**: Model versions with performance metrics
- **Performance Comparison**: Bar chart comparing model versions
- **Training Status**: Current training progress (if running)
- **Retraining Triggers**: Log of what triggered past retraining

#### 6. **Cost Optimization Tracking**

**Metrics** (aligned with Caelum MCP):
```typescript
interface CostMetrics {
  totalRequests: number;
  localProcessingRate: number; // Percentage handled locally
  llmApiCalls: number;
  estimatedCostSavings: number; // $ saved by local processing
  requestsByType: {
    sentiment_analysis: { local: number; llm: number };
    text_summarization: { local: number; llm: number };
    // ... other request types
  };
}
```

**Visual Components**:
- **Local vs. LLM**: Pie chart (target: >80% local)
- **Cost Savings**: Large number display in $
- **Request Type Breakdown**: Stacked bar chart
- **Trend**: Line chart of local processing rate over time

### Implementation

#### Frontend Stack (existing PIM UI)

```typescript
// /client/src/pages/swarm-dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LineChart, PieChart, BarChart } from '@/components/charts';

export function SwarmDashboard() {
  const [metrics, setMetrics] = useState<SwarmMetrics | null>(null);

  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:5000/api/swarm/metrics');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMetrics(data);
    };

    return () => ws.close();
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {/* Swarm Health */}
      <Card>
        <h2>Swarm Health</h2>
        <Badge variant={getHealthVariant(metrics?.overallStatus)}>
          {metrics?.overallStatus || 'Loading...'}
        </Badge>
        <p>Active Agents: {metrics?.activeAgents}</p>
      </Card>

      {/* Agent Bus Activity */}
      <Card>
        <h2>Message Throughput</h2>
        <LineChart data={metrics?.messageThroughput} />
        <p>{metrics?.messagesPerSecond} msg/sec</p>
      </Card>

      {/* Trading Performance */}
      <Card>
        <h2>Performance</h2>
        <p>Sharpe Ratio: {metrics?.sharpeRatio?.toFixed(2)}</p>
        <p>Win Rate: {(metrics?.winRate * 100).toFixed(1)}%</p>
        <p>P/L Today: ${metrics?.profitLoss?.daily?.toFixed(2)}</p>
      </Card>

      {/* ... more cards */}
    </div>
  );
}
```

#### Backend API Endpoints

```typescript
// /server/routes/swarm-metrics.ts
import express from 'express';
import { WebSocketServer } from 'ws';
import { getAgentBus } from '../services/agent-bus';
import { getSystemHealth } from '../services/system-health';
import { getPerformanceMonitor } from '../services/performance-monitor';

const router = express.Router();

// REST endpoint for current metrics
router.get('/api/swarm/metrics', async (req, res) => {
  const agentBus = getAgentBus();
  const healthService = getSystemHealth();
  const perfMonitor = getPerformanceMonitor();

  const metrics = {
    health: await healthService.getHealthStatus(),
    agentBus: agentBus.getStats(),
    trading: await perfMonitor.getMetrics(),
    timestamp: new Date()
  };

  res.json(metrics);
});

// WebSocket for real-time updates
export function setupMetricsWebSocket(wss: WebSocketServer) {
  // Broadcast metrics every 5 seconds
  setInterval(async () => {
    const metrics = await collectAllMetrics();

    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(metrics));
      }
    });
  }, 5000);
}

async function collectAllMetrics() {
  const agentBus = getAgentBus();
  const healthService = getSystemHealth();
  const perfMonitor = getPerformanceMonitor();

  return {
    health: {
      overall: healthService.getStatus(),
      activeAgents: agentBus.getAllAgents().length,
      agentsByStatus: healthService.getAgentsByStatus()
    },
    agentBus: {
      messagesPerSecond: agentBus.getMessageRate(),
      queueDepth: agentBus.getCoordinationTaskCount(),
      messagesByTopic: agentBus.getTopicDistribution()
    },
    trading: {
      sharpeRatio: await perfMonitor.getSharpeRatio(),
      winRate: await perfMonitor.getWinRate(),
      profitLoss: await perfMonitor.getProfitLoss(),
      recentTrades: await perfMonitor.getRecentTrades(10)
    },
    predictions: {
      accuracy: await perfMonitor.getPredictionAccuracy(),
      averageConfidence: await perfMonitor.getAverageConfidence()
    },
    costs: {
      localProcessingRate: await caelumMCP.getLocalProcessingRate(),
      estimatedSavings: await caelumMCP.getEstimatedSavings()
    },
    timestamp: new Date()
  };
}
```

### Database Additions for Metrics

```sql
-- Store metrics history for charting
CREATE TABLE swarm_metrics_history (
  id SERIAL PRIMARY KEY,
  metric_type TEXT NOT NULL, -- 'health', 'trading', 'predictions', etc.
  metric_data JSONB NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Index for fast time-based queries
CREATE INDEX idx_metrics_timestamp ON swarm_metrics_history(timestamp DESC);
CREATE INDEX idx_metrics_type ON swarm_metrics_history(metric_type);

-- Store agent communication patterns
CREATE TABLE agent_communications (
  id SERIAL PRIMARY KEY,
  from_agent_id TEXT NOT NULL,
  to_agent_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  message_count INTEGER DEFAULT 1,
  last_communication TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_comm ON agent_communications(from_agent_id, to_agent_id);
```

### Alert Configuration

```typescript
// Dashboard alerts based on thresholds
interface AlertRule {
  metric: string;
  condition: 'above' | 'below';
  threshold: number;
  message: string;
  severity: 'info' | 'warning' | 'critical';
}

const ALERT_RULES: AlertRule[] = [
  {
    metric: 'sharpeRatio',
    condition: 'below',
    threshold: 1.2,
    message: 'Sharpe ratio dropped below target',
    severity: 'warning'
  },
  {
    metric: 'agentBus.queueDepth',
    condition: 'above',
    threshold: 100,
    message: 'Agent Bus queue depth high',
    severity: 'warning'
  },
  {
    metric: 'health.activeAgents',
    condition: 'below',
    threshold: 5,
    message: 'Critical agents offline',
    severity: 'critical'
  },
  {
    metric: 'costs.localProcessingRate',
    condition: 'below',
    threshold: 0.70, // 70%
    message: 'Local processing rate below target',
    severity: 'info'
  }
];
```

### Mobile-Responsive Design

```typescript
// Dashboard adapts to screen size
const DashboardLayout = () => {
  return (
    <div className="dashboard">
      {/* Desktop: 3-column grid */}
      <div className="hidden lg:grid lg:grid-cols-3 gap-4">
        <SwarmHealthCard />
        <AgentBusCard />
        <TradingCard />
        {/* ... more cards */}
      </div>

      {/* Tablet: 2-column grid */}
      <div className="hidden md:grid md:grid-cols-2 lg:hidden gap-4">
        {/* Same cards, different layout */}
      </div>

      {/* Mobile: Single column, scrollable */}
      <div className="md:hidden space-y-4">
        {/* Prioritize most important metrics */}
        <SwarmHealthCard />
        <TradingCard />
        {/* ... collapsible sections for others */}
      </div>
    </div>
  );
};
```

### Refresh Rates

- **Real-time** (WebSocket, 5s updates): Swarm health, Agent Bus activity
- **Near real-time** (15s polling): Trading metrics, Predictions
- **Periodic** (1 min polling): Model evolution, Cost tracking
- **Historical** (on-demand): Performance charts, Backtests

---

## What This Means for Deployment

### Traditional Microservices Approach (WRONG)

```
Deploy PIM → Deploy FinColl → Deploy SenVec
Each is independent, loosely coupled, replaceable
Configuration: URL endpoints, API keys
Communication: HTTP REST
```

**Problems**:
- Treats them as separate products
- No swarm intelligence
- No shared learning
- Static configuration
- No self-evolution

### Swarm Intelligence Approach (CORRECT)

```
Deploy THE STRATEGY as a single organism:
  1. Start Caelum MCP (swarm coordinator)
  2. Start PostgreSQL + Redis (shared memory)
  3. Start all agents simultaneously
  4. Agents auto-discover via Agent Bus
  5. Agents register with Caelum MCP
  6. Swarm begins collective intelligence

Configuration: User goals, risk tolerance
Communication: Agent Bus (events) + Caelum MCP (TCP)
Learning: Continuous feedback loops
Evolution: Automatic based on performance
```

**Benefits**:
- One unified strategy
- Collective intelligence emerges
- Continuous learning and adaptation
- Self-optimization toward user goals
- Resilient (agents can restart and rejoin swarm)

---

## Resilience and Fault Tolerance

### Agent Failure Detection

**Heartbeat Mechanism** (Currently Implemented):
```typescript
// SystemHealthService monitors all agents every 60s
class SystemHealthService {
  private healthCheckInterval = 60000; // 60 seconds

  async checkComponentHealth(): Promise<void> {
    // Checks: Database, Alpaca API, Qdrant, Agent availability
    // Emits: componentUnhealthy, componentDegraded events
  }
}

// Agent Bus tracks last activity
agentRegistry.set(key, {
  agentId,
  agentType,
  lastActive: Date.now(),
  capabilities: agent.getCapabilities?.() || []
});
```

**Health Status Levels**:
- `HEALTHY`: All components operational, response time < 1s
- `DEGRADED`: Component slow or returning errors, response time 1-5s
- `UNHEALTHY`: Component unreachable or failing, response time > 5s

### Agent Recovery Strategies

#### 1. **Circuit Breaker Pattern**

```typescript
// Prevent cascading failures when agents become unhealthy
class CircuitBreaker {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failureCount = 0;
  private failureThreshold = 5;
  private resetTimeout = 60000; // 1 minute

  async callAgent(agentId: string, action: string, data: any): Promise<any> {
    if (this.state === 'OPEN') {
      throw new Error(`Circuit open for agent ${agentId}`);
    }

    try {
      const result = await agentBus.dispatchToAgent(agentId, { action, data });
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onFailure(): void {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      setTimeout(() => this.state = 'HALF_OPEN', this.resetTimeout);
    }
  }
}
```

#### 2. **Automatic Retry with Exponential Backoff**

```typescript
// For transient failures (network issues, temporary overload)
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;

      const delay = baseDelay * Math.pow(2, attempt); // 1s, 2s, 4s
      logger.warn(`Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw new Error('Max retries exceeded');
}

// Usage in Agent Bus
async dispatchToAgent(agentId: string, message: AgentMessage): Promise<any> {
  return retryWithBackoff(async () => {
    const agent = this.agentRegistry.get(agentId);
    if (!agent) throw new Error(`Agent ${agentId} not found`);
    return agent.processMessage(message);
  });
}
```

#### 3. **Dead Letter Queue (DLQ)**

```typescript
// For messages that fail processing after all retries
interface DeadLetterMessage {
  originalMessage: AgentMessage;
  targetAgentId: string;
  error: string;
  attempts: number;
  timestamp: Date;
}

class DeadLetterQueue {
  private dlq: DeadLetterMessage[] = [];

  async addToQueue(msg: DeadLetterMessage): Promise<void> {
    this.dlq.push(msg);
    await storage.storeFailedMessage(msg);

    // Alert monitoring
    await monitorAgent.publish('message:dead_letter', {
      agentId: msg.targetAgentId,
      error: msg.error
    });
  }

  async reprocessDLQ(): Promise<void> {
    // Periodically retry DLQ messages (e.g., after agent recovery)
    for (const msg of this.dlq) {
      try {
        await agentBus.dispatchToAgent(msg.targetAgentId, msg.originalMessage);
        this.dlq = this.dlq.filter(m => m !== msg);
      } catch (error) {
        logger.warn(`DLQ message still failing: ${error}`);
      }
    }
  }
}
```

#### 4. **Agent Auto-Restart**

```typescript
// Automatically recreate crashed agents
class AgentSupervisor {
  async monitorAgentHealth(): Promise<void> {
    const expectedAgents = ['fincoll-001', 'senvec-001', 'finvec-001'];

    for (const agentId of expectedAgents) {
      const agent = agentRegistry.get(agentId);

      if (!agent || Date.now() - agent.lastActive > 120000) {
        logger.warn(`Agent ${agentId} unresponsive, restarting...`);
        await this.restartAgent(agentId);
      }
    }
  }

  async restartAgent(agentId: string): Promise<void> {
    const [agentType] = agentId.split(':');

    // Unregister dead agent
    agentBus.unregisterAgent(agentId);

    // Create new instance with same configuration
    const config = await storage.getAgentConfig(agentType);
    const newAgent = await agentRegistry.createAgent(agentType, config);

    // Register with new ID
    agentBus.registerAgent(agentType, newAgent);

    logger.info(`Agent ${agentType} restarted successfully`);
  }
}
```

### Graceful Degradation Strategies

**When FinColl Agent Fails** (Prediction Brain):
```typescript
// Impact: Cannot generate new trade signals
// Strategy:
1. PIM Agent pauses new trades
2. Existing positions continue to be monitored
3. Use cached predictions (max age: 15 minutes)
4. Alert user: "Prediction service degraded"
5. Auto-restart FinColl agent
6. If restart fails after 3 attempts, fall back to manual-only mode
```

**When SenVec Agent Fails** (Sentiment Sensor):
```typescript
// Impact: Missing 72D sentiment features
// Strategy:
1. FinColl uses last cached sentiment features (max age: 1 hour)
2. Reduce prediction confidence by 15% (account for stale data)
3. Increase trading threshold from 0.75 to 0.85 (more conservative)
4. Alert user: "Sentiment data stale, trading conservatively"
5. Continue operation with degraded accuracy
```

**When FinVec Agent Fails** (Learning Brain):
```typescript
// Impact: Cannot retrain models
// Strategy:
1. FinColl continues using current model checkpoint
2. Disable automatic model updates
3. Log training requests to queue for later processing
4. Alert user: "Model training offline, using stable v{version}"
5. No immediate impact on trading (training is async)
```

**When PostgreSQL Fails** (Persistent Memory):
```typescript
// Impact: Cannot persist new trades, configs, history
// Strategy:
1. CRITICAL - Halt all new trades immediately
2. Buffer new data in Redis (temporary, max 1000 entries)
3. Read-only mode using Redis cache
4. Alert user: "Database offline, trades paused"
5. When PostgreSQL recovers, flush Redis buffer to database
```

**When Redis Fails** (Short-term Memory):
```typescript
// Impact: No real-time cache, slower performance
// Strategy:
1. Fall back to direct PostgreSQL queries (slower but functional)
2. Reduce prediction frequency (60s → 5 minutes)
3. Disable high-frequency features (sub-minute updates)
4. Alert user: "Performance degraded, cache offline"
5. System remains operational, just slower
```

**When Caelum MCP Fails** (Swarm Coordinator):
```typescript
// Impact: Cross-device coordination unavailable
// Strategy:
1. Local agents continue via Agent Bus (EventEmitter)
2. Disable distributed features (multi-device sync)
3. LLM routing falls back to direct API calls
4. Alert user: "Swarm coordination offline, local-only mode"
5. Single-host operation continues normally
```

### Data Consistency Guarantees

**PostgreSQL (Persistent State)**:
- **ACID transactions** for critical operations (trades, account updates)
- **Row-level locking** for concurrent agent writes
- **Isolation level**: READ COMMITTED (prevent dirty reads)
- **Conflict resolution**: Last-write-wins with timestamp ordering

```sql
-- Example: Atomic trade execution
BEGIN;
INSERT INTO trades (user_id, agent_id, symbol, action, quantity, price, status)
VALUES ($1, $2, $3, $4, $5, $6, 'PENDING')
RETURNING id;

UPDATE accounts SET balance = balance - $totalCost WHERE id = $userId;
COMMIT;
```

**Redis (Short-term State)**:
- **Eventual consistency** acceptable for cache
- **TTL-based invalidation**: Predictions expire after 15 minutes
- **Optimistic locking** using WATCH/MULTI/EXEC for critical updates
- **Conflict resolution**: Newest data wins (timestamp-based)

```typescript
// Example: Optimistic lock for prediction update
await redis.watch(`predictions:${symbol}`);
const current = await redis.get(`predictions:${symbol}`);

if (current && current.timestamp > newPrediction.timestamp) {
  await redis.unwatch(); // Abort, existing data is newer
} else {
  await redis.multi()
    .set(`predictions:${symbol}`, newPrediction, 'EX', 900) // 15 min TTL
    .exec();
}
```

**Cross-Agent Consistency**:
```typescript
// Use coordination tasks for multi-agent operations requiring consistency
const task = await agentBus.createCoordinationTask({
  type: 'trade_execution',
  priority: 'high',
  agents: ['risk_manager', 'portfolio_manager', 'trade_executor'],
  data: { symbol: 'AAPL', action: 'BUY', quantity: 100 }
});

// Each agent votes on the action
// Consensus required before execution (2 out of 3 must approve)
const consensus = await task.waitForConsensus();
if (consensus.approved) {
  await executeTrade(task.data);
}
```

### Network Partition Handling

**Split-Brain Prevention** (for multi-host deployment):
```typescript
// Use Caelum MCP as distributed coordinator with leader election
class NetworkPartitionHandler {
  async detectPartition(): Promise<boolean> {
    try {
      const ping = await caelumMCP.ping({ timeout: 5000 });
      return false; // Network OK
    } catch (error) {
      logger.error('Network partition detected');
      return true;
    }
  }

  async handlePartition(): Promise<void> {
    // Strategy: Prefer availability over consistency (AP in CAP theorem)

    // 1. Enter autonomous mode
    await this.enterAutonomousMode();

    // 2. Use local Agent Bus only (disable cross-host coordination)
    agentBus.setMode('local-only');

    // 3. When partition heals, reconcile state
    this.onNetworkRestore(async () => {
      await this.reconcileState();
      agentBus.setMode('distributed');
    });
  }

  async reconcileState(): Promise<void> {
    // After partition heals, merge divergent state
    // Priority: User account data > Trading history > Predictions

    const localState = await storage.getStateSince(partitionStart);
    const remoteState = await caelumMCP.getStateSince(partitionStart);

    // Merge with conflict resolution (last-write-wins)
    const merged = this.mergeStates(localState, remoteState);
    await storage.applyMergedState(merged);
  }
}
```

### Testing Resilience

**Chaos Engineering**:
```bash
# Kill random agent to test auto-recovery
node scripts/chaos/kill-random-agent.js

# Inject 500ms latency into Agent Bus
node scripts/chaos/inject-latency.js --delay=500

# Simulate network partition
node scripts/chaos/partition-network.js --duration=60

# Overload agent with requests (test circuit breaker)
node scripts/chaos/flood-agent.js --agent=fincoll --rps=1000
```

**Integration Tests**:
```typescript
describe('Agent Resilience', () => {
  it('should restart crashed agent within 30s', async () => {
    const agentId = 'fincoll-001';

    // Simulate crash
    agentBus.unregisterAgent(agentId);

    // Wait for supervisor to detect and restart
    await waitFor(() => agentRegistry.get(agentId), { timeout: 30000 });

    expect(agentRegistry.get(agentId)).toBeDefined();
  });

  it('should use DLQ for failed messages', async () => {
    const badMessage = { action: 'invalid', data: {} };

    await agentBus.dispatchToAgent('nonexistent-agent', badMessage);

    const dlq = await storage.getDeadLetterQueue();
    expect(dlq).toContainEqual(
      expect.objectContaining({ originalMessage: badMessage })
    );
  });
});
```

---

## Database Schema for Swarm Coordination

### Current Schema Status

**✅ Implemented** (from `init-database.ts`):
```sql
agents (id, name, type, status, config_json, last_active, created_at, updated_at)
insights (id, title, agent_id, type, content, signal, symbol, metadata)
trades (id, user_id, agent_id, symbol, action, quantity, price, status, metadata)
configurations (id, name, value, type, description)
```

**❌ Missing for Full Swarm Coordination**:

### 1. Coordination Tasks Table

**Purpose**: Persist multi-agent coordination tasks (currently only in-memory in Agent Bus)

```sql
CREATE TABLE coordination_tasks (
  id SERIAL PRIMARY KEY,
  task_id TEXT UNIQUE NOT NULL, -- UUID for external reference
  task_type TEXT NOT NULL, -- 'trade_execution', 'risk_assessment', 'model_training'
  priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),

  -- Agent participation
  agents TEXT[] NOT NULL, -- Array of agent IDs
  orchestrator_agent_id INTEGER REFERENCES agents(id),

  -- Status tracking
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  data JSONB, -- Task input data
  results JSONB, -- Task output results
  error_message TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_coordination_status ON coordination_tasks(status);
CREATE INDEX idx_coordination_priority ON coordination_tasks(priority);
CREATE INDEX idx_coordination_type ON coordination_tasks(task_type);
```

**Usage**:
```typescript
// Agent Bus persists coordination tasks
const task = await agentBus.createCoordinationTask({
  type: 'trade_execution',
  priority: 'high',
  agents: ['risk_manager:001', 'portfolio_manager:002', 'trade_executor:003'],
  data: { symbol: 'AAPL', action: 'BUY', quantity: 100 }
});

// Store in database
await storage.insertCoordinationTask(task);

// Later: Retrieve pending tasks for retry
const pendingTasks = await storage.getPendingCoordinationTasks();
```

### 2. Agent Health History Table

**Purpose**: Track agent health over time for trend analysis

```sql
CREATE TABLE agent_health_history (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER REFERENCES agents(id),
  status TEXT NOT NULL CHECK (status IN ('HEALTHY', 'DEGRADED', 'UNHEALTHY')),

  -- Detailed metrics
  metrics JSONB, -- { responseTime: 250, memoryUsage: 0.75, errorRate: 0.02 }

  -- Error tracking
  last_error TEXT,
  consecutive_failures INTEGER DEFAULT 0,

  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_health_agent ON agent_health_history(agent_id, timestamp DESC);
CREATE INDEX idx_health_status ON agent_health_history(status);

-- Partition by month for performance (optional, for high-frequency logging)
CREATE TABLE agent_health_history_2025_01 PARTITION OF agent_health_history
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

**Usage**:
```typescript
// SystemHealthService logs health checks
await storage.logAgentHealth({
  agentId: agent.id,
  status: 'HEALTHY',
  metrics: {
    responseTime: 250,
    memoryUsage: 0.75,
    cpuUsage: 0.32
  }
});

// Query health trends
const healthTrend = await storage.getAgentHealthTrend(agentId, { hours: 24 });
```

### 3. Agent Handoffs Table

**Purpose**: Track swarm handoffs between agents (LangGraph Swarm feature)

```sql
CREATE TABLE agent_handoffs (
  id SERIAL PRIMARY KEY,

  -- Handoff participants
  from_agent_id INTEGER REFERENCES agents(id),
  to_agent_id INTEGER REFERENCES agents(id),

  -- Handoff details
  reason TEXT, -- 'specialized_task', 'overload', 'capability_requirement'
  state_data JSONB, -- Conversation state transferred

  -- Outcome
  accepted BOOLEAN, -- Did target agent accept handoff?
  rejection_reason TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

CREATE INDEX idx_handoffs_from ON agent_handoffs(from_agent_id);
CREATE INDEX idx_handoffs_to ON agent_handoffs(to_agent_id);
CREATE INDEX idx_handoffs_timestamp ON agent_handoffs(created_at DESC);
```

**Usage**:
```typescript
// PIMSwarmAgent hands off to specialist
const handoff = await agent.handoffToAgent('risk_manager', {
  reason: 'specialized_task',
  stateData: { symbol: 'AAPL', proposedTrade: { ... } }
});

await storage.logAgentHandoff(handoff);

// Analytics: Which agents hand off most frequently?
const handoffStats = await storage.getHandoffStatistics();
```

### 4. Agent Capabilities Table

**Purpose**: Dynamic capability discovery (currently hardcoded)

```sql
CREATE TABLE agent_capabilities (
  id SERIAL PRIMARY KEY,
  agent_id INTEGER REFERENCES agents(id),

  capability TEXT NOT NULL, -- 'trade:execute', 'prediction:create', 'risk:assess'
  enabled BOOLEAN DEFAULT true,

  -- Capability metadata
  confidence_level DECIMAL(3,2), -- 0.0 - 1.0 (how good the agent is at this)
  metadata JSONB, -- { max_concurrency: 5, supported_symbols: ['AAPL', 'MSFT'] }

  -- Timestamps
  added_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  UNIQUE(agent_id, capability)
);

CREATE INDEX idx_capabilities_agent ON agent_capabilities(agent_id);
CREATE INDEX idx_capabilities_name ON agent_capabilities(capability);
CREATE INDEX idx_capabilities_enabled ON agent_capabilities(enabled);
```

**Usage**:
```typescript
// Register agent capabilities dynamically
await storage.setAgentCapability({
  agentId: finCollAgent.id,
  capability: 'prediction:create',
  enabled: true,
  confidenceLevel: 0.87,
  metadata: { supportedSymbols: ['AAPL', 'MSFT', 'GOOGL'] }
});

// Discover agents by capability
const predictors = await storage.findAgentsByCapability('prediction:create');
```

### 5. Model Versions Table

**Purpose**: Track FinVec model evolution and performance

```sql
CREATE TABLE model_versions (
  id SERIAL PRIMARY KEY,

  -- Version identification
  version_name TEXT UNIQUE NOT NULL, -- 'llm1-tech-v1.2.3'
  model_type TEXT NOT NULL, -- 'llm1-tech', 'llm2-finance', 'llm3-sentiment'
  major INTEGER NOT NULL,
  minor INTEGER NOT NULL,
  patch INTEGER NOT NULL,

  -- Model metadata
  checkpoint_path TEXT NOT NULL, -- NFS path to model weights
  training_config JSONB, -- Hyperparameters used

  -- Performance metrics
  sharpe_ratio DECIMAL(10,4),
  win_rate DECIMAL(5,4),
  max_drawdown DECIMAL(5,4),
  backtest_period TSRANGE, -- Date range of backtest

  -- Deployment status
  status TEXT DEFAULT 'testing' CHECK (status IN ('testing', 'canary', 'production', 'retired')),
  deployed_at TIMESTAMP,
  retired_at TIMESTAMP,

  -- Training metadata
  trained_by TEXT, -- GPU server ID
  training_duration INTERVAL,
  dataset_size INTEGER,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_model_version ON model_versions(version_name);
CREATE INDEX idx_model_status ON model_versions(status);
CREATE INDEX idx_model_performance ON model_versions(sharpe_ratio DESC);
```

**Usage**:
```typescript
// FinVec Agent registers new model version
await storage.createModelVersion({
  versionName: 'llm1-tech-v1.2.3',
  modelType: 'llm1-tech',
  checkpointPath: '/home/rford/caelum/ss/finvec/checkpoints/llm1-tech-v1.2.3/',
  sharpeRatio: 1.85,
  winRate: 0.58,
  status: 'canary'
});

// Compare model versions
const comparison = await storage.compareModelVersions(['v1.2.2', 'v1.2.3']);

// Rollback to previous version
await storage.setModelStatus('llm1-tech-v1.2.2', 'production');
await storage.setModelStatus('llm1-tech-v1.2.3', 'retired');
```

### 6. Swarm Events Table

**Purpose**: Audit log of significant swarm events

```sql
CREATE TABLE swarm_events (
  id SERIAL PRIMARY KEY,

  -- Event classification
  event_type TEXT NOT NULL, -- 'agent:registered', 'prediction:ready', 'model:updated', etc.
  severity TEXT CHECK (severity IN ('info', 'warning', 'error', 'critical')),

  -- Event source
  source_agent_id INTEGER REFERENCES agents(id),
  target_agent_id INTEGER REFERENCES agents(id),

  -- Event data
  message TEXT NOT NULL,
  metadata JSONB,

  -- User association (optional)
  user_id INTEGER REFERENCES users(id),

  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_type ON swarm_events(event_type);
CREATE INDEX idx_events_timestamp ON swarm_events(timestamp DESC);
CREATE INDEX idx_events_severity ON swarm_events(severity);

-- Partition by month for high-volume logging
CREATE TABLE swarm_events_2025_01 PARTITION OF swarm_events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

**Usage**:
```typescript
// Log significant events
await storage.logSwarmEvent({
  eventType: 'performance:degraded',
  severity: 'warning',
  sourceAgentId: monitorAgent.id,
  message: 'Sharpe ratio dropped from 1.8 to 1.2',
  metadata: { oldSharpe: 1.8, newSharpe: 1.2, threshold: 1.5 }
});

// Query recent critical events
const criticalEvents = await storage.getSwarmEvents({
  severity: 'critical',
  since: new Date(Date.now() - 86400000) // Last 24 hours
});
```

### Migration Script

```sql
-- migrations/003_swarm_coordination_tables.sql
-- Run after existing schema is in place

BEGIN;

-- Create all swarm coordination tables
\i create_coordination_tasks.sql
\i create_agent_health_history.sql
\i create_agent_handoffs.sql
\i create_agent_capabilities.sql
\i create_model_versions.sql
\i create_swarm_events.sql

-- Update existing agents table
ALTER TABLE agents ADD COLUMN IF NOT EXISTS capabilities TEXT[];
ALTER TABLE agents ADD COLUMN IF NOT EXISTS health_status TEXT DEFAULT 'HEALTHY';

-- Seed default capabilities for existing agents
UPDATE agents SET capabilities = ARRAY['trade:execute', 'position:manage'] WHERE type = 'portfolio_manager';
UPDATE agents SET capabilities = ARRAY['risk:assess', 'trade:approve'] WHERE type = 'risk_manager';
UPDATE agents SET capabilities = ARRAY['prediction:create', 'market:analyze'] WHERE type = 'price_analyzer';

COMMIT;
```

### Storage Service Updates

```typescript
// server/storage.ts - Add methods for new tables

interface IStorage {
  // Existing methods...

  // Coordination tasks
  insertCoordinationTask(task: CoordinationTask): Promise<number>;
  getCoordinationTask(taskId: string): Promise<CoordinationTask | null>;
  updateCoordinationTask(taskId: string, updates: Partial<CoordinationTask>): Promise<void>;
  getPendingCoordinationTasks(): Promise<CoordinationTask[]>;

  // Agent health
  logAgentHealth(log: AgentHealthLog): Promise<void>;
  getAgentHealthTrend(agentId: number, options: { hours: number }): Promise<AgentHealthLog[]>;

  // Agent handoffs
  logAgentHandoff(handoff: AgentHandoff): Promise<number>;
  getHandoffStatistics(): Promise<HandoffStats>;

  // Agent capabilities
  setAgentCapability(capability: AgentCapability): Promise<void>;
  findAgentsByCapability(capability: string): Promise<Agent[]>;

  // Model versions
  createModelVersion(version: ModelVersion): Promise<number>;
  getModelVersion(versionName: string): Promise<ModelVersion | null>;
  compareModelVersions(versions: string[]): Promise<ModelComparison>;
  setModelStatus(versionName: string, status: ModelStatus): Promise<void>;

  // Swarm events
  logSwarmEvent(event: SwarmEvent): Promise<void>;
  getSwarmEvents(filter: EventFilter): Promise<SwarmEvent[]>;
}
```

### Indexes for Performance

```sql
-- Composite indexes for common queries

-- Find active tasks by agent
CREATE INDEX idx_tasks_agent_status
ON coordination_tasks USING btree(orchestrator_agent_id, status);

-- Health trend queries
CREATE INDEX idx_health_trend
ON agent_health_history USING btree(agent_id, timestamp DESC);

-- Recent events by type
CREATE INDEX idx_events_type_time
ON swarm_events USING btree(event_type, timestamp DESC);

-- Model version comparison
CREATE INDEX idx_model_perf_comparison
ON model_versions USING btree(model_type, sharpe_ratio DESC, created_at DESC);
```

### Cleanup Jobs (Maintenance)

```sql
-- Delete old health logs (keep 30 days)
DELETE FROM agent_health_history
WHERE timestamp < NOW() - INTERVAL '30 days';

-- Archive completed coordination tasks (keep 90 days)
DELETE FROM coordination_tasks
WHERE status IN ('completed', 'failed')
AND completed_at < NOW() - INTERVAL '90 days';

-- Delete low-severity events (keep 7 days)
DELETE FROM swarm_events
WHERE severity = 'info'
AND timestamp < NOW() - INTERVAL '7 days';
```

---

## Testing Strategy

### Test Pyramid for Swarm Intelligence

```
                    /\
                   /  \
                  / E2E \ ← Full swarm integration tests
                 /______\
                /        \
               / Swarm    \ ← Multi-agent workflow tests
              / Integration\
             /____________  \
            /                \
           /   Agent Unit     \ ← Individual agent logic
          /____________________\
```

### 1. Unit Tests (Individual Agent Logic)

**Target**: 85%+ code coverage (already achieved in Phase 1)
**Location**: `__tests__/` subdirectories within each service
**Framework**: Jest with TypeScript

```typescript
// Example: FinColl Agent unit test
describe('FinCollAgent', () => {
  let agent: FinCollAgent;
  let mockDependencies: MockDependencies;

  beforeEach(() => {
    mockDependencies = createTestDependencies();
    agent = new FinCollAgent(mockDependencies);
  });

  it('should generate prediction with valid market data', async () => {
    const marketData = {
      symbol: 'AAPL',
      price: 185.23,
      volume: 45000000,
      timestamp: Date.now()
    };

    const prediction = await agent.predict(marketData);

    expect(prediction).toMatchObject({
      symbol: 'AAPL',
      confidence: expect.any(Number),
      direction: expect.stringMatching(/^(bullish|bearish|neutral)$/),
      targets: expect.objectContaining({
        t1: expect.any(Number),
        t2: expect.any(Number)
      })
    });

    expect(prediction.confidence).toBeGreaterThanOrEqual(0);
    expect(prediction.confidence).toBeLessThanOrEqual(1);
  });

  it('should reject prediction when confidence < threshold', async () => {
    const lowConfidenceData = { symbol: 'AAPL', ...noisyMarketData };

    const prediction = await agent.predict(lowConfidenceData);

    expect(prediction).toBeNull(); // Or throws error
  });

  it('should use cached sentiment when SenVec unavailable', async () => {
    mockDependencies.senVecAgent.getSentiment.mockRejectedValue(
      new Error('SenVec offline')
    );

    const prediction = await agent.predict(marketData);

    // Should fall back to cached sentiment
    expect(mockDependencies.cache.get).toHaveBeenCalledWith('sentiment:AAPL');
    expect(prediction).toBeDefined();
    expect(prediction.confidence).toBeLessThan(0.8); // Reduced confidence
  });
});
```

**Mocking Pattern**:
```typescript
// test-utils.ts
export function createTestDependencies(): MockDependencies {
  return {
    storage: {
      getAgentByType: jest.fn(),
      createAgentMemory: jest.fn(),
      storeAgentConfig: jest.fn()
    },
    cache: {
      get: jest.fn(),
      set: jest.fn(),
      del: jest.fn()
    },
    agentBus: {
      publish: jest.fn(),
      subscribe: jest.fn(),
      dispatchToAgent: jest.fn()
    },
    senVecAgent: {
      getSentiment: jest.fn().mockResolvedValue({ score: 0.75, features: [...] })
    },
    logger: {
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn()
    }
  };
}
```

### 2. Integration Tests (Multi-Agent Workflows)

**Purpose**: Test Agent Bus communication, coordination tasks, event propagation

```typescript
describe('Swarm Integration', () => {
  let agentBus: AgentBus;
  let finCollAgent: FinCollAgent;
  let tradingAgent: TradingAgent;
  let riskAgent: RiskManagerAgent;

  beforeEach(async () => {
    agentBus = new AgentBus();

    // Register real agents (not mocks)
    finCollAgent = await agentBus.registerAgent('fincoll', new FinCollAgent());
    tradingAgent = await agentBus.registerAgent('trading', new TradingAgent());
    riskAgent = await agentBus.registerAgent('risk', new RiskManagerAgent());
  });

  it('should coordinate trade execution across agents', async () => {
    const eventCollector = new EventCollector();

    // Subscribe to all events
    agentBus.subscribe('prediction:ready', eventCollector.collect);
    agentBus.subscribe('risk:assessed', eventCollector.collect);
    agentBus.subscribe('trade:executed', eventCollector.collect);

    // Trigger workflow
    await finCollAgent.publishPrediction({
      symbol: 'AAPL',
      confidence: 0.87,
      direction: 'bullish'
    });

    // Wait for workflow to complete
    await eventCollector.waitForEvent('trade:executed', { timeout: 5000 });

    // Verify event sequence
    const events = eventCollector.getEvents();
    expect(events[0].type).toBe('prediction:ready');
    expect(events[1].type).toBe('risk:assessed');
    expect(events[2].type).toBe('trade:executed');

    // Verify data flow
    expect(events[2].data.symbol).toBe('AAPL');
    expect(events[2].data.quantity).toBeGreaterThan(0);
  });

  it('should reject trade when risk assessment fails', async () => {
    const eventCollector = new EventCollector();
    agentBus.subscribe('trade:rejected', eventCollector.collect);

    // High-risk prediction
    await finCollAgent.publishPrediction({
      symbol: 'GME', // Volatile stock
      confidence: 0.65, // Low confidence
      direction: 'bullish'
    });

    await eventCollector.waitForEvent('trade:rejected', { timeout: 5000 });

    const rejection = eventCollector.getLastEvent();
    expect(rejection.data.reason).toMatch(/risk/i);
  });

  it('should handle agent failure gracefully', async () => {
    // Simulate FinColl crash
    agentBus.unregisterAgent('fincoll:001');

    // Trading agent should handle missing prediction source
    const result = await tradingAgent.requestPrediction('AAPL');

    expect(result).toMatchObject({
      status: 'error',
      message: expect.stringMatching(/prediction service unavailable/i)
    });

    // Should use cached predictions
    expect(tradingAgent.usedCachedPrediction).toBe(true);
  });
});
```

**Event Collector Utility**:
```typescript
class EventCollector {
  private events: Array<{ type: string; data: any; timestamp: number }> = [];

  collect = (event: { type: string; data: any }) => {
    this.events.push({ ...event, timestamp: Date.now() });
  };

  async waitForEvent(
    type: string,
    options: { timeout?: number } = {}
  ): Promise<void> {
    const { timeout = 10000 } = options;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (this.events.some(e => e.type === type)) {
        return;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    throw new Error(`Timeout waiting for event: ${type}`);
  }

  getEvents(): Array<{ type: string; data: any; timestamp: number }> {
    return this.events;
  }

  getLastEvent() {
    return this.events[this.events.length - 1];
  }
}
```

### 3. Swarm Simulation Tests (Historical Data Replay)

**Purpose**: Validate self-evolution and performance using real market data

```typescript
describe('Swarm Performance Simulation', () => {
  let swarm: SwarmOrchestrator;
  let historicalData: MarketDataset;

  beforeAll(async () => {
    // Load 3 months of historical data
    historicalData = await loadHistoricalData({
      symbols: ['AAPL', 'MSFT', 'GOOGL'],
      startDate: '2024-01-01',
      endDate: '2024-03-31'
    });
  });

  it('should achieve >1.5 Sharpe ratio on backtest', async () => {
    swarm = new SwarmOrchestrator();

    // Replay historical data (60 trading days)
    for (const day of historicalData.days) {
      await swarm.processMarketDay(day);
    }

    const metrics = swarm.getPerformanceMetrics();

    expect(metrics.sharpeRatio).toBeGreaterThan(1.5);
    expect(metrics.winRate).toBeGreaterThan(0.55);
    expect(metrics.maxDrawdown).toBeLessThan(0.20); // < 20%
  });

  it('should adapt to market regime change', async () => {
    // January: Low volatility, bullish
    const janMetrics = await swarm.simulate(historicalData.january);

    // February: High volatility (VIX spike)
    const febMetrics = await swarm.simulate(historicalData.february);

    // Verify swarm adapted strategy
    expect(febMetrics.avgPositionSize).toBeLessThan(janMetrics.avgPositionSize);
    expect(febMetrics.confidenceThreshold).toBeGreaterThan(janMetrics.confidenceThreshold);

    // Check for regime-change event
    const events = swarm.getEmittedEvents();
    expect(events).toContainEqual(
      expect.objectContaining({ type: 'market:regime_change' })
    );
  });

  it('should trigger model retraining when performance degrades', async () => {
    let retrainingTriggered = false;

    swarm.on('model:retraining_started', () => {
      retrainingTriggered = true;
    });

    // Simulate poor performance period
    await swarm.simulate(historicalData.badPerformancePeriod);

    expect(retrainingTriggered).toBe(true);
  });
});
```

### 4. End-to-End Tests (Full System)

**Purpose**: Test complete user workflows from UI to trade execution

```typescript
describe('E2E: User Onboarding to First Trade', () => {
  let browser: Browser;
  let page: Page;
  let swarm: SwarmOrchestrator;

  beforeAll(async () => {
    browser = await puppeteer.launch({ headless: true });
    page = await browser.newPage();
    swarm = await startSwarmInTestMode();
  });

  it('should complete full user journey', async () => {
    // 1. User registers account
    await page.goto('http://localhost:5000/register');
    await page.type('#email', 'test@example.com');
    await page.type('#password', 'SecurePassword123!');
    await page.click('#submit');

    await page.waitForNavigation();
    expect(page.url()).toBe('http://localhost:5000/dashboard');

    // 2. User sets risk tolerance
    await page.click('#settings');
    await page.select('#riskTolerance', 'conservative');
    await page.type('#profitTarget', '10'); // 10% annual return
    await page.click('#saveSettings');

    // Wait for swarm to acknowledge settings
    await page.waitForSelector('.notification.success');

    // 3. User connects brokerage
    await page.click('#connectBroker');
    await page.select('#broker', 'TradeStation');
    await page.type('#apiKey', process.env.TEST_TS_API_KEY);
    await page.type('#apiSecret', process.env.TEST_TS_API_SECRET);
    await page.click('#connect');

    await page.waitForSelector('.brokerConnected');

    // 4. System generates first prediction
    // (Inject market data via swarm)
    await swarm.injectMarketData({
      symbol: 'AAPL',
      price: 185.23,
      volume: 45000000,
      sentiment: 0.75
    });

    // Wait for prediction to appear in UI
    await page.waitForSelector('.prediction', { timeout: 10000 });

    const predictionText = await page.$eval('.prediction', el => el.textContent);
    expect(predictionText).toMatch(/AAPL/);
    expect(predictionText).toMatch(/bullish|bearish/);

    // 5. User approves trade
    await page.click('#approveTrade');

    // Wait for trade execution
    await page.waitForSelector('.tradeExecuted', { timeout: 15000 });

    // Verify trade appears in history
    await page.click('#tradeHistory');
    const trades = await page.$$('.tradeRow');
    expect(trades.length).toBeGreaterThan(0);

    const firstTrade = await trades[0].$eval('.symbol', el => el.textContent);
    expect(firstTrade).toBe('AAPL');
  });

  afterAll(async () => {
    await browser.close();
    await swarm.shutdown();
  });
});
```

### 5. Chaos Engineering (Resilience Testing)

**Purpose**: Verify swarm survives failures and partitions

```bash
#!/bin/bash
# scripts/chaos/run-chaos-tests.sh

set -e

echo "🔥 Starting Chaos Engineering Tests"

# Test 1: Kill random agent
echo "Test 1: Killing random agent..."
node scripts/chaos/kill-random-agent.js
sleep 30
node scripts/chaos/verify-swarm-recovered.js

# Test 2: Inject network latency
echo "Test 2: Injecting 500ms latency..."
node scripts/chaos/inject-latency.js --delay=500
node scripts/chaos/run-performance-test.js
node scripts/chaos/remove-latency.js

# Test 3: Simulate database failure
echo "Test 3: PostgreSQL failure..."
docker stop caelum-postgres
sleep 10
node scripts/chaos/verify-graceful-degradation.js
docker start caelum-postgres
sleep 10
node scripts/chaos/verify-recovery.js

# Test 4: Network partition (multi-host)
echo "Test 4: Network partition..."
node scripts/chaos/partition-network.js --duration=60
sleep 60
node scripts/chaos/verify-state-reconciliation.js

echo "✅ All chaos tests passed!"
```

**Chaos Test Implementation**:
```typescript
// scripts/chaos/kill-random-agent.js
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function killRandomAgent() {
  const agents = ['fincoll', 'senvec', 'finvec', 'trading'];
  const victim = agents[Math.floor(Math.random() * agents.length)];

  console.log(`Killing ${victim} agent...`);

  // Find process
  const { stdout } = await execAsync(`pgrep -f "agent-${victim}"`);
  const pid = stdout.trim();

  if (pid) {
    await execAsync(`kill -9 ${pid}`);
    console.log(`Killed ${victim} agent (PID: ${pid})`);
  }
}

killRandomAgent().catch(console.error);
```

```typescript
// scripts/chaos/verify-swarm-recovered.js
import { AgentBus } from '../PassiveIncomeMaximizer/server/services/agent-bus';

async function verifyRecovery() {
  const bus = new AgentBus();
  await bus.initialize();

  const expectedAgents = ['fincoll', 'senvec', 'finvec', 'trading', 'risk', 'portfolio'];

  for (const agentType of expectedAgents) {
    const agents = bus.getAgentsByType(agentType);

    if (agents.length === 0) {
      console.error(`❌ ${agentType} agent not recovered!`);
      process.exit(1);
    }

    console.log(`✅ ${agentType} agent recovered`);
  }

  console.log('✅ All agents recovered successfully');
  process.exit(0);
}

verifyRecovery().catch(err => {
  console.error('Recovery verification failed:', err);
  process.exit(1);
});
```

### 6. Load Testing (Agent Bus Throughput)

```typescript
// scripts/load-test/agent-bus-stress.ts
import { AgentBus } from '../server/services/agent-bus';

async function loadTest() {
  const bus = new AgentBus();
  await bus.initialize();

  const messagesSent = 10000;
  const startTime = Date.now();

  // Send 10,000 messages concurrently
  const promises = Array.from({ length: messagesSent }, (_, i) => {
    return bus.publish('test:message', {
      id: i,
      timestamp: Date.now(),
      data: { symbol: 'AAPL', price: 185.23 }
    });
  });

  await Promise.all(promises);

  const duration = Date.now() - startTime;
  const throughput = messagesSent / (duration / 1000);

  console.log(`Sent ${messagesSent} messages in ${duration}ms`);
  console.log(`Throughput: ${throughput.toFixed(0)} messages/sec`);

  // Target: >1000 messages/sec
  if (throughput < 1000) {
    console.error('❌ Throughput below target!');
    process.exit(1);
  }

  console.log('✅ Load test passed');
}

loadTest().catch(console.error);
```

### Testing Checklist

**Unit Tests** (85%+ coverage):
- [ ] Agent logic (predictions, risk assessment, trading)
- [ ] Agent Bus (pub/sub, dispatch, coordination)
- [ ] Storage layer (CRUD operations)
- [ ] Health monitoring
- [ ] Error handling

**Integration Tests**:
- [ ] Multi-agent workflows (prediction → risk → trade)
- [ ] Agent Bus message routing
- [ ] Coordination tasks
- [ ] Event propagation
- [ ] Graceful degradation

**Swarm Simulation**:
- [ ] Backtesting with historical data
- [ ] Sharpe ratio >1.5
- [ ] Win rate >55%
- [ ] Max drawdown <20%
- [ ] Market regime adaptation
- [ ] Self-evolution triggers

**End-to-End**:
- [ ] User registration and onboarding
- [ ] Brokerage connection
- [ ] Prediction generation
- [ ] Trade execution
- [ ] Portfolio tracking
- [ ] Settings updates

**Chaos Engineering**:
- [ ] Agent crash recovery (<30s)
- [ ] Database failure graceful degradation
- [ ] Network partition handling
- [ ] Latency injection (performance)
- [ ] Load testing (>1000 msg/sec)

**Security**:
- [ ] Authentication bypass attempts
- [ ] Authorization violations
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Rate limiting enforcement
- [ ] Multi-tenant isolation

---

## Commercialization Strategy

### Product 1: "PassiveIncomeMaximizer Pro" (Full Swarm)

**What customer gets**:
- Complete source code (PIM, FinColl, FinVec)
- Docker deployment orchestration
- Documentation and setup guides
- 1 year of model updates
- Access to SenVec API (usage-based pricing)
- Access to Caelum MCP swarm coordination (multi-tenant)

**What customer deploys**:
- Their own PIM instance (white-labeled)
- Their own FinColl instance (isolated)
- Their own PostgreSQL/Redis (isolated data)
- Their own brokerage connections

**What they connect to (your infrastructure)**:
- Caelum MCP swarm coordinator (shared, multi-tenant)
- SenVec sentiment API (shared, usage billing)
- Model update registry (new FinVec checkpoints)

**Pricing**: $10k-50k one-time + $500/mo maintenance + SenVec usage

### Product 2: "SenVec Sentiment API" (Standalone)

**What customer gets**:
- API access to 72D sentiment features
- Real-time updates
- Historical data access
- Documentation

**Pricing**: $49-299/mo based on request volume (as already designed)

### Product 3: "Caelum Swarm Platform" (Infrastructure)

**What customer gets**:
- MCP server for building multi-agent systems
- Agent coordination infrastructure
- LLM routing and cost optimization
- Device orchestration

**Target market**: AI/agent developers, not just traders

**Pricing**: $99-999/mo per deployment or per-device licensing

### Product 4: "FinVec Training Pipeline" (ML Infrastructure)

**What customer gets**:
- Financial LLM training code
- Multi-GPU orchestration
- TradeStation integration
- Feature engineering pipeline

**Target market**: Hedge funds, ML researchers

**Pricing**: $25k-100k one-time license + training-as-a-service

---

## Key Takeaway

**This is not microservices. This is swarm intelligence.**

Every component is a specialized agent with its own intelligence, but they are not independent. They are organs of a single organism - THE STRATEGY.

The strategy:
1. **Observes** markets via SenVec (sensors)
2. **Predicts** via FinColl (neural network brain)
3. **Decides** via PIM (executive brain)
4. **Executes** via Trading Agent (motor cortex)
5. **Learns** via FinVec (evolution brain)
6. **Coordinates** via Agent Bus + Caelum MCP (nervous system)
7. **Adapts** via continuous feedback loops (self-evolution)

All customized to each user's goals and risk tolerance, but running as ONE unified strategy.

---

**Document Version**: 2.1.0 (Enhanced with Resilience, Testing, Monitoring, and Database Schema)
**Last Updated**: 2025-11-09
**Changes in 2.1.0**:
- Added comprehensive Resilience & Fault Tolerance section (circuit breakers, retry logic, graceful degradation)
- Added Testing Strategy section (unit tests, integration tests, chaos engineering, E2E tests)
- Enhanced Agent Bus Implementation Details with technical specifications
- Added Monitoring Dashboard Design section (real-time metrics, WebSocket integration)
- Added Database Schema section for swarm coordination (6 new tables)
- Fixed cost_sensitivity references (replaced with prefer_local)
- Clarified model naming convention (LLM-5 → model V5)
- Added agent role clarification (Trading/Monitor capabilities)

**Next**: Implement swarm deployment orchestration recognizing interdependencies
