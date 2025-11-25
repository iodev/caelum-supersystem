# Caelum SuperSystem - Submodule Overview

**Vision, purpose, and interconnections of all ecosystem components**

---

## Ecosystem Vision

The Caelum SuperSystem is an **AI-powered autonomous trading and development ecosystem** that combines:

1. **Autonomous Trading** - Multi-agent system making real trading decisions
2. **ML Predictions** - Deep learning models for market prediction
3. **Self-Evolution** - MCP servers that improve themselves over time
4. **Knowledge Systems** - Graph-based reasoning and multi-LLM collaboration
5. **Shared Infrastructure** - Common databases, caches, and vector stores

The goal: **Maximize passive income through intelligent, self-improving AI systems.**

---

## Submodule Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAELUM SUPERSYSTEM                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │              PassiveIncomeMaximizer (PRIMARY)             │       │
│  │  9 LLM Agents → Committee Voting → Trade Execution        │       │
│  │  Layer 1 + Layer 2 RL + Meta-Learning CONNECTED           │       │
│  │  Ports: 5000, 5500, 5002                                  │       │
│  └──────────────────────────┬───────────────────────────────┘       │
│                             │                                        │
│              ┌──────────────┴──────────────┐                        │
│              ▼                              ▼                        │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │       finvec         │    │   caelum-unified     │               │
│  │  (ML Predictions)    │    │  (Infrastructure)    │               │
│  │  V6/V7 Features      │    │  PostgreSQL, Redis   │               │
│  │  Cluster Learning    │    │  Qdrant Vectors      │               │
│  │  Ports: 8002,18000   │    │  Port: 15432,6379    │               │
│  └──────────────────────┘    └──────────────────────┘               │
│                                                                      │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │    concept-graph     │    │ democratic-congress  │               │
│  │  (Knowledge Graphs)  │    │  (Multi-LLM Voting)  │               │
│  │  Reconstructive Mem  │    │  Heterogeneous AI    │               │
│  │  Research Project    │    │  Port: 3000,5173     │               │
│  └──────────────────────┘    └──────────────────────┘               │
│                                                                      │
│  External: caelum MCP (github.com/iodev/caelum) - orchestration     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. PassiveIncomeMaximizer (PIM)

**Purpose**: Autonomous multi-agent trading system that transforms ML predictions into real trades.

**Vision**: A self-improving trading system where 9 AI agents collaborate, learn from outcomes, and continuously optimize their decision-making through meta-learning.

### Architecture

```
Information Gatherer (scans every 5 min)
        │
        ▼
   Coordinator (Portfolio Manager)
        │
        ├── Price Analyzer (technical)
        ├── News Processor (sentiment)
        ├── Risk Manager (portfolio risk)
        └── Trend Analyzer (market trends)
        │
        ▼
Committee Voting (meta-learning weights)
        │
        ▼
Trade Execution (Alpaca/TradeStation)
```

### Key Features
- **9 LLM Agents**: Portfolio Manager, Price Analyzer, News Processor, Risk Manager, Trend Analyzer, Metrics Evaluator, Event Trigger, Web Search, Information Gatherer
- **Agent Bus**: Event-driven pub/sub for agent communication
- **Meta-Learning**: Neural network learns optimal agent weights from trade outcomes
- **Dual Frontends**: Vue3 (modern) + React (legacy)
- **Layer 2 RL Filtering**: 9 trained RL agents filter predictions by confidence

### Ports
- 5000: Express API + React
- 5500: Vue3 Dashboard
- 5002: PIM Engine (Python)

### Dependencies
- FinVec/FinColl (8002) for V7 predictions
- FinVec/SenVec (18000) for sentiment
- PostgreSQL (15432) for persistence
- Redis for caching

**CLAUDE.md**: [PassiveIncomeMaximizer/CLAUDE.md](../PassiveIncomeMaximizer/CLAUDE.md)

---

## 2. FinVec (Financial Vectors)

**Purpose**: Multi-modal financial prediction using engineered feature vectors and cluster-based learning.

**Vision**: A prediction system that learns market patterns across similar assets (clusters), not symbol-specific behaviors, enabling generalization and relative value insights.

### Architecture

```
Market Data (TradeStation/Alpaca/yfinance)
        │
        ▼
Feature Extraction (336D vectors)
├── Technical (50D): RSI, MACD, momentum
├── Sentiment (72D): SenVec from news/social
├── Sector (14D): One-hot classification
├── VWAP (5D): Multi-timeframe
├── Options + Fundamentals (~195D)
        │
        ▼
FinVec V7 Model (Transformer)
├── Cluster-based learning
├── Profit-aware training
├── Multi-horizon (1d, 5d, 20d)
        │
        ▼
Predictions + Confidence Scores
```

### Key Features
- **V6 (335D) / V7 (336D)** feature vectors
- **Cluster-Based Learning**: NOT symbol-specific
- **Profit-Aware Training**: Optimizes for trading profit, not just accuracy
- **Multi-Horizon Predictions**: 1-day, 5-day, 20-day forecasts
- **Variable Sequence Length**: 50-512 tokens with curriculum learning

### Subprojects
- **FinColl** (port 8002): V7 prediction API for PIM
- **SenVec** (port 18000): 72D sentiment feature extraction

### Critical Rule
**ALWAYS check git branch before training** - newer feature branches may exist.

**CLAUDE.md**: [finvec/CLAUDE.md](../finvec/CLAUDE.md)

---

## 3. Caelum MCP (External)

**Note**: Caelum MCP servers are managed separately at github.com/iodev/caelum

**Purpose**: Model Context Protocol servers for multi-device orchestration, self-evolution, and automation.

**Published npm Packages**: @iodev/* namespace on GitHub registry
- device-orchestration-server (2.0.3)
- analytics-metrics-server (1.0.1)
- opportunity-discovery-server (0.1.1)
- caelum-tier0-llm (1.0.0)

---

## 4. Concept-Graph

**Purpose**: Research project implementing multi-dimensional concept chains with reconstructive memory.

**Vision**: A novel approach to LLM reasoning where concepts are compressed and reconstructed from semantic building blocks, enabling efficient storage and sophisticated reasoning.

### Architecture

```
Concept Extraction (Claude API)
        │
        ▼
Compositional Compression (26%)
├── Decompose into semantic units
├── Deduplicate similar units
├── Unit registry with sharing
        │
        ▼
Hierarchical Compression (29.3% total)
├── Find similar base concepts
├── Store deltas (differences)
├── Two-level compression
        │
        ▼
Perfect Reconstruction (100%)
```

### Key Achievements (Phases 1-5)
- **26% Compositional Compression**: Semantic unit sharing
- **29.3% Total Compression**: With hierarchical delta storage
- **100% Reconstruction**: Lossless compression validated
- **48 Unit Tests**: All passing
- **Key Finding**: LLMs generate 100% unique concepts for similar problems

### Research Contributions
1. LLM concept uniqueness discovery
2. Compositional compression via semantic units
3. Hierarchical compression with deltas
4. Perfect reconstruction validation

**CLAUDE.md**: [concept-graph/CLAUDE.md](../concept-graph/CLAUDE.md)

---

## 5. Democratic-Congress

**Purpose**: Heterogeneous multi-LLM framework for democratic decision-making through deliberation and voting.

**Vision**: Enable AI agents powered by different LLM providers to collaborate democratically, combining diverse perspectives for better decisions.

### Architecture

```
┌─────────────────────────────────────────┐
│   Democratic Deliberation Session       │
├─────────────────────────────────────────┤
│  Proposal → Opinions → Rebuttals → Vote │
├─────────────────────────────────────────┤
│  Agent 1 (Claude)      │ YES  │ 85%    │
│  Agent 2 (GPT-4)       │ NO   │ 72%    │
│  Agent 3 (Llama 3.1)   │ YES  │ 68%    │
│  Agent 4 (Mistral)     │ YES  │ 91%    │
├─────────────────────────────────────────┤
│  Decision: APPROVED (75% YES)           │
└─────────────────────────────────────────┘
```

### Key Features
- **Multi-LLM Support**: Anthropic, OpenAI, Ollama, Google (planned)
- **Real-Time UI**: WebSocket-powered live conversation view
- **Cost Optimization**: Mix premium + local LLMs for 80% savings
- **Democratic Patterns**: Deliberation, voting, consensus building
- **Full-Stack TypeScript**: Express + Vue3 + Socket.IO

### LLM Providers
- **Premium**: Claude, GPT-4, Gemini
- **Local (Free)**: Ollama (Llama 3.1), Tier-0 (planned)

### Ports
- 3000: Backend API + WebSocket
- 5173: Vue3 Frontend

**CLAUDE.md**: [democratic-congress/CLAUDE.md](../democratic-congress/CLAUDE.md)

---

## 6. Supporting Submodules

### FinColl (Prediction API)
- **Purpose**: V7 model inference API
- **Port**: 8002
- **Consolidates**: Price Analyzer, News Processor, Fundamental Analyzer, Trend Analysis
- **Parent**: finvec

### SenVec (Sentiment API)
- **Purpose**: 72D sentiment feature extraction
- **Port**: 18000
- **Sources**: Twitter, Reddit, News
- **Parent**: finvec

### Caelum-Unified (Infrastructure)
- **Purpose**: Shared infrastructure
- **Services**: PostgreSQL, Redis, Qdrant
- **Status**: Planned consolidation

### OpenCode (Development Tools)
- **Purpose**: Development and automation tools
- **Status**: Development utilities

---

## Cross-Repository Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TradeStation API                                                    │
│        │                                                             │
│        ▼                                                             │
│  ┌─────────────┐                                                     │
│  │   finvec    │ Feature extraction (336D vectors)                   │
│  └──────┬──────┘                                                     │
│         │                                                            │
│    ┌────┴────┐                                                       │
│    ▼         ▼                                                       │
│  FinColl   SenVec                                                    │
│  (8002)    (18000)                                                   │
│    │         │                                                       │
│    └────┬────┘                                                       │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────┐                                         │
│  │ PassiveIncomeMaximizer  │                                         │
│  │  Information Gatherer   │ ← fetches predictions every 5 min      │
│  │  Layer 2 RL Filtering   │ ← filters by confidence                │
│  │  Layer 1 LLM Committee  │ ← deliberates and votes                │
│  │  Trade Execution        │ → sends to broker                      │
│  └───────────┬─────────────┘                                         │
│              │                                                       │
│              ▼                                                       │
│  ┌─────────────────────────┐                                         │
│  │   Alpaca/TradeStation   │ Real trades                             │
│  └─────────────────────────┘                                         │
│                                                                      │
│  ┌─────────────┐   ┌─────────────────┐                               │
│  │   caelum    │   │ caelum-unified  │                               │
│  │  MCP Orch   │   │  PostgreSQL     │                               │
│  │  Notifs     │   │  Redis, Qdrant  │                               │
│  └─────────────┘   └─────────────────┘                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### PIM ↔ FinVec
- PIM calls FinColl API (8002) for V7 predictions
- PIM calls SenVec API (18000) for sentiment features
- FinVec models trained on GPU servers (10.32.3.44, 10.32.3.62)

### PIM ↔ Caelum
- Optional MCP orchestration for multi-device coordination
- Optional external memory (MongoDB, Redis, Qdrant)
- Notifications and alerts

### Democratic-Congress ↔ Caelum (Future)
- Democratic deliberation for complex trading decisions
- Multi-LLM committee voting integrated with PIM agents
- Tier-0 LLM as local participant

### Concept-Graph ↔ PIM (Future)
- Knowledge graph for market relationships
- Concept chains for reasoning about trades
- Semantic compression for agent memory

---

## Technology Stack Summary

| Component | Backend | Frontend | Database | ML |
|-----------|---------|----------|----------|-----|
| PIM | Express (TS) + Flask (Py) | Vue3 + React | PostgreSQL | - |
| FinVec | Python (FastAPI) | - | PostgreSQL | PyTorch |
| Caelum | TypeScript (MCP) | - | MongoDB, Redis | Custom |
| Concept-Graph | Python | - | - | sentence-transformers |
| Democratic-Congress | Express (TS) | Vue3 | PostgreSQL | Multi-LLM |

---

## Future Roadmap

### Near-Term
- [ ] Connect PIM Python Engine to trading flow
- [ ] Integrate Layer 2 RL filtering
- [ ] Enable learning feedback loop
- [ ] Democratic-Congress integration with PIM

### Medium-Term
- [ ] Tier-0 LLM for local inference
- [ ] Concept-Graph for agent memory
- [ ] Self-evolution for trading strategies
- [ ] Caelum-Unified infrastructure consolidation

### Long-Term
- [ ] Fully autonomous trading system
- [ ] Self-improving prediction models
- [ ] Cross-project knowledge sharing
- [ ] Mobile device orchestration

---

**Last Updated**: 2025-11-24
