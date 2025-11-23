# Shared Documentation Library - Proposal

## Problem
- 5 separate git repos (PIM, FinColl, FinVec, SenVec, caelum-unified)
- Each has its own `docs/` directory
- No central place to find ecosystem-level documentation
- New docs (auto-start, health monitoring) scattered across directories

## Current Structure
```
/home/rford/caelum/ss/           (NOT a git repo)
├── PassiveIncomeMaximizer/      (GIT REPO - 50+ docs)
├── fincoll/                     (GIT REPO)
├── finvec/                      (GIT REPO)
├── senvec/                      (GIT REPO)
└── caelum-unified/              (GIT REPO)
```

---

## Recommended Solution: **pim-ecosystem** Repo

Create a new git repo that serves as the **ecosystem orchestrator**:

```
/home/rford/caelum/ss/
├── pim-ecosystem/               ← NEW git repo
│   ├── README.md               ← Ecosystem overview
│   ├── docs/                   ← Shared ecosystem docs
│   │   ├── architecture/
│   │   │   ├── SYSTEM_OVERVIEW.md
│   │   │   └── COMPONENT_INTERACTIONS.md
│   │   ├── deployment/
│   │   │   ├── AUTO_START_SETUP.md        ← Move here
│   │   │   ├── HEALTH_MONITORING.md
│   │   │   └── DOCKER_COMPOSE_GUIDE.md
│   │   ├── operations/
│   │   │   ├── POSITION_RECOVERY.md
│   │   │   └── EMERGENCY_PROCEDURES.md
│   │   └── development/
│   │       └── CONTRIBUTION_GUIDE.md
│   │
│   ├── scripts/                ← Shared scripts
│   │   ├── pm2-ecosystem.config.js    ← Move here
│   │   ├── health-monitor.sh          ← Move here
│   │   ├── setup-auto-start.sh        ← Move here
│   │   └── start-all-services.sh
│   │
│   ├── docker-compose.ecosystem.yml   ← Move here
│   │
│   ├── components/             ← Git submodules
│   │   ├── PassiveIncomeMaximizer/    (submodule)
│   │   ├── fincoll/                   (submodule)
│   │   ├── finvec/                    (submodule)
│   │   ├── senvec/                    (submodule)
│   │   └── caelum-unified/            (submodule)
│   │
│   └── .github/
│       └── workflows/
│           └── test-ecosystem.yml
```

### Why This Works:

1. **Single Entry Point**: `git clone pim-ecosystem` gets everything
2. **Independent Components**: Each component repo stays independent
3. **Shared Docs**: Ecosystem-level docs in one place
4. **Orchestration**: Scripts and configs for entire system
5. **Easy Discovery**: New team members clone one repo

---

## Implementation Steps

### Step 1: Create Ecosystem Repo
```bash
cd /home/rford/caelum/ss
mkdir pim-ecosystem
cd pim-ecosystem
git init
```

### Step 2: Add Component Repos as Submodules
```bash
git submodule add ./PassiveIncomeMaximizer components/PassiveIncomeMaximizer
git submodule add ./fincoll components/fincoll
git submodule add ./finvec components/finvec
git submodule add ./senvec components/senvec
git submodule add ./caelum-unified components/caelum-unified
```

### Step 3: Create Shared Docs Structure
```bash
mkdir -p docs/{architecture,deployment,operations,development}
mkdir -p scripts
```

### Step 4: Move Ecosystem-Level Files
```bash
# Move PM2 config and scripts
mv ../pm2-ecosystem.config.js scripts/
mv ../health-monitor.sh scripts/
mv ../setup-auto-start.sh scripts/

# Move ecosystem docs
mv ../AUTO_START_SETUP.md docs/deployment/

# Move docker-compose
mv ../docker-compose.ecosystem.yml .
```

### Step 5: Create Documentation Index
Create `docs/README.md` as a central index pointing to all docs.

### Step 6: Link Component Docs
Create symlinks or a documentation aggregator:
```bash
ln -s ../components/PassiveIncomeMaximizer/docs docs/pim
ln -s ../components/fincoll/docs docs/fincoll
ln -s ../components/finvec/docs docs/finvec
ln -s ../components/senvec/docs docs/senvec
```

---

## Alternative: Simpler Approach (No Git Submodules)

If submodules are too complex, just create shared docs at `/home/rford/caelum/ss/docs/`:

```
/home/rford/caelum/ss/
├── docs/                        ← NEW shared docs (not in git)
│   ├── ECOSYSTEM_OVERVIEW.md
│   ├── deployment/
│   │   └── AUTO_START_SETUP.md
│   ├── operations/
│   │   └── HEALTH_MONITORING.md
│   └── components/              ← Symlinks
│       ├── pim -> ../PassiveIncomeMaximizer/docs
│       ├── fincoll -> ../fincoll/docs
│       ├── finvec -> ../finvec/docs
│       └── senvec -> ../senvec/docs
│
├── scripts/                     ← Shared scripts
│   ├── pm2-ecosystem.config.js
│   ├── health-monitor.sh
│   └── setup-auto-start.sh
│
├── PassiveIncomeMaximizer/      (keep as-is)
├── fincoll/                     (keep as-is)
├── finvec/                      (keep as-is)
└── senvec/                      (keep as-is)
```

**Pros**: Simple, no git complexity
**Cons**: Shared docs not version controlled

---

## Recommended Doc Categories

### Ecosystem-Level (`pim-ecosystem/docs/`)
- Architecture overviews
- Deployment guides
- Operations runbooks
- Auto-start setup
- Health monitoring
- Position recovery
- Emergency procedures

### Component-Level (stays in each repo)
- Component-specific architecture
- API documentation
- Development guides
- Testing guides

---

## My Recommendation

**Go with the pim-ecosystem repo** because:
1. ✅ Everything version controlled
2. ✅ Single `git clone` gets entire system
3. ✅ Components stay independent
4. ✅ Clear separation: ecosystem vs component docs
5. ✅ Easy to onboard new developers
6. ✅ CI/CD can test entire system together

**Trade-off**: Submodules add complexity, but it's worth it for this system.

---

## Quick Start Command

```bash
# Create ecosystem repo
cd /home/rford/caelum/ss
mkdir pim-ecosystem && cd pim-ecosystem
git init

# Create structure
mkdir -p docs/{architecture,deployment,operations,development}
mkdir -p scripts components

# Add submodules (relative paths)
git submodule add ../PassiveIncomeMaximizer components/pim
git submodule add ../fincoll components/fincoll
git submodule add ../finvec components/finvec
git submodule add ../senvec components/senvec

# Move ecosystem files
mv ../pm2-ecosystem.config.js scripts/
mv ../AUTO_START_SETUP.md docs/deployment/

# Commit
git add .
git commit -m "Initial pim-ecosystem structure"
```

---

## For New Developers

With ecosystem repo:
```bash
# Clone entire system
git clone <pim-ecosystem-url>
cd pim-ecosystem

# Initialize submodules
git submodule update --init --recursive

# All docs available
ls docs/                    # Ecosystem docs
ls components/pim/docs/     # PIM docs
ls components/fincoll/docs/ # FinColl docs

# Start everything
./scripts/setup-auto-start.sh
```

Without ecosystem repo (current):
```bash
# Clone 5 separate repos
git clone <pim-url>
git clone <fincoll-url>
git clone <finvec-url>
git clone <senvec-url>
git clone <caelum-unified-url>

# Hunt for docs in each repo
# No clear starting point
```
