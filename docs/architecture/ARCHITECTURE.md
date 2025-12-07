# PassiveIncomeMaximizer - System Architecture

**Last Updated**: 2025-11-14
**Version**: 2.0 (Clean Architecture with PIM Engine)
**Pattern**: Multi-Agent Trading System with Prediction-to-Execution Pipeline

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Layers](#component-layers)
4. [Data Flow](#data-flow)
5. [Repository Structure](#repository-structure)
6. [Communication Patterns](#communication-patterns)
7. [Deployment Architecture](#deployment-architecture)
8. [Service Interactions](#service-interactions)

---

## System Overview

PassiveIncomeMaximizer (PIM) is a multi-agent autonomous trading system that transforms ML predictions into trading decisions through collaborative intelligence.

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     FinVec Repository                         │
│              (Prediction Model Training & Serving)            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  FinColl API │  │  SenVec API  │  │  V7 Training    │   │
│  │  (Port 8002) │  │ (Port 18000) │  │  (GPU Jobs)     │   │
│  │  Predictions │  │  Sentiment   │  │  Model Updates  │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
└─────────┼──────────────────┼───────────────────┼────────────┘
          │                  │                   │
          │                  │                   │
          ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────────────┐
│           PassiveIncomeMaximizer Repository                   │
│                 (Trading System)                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              PIM Engine (Python)                        │ │
│  │              Port 5002 - REST API                       │ │
│  │                                                         │ │
│  │  Information Gatherer → Coordinator → 9 Subagents      │ │
│  │                                                         │ │
│  │  Agents: Portfolio Manager, Price Analyzer, Risk       │ │
│  │          News Processor, Trend Analyzer, + 4 more      │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────┴───────────────────────────────────┐ │
│  │         Backend APIs (Multi-Stack)                     │ │
│  │                                                         │ │
│  │  ┌──────────────┐         ┌─────────────────┐         │ │
│  │  │  Express API │         │    Flask API    │         │ │
│  │  │  (TypeScript)│         │    (Python)     │         │ │
│  │  │  Port 5000   │         │    Port 5000    │         │ │
│  │  │  Full Stack  │         │    Alternative  │         │ │
│  │  └──────┬───────┘         └────────┬────────┘         │ │
│  └─────────┼──────────────────────────┼──────────────────┘ │
│            │                          │                     │
│  ┌─────────┴──────────────────────────┴──────────────────┐ │
│  │              Frontends (Dual-UI)                       │ │
│  │                                                         │ │
│  │  ┌──────────────┐         ┌─────────────────┐         │ │
│  │  │ Vue3 + Vuetify│        │   React UI      │         │ │
│  │  │  Port 5500    │        │   Port 5000     │         │ │
│  │  │  Modern UI    │        │   Legacy UI     │         │ │
│  │  │  D3.js Swarm  │        │   Full-featured │         │ │
│  │  └──────────────┘         └─────────────────┘         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      │ Uses infrastructure from
                      ▼
┌──────────────────────────────────────────────────────────────┐
│              Caelum-Unified Infrastructure                    │
│              (Shared Services - Separate System)             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  Qdrant VDB  │      │
│  │  (15432)     │  │    (6379)    │  │   (6333)     │      │
│  │  Database    │  │    Cache     │  │  Vector DB   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  MongoDB     │  │  Caelum MCP  │                         │
│  │  (27017)     │  │   (8090)     │                         │
│  │  Documents   │  │  Coordinator │                         │
│  └──────────────┘  └──────────────┘                         │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### 1. Clean Separation of Concerns

**Express/Flask = Thin Routing Layer**
- HTTP request routing
- Input validation
- Authentication/authorization
- Lightweight database CRUD
- WebSocket management
- **NO heavy computation**

**Python Services = Computation Workers**
- ML inference
- Agent execution
- Backtesting
- Risk calculations
- Pattern recognition
- Independent scalability

**PIM Engine = Agent Orchestration**
- Information gathering
- Multi-agent coordination
- Decision synthesis
- External memory integration

### 2. Repository Independence

```
/home/rford/caelum/ss/
├── PassiveIncomeMaximizer/    # Trading system (PIM + UI)
├── finvec/                    # Prediction models (FinColl/V7)
└── caelum-unified/            # Shared infrastructure
```

**Benefits:**
- Independent versioning
- Separate deployment cycles
- Clear API contracts
- Modular development

### 3. Dual-Stack Flexibility

**Frontend Options:**
- **Vue3** (Modern, Vuetify, D3.js) - Port 5500
- **React** (Legacy, full-featured) - Port 5000

**Backend Options:**
- **Express** (TypeScript, full-stack) - Port 5000
- **Flask** (Python, API-only) - Port 5000

Both frontends use same backend APIs.

### 4. Event-Driven Agent Communication

**Agent Bus Pattern:**
- Pub/sub event system
- Asynchronous messaging
- Parallel agent execution
- Decoupled components

---

## Component Layers

### Layer 1: Frontend (Presentation)

#### Vue3 Dashboard (Port 5500)

```
src/
├── views/
│   ├── Monitor.vue              # Real-time positions & P/L
│   ├── SwarmNetwork.vue         # D3.js agent visualization
│   ├── Backtest.vue             # Signal-based backtesting
│   ├── Insights.vue             # Trading analytics
│   ├── History.vue              # Trade history
│   └── Scheduler.vue            # Automation
├── components/
│   ├── SwarmGraph.vue           # Force-directed agent graph
│   ├── PositionTable.vue        # Real-time positions
│   └── PredictionCard.vue       # V7 predictions
└── composables/
    └── useApi.ts                # API integration
```

**Features:**
- Modern Material Design (Vuetify 3)
- Real-time WebSocket updates
- D3.js force-directed graph
- Chart.js visualizations

#### React Dashboard (Port 5000)

```
client/
├── src/
│   ├── pages/
│   │   ├── TradingDashboard.tsx
│   │   ├── AgentStatus.tsx
│   │   ├── Performance.tsx
│   │   └── Configuration.tsx
│   └── components/
│       ├── PositionManager.tsx
│       ├── RiskAnalyzer.tsx
│       └── BacktestResults.tsx
```

**Features:**
- Full-featured interface
- All existing functionality
- Legacy compatibility

### Layer 2: Backend APIs (Application Logic)

#### Express API (TypeScript) - Port 5000

```
server/
├── routes/
│   ├── agents.ts               # Agent management
│   ├── positions.ts            # Position CRUD
│   ├── backtest.ts             # Backtest runner
│   ├── performance.ts          # Metrics
│   └── scheduler.ts            # Task automation
├── services/
│   ├── agents/
│   │   ├── swarm-base-agent.ts      # Base agent class
│   │   ├── swarm-portfolio-manager.ts
│   │   ├── swarm-price-analyzer.ts
│   │   └── ... (9 agents total)
│   ├── position-manager.ts
│   ├── risk-manager.ts
│   ├── backtest-client.ts      # Calls Python backtest service
│   └── pimEngineService.ts     # Calls PIM Engine API
└── index.ts                     # Main server entry
```

**Responsibilities:**
- Route HTTP requests
- Validate inputs
- Authenticate users
- Coordinate services
- Manage WebSockets
- Return responses

**What Express Does NOT Do:**
- ❌ Heavy computation
- ❌ ML inference
- ❌ Complex backtesting
- ❌ GPU operations

#### Flask API (Python) - Port 5000 (Alternative)

```
api/
├── app.py                      # Main Flask app
├── routes/
│   ├── evaluate.py             # V7 → PIM evaluation
│   ├── positions.py            # Position tracking
│   ├── backtest.py             # Backtest proxy
│   └── performance.py          # Metrics
└── models/
    ├── position.py
    └── decision.py
```

**Purpose:** Lightweight Python alternative to Express for simpler deployments.

### Layer 3: PIM Engine (Agent Intelligence)

#### Python REST API - Port 5002

```
engine/
├── pim/
│   ├── engine.py                    # Main orchestrator
│   ├── caelum_integration.py        # External memory
│   ├── committee.py                 # Multi-agent voting
│   ├── monitors/                    # 24/7 Monitoring Services
│   │   ├── risk_monitor.py          # Continuous risk monitoring (60s)
│   │   └── __init__.py
│   ├── evolution/                   # Self-Improvement Systems
│   │   ├── self_evaluator.py        # Daily self-evaluation (4PM ET)
│   │   └── __init__.py
│   └── agents/
│       ├── v7_agent.py              # PIMV7Agent
│       ├── momentum_agent.py
│       ├── sentiment_agent.py
│       ├── risk_agent.py
│       ├── technical_agent.py
│       └── ... (9 agents)
├── pim_service.py                   # REST API server
├── 24x7_ARCHITECTURE.md             # 24/7 system documentation
└── data/
    └── providers/
        ├── yfinance_provider.py
        └── tradestation_provider.py
```

**Architecture Pattern:**

```
┌─────────────────────────────────────────────────────────┐
│              PIM Engine Orchestrator (24/7 Mode)         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Information Gatherer (Scans every 5 min)        │  │
│  │  - Calls FinColl for V7 predictions              │  │
│  │  - Calls SenVec for sentiment                    │  │
│  │  - Creates "suggested topics" for discussion     │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       │                                 │
│                       ▼                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Coordinator                                      │  │
│  │  - Receives suggested topics                      │  │
│  │  - Spawns 4 subagents IN PARALLEL:               │  │
│  │    1. V7Agent (price analysis)                    │  │
│  │    2. SentimentAgent (news analysis)              │  │
│  │    3. RiskAgent (risk assessment)                 │  │
│  │    4. TechnicalAgent (trend analysis)             │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       │                                 │
│                       ▼                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Committee                                        │  │
│  │  - Weights agent votes                            │  │
│  │  - Aggregates to final decision                   │  │
│  │  - Returns: direction, confidence, position_size  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  24/7 Services (Continuous Operation)            │  │
│  │                                                   │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Risk Monitor (Every 60 seconds)           │  │  │
│  │  │  - Monitors open positions                 │  │  │
│  │  │  - Checks stop-loss breaches               │  │  │
│  │  │  - Detects unrealized losses (>5% warn)    │  │  │
│  │  │  - Pre-market & after-hours alerts         │  │  │
│  │  │  - Runs even when market closed            │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │                                                   │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Daily Self-Evaluator (4:00 PM ET)        │  │  │
│  │  │  - Analyzes all agent performance          │  │  │
│  │  │  - Generates improvement suggestions       │  │  │
│  │  │  - Auto-implements LOW-RISK changes        │  │  │
│  │  │  - Stores results for review               │  │  │
│  │  │  - Compound 1% daily = 37x yearly          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Endpoints:**
- `POST /api/pim/scan` - Run market scan
- `GET /api/pim/status` - Engine status
- `POST /api/pim/start` - Start continuous operation
- `POST /api/pim/stop` - Stop engine
- `GET /api/pim/discussions` - Get discussion history

**24/7 Service Endpoints:**
- `GET /api/pim/risk/alerts` - Recent risk alerts (INFO/WARNING/CRITICAL/EMERGENCY)
- `GET /api/pim/evolution/report` - Latest daily self-evaluation
- `GET /api/pim/evolution/improvements?days=7` - Improvement history

**See also:** `engine/24x7_ARCHITECTURE.md` for complete 24/7 system documentation

### Layer 4: External Services (Predictions & Data)

#### FinColl API (Port 8002)

**Repository:** `/home/rford/caelum/ss/finvec`

```python
# FinColl API endpoints
POST /api/v1/inference/predict
GET  /api/health
```

**Purpose:**
- V7 model predictions (336D features)
- Technical analysis
- Entry/exit signals

**NOT an agent** - Just a service that agents use.

#### SenVec API (Port 18000)

**Repository:** `/home/rford/caelum/ss/finvec` (senvec module)

```python
# SenVec API endpoints
GET /features/{symbol}/compact
GET /health
```

**Purpose:**
- Sentiment analysis (72D features)
- Social media sentiment
- News sentiment

**NOT an agent** - Just a service that agents use.

---

## Data Flow

### Prediction-to-Execution Flow

```
Step 1: Prediction Generation
┌─────────────┐
│  FinColl    │──→ V7 Model predicts price movement
│  (V7 API)   │    confidence, entry signal, targets
└─────────────┘
       │
       ▼
Step 2: Information Gathering
┌─────────────┐
│ Information │──→ Scans all predictions every 5 min
│  Gatherer   │    Filters by confidence threshold
│   Agent     │    Creates "suggested topics"
└─────────────┘
       │
       ▼
Step 3: Topic Prioritization
┌─────────────┐
│ Coordinator │──→ Reviews suggested topics
│   Agent     │    Prioritizes by urgency + confidence
│             │    Decides which to discuss
└─────────────┘
       │
       ▼
Step 4: Team Discussion (Parallel)
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ V7Agent     │SentimentAgent│ RiskAgent   │TechnicalAgent│
│ Price       │ News         │ Portfolio   │ Trend       │
│ Analysis    │ Analysis     │ Risk        │ Analysis    │
└─────────────┴─────────────┴─────────────┴─────────────┘
       │              │            │             │
       └──────────────┴────────────┴─────────────┘
                      │
                      ▼
Step 5: Committee Voting
┌─────────────┐
│  Committee  │──→ Weights votes by agent performance
│             │    Aggregates to final decision
│             │    BUY/SELL/HOLD + confidence
└─────────────┘
       │
       ▼
Step 6: Execution
┌─────────────┐
│  Express/   │──→ Validates decision
│  Flask API  │    Checks risk limits
│             │    Executes trade via Alpaca/TradeStation
└─────────────┘
       │
       ▼
Step 7: Storage
┌─────────────┐
│ PostgreSQL  │──→ Stores decision + outcome
│ + Caelum    │    Tracks performance
│   Memory    │    Triggers retraining if needed
└─────────────┘
```

### Agent Communication Flow

```
┌──────────────────────────────────────────────────────────┐
│                    Agent Bus (Pub/Sub)                    │
│                                                           │
│  Topic: OPPORTUNITIES_DETECTED                           │
│  ├─ Publisher: Information Gatherer                      │
│  └─ Subscribers: Portfolio Manager                       │
│                                                           │
│  Topic: PREDICTION_READY                                 │
│  ├─ Publisher: FinColl Service                           │
│  └─ Subscribers: Portfolio Manager, Price Analyzer       │
│                                                           │
│  Topic: SENTIMENT_UPDATE                                 │
│  ├─ Publisher: News Processor                            │
│  └─ Subscribers: Portfolio Manager, Risk Manager         │
│                                                           │
│  Topic: RISK_THRESHOLD_BREACH                            │
│  ├─ Publisher: Risk Manager                              │
│  └─ Subscribers: Portfolio Manager, ALL agents           │
│                                                           │
│  Topic: TRADE_EXECUTED                                   │
│  ├─ Publisher: Portfolio Manager                         │
│  └─ Subscribers: Metrics Evaluator, Risk Manager         │
└──────────────────────────────────────────────────────────┘
```

---

## Repository Structure

### PassiveIncomeMaximizer

```
PassiveIncomeMaximizer/
├── server/                      # Express backend (TypeScript)
│   ├── index.ts                 # Main entry point
│   ├── routes/                  # HTTP routes
│   ├── services/
│   │   ├── agents/              # 9 PIM agents
│   │   ├── agent-bus.ts         # Event bus
│   │   ├── position-manager.ts
│   │   ├── risk-manager.ts
│   │   └── pimEngineService.ts
│   └── storage.ts               # Database layer
│
├── client/                      # React frontend (legacy)
│   └── src/
│       ├── pages/
│       └── components/
│
├── src/                         # Vue3 frontend (modern)
│   ├── views/
│   ├── components/
│   ├── composables/
│   └── router.ts
│
├── engine/                      # Python PIM Engine
│   ├── pim/
│   │   ├── engine.py            # Main orchestrator
│   │   ├── agents/              # 9 trading agents
│   │   ├── committee.py         # Voting system
│   │   └── caelum_integration.py
│   ├── pim_service.py           # REST API (port 5002)
│   ├── data/                    # Data providers
│   ├── scripts/                 # Utility scripts
│   └── requirements.txt
│
├── api/                         # Flask API (alternative)
│   ├── app.py
│   └── routes/
│
├── shared/                      # Shared TypeScript types
├── tests/                       # Test suites
├── docs/                        # Documentation
├── .env                         # Environment config
├── package.json                 # Node dependencies
├── vite.config.ts               # Vite config (Vue3)
└── docker-compose.yml           # Container orchestration
```

### FinVec Repository

```
finvec/
├── fincoll/                     # FinColl API
│   ├── api/
│   │   └── server.py            # FastAPI server (port 8002)
│   ├── models/                  # V7 model
│   └── inference/               # Prediction logic
│
├── fincoll-v7/                  # V7 feature extraction
│   ├── features/
│   └── preprocessing/
│
├── models/                      # Model architectures
├── training/                    # Training pipelines
└── scripts/                     # Utility scripts
```

---

## Communication Patterns

### Pattern 1: Spawned Child Process (Quick Tasks)

**Use Case:** One-off operations (<5 seconds)
**Examples:** Order execution, risk calculation

```typescript
async function spawnPythonService(script: string, input: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [
      `services/python/${script}.py`,
      JSON.stringify(input)
    ]);

    let output = '';
    process.stdout.on('data', (data) => output += data);
    process.on('close', (code) => {
      if (code === 0) resolve(JSON.parse(output));
      else reject(new Error(`Process exited with code ${code}`));
    });
  });
}
```

### Pattern 2: Long-Running REST Service

**Use Case:** Continuous services handling multiple requests
**Examples:** PIM Engine, Backtest service

```typescript
// PIM Engine service client
const PIM_ENGINE_URL = 'http://10.32.3.27:5002';

async function runPIMScan(symbols: string[]) {
  const response = await axios.post(`${PIM_ENGINE_URL}/api/pim/scan`, {
    symbols
  });
  return response.data;
}
```

### Pattern 3: Event Bus (Pub/Sub)

**Use Case:** Agent-to-agent communication
**Examples:** Agent collaboration, notifications

```typescript
// Publish event
agentBus.publish(PIMEventTopics.PREDICTION_READY, {
  symbol: 'AAPL',
  prediction: 'bullish',
  confidence: 0.85
});

// Subscribe to event
agentBus.subscribe(PIMEventTopics.PREDICTION_READY, async (event) => {
  await portfolioManager.handlePrediction(event);
});
```

### Pattern 4: WebSocket (Real-Time)

**Use Case:** Frontend real-time updates
**Examples:** Position updates, agent activity

```typescript
// Server broadcasts
io.emit('agent:message', {
  agentId: 'portfolio_manager',
  message: 'Trade executed',
  timestamp: Date.now()
});

// Client receives
socket.on('agent:message', (data) => {
  updateAgentStatus(data);
});
```

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────┐
│                    Local Machine                         │
│                                                          │
│  Port 5000:  Express API + React Frontend               │
│  Port 5500:  Vue3 Frontend (Vite dev server)            │
│  Port 5002:  PIM Engine (Python)                        │
│  Port 8002:  FinColl API                                 │
│  Port 18000: SenVec API                                  │
│  Port 15432: PostgreSQL (Docker)                         │
│  Port 6379:  Redis (10.32.3.27)                          │
│  Port 6333:  Qdrant (10.32.3.27)                         │
└─────────────────────────────────────────────────────────┘
```

### Production Environment (Docker)

```yaml
# docker-compose.yml
services:
  express-api:
    build: ./server
    ports: ["5000:5000"]
    environment:
      DATABASE_URL: postgresql://...
      PIM_ENGINE_URL: http://pim-engine:5002
      FINCOLL_URL: http://fincoll:8002
    depends_on: [postgres, redis, pim-engine]

  pim-engine:
    build: ./engine
    ports: ["5002:5002"]
    environment:
      FINCOLL_URL: http://fincoll:8002
      SENVEC_URL: http://senvec:18000
    depends_on: [fincoll, senvec]

  fincoll:
    build: ../finvec
    ports: ["8002:8002"]
    depends_on: [senvec]

  senvec:
    build: ../finvec/senvec
    ports: ["18000:18000"]

  postgres:
    image: postgres:15
    ports: ["15432:5432"]
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports: ["6379:6379"]

  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes:
      - qdrant-data:/qdrant/storage
```

### Multi-Machine Deployment

**GPU Servers** (10.32.3.44, 10.32.3.62):
- PIM Engine training jobs
- FinVec V7 model training
- Same NFS mount from 10.32.3.27 (no setup time!)

**Application Server** (10.32.3.27):
- Express/Flask API
- Vue3/React frontends
- PostgreSQL, Redis, Qdrant
- NFS file server

---

## Service Interactions

### Startup Sequence

```bash
# 1. Infrastructure (Caelum-Unified)
docker start caelum-postgres  # Port 15432
redis-server                   # Port 6379 (10.32.3.27)

# 2. Prediction Services (FinVec)
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server   # Port 8002

# 3. PIM Engine
cd /home/rford/caelum/ss/PassiveIncomeMaximizer/engine
source .venv/bin/activate
python pim_service.py          # Port 5002

# 4. Backend API
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run dev                    # Port 5000 (Express + React)

# 5. Vue3 Frontend (Optional)
npm run vue                    # Port 5500
```

### Health Check Sequence

```bash
# Check all services
curl http://10.32.3.27:5000/api/health     # Express API
curl http://10.32.3.27:5002/api/pim/status # PIM Engine
curl http://10.32.3.27:8002/api/health     # FinColl
curl http://10.32.3.27:18000/health        # SenVec
redis-cli -h 10.32.3.27 ping              # Redis
docker ps | grep caelum-postgres          # PostgreSQL
```

---

## Key Architectural Decisions

### 1. Why Dual Frontends?

**Flexibility** - Choose best tool for each feature
**Migration Path** - Gradual Vue3 adoption
**Redundancy** - If one breaks, other works
**Learning** - Compare frameworks side-by-side

### 2. Why Separate PIM Engine?

**Clean Separation** - Express = routing, Python = computation
**Scalability** - Engine can scale independently
**Language Optimization** - Python for ML, TypeScript for web
**GPU Support** - Easy deployment to GPU servers

### 3. Why Agent Bus?

**Decoupling** - Agents don't need direct references
**Scalability** - Easy to add new agents
**Event-Driven** - React to changes instantly
**Testing** - Mock events for unit tests

### 4. Why External Memory?

**Context Limits** - LLM context windows limited
**Cost Reduction** - Don't repeat large data
**Shared State** - All agents see same context
**Persistence** - Decisions survive restarts

---

## Related Documentation

- **GETTING_STARTED.md** - Setup and installation
- **AGENT_SYSTEM.md** - Agent details and swarm mechanics
- **TRADING_OPERATIONS.md** - Backtesting and trading
- **INTEGRATIONS.md** - FinVec, Caelum, external services
- **DEVELOPMENT_GUIDE.md** - Development workflow
- **EVOLUTION_HISTORY.md** - Project history and phases

---

**For detailed agent architecture and swarm mechanics, see AGENT_SYSTEM.md**
**For trading operations and backtesting details, see TRADING_OPERATIONS.md**
**For integration with external services, see INTEGRATIONS.md**
