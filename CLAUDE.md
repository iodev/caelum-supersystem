# Caelum SuperSystem - Claude Code Guide

**Streamlined session guide for AI assistants. For detailed docs, see [docs/INDEX.md](./docs/INDEX.md)**

---

## Quick Context

This is a **meta-repository** containing 8 interconnected AI/ML projects for autonomous trading and development.

**Critical Infrastructure**:
- **GPU Servers**: 10.32.3.44 and 10.32.3.62 (both mount NFS from 10.32.3.27 - instant code access)
- **Database**: PostgreSQL at 10.32.3.27:15433 (user: `pim_user`, container: `pim-postgres`)
- **Cache**: Redis at 10.32.3.27:6379, Qdrant at 10.32.3.27:6333
- **Data Source**: TradeStation API (primary), Alpaca (fallback), yfinance (last resort)

---

## Submodule Quick Reference

| Submodule | Purpose | Ports | CLAUDE.md |
|-----------|---------|-------|-----------|
| **PassiveIncomeMaximizer** | 9-agent trading system (PRIMARY) | 5000, 5500, 5002 | [Link](./PassiveIncomeMaximizer/CLAUDE.md) |
| **finvec** | ML predictions (V6/V7) | 8002, 18000 | [Link](./finvec/CLAUDE.md) |
| **concept-graph** | Knowledge graphs, compression | - | [Link](./concept-graph/CLAUDE.md) |
| **democratic-congress** | Multi-LLM voting | 3000, 5173 | [Link](./democratic-congress/CLAUDE.md) |
| fincoll | V7 prediction API | 8002 | (subset of finvec) |
| senvec | Sentiment API | 18000 | (subset of finvec) |
| caelum-unified | Shared infrastructure | 15432 | (check submodule) |
| opencode | Dev tools | - | (check submodule) |

**Note**: `caelum` MCP servers managed separately at github.com/iodev/caelum

**For vision and interconnections**: [docs/SUBMODULE_OVERVIEW.md](./docs/SUBMODULE_OVERVIEW.md)

---

## Decision Tree: What Are You Working On?

### Trading System, Agents, Dashboard
1. Read: [PassiveIncomeMaximizer/CLAUDE.md](./PassiveIncomeMaximizer/CLAUDE.md)
2. Then: PassiveIncomeMaximizer/GETTING_STARTED.md
3. Ports: 5000 (Express+React), 5500 (Vue3), 5002 (PIM Engine)

### ML Training, Predictions, Models
1. Read: [finvec/CLAUDE.md](./finvec/CLAUDE.md)
2. **CRITICAL**: Check branch before training: `git branch -a`
3. Verify TradeStation token: `ls -la ~/.tradestation_token.json`
4. Train on GPU: `ssh rford@10.32.3.44`

### MCP Servers, Orchestration, Automation
1. Caelum MCP managed separately: github.com/iodev/caelum
2. Published packages: @iodev/* on npm

### Knowledge Graphs, Concept Chains
1. Read: [concept-graph/CLAUDE.md](./concept-graph/CLAUDE.md)
2. Current: Phases 1-5 complete (29.3% compression)
3. Start with: concept-chains/NEXT_SESSION.md

### Multi-LLM Voting, Consensus
1. Read: [democratic-congress/CLAUDE.md](./democratic-congress/CLAUDE.md)
2. Full-stack TypeScript (Express + Vue3)
3. Ports: 3000 (backend), 5173 (frontend)

---

## Quick Health Check

```bash
# All services
curl -s http://localhost:5000/api/health   # PIM Express
curl -s http://localhost:5002/api/pim/status  # PIM Engine
curl -s http://localhost:8002/health       # FinColl (NOTE: /health, not /api/health)
curl -s http://localhost:18000/health      # SenVec

# Infrastructure
redis-cli -h 10.32.3.27 ping
docker ps | grep pim-postgres
```

---

## Quick Start Commands

```bash
# PIM Development (most common)
cd PassiveIncomeMaximizer && npm run dev  # Port 5000

# FinVec Training
cd finvec && git branch -a  # Check branch first!
source .venv/bin/activate
python train_production.py --symbols diversified --epochs 100

# Full System Startup
docker start pim-postgres
cd finvec && source .venv/bin/activate && python -m fincoll.api.server &
cd ../PassiveIncomeMaximizer/engine && source .venv/bin/activate && python pim_service.py &
cd .. && npm run dev
```

---

## Cross-Repository Dependencies

```
PassiveIncomeMaximizer (PRIMARY - all roads lead here)
    ├── requires: FinColl (8002), SenVec (18000)
    ├── requires: PostgreSQL (15433), Redis (6379)
    ├── integration: Layer 1 (PIM Engine) + Layer 2 (RL) CONNECTED
    └── learning: Meta-learner feedback loop ACTIVE

FinVec/FinColl
    ├── requires: SenVec for 72D sentiment
    ├── requires: TradeStation/yfinance for data
    └── provides: V7 predictions to PIM

caelum-unified
    └── provides: Shared PostgreSQL, Redis, Qdrant
```

---

## Critical Rules

1. **FinVec Branch Check**: ALWAYS verify branch before training
2. **GPU Access**: Same NFS path on both servers - no copying needed
3. **Service Order**: Infrastructure → FinColl/SenVec → PIM Engine → Express → Frontend
4. **Graceful Degradation**: System works without optional services (reduced features)
5. **Submodule CLAUDE.md**: Read the relevant one for your task

---

## Documentation Structure

```
caelum-supersystem/
├── CLAUDE.md          ← You are here (quick guide)
├── README.md          ← Setup and overview
├── config/            ← Docker, PM2 configs
├── scripts/           ← Shell scripts
├── docs/
│   ├── INDEX.md       ← Master documentation index
│   ├── SUBMODULE_OVERVIEW.md  ← Vision & interconnections
│   ├── architecture/  ← System design docs
│   ├── runbooks/      ← Operational procedures
│   ├── reference/     ← Technical reference
│   └── archive/       ← Historical docs
└── [submodules]/      ← Each has own CLAUDE.md
```

**Full documentation index**: [docs/INDEX.md](./docs/INDEX.md)

---

## Port Quick Reference

| Port | Service |
|------|---------|
| 5000 | PIM Express + React |
| 5500 | PIM Vue3 |
| 5002 | PIM Engine |
| 8002 | FinColl API |
| 18000 | SenVec API |
| 3000 | Democratic Congress Backend |
| 5173 | Democratic Congress Frontend |
| 15433 | PostgreSQL |
| 6379 | Redis |
| 6333 | Qdrant |

---

**Updated**: 2025-11-24
