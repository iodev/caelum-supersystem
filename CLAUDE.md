# Caelum SuperSystem - Root Instructions for Claude Code

**This is the ROOT CLAUDE.md for the entire /home/rford/caelum/ss/ ecosystem**

---

## 🚨 CRITICAL CONTEXT

### GPU Infrastructure (ALWAYS REMEMBER)
- **GPU Servers**: 10.32.3.44 and 10.32.3.62
- **NO SETUP TIME NEEDED**: Both servers mount same NFS share from 10.32.3.27 at same path
- **Implication**: Code, models, data instantly available on both GPUs without copying/syncing

### Repository Structure

```
/home/rford/caelum/ss/
├── PassiveIncomeMaximizer/     # Trading system (MAIN PROJECT)
├── finvec/                     # Prediction models (V4/V5/V7)
├── caelum/                     # MCP servers & orchestration
├── caelum-unified/             # Shared infrastructure (planned)
├── fincoll/                    # V7 prediction API (subset of finvec)
├── senvec/                     # Sentiment analysis (subset of finvec)
└── concept-graph/              # Knowledge graphs
```

Each subdirectory has its own `CLAUDE.md` with specific instructions. **READ THEM IN ORDER OF RELEVANCE TO YOUR TASK.**

---

## 📚 Repository-Specific CLAUDE.md Files

### 1. PassiveIncomeMaximizer (Primary Trading System)
**Location**: `/home/rford/caelum/ss/PassiveIncomeMaximizer/CLAUDE.md`
**When to read**: Working on trading system, agent swarm, backtesting, UI
**Key topics**:
- 9-agent swarm architecture
- Information Gatherer → Coordinator → Subagents pattern
- Dual frontends (Vue3 + React)
- PIM Engine (Python) integration
- Trading operations and risk management

### 2. FinVec (Prediction Models)
**Location**: `/home/rford/caelum/ss/finvec/CLAUDE.md`
**When to read**: Working on ML models, training, predictions
**Key topics**:
- V6 (335D) and V7 (336D) feature vectors
- Cluster-based learning (NOT symbol-specific)
- Profit-aware training
- Multi-horizon predictions (1d, 5d, 20d)
- TradeStation integration and branch management

### 3. Caelum (MCP Servers)
**Location**: `/home/rford/caelum/ss/caelum/CLAUDE.md`
**When to read**: Working on MCP servers, orchestration, automation
**Key topics**:
- Self-evolution workflows
- Multi-device orchestration
- Tier-0 self-evolving LLM
- Published npm packages (@iodev namespace)
- Workflow optimization priority

### 4. FinColl (Prediction API - subset of finvec)
**Location**: `/home/rford/caelum/ss/fincoll/` (check if CLAUDE.md exists)
**When to read**: Working on FinColl API server (port 8002)

### 5. SenVec (Sentiment - subset of finvec)
**Location**: `/home/rford/caelum/ss/senvec/` (check if CLAUDE.md exists)
**When to read**: Working on sentiment analysis API (port 18000)

### 6. Caelum-Unified (Planned)
**Location**: `/home/rford/caelum/ss/caelum-unified/` (may not exist yet)
**When to read**: Working on shared infrastructure (PostgreSQL, Redis, Qdrant)

---

## 🎯 Quick Start Decision Tree

**Question 1**: What are you working on?

### → Trading System, Agents, Dashboard, Backtesting
1. Read: `PassiveIncomeMaximizer/CLAUDE.md`
2. Then: `PassiveIncomeMaximizer/GETTING_STARTED.md`
3. Then: `PassiveIncomeMaximizer/ARCHITECTURE.md`

### → ML Training, Model Development, Predictions
1. Read: `finvec/CLAUDE.md`
2. Check branch status (CRITICAL - see finvec CLAUDE.md)
3. Verify TradeStation OAuth token if training

### → MCP Servers, Automation, Orchestration
1. Read: `caelum/CLAUDE.md`
2. Review self-evolution workflows
3. Check published packages status

### → API Integration, External Services
1. Read: `PassiveIncomeMaximizer/INTEGRATIONS.md`
2. Check service availability (FinColl, SenVec)
3. Verify API keys in `.env`

### → Bug Fixing, Development Workflow
1. Read: `PassiveIncomeMaximizer/DEVELOPMENT_GUIDE.md`
2. Check testing strategy
3. Review CI/CD pipeline

---

## 🔄 Cross-Repository Dependencies

### PassiveIncomeMaximizer depends on:
- **FinVec/FinColl** (port 8002) - V7 predictions
- **FinVec/SenVec** (port 18000) - Sentiment features
- **Caelum** (optional) - MCP orchestration
- **PostgreSQL** (port 15432) - Database
- **Redis** (10.32.3.27:6379) - Cache

### FinVec provides to:
- **FinColl API** - Prediction service for PIM
- **SenVec API** - Sentiment service for PIM
- **Trained models** - Stored on NFS (10.32.3.27)

### Caelum orchestrates:
- **Multi-device workflows** across machines
- **Self-evolution** of MCP system
- **Notifications** and alerts

---

## 🛠️ Common Cross-Repository Operations

### Full System Startup

```bash
# 1. Infrastructure (Caelum-Unified)
docker start caelum-postgres
redis-cli -h 10.32.3.27 ping

# 2. FinVec Prediction Services
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server  # Port 8002

# 3. PIM Engine
cd /home/rford/caelum/ss/PassiveIncomeMaximizer/engine
source .venv/bin/activate
python pim_service.py  # Port 5002

# 4. PIM Backend + Frontend
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run dev  # Port 5000 (Express + React)
npm run vue  # Port 5500 (Vue3)
```

### Health Check All Services

```bash
# PIM
curl http://localhost:5000/api/health
curl http://localhost:5002/api/pim/status

# FinVec
curl http://localhost:8002/api/health
curl http://localhost:18000/health

# Infrastructure
redis-cli -h 10.32.3.27 ping
docker ps | grep caelum-postgres
```

### GPU Training (FinVec)

```bash
# ALWAYS check branch first (see finvec/CLAUDE.md)
cd /home/rford/caelum/ss/finvec
git branch -a
git log --oneline -5 HEAD

# Verify TradeStation token
ls -la ~/.tradestation_token.json

# Run on GPU server (10.32.3.44 or 10.32.3.62)
ssh rford@10.32.3.44
cd /home/rford/caelum/ss/finvec  # Same path, instant access!
source .venv/bin/activate
python train_production.py --symbols diversified --epochs 100
```

---

## 📋 Documentation Inventory

### PassiveIncomeMaximizer - 7 Core Docs (NEW - 2025-11-14)

Consolidated from 124 files into 7 comprehensive documents:

1. **GETTING_STARTED.md** - Setup, installation, startup, troubleshooting
2. **ARCHITECTURE.md** - System design, components, data flow, deployment
3. **AGENT_SYSTEM.md** - 9 agents, swarm mechanics, committee voting
4. **TRADING_OPERATIONS.md** - Backtesting, positions, risk, execution
5. **INTEGRATIONS.md** - FinVec, SenVec, Caelum, Alpaca, AI models
6. **DEVELOPMENT_GUIDE.md** - Dev workflow, testing, CI/CD
7. **EVOLUTION_HISTORY.md** - Phases 1-4, architectural evolution

**Archived**: `docs/archive/` contains historical docs (124 old files)

### FinVec - Extensive Documentation

- **ARCHITECTURE_OVERVIEW.md** - V6/V7 feature extraction, model design
- **TRAINING_GUIDE.md** - Production training commands
- **DATA_PROVIDERS.md** - TradeStation, yfinance, market data
- **CLAUDE.md** - Session startup checklist, branch management

### Caelum - MCP Architecture

- **ARCHITECTURE.md** - MCP server patterns
- **SELF_EVOLUTION.md** - Workflow optimization
- **PUBLISHED_PACKAGES.md** - npm package versions
- **CLAUDE.md** - Todo management, development commands

---

## 🚨 Critical Rules

### 1. Branch Management (FinVec)
- **ALWAYS** check branch status before training
- **WARN USER** if newer feature branches exist
- **NEVER** run long training without branch confirmation
- See `finvec/CLAUDE.md` for detailed checklist

### 2. GPU Access
- Both GPU servers (10.32.3.44, 10.32.3.62) have instant access to code
- No copying, no syncing needed
- Same NFS mount from 10.32.3.27

### 3. Service Dependencies
- PIM needs FinColl (8002) and SenVec (18000) running
- FinColl needs SenVec for 72D sentiment features
- Both need market data providers (TradeStation/yfinance)

### 4. Documentation
- **READ repository-specific CLAUDE.md FIRST**
- Then read detailed docs (GETTING_STARTED, ARCHITECTURE, etc.)
- Archive is reference only - use current 7 core docs

### 5. Self-Evolution (Caelum)
- ALWAYS check if Caelum supports capability before workarounds
- Propose evolution in `/self-evolution-workflows/` first
- See `caelum/CLAUDE.md` for evolution guidelines

---

## 🎓 Learning Path for New Claude Sessions

### First-Time Setup
1. Read this file (`/home/rford/caelum/ss/CLAUDE.md`)
2. Identify which repository you're working in
3. Read that repository's CLAUDE.md
4. Read GETTING_STARTED.md (if PassiveIncomeMaximizer)
5. Skim ARCHITECTURE.md for system understanding

### Ongoing Sessions
1. Check service health
2. Verify branch status (if finvec)
3. Review recent changes in git log
4. Proceed with task

---

## 📞 When in Doubt

### Questions to Ask User

1. **"Which repository/component are we working on?"**
   - PassiveIncomeMaximizer? FinVec? Caelum?

2. **"Should I check service status before starting?"**
   - Especially for PIM, FinColl, SenVec

3. **"Are we training models?"**
   - If yes, read finvec/CLAUDE.md branch checklist

4. **"Is this a new feature or bug fix?"**
   - New feature: Review architecture first
   - Bug fix: Check relevant subsystem docs

---

## 🔗 Quick Links

### Most Common Commands
```bash
# PIM Development
cd /home/rford/caelum/ss/PassiveIncomeMaximizer && npm run dev

# FinVec Training Status
cd /home/rford/caelum/ss/finvec && git branch -a

# Service Health Check
curl http://localhost:5000/api/health && \
curl http://localhost:8002/api/health && \
curl http://localhost:18000/health
```

### Port Reference
- **5000**: Express API + React (PIM)
- **5500**: Vue3 Dashboard (PIM)
- **5002**: PIM Engine (Python)
- **8002**: FinColl API (V7 predictions)
- **18000**: SenVec API (sentiment)
- **15432**: PostgreSQL
- **6379**: Redis (10.32.3.27)
- **6333**: Qdrant (10.32.3.27)

---

**Remember**: This is a multi-repository ecosystem. Each repo has specific instructions in its own CLAUDE.md. Read them in order of task relevance!

**Updated**: 2025-11-14 - PassiveIncomeMaximizer documentation consolidation complete
- using postgres credential of "pim_user" on docker container "pim-postgres" at host 10.32.3.27 port 15433
- using TRADESTATION API (Alpaca api and YFinance api are only if there is something not available on Tradestation)

## 🗳️ Democratic Agent Congress Architecture

### 7. Democratic Congress (New - Planned)
**Location**: `/home/rford/caelum/ss/democratic-congress/` (to be created)
**Purpose**: Heterogeneous multi-LLM democratic decision-making framework

**When to use**:
- Need diverse perspectives from multiple LLM providers
- Require transparent deliberation and voting
- Want cost optimization (mix expensive + local LLMs)
- Building consensus-based decision systems
- we have zero desire or need for fake/non-real data in this endeavor since we aim to characterize and learn from these characterizations of real data behaviors