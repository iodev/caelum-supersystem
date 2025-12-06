# Agent Architecture Review & Alignment Plan

**Date**: 2025-11-30
**Purpose**: Identify duplicate agents, clarify roles, align TypeScript and Python implementations

---

## Current State Analysis

### ⚠️ **Critical Finding: Duplicate Agent Implementations**

We have **TWO separate agent implementations** that are NOT aligned:

1. **TypeScript Layer 1 Agents** (`/server/services/agents/`) - 12+ agents found
2. **Python PIM Engine Agents** (`/engine/pim/agents/`) - 9 agents documented

---

## 🎯 **Original Design (Per CLAUDE.md)**

### **Layer 1 (LLM Collaborative Agents) - 9 Agents**:

According to CLAUDE.md:29-30, the original design specified:

1. **Information Gatherer** - Market scanner, fetches predictions every 5 minutes
2. **Portfolio Manager (Coordinator)** - Lead decision maker, position sizing, trade execution
3. **EventTrigger** - Receives Layer 2 RL signals, publishes opportunities to team
4. **Price Analyzer** - Technical analysis, chart patterns (supplements FinColl)
5. **News Processor** - Sentiment analysis, news impact (supplements FinColl)
6. **Risk Manager** - Portfolio risk, stop-loss monitoring, PDT compliance
7. **Trend Analyzer** - Market trends, sector rotation (supplements FinColl)
8. **Metrics Evaluator** - Performance monitoring, agent evaluation
9. **Web Search** - Tavily web search, political climate, current events

**Purpose**: These agents were designed to do **parallel research from various sources** to determine what to trade.

**Evolution**: This research function has NOW moved into FinColl (Data Layer) + EventTrigger (RL Layer 2 → Layer 1 bridge).

---

## 🔍 **Current TypeScript Implementation**

### **Found 12+ Agents in `/server/services/agents/`**:

| Agent | File | Has LLM Prompt? | Purpose | Status |
|-------|------|----------------|---------|--------|
| **SwarmPortfolioManager** | swarm-portfolio-manager.ts | ✅ Yes | Portfolio management (newer) | ⚠️ Duplicate |
| **PortfolioManager** | portfolio-manager.ts | ✅ Yes | Portfolio management (legacy) | ⚠️ Duplicate |
| **EnhancedMetricsEvaluator** | enhanced-metrics-evaluator.ts | ✅ Yes | Performance monitoring (newer) | ⚠️ Duplicate |
| **MetricsEvaluator** | metrics-evaluator.ts | ✅ Yes | Performance monitoring (older) | ⚠️ Duplicate |
| **Supervisor** | supervisor.ts | ✅ Yes | Routing agent | ✅ Unique |
| **TradingAgent** | trading-agent.ts | ❌ No | Trade execution wrapper | ⚠️ Redundant? |
| **RiskManagerAgent** | risk-manager.ts | ❌ No | Rule-based risk checking | ⚠️ Unclear role |
| **PriceAnalyzerAgent** | price-analyzer.ts | ❌ No | Technical analysis | ⚠️ Unclear role |
| **NewsProcessorAgent** | news-processor.ts | ❌ No | Event-driven news | ⚠️ Unclear role |
| **WebAgent** | web-agent.ts | ❓ Unknown | Web research, symbol management | ⚠️ Tool or Agent? |
| **EventTriggerAgent** | event-trigger.ts | ❌ No | Event triggers (time, news, market) | ⚠️ Unclear role |
| **InformationGathererAgent** | information-gatherer.ts | ❌ No | Data aggregation, system health | ⚠️ Unclear role |

**Additional Found**:
- MetricsEvaluatorJudge
- MetricsEvaluatorTeamJudge
- PortfolioOptimizer
- EnhancedPriceAnalyzer
- SocialSentimentAgent
- SenvecSentimentAgent
- FinvecPredictionAgent
- FinvecAgent

---

## 🔄 **Python PIM Engine Implementation**

### **Found in `/engine/pim/agents/`**:

According to previous reads, the Python engine has:

1. **BaseAgent** - Base class for all agents
2. **TradingAgent** - Likely the Python equivalent of Portfolio Manager
3. (Need to verify the complete Python agent list)

**Critical Gap**: We haven't fully cataloged the Python agents vs. TypeScript agents.

---

## ❓ **Key Architectural Questions**

### **1. Why Two Portfolio Managers?**

**Answer**: Evolution + lack of cleanup

- **PortfolioManager** (portfolio-manager.ts) - Original implementation
- **SwarmPortfolioManager** (swarm-portfolio-manager.ts) - Newer "swarm" architecture

**Issue**: Both exist, unclear which is active in production.

**Recommendation**:
- ✅ **Keep**: SwarmPortfolioManager (newer, swarm pattern)
- ❌ **Deprecate**: PortfolioManager (legacy)
- 📝 **Action**: Verify production usage, migrate if needed, delete legacy

---

### **2. Why Two Metrics Evaluators?**

**Answer**: Incremental enhancement without deprecation

- **MetricsEvaluator** (metrics-evaluator.ts:54-97) - Original performance monitoring
- **EnhancedMetricsEvaluator** (enhanced-metrics-evaluator.ts:107-154) - Enhanced with velocity tracking

**Issue**: Both exist, EnhancedMetricsEvaluator has more features.

**Recommendation**:
- ✅ **Keep**: EnhancedMetricsEvaluator (has velocity, market regime, advanced metrics)
- ❌ **Deprecate**: MetricsEvaluator (basic version)
- 📝 **Action**: Migrate any unique features, delete old version

---

### **3. TradingAgent, RiskManagerAgent, PriceAnalyzerAgent - Redundant with SwarmPortfolioManager?**

**Analysis**:

**TradingAgent** (trading-agent.ts):
- Purpose: Wraps trade execution via TradeExecutor
- No LLM prompt - pure execution
- **Question**: Should this logic be **inside** SwarmPortfolioManager instead of a separate agent?
- **Likely Answer**: This is NOT an "agent" in the LLM sense - it's a **utility class** for execution

**RiskManagerAgent** (risk-manager.ts):
- Purpose: Rule-based risk checking (max position size, concentration)
- No LLM prompt - calculation-based
- **Question**: Should this be a **module** used by SwarmPortfolioManager, not a separate "agent"?
- **Likely Answer**: This is a **risk calculation utility**, not an LLM agent

**PriceAnalyzerAgent** (price-analyzer.ts):
- Purpose: Technical analysis (OHLCV, indicators)
- No LLM prompt - uses data provider
- **Question**: Is this redundant with FinColl (which already does technical analysis)?
- **Likely Answer**: This MAY be legacy - FinColl now handles Price Analyzer role

**Recommendation**:
- 🔍 **Investigate**: Are these called by SwarmPortfolioManager or independently?
- 📝 **Action**: If called by SwarmPortfolioManager as utilities → Rename to `*Service` or `*Module` (not Agent)
- 📝 **Action**: If independent LLM agents → Add LLM prompts OR deprecate in favor of FinColl

---

### **4. NewsProcessorAgent - Original Design vs. Current State**

**Original Intent** (per CLAUDE.md):
- NewsProcessorAgent was part of the **parallel research** team
- Each agent researched from different sources
- All contributed to the committee decision

**Current State**:
- NewsProcessorAgent is **event-driven** (listens to AlpacaNewsService)
- Processes news queue asynchronously
- **May** use LLM for sentiment analysis (not in constructor, possibly in methods)

**FinColl Evolution**:
- FinColl NOW consolidates **News Processor** role (sentiment via SenVec 72D features)
- FinColl returns predictions with sentiment already embedded

**Question**: Is NewsProcessorAgent redundant with FinColl's sentiment analysis?

**Recommendation**:
- 🔍 **Investigate**: Does NewsProcessorAgent add value beyond FinColl?
- ✅ **Keep IF**: It provides real-time news alerts, breaking news signals
- ❌ **Deprecate IF**: It duplicates FinColl sentiment without adding real-time value

---

### **5. WebAgent - Tool or Agent?**

**Current Implementation**:
- Manages 2000-3000 symbol universe
- Uses TavilySearchClient for web research
- Handles symbol refresh, filtering

**Question**: Is this an LLM collaborative agent or a utility tool?

**Likely Answer**: This seems like a **background service/tool** rather than a committee member.

**Original Design**: "Web Search" was one of the 9 agents - meant for political climate, current events research.

**Recommendation**:
- 🔍 **Investigate**: Does WebAgent have LLM prompts for analysis?
- 📝 **Action IF LLM agent**: Keep as agent, ensure LLM prompt for web research insights
- 📝 **Action IF utility**: Rename to `SymbolManagementService` and remove from agent list

---

### **6. EventTriggerAgent - Role Clarity**

**Original Design** (CLAUDE.md):
- EventTrigger receives Layer 2 RL signals
- Publishes RL_OPPORTUNITY_DETECTED to Agent Bus
- Triggers Layer 1 team collaboration

**Current Implementation**:
- Manages event triggers (news, time, market conditions)
- Stores trigger state
- Checks trigger conditions

**Question**: Are these the SAME EventTrigger or different purposes?

**Recommendation**:
- 🔍 **Investigate**: Does EventTriggerAgent serve as the RL → Layer 1 bridge?
- 📝 **Action**: Clarify role - is this the RL signal receiver or generic event system?

---

### **7. InformationGathererAgent - Original Design vs. Current**

**Original Design** (CLAUDE.md):
- Market scanner (runs every 5 minutes)
- Fetches predictions from FinColl
- Kicks off the trading workflow

**Current Implementation**:
- Aggregates data across all agents and components
- Summarizes agent activities and performance
- Generates actionable insights
- Prepares dashboard metrics
- Tracks system health

**Question**: These seem like DIFFERENT roles!

**Analysis**:
- **Original**: Prediction fetcher / workflow initiator (critical for trading loop)
- **Current**: System health monitor / dashboard data aggregator (non-critical)

**Recommendation**:
- 🔍 **Investigate**: Is there a SEPARATE prediction-fetching agent?
- 📝 **Action IF missing**: Create or identify the **prediction loop** agent (scans FinColl every 5 min)
- 📝 **Action IF found**: Rename current InformationGatherer → `SystemHealthMonitor` or `DashboardAggregator`

---

## 🚨 **Critical Misalignment**

### **TypeScript Layer 1 vs. Python PIM Engine**

**CLAUDE.md states**:
> "Layer 1 (Python PIM) is PRIMARY - This is the decision-making system"
> "NOT the TypeScript agents (those are temporary fallback)"

**But we found**:
- 12+ TypeScript "agents" in `/server/services/agents/`
- Many with LLM prompts (SwarmPortfolioManager, MetricsEvaluator, etc.)
- Seems like active development, not "temporary fallback"

**Question**: Which is the **actual production system**?

**Hypothesis**:
1. **Python PIM Engine** (`/engine/pim/`) is the PRIMARY Layer 1 (with meta-learning, committee voting)
2. **TypeScript agents** are the FALLBACK when PIM Engine is unavailable
3. **Current state**: Dual implementation without clear deprecation path

**Recommendation**:
- 🔍 **Investigate**: What happens when PIM Engine is DOWN?
- 📝 **Action**: Document which system is active in production
- 📝 **Action**: Create deprecation plan for fallback system once primary is stable

---

## 📋 **Alignment Plan - Next Steps**

### **Phase 1: Inventory & Classification**

1. ✅ **Catalog TypeScript agents** (DONE - see table above)
2. 🔲 **Catalog Python PIM agents** (TODO - read `/engine/pim/agents/`)
3. 🔲 **Map TypeScript → Python equivalents** (TODO)
4. 🔲 **Identify unique agents** (only in TS or only in Python)
5. 🔲 **Classify each agent**:
   - **LLM Collaborative Agent** (has prompt, participates in committee)
   - **Utility Service** (no LLM, provides data/calculations)
   - **Background Worker** (event-driven, no committee participation)

### **Phase 2: Role Clarification**

For each agent, answer:
1. **What is its PURPOSE?** (original design intent)
2. **What does it DO currently?** (actual implementation)
3. **Is it REDUNDANT?** (with FinColl, other agents, or Python equivalent)
4. **Is it a TRUE agent or utility?** (LLM-driven vs. rule-based)
5. **Which layer owns this responsibility?** (FinColl, Layer 2 RL, Layer 1 LLM, or Express API)

### **Phase 3: Consolidation & Deprecation**

1. **Merge duplicates**:
   - SwarmPortfolioManager ← PortfolioManager (legacy)
   - EnhancedMetricsEvaluator ← MetricsEvaluator (basic)

2. **Rename utilities** (not agents):
   - TradingAgent → TradeExecutionService
   - RiskManagerAgent → RiskCalculationModule
   - WebAgent → SymbolManagementService (if not LLM-based)

3. **Deprecate redundant**:
   - PriceAnalyzerAgent (if FinColl handles this)
   - NewsProcessorAgent (if FinColl sentiment is sufficient)

4. **Clarify EventTrigger** and **InformationGatherer** roles

### **Phase 4: Python ↔ TypeScript Alignment**

1. Ensure **9 Python agents** match **9 TypeScript agents** (as documented in CLAUDE.md)
2. Decide: Is TypeScript a fallback or should it be deprecated entirely?
3. If fallback: Ensure feature parity (same prompts, same logic)
4. If deprecated: Create migration plan to Python-only

### **Phase 5: Documentation Update**

1. Update CLAUDE.md with final agent list
2. Update AGENT_SYSTEM.md (once we find it) with clear roles
3. Create AGENT_MAPPING.md (TypeScript ↔ Python equivalents)
4. Document which agents have LLM prompts vs. which are utilities

---

## 🤔 **Questions for Discussion**

1. **Which system is PRIMARY in production?** Python PIM Engine or TypeScript agents?
2. **What happens when PIM Engine is unavailable?** Does TypeScript take over?
3. **Should we keep dual implementation** or migrate to single system?
4. **FinColl consolidation** - Which of the original 9 agents are NOW handled by FinColl?
   - Original: Price Analyzer, News Processor, Fundamental Analyzer, Trend Analysis
   - Current: Are these ALL in FinColl or do some still exist as separate agents?
5. **EventTrigger role** - Is it the RL→Layer1 bridge or generic event system?
6. **InformationGatherer role** - Is it the prediction loop or system health monitor?

---

## 🎯 **Immediate Actions**

### **Before Making Changes**:

1. **Read Python PIM agents** - Catalog `/engine/pim/agents/` directory
2. **Check production routing** - Trace code path from FinColl prediction → final trade
3. **Identify active agents** - Which agents are ACTUALLY called in production?
4. **Map TypeScript↔Python** - Which TypeScript agents map to which Python agents?

### **After Clarity**:

1. **Enhance Portfolio Manager prompts** (SwarmPortfolioManager + Python equivalent)
2. **Deprecate legacy agents** (PortfolioManager, MetricsEvaluator)
3. **Rename utilities** (TradingAgent → Service, RiskManager → Module)
4. **Update CLAUDE.md** with final architecture

---

**Next Step**: Catalog Python PIM agents and create TypeScript↔Python mapping table.
