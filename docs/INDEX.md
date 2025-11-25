# Caelum SuperSystem - Documentation Index

**Master index for all documentation across the ecosystem**

---

## Quick Navigation

| Need To... | Go To |
|------------|-------|
| Start a Claude session | [CLAUDE.md](../CLAUDE.md) (root) |
| Understand the ecosystem | [SUBMODULE_OVERVIEW.md](./SUBMODULE_OVERVIEW.md) |
| Set up the system | [README.md](../README.md) |
| Learn architecture | [architecture/](./architecture/) |
| Run operational tasks | [runbooks/](./runbooks/) |
| Find reference info | [reference/](./reference/) |

---

## Root Documentation

| File | Purpose | Size |
|------|---------|------|
| [CLAUDE.md](../CLAUDE.md) | AI session startup guide - read first | ~4KB |
| [README.md](../README.md) | Repository overview, quick start, setup | ~9KB |

---

## Architecture (`docs/architecture/`)

| File | Purpose |
|------|---------|
| [ECOSYSTEM_ARCHITECTURE.md](./architecture/ECOSYSTEM_ARCHITECTURE.md) | System design, component layers, data flow |
| [DEPLOYMENT_STRATEGY.md](./architecture/DEPLOYMENT_STRATEGY.md) | Deployment patterns, infrastructure, scaling |

---

## Runbooks (`docs/runbooks/`)

Operational procedures and checklists:

| File | Purpose |
|------|---------|
| [FINCOLL_RESTART_INSTRUCTIONS.md](./runbooks/FINCOLL_RESTART_INSTRUCTIONS.md) | How to restart FinColl prediction service |
| [TESTING_CHECKLIST.md](./runbooks/TESTING_CHECKLIST.md) | Pre-deployment testing checklist |

---

## Reference (`docs/reference/`)

| File | Purpose |
|------|---------|
| [LOCAL_REPOS.md](./reference/LOCAL_REPOS.md) | Local-only repositories (not in git) |
| [SUDO_ACCESS_NOTE.md](./reference/SUDO_ACCESS_NOTE.md) | Security and sudo access notes |
| [SWARM_INTELLIGENCE_ARCHITECTURE.md](./reference/SWARM_INTELLIGENCE_ARCHITECTURE.md) | Detailed swarm architecture (81KB) |
| [FINVEC_PIM_INTEGRATION_ANALYSIS.md](./reference/FINVEC_PIM_INTEGRATION_ANALYSIS.md) | Integration patterns |
| [GPU_TRAINING_STRATEGY_V4.md](./reference/GPU_TRAINING_STRATEGY_V4.md) | GPU training approach |
| [PHASE4_SELF_EVOLUTION.md](./reference/PHASE4_SELF_EVOLUTION.md) | Self-evolution architecture |

---

## Archive (`docs/archive/`)

Historical documentation - session summaries, old analyses, completed projects.

| File | Purpose |
|------|---------|
| [CAELUM_CONSOLIDATION_ANALYSIS.md](./archive/CAELUM_CONSOLIDATION_ANALYSIS.md) | Caelum consolidation analysis |
| [FINVEC_CONSOLIDATION_ANALYSIS.md](./archive/FINVEC_CONSOLIDATION_ANALYSIS.md) | FinVec consolidation analysis |
| SESSION_*.md files | Historical session summaries |

---

## Submodule Documentation

Each submodule has its own CLAUDE.md with specific instructions:

| Submodule | CLAUDE.md | Purpose |
|-----------|-----------|---------|
| **PassiveIncomeMaximizer** | [CLAUDE.md](../PassiveIncomeMaximizer/CLAUDE.md) | Trading system, 9-agent swarm, dual frontends |
| **finvec** | [CLAUDE.md](../finvec/CLAUDE.md) | ML models, V6/V7 features, training, branch management |
| **caelum** | [CLAUDE.md](../caelum/CLAUDE.md) | MCP servers, self-evolution, orchestration |
| **concept-graph** | [CLAUDE.md](../concept-graph/CLAUDE.md) | Knowledge graphs, reconstructive memory |
| **democratic-congress** | [CLAUDE.md](../democratic-congress/CLAUDE.md) | Multi-LLM voting, consensus building |
| **fincoll** | (check submodule) | V7 prediction API |
| **senvec** | [CLAUDE.md](../senvec/CLAUDE.md) | Sentiment analysis API (72D features) |
| **caelum-unified** | (check submodule) | Shared infrastructure |
| **opencode** | (check submodule) | Development tools |

**For detailed submodule vision and interconnections, see [SUBMODULE_OVERVIEW.md](./SUBMODULE_OVERVIEW.md)**

---

## Configuration Files (`config/`)

| File | Purpose |
|------|---------|
| [docker-compose.ecosystem.yml](../config/docker-compose.ecosystem.yml) | Full ecosystem Docker setup |
| [pm2-ecosystem.config.js](../config/pm2-ecosystem.config.js) | PM2 process management |
| [ecosystem_27.config.js](../config/ecosystem_27.config.js) | Server 10.32.3.27 config |

---

## Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| [health-monitor.sh](../scripts/health-monitor.sh) | Service health monitoring |
| [setup-auto-start.sh](../scripts/setup-auto-start.sh) | Auto-start configuration |
| [setup-weekly-backups.sh](../scripts/setup-weekly-backups.sh) | Backup automation |
| [verify-nfs-setup.sh](../scripts/verify-nfs-setup.sh) | NFS mount verification |
| [LAUNCH_PARALLEL_SESSIONS.sh](../scripts/LAUNCH_PARALLEL_SESSIONS.sh) | Multi-session launcher |
| [secondary-node/](../scripts/secondary-node/) | Secondary node MCP scripts |

---

## Port Reference (Quick Lookup)

| Port | Service | Submodule |
|------|---------|-----------|
| 5000 | Express API + React | PassiveIncomeMaximizer |
| 5500 | Vue3 Dashboard | PassiveIncomeMaximizer |
| 5002 | PIM Engine (Python) | PassiveIncomeMaximizer |
| 8002 | FinColl API (V7 predictions) | finvec/fincoll |
| 18000 | SenVec API (sentiment) | finvec/senvec |
| 3000 | Democratic Congress Backend | democratic-congress |
| 5173 | Democratic Congress Frontend | democratic-congress |
| 15432/15433 | PostgreSQL | infrastructure |
| 6379 | Redis | 10.32.3.27 |
| 6333 | Qdrant | 10.32.3.27 |
| 11434 | Ollama (local LLMs) | infrastructure |

---

## Infrastructure Reference

### GPU Servers
- **10.32.3.44** - Training server 1 (NFS mount)
- **10.32.3.62** - Training server 2 (NFS mount)
- **10.32.3.27** - NFS storage server, Redis, Qdrant

### Database Credentials
- PostgreSQL: `pim_user` on container `pim-postgres` at 10.32.3.27:15433
- Redis: 10.32.3.27:6379 (no auth)
- Qdrant: 10.32.3.27:6333 (no auth)

### Data Sources (Priority Order)
1. TradeStation API (primary)
2. Alpaca API (fallback)
3. yfinance (last resort)

---

**Last Updated**: 2025-11-24
