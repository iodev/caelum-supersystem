# Documentation Organization & System Cleanup Plan
**Date**: 2025-11-13
**Status**: URGENT - Action Required Before Further Development

---

## 🚨 **Current Crisis**

### Documentation Chaos
- **325+ markdown files in finvec/** alone
- **106 root-level MD files** in finvec (should be organized into directories)
- **91 files reference old V2-V5** versions (likely obsolete)
- **27 files in fincoll-v7/** (redundant with finvec?)
- **Multiple conflicting roadmaps and status documents**

### System Boundary Confusion
Two separate systems being developed but boundaries unclear:
1. **FinVec Ecosystem** (Financial ML Trading System)
2. **Caelum Infrastructure** (Distributed AI Platform)

### Problems This Causes
- ❌ **Every Claude session** spends hours relearning architecture
- ❌ **Old artifacts** get reused incorrectly (V2-V5 code contaminating V7)
- ❌ **Conflicting information** across documents
- ❌ **No single source of truth** for system status
- ❌ **Memory limitations** overwhelmed by doc volume
- ❌ **Lost context** between sessions

---

## 🎯 **The Two Systems**

### System 1: FinVec Ecosystem (Financial ML)

**Purpose**: Profit-aware financial prediction and automated trading

**Components**:
```
finvec/                  # Core ML model (V7: 336D features)
├─ models/              # Transformer architecture
├─ training/            # Profit-aware training
├─ data/                # Data pipelines
└─ pim/                 # Trading agents (NEW - Layer 4 just completed)

fincoll-v7/             # Feature extraction (336D vectors)
├─ Technical indicators (50D)
├─ SenVec integration (72D)
├─ Sector classification (14D)
├─ VWAP multi-timeframe (5D)
├─ Options flow (~20D)
└─ Fundamentals (~20D)

senvec/                 # Sentiment/visibility features (72D)

PassiveIncomeMaximizer/ # PIM trading agent system
├─ agents/              # Multi-agent committee (Technical, Sentiment, V7)
├─ committee.py         # Meta-learning vote aggregation
└─ training/            # PPO trainer for agents
```

**Current Status**:
- ✅ V7 model trained (200 epochs, 107.8M params)
- ✅ FinColl-V7 API running (port 8002)
- ✅ Layer 4 complete: Multi-agent committee with meta-learning
- ⏳ Backtesting needed
- ⏳ Paper trading not started
- ⏳ Live trading not started

### System 2: Caelum Infrastructure (Distributed AI)

**Purpose**: Distributed AI development platform with LLM orchestration

**Components**:
```
caelum/                 # Original infrastructure
caelum-unified/         # MCP unified interface
├─ TCP Server: port 8090
├─ WebSocket: port 8091
├─ Web UI: port 8082
└─ Services: Business intel, code analysis, workflows

caelum-cli/             # CLI tools for cluster management
```

**Current Status**:
- ✅ MCP server running (10.32.3.27:8090)
- ✅ Web interface operational (port 8082)
- ✅ Phase 1 complete: Unified interface
- 🚧 Phase 2 in progress: Service swarm architecture
- ⏳ Phase 3 planned: Intelligence distribution
- ⏳ Phase 4 planned: Autonomous evolution

**Integration Point**:
- Caelum was supposed to help FinVec with distributed training
- Currently minimal integration between the two systems

---

## 📋 **Organization Strategy**

### Phase 1: Consolidate Critical Documentation (Week 1)

**Goal**: Create single source of truth for each system

#### For FinVec Ecosystem:

Create `/home/rford/caelum/ss/finvec/docs/00-START-HERE/` with:

1. **`SYSTEM_OVERVIEW.md`** - What FinVec is, current V7 status
2. **`ARCHITECTURE.md`** - Technical architecture (consolidate from 5+ existing)
3. **`CURRENT_STATUS.md`** - What's working, what's not (updated weekly)
4. **`NEXT_STEPS.md`** - Clear priorities (backtesting, paper trading, live)
5. **`SESSION_GUIDE.md`** - Quick reference for new Claude sessions

#### For Caelum Infrastructure:

Create `/home/rford/caelum/ss/caelum-unified/docs/00-START-HERE/` with:

1. **`SYSTEM_OVERVIEW.md`** - What Caelum is, MCP architecture
2. **`DEPLOYMENT_STATUS.md`** - Running services, ports, health
3. **`INTEGRATION_WITH_FINVEC.md`** - How the two systems collaborate
4. **`SERVICE_CATALOG.md`** - Available MCP tools and services
5. **`DEVELOPMENT_ROADMAP.md`** - Phase 2-4 plans

### Phase 2: Reorganize Existing Documentation (Week 1-2)

Create proper directory structure:

```
finvec/
├─ docs/
│  ├─ 00-START-HERE/           # Essential reading (5 files max)
│  ├─ architecture/            # Design docs
│  ├─ research/                # Experiments and analysis
│  ├─ roadmaps/                # Project planning
│  ├─ historical/              # Old versions (V2-V6)
│  │  ├─ v2/
│  │  ├─ v3/
│  │  ├─ v4/
│  │  ├─ v5/
│  │  └─ v6/
│  └─ obsolete/                # Deprecated docs (archive, don't delete)
```

**Move 106 root-level MD files** into appropriate directories

### Phase 3: Identify and Archive Obsolete Content (Week 2)

**Criteria for "obsolete"**:
- References V2-V5 models (91 files identified)
- Contradicts current V7 architecture
- Superseded by newer documents
- No longer relevant to current development

**Action**: Move to `docs/obsolete/` or `docs/historical/v{X}/`
**Do NOT delete** - may contain useful historical context

### Phase 4: Knowledge Base Integration (Week 2-3)

**Option A: Use Caelum-Unified MCP for Document Storage**

Create new MCP resource endpoints:
- `/finvec/architecture` - Core architecture docs
- `/finvec/status` - Current status
- `/finvec/guides` - How-to guides
- `/caelum/architecture` - Caelum infrastructure
- `/caelum/services` - Service catalog

**Option B: Create Structured Knowledge Database**

Use PostgreSQL + vector embeddings:
- Index all current documentation
- Semantic search across all docs
- Version tracking
- Query interface via MCP

**Option C: Hybrid Approach (RECOMMENDED)**

1. **Critical docs** → `/docs/00-START-HERE/` (always read)
2. **Architecture** → Caelum MCP resources (searchable)
3. **Historical** → Organized archives (reference only)

### Phase 5: Continuous Maintenance (Ongoing)

**Rules**:
1. **No new root-level MD files** - must go in proper directory
2. **Update CURRENT_STATUS.md after each milestone**
3. **Archive superseded documents** - don't leave duplicates
4. **Weekly cleanup** - move misplaced docs to proper locations
5. **Session guide** - update after major architecture changes

---

## 🔧 **Implementation Checklist**

### Week 1: Critical Consolidation
- [ ] Create `finvec/docs/00-START-HERE/` directory
- [ ] Write SYSTEM_OVERVIEW.md (consolidate from existing)
- [ ] Write ARCHITECTURE.md (V7 current state)
- [ ] Write CURRENT_STATUS.md (Layer 4 complete, what's next)
- [ ] Write NEXT_STEPS.md (backtesting, paper trading, live)
- [ ] Write SESSION_GUIDE.md (quick reference for Claude)
- [ ] Create `caelum-unified/docs/00-START-HERE/` directory
- [ ] Write Caelum system overview docs (5 files)

### Week 2: Reorganization
- [ ] Create new directory structure in `finvec/docs/`
- [ ] Categorize all 106 root-level MD files
- [ ] Move files to appropriate directories
- [ ] Create `docs/historical/v2-v6/` archives
- [ ] Move 91 old-version docs to historical archives
- [ ] Create index files for each directory
- [ ] Update all internal links

### Week 3: Knowledge Base
- [ ] Design Caelum MCP document storage schema
- [ ] Implement MCP resource endpoints
- [ ] Index critical documentation
- [ ] Create query interface
- [ ] Test retrieval from Claude sessions
- [ ] Document how to use knowledge base

### Ongoing: Maintenance
- [ ] Add pre-commit hook: reject root-level MD files
- [ ] Weekly status update to CURRENT_STATUS.md
- [ ] Monthly archive sweep: obsolete → historical/
- [ ] Update SESSION_GUIDE.md after major changes

---

## 📊 **Success Metrics**

### Short-term (2 weeks)
- ✅ New Claude session can understand system in <5 minutes (read 00-START-HERE/)
- ✅ Zero root-level MD files (all organized)
- ✅ All V2-V6 docs archived separately
- ✅ Single source of truth for current status

### Medium-term (1 month)
- ✅ Caelum MCP knowledge base operational
- ✅ Semantic search across all documentation
- ✅ Zero conflicting/contradictory docs
- ✅ Clear system boundaries maintained

### Long-term (3 months)
- ✅ Auto-updating status from CI/CD
- ✅ Version-controlled knowledge base
- ✅ Historical analysis: "How did we solve X in V5?"
- ✅ Zero documentation-related confusion in sessions

---

## 🚀 **Immediate Actions (DO FIRST)**

Before any more FinVec/PIM development:

1. **STOP** creating new documentation at root level
2. **CREATE** the 00-START-HERE directories
3. **WRITE** the 5 critical FinVec docs (SYSTEM_OVERVIEW, ARCHITECTURE, CURRENT_STATUS, NEXT_STEPS, SESSION_GUIDE)
4. **MOVE** PROJECT_STATUS.md into 00-START-HERE/
5. **TEST** - Start fresh Claude session and see if it can understand the system from START-HERE docs alone

**Success = New session productive in <10 minutes instead of hours**

---

## 📝 **Document Content Guidelines**

### SYSTEM_OVERVIEW.md should answer:
- What is this system for?
- What problem does it solve?
- What's the current version/status?
- Where is it deployed?
- Who uses it?

### ARCHITECTURE.md should answer:
- What are the major components?
- How do they interact?
- What are the data flows?
- What are the key design decisions?
- Why this architecture?

### CURRENT_STATUS.md should answer:
- What's working? (with versions and metrics)
- What's broken? (with severity)
- What's in progress?
- What's the last completed milestone?
- What's blocking progress?

### NEXT_STEPS.md should answer:
- What are the top 3 priorities?
- What's the estimated timeline?
- What are the dependencies?
- What are the success criteria?
- Who needs to do what?

### SESSION_GUIDE.md should answer:
- What should I read first?
- Where is the code I'll work on?
- What are the common tasks?
- What are the gotchas?
- Where do I find X?

---

## 🔗 **System Integration Clarification**

### How FinVec and Caelum Should Collaborate:

**Caelum provides to FinVec**:
1. Distributed training across LAN nodes
2. MCP tools for business intelligence
3. Workflow orchestration for complex tasks
4. Document storage and retrieval
5. Cluster resource management

**FinVec provides to Caelum**:
1. Real-world use case for service swarm
2. Test bed for distributed AI patterns
3. Financial domain knowledge
4. Performance optimization requirements
5. Autonomous evolution test cases

**Current Integration**: Minimal - needs architecture design

---

## 🎯 **Next Session Prompt Template**

After implementing this plan, use this prompt for new sessions:

```
I'm working on [FinVec financial ML system / Caelum distributed AI platform].

Please read these essential docs first:
- /home/rford/caelum/ss/[finvec or caelum-unified]/docs/00-START-HERE/SYSTEM_OVERVIEW.md
- /home/rford/caelum/ss/[finvec or caelum-unified]/docs/00-START-HERE/CURRENT_STATUS.md
- /home/rford/caelum/ss/[finvec or caelum-unified]/docs/00-START-HERE/SESSION_GUIDE.md

Then help me with: [specific task]
```

**Expected result**: Claude productive immediately, no confusion about system state

---

## 📞 **Escalation Path**

If documentation still confusing after this cleanup:
1. Check if 00-START-HERE/ docs were actually updated
2. Verify no conflicting root-level docs remain
3. Check if obsolete docs were properly archived
4. Review if SESSION_GUIDE.md has current locations
5. Consider if new documentation structure is needed

---

**Status**: Plan complete, ready for implementation
**Priority**: CRITICAL - blocks effective development
**Timeline**: 2-3 weeks for full implementation
**Owner**: Next Claude session + Roderick Ford

