# Caelum SuperSystem

Meta repository for the complete Caelum AI trading and development ecosystem.

## Components

- **PassiveIncomeMaximizer** - Multi-agent autonomous trading system with 9 LLM agents
- **finvec** - ML prediction models (V6/V7 feature vectors, cluster-based learning)
- **caelum** - MCP servers & orchestration, self-evolution workflows
- **caelum-unified** - Shared infrastructure (PostgreSQL, Redis, Qdrant)
- **fincoll** - V7 prediction API (subset of finvec)
- **senvec** - Sentiment analysis API (subset of finvec)
- **concept-graph** - Knowledge graphs
- **democratic-congress** - Heterogeneous multi-LLM decision framework
- **opencode** - Development tools

**Note**: caelum-cli is local-only (no remote), not included as submodule

## Quick Start

```bash
# Clone with all submodules
git clone --recursive https://github.com/iodev/caelum-supersystem.git
cd caelum-supersystem

# Or if already cloned, initialize submodules
git submodule update --init --recursive

# Update all submodules to latest
git submodule update --remote
```

## Structure

```
caelum-supersystem/
├── PassiveIncomeMaximizer/  (submodule → github.com/iodev/Passive-Income-Maximizer)
├── finvec/                  (submodule → github.com/iodev/finvec)
├── caelum/                  (submodule → github.com/iodev/caelum)
├── caelum-unified/          (submodule → github.com/iodev/caelum-unified)
├── fincoll/                 (submodule → github.com/iodev/fincoll)
├── senvec/                  (submodule → github.com/iodev/senvec)
├── concept-graph/           (submodule → github.com/iodev/concept-graph)
├── democratic-congress/     (submodule → github.com/iodev/democratic-congress)
└── opencode/                (submodule → github.com/iodev/opencode)
```

## Benefits

✅ Each project remains independent with its own git history
✅ Each can push to its own remote repository
✅ One command to clone entire ecosystem
✅ Easy to track versions of each component
✅ Can pin specific versions of dependencies
✅ Centralized documentation and workflow coordination

## Working with Submodules

### Clone specific component
```bash
# Clone entire system
git clone --recursive https://github.com/iodev/caelum-supersystem.git

# Work in specific component
cd PassiveIncomeMaximizer
git checkout -b feature/my-feature
# ... make changes ...
git commit -m "feat: add feature"
git push origin feature/my-feature

# Update meta-repo to track new commit
cd ..
git add PassiveIncomeMaximizer
git commit -m "chore: update PassiveIncomeMaximizer to latest"
git push
```

### Update all submodules to latest
```bash
git submodule update --remote --merge
git commit -am "chore: update all submodules to latest"
git push
```

### Pull latest from meta-repo
```bash
git pull
git submodule update --init --recursive
```

## Component Details

### PassiveIncomeMaximizer
**Tech**: TypeScript (Express + Vue3/React), Python (Flask + PIM Engine)
**Ports**: 5000 (Express), 5500 (Vue3), 5002 (PIM Engine)
**Purpose**: Multi-agent trading system with self-evolution feedback loop

### finvec
**Tech**: Python (PyTorch, scikit-learn)
**Purpose**: V6 (335D) and V7 (336D) feature extraction, cluster-based learning, profit-aware training
**Deployed**: FinColl API (8002), SenVec API (18000)

### caelum
**Tech**: TypeScript (MCP servers)
**Purpose**: Multi-device orchestration, self-evolution workflows, automation
**Published**: @iodev/* npm packages

### caelum-unified
**Tech**: Docker, PostgreSQL, Redis, Qdrant
**Purpose**: Shared infrastructure across all components

### fincoll
**Tech**: Python (FastAPI)
**Port**: 8002
**Purpose**: V7 model inference API for PassiveIncomeMaximizer

### senvec
**Tech**: Python (FastAPI)
**Port**: 18000
**Purpose**: 72D sentiment feature extraction (Twitter, Reddit, News)

### concept-graph
**Tech**: Python (NetworkX, Neo4j)
**Purpose**: Knowledge graph construction and reasoning

### democratic-congress
**Tech**: Python (multi-LLM)
**Purpose**: Heterogeneous LLM voting and consensus building

### opencode
**Tech**: TypeScript
**Purpose**: Development and automation tools

## Documentation

Each submodule has its own CLAUDE.md with specific instructions:

- `/PassiveIncomeMaximizer/CLAUDE.md` - Trading system, 9 agents, dual frontends
- `/finvec/CLAUDE.md` - ML models, training, branch management, TradeStation
- `/caelum/CLAUDE.md` - MCP servers, self-evolution, published packages

**Root instructions**: `/home/rford/caelum/ss/CLAUDE.md` (symlinked or copied here)

## Infrastructure

### Databases
- **PostgreSQL** (port 15432) - PIM database
- **Redis** (10.32.3.27:6379) - Cache
- **Qdrant** (10.32.3.27:6333) - Vector store

### GPU Servers
- **10.32.3.44** - Training server 1 (NFS mount)
- **10.32.3.62** - Training server 2 (NFS mount)
- **10.32.3.27** - NFS storage server

### Port Reference
- 5000 - Express API + React (PIM)
- 5500 - Vue3 Dashboard (PIM)
- 5002 - PIM Engine (Python)
- 8002 - FinColl API (V7 predictions)
- 18000 - SenVec API (sentiment)
- 15432 - PostgreSQL (Docker)
- 6379 - Redis
- 6333 - Qdrant

## Development Workflow

### Full System Startup
```bash
# 1. Infrastructure
docker start caelum-postgres
redis-cli -h 10.32.3.27 ping

# 2. Prediction Services
cd finvec
source .venv/bin/activate
python -m fincoll.api.server  # Port 8002 (terminal 1)
python -m senvec.api.server   # Port 18000 (terminal 2)

# 3. PIM Engine
cd ../PassiveIncomeMaximizer/engine
source .venv/bin/activate
python pim_service.py  # Port 5002 (terminal 3)

# 4. PIM Backend + Frontends
cd ..
npm run dev  # Port 5000 - Express + React (terminal 4)
npm run vue  # Port 5500 - Vue3 (terminal 5)
```

### Health Check All Services
```bash
curl http://localhost:5000/api/health   # PIM Express
curl http://localhost:5002/api/pim/status  # PIM Engine
curl http://localhost:8002/api/health   # FinColl
curl http://localhost:18000/health      # SenVec
redis-cli -h 10.32.3.27 ping           # Redis
docker ps | grep caelum-postgres        # PostgreSQL
```

### GPU Training (FinVec)
```bash
# On local machine or SSH to GPU
ssh rford@10.32.3.44

# IMPORTANT: Check branch first (see finvec/CLAUDE.md)
cd /home/rford/caelum/ss/finvec
git branch -a
git log --oneline -5 HEAD

# Verify TradeStation token
ls -la ~/.tradestation_token.json

# Run training
source .venv/bin/activate
python train_production.py --symbols diversified --epochs 100
```

## Maintenance

### Update Submodule to Specific Commit
```bash
cd PassiveIncomeMaximizer
git checkout main
git pull
cd ..
git add PassiveIncomeMaximizer
git commit -m "chore: update PIM to commit abc123"
git push
```

### Revert Submodule to Earlier Version
```bash
cd PassiveIncomeMaximizer
git checkout <commit-hash>
cd ..
git add PassiveIncomeMaximizer
git commit -m "chore: revert PIM to stable version"
git push
```

### Check Status of All Submodules
```bash
git submodule status
```

### Remove Submodule (if needed)
```bash
git submodule deinit -f <path>
rm -rf .git/modules/<path>
git rm -f <path>
```

## License

Each component has its own license. See individual repositories for details.

## Contact

Repository maintained by Roderick Ford (iodev)

---

**Created**: 2025-11-21
**Purpose**: Unified tracking and deployment of Caelum AI ecosystem
