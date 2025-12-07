# PassiveIncomeMaximizer - Agent System

**Last Updated**: 2025-11-14
**Pattern**: Multi-Agent Swarm with Information Gatherer → Coordinator → Subagents
**Communication**: Event-driven Agent Bus + External Memory

---

## Agent System Overview

The PIM system uses 9 specialized AI agents that collaborate through an event-driven architecture to make trading decisions. This follows Anthropic's multi-agent pattern with parallel execution and shared context.

**Operating Mode:** 24/7 Continuous Operation - The system works nights, weekends, and holidays, continuously researching, analyzing, and improving like a trader who can't afford to miss anything.

### The 9 Agents

1. **Portfolio Manager** (Coordinator) - Opus 4
2. **Price Analyzer** (Subagent) - Sonnet 4
3. **News Processor** (Subagent) - Sonnet 4
4. **Risk Manager** (Subagent) - Sonnet 4
5. **Trend Analyzer** (Subagent) - Sonnet 4
6. **Metrics Evaluator** (Monitor) - Sonnet 4
7. **Event Trigger** (Monitor) - Sonnet 4
8. **Web Search** (Tool) - Sonnet 4
9. **Information Gatherer** (Scanner) - Sonnet 4

### 24/7 Monitoring Services

**NEW:** Two additional services run continuously alongside the agents:

10. **Risk Monitor** - Continuous risk surveillance (every 60 seconds)
11. **Daily Self-Evaluator** - Self-improvement loop (4:00 PM ET daily)

---

## Architecture Pattern

### Information Gatherer → Coordinator → Subagents

```
┌──────────────────────────────────────────────────────────┐
│  Information Gatherer (every 5 min)                      │
│  • Scans FinColl for high-confidence predictions         │
│  • Scans SenVec for sentiment shifts                     │
│  • Creates "suggested topics" for discussion             │
│  • Publishes: OPPORTUNITIES_DETECTED event               │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Portfolio Manager Coordinator                           │
│  • Receives suggested topics                             │
│  • Loads shared context from external memory             │
│  • Decides: "Do any warrant analysis?"                   │
│  • If YES: Spawn 4 subagents IN PARALLEL                 │
└────────────────────┬─────────────────────────────────────┘
                     │
       ┌─────────────┼──────────────┬───────────────┐
       │             │              │               │
       ▼             ▼              ▼               ▼
┌───────────┐ ┌───────────┐ ┌──────────┐ ┌────────────┐
│   Price   │ │   News    │ │   Risk   │ │   Trend    │
│  Analyzer │ │ Processor │ │  Manager │ │  Analyzer  │
└─────┬─────┘ └─────┬─────┘ └────┬─────┘ └──────┬─────┘
      │             │            │              │
      │ 500 tokens  │ 500 tokens │ 500 tokens   │ 500 tokens
      └─────────────┴────────────┴──────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Committee (Voting & Synthesis)                          │
│  • Weights agent votes by historical performance         │
│  • Aggregates to final decision                          │
│  • Returns: BUY/SELL/HOLD + confidence + size            │
└──────────────────────────────────────────────────────────┘
```

---

## Agent Details

### 1. Portfolio Manager (Coordinator)

**Model**: Opus 4
**Role**: Lead decision maker
**Responsibilities**:
- Receives opportunity suggestions
- Spawns subagents for analysis
- Synthesizes team discussion
- Makes final trading decisions
- Manages portfolio allocation

**Event Subscriptions**:
- `OPPORTUNITIES_DETECTED` (from Information Gatherer)
- `RISK_THRESHOLD_BREACH` (from Risk Manager)
- `MARKET_OPEN/CLOSE` (from Event Trigger)

**Event Publications**:
- `TRADE_EXECUTED`
- `POSITION_OPENED/CLOSED`
- `PORTFOLIO_UPDATE`

### 2. Price Analyzer (Subagent)

**Model**: Sonnet 4
**Role**: Technical analysis specialist
**Responsibilities**:
- Analyze price patterns, RSI, MACD
- Call FinColl API for predictions
- Identify support/resistance levels
- Recommend BUY/SELL based on technicals

**Tools Used**:
- FinColl API (http://10.32.3.27:8002)
- Technical indicators library
- Historical price data

### 3. News Processor (Subagent)

**Model**: Sonnet 4
**Role**: Sentiment analysis specialist
**Responsibilities**:
- Analyze financial news, earnings
- Call SenVec API for sentiment
- Identify market-moving events
- Recommend based on sentiment

**Tools Used**:
- SenVec API (http://10.32.3.27:18000)
- News aggregation services
- SEC EDGAR for filings

### 4. Risk Manager (Subagent)

**Model**: Sonnet 4
**Role**: Portfolio risk specialist
**Responsibilities**:
- Assess portfolio risk exposure
- Calculate position sizing
- Monitor stop-loss levels
- Veto risky trades

**Risk Metrics**:
- Value at Risk (VaR)
- Portfolio correlation
- Sector concentration
- Maximum drawdown

### 5. Trend Analyzer (Subagent)

**Model**: Sonnet 4
**Role**: Market trend specialist
**Responsibilities**:
- Identify market trends (bull/bear/sideways)
- Detect regime changes
- Recommend strategy adjustments
- Validate price predictions

### 6. Metrics Evaluator (Monitor)

**Model**: Sonnet 4
**Role**: Performance monitor
**Responsibilities**:
- Track all trading outcomes
- Calculate Sharpe ratio, win rate
- Trigger retraining if performance degrades
- Generate performance reports

### 7. Event Trigger (Monitor)

**Model**: Sonnet 4
**Role**: Event coordinator
**Responsibilities**:
- Monitor for significant market events
- Coordinate multi-agent responses
- Can pause trading during uncertainty
- Broadcasts system-wide alerts

### 8. Web Search (Tool)

**Model**: Sonnet 4
**Role**: Information retrieval
**Responsibilities**:
- Search web for relevant information
- Supplement news with real-time data
- Research specific topics on-demand

### 9. Information Gatherer (Scanner)

**Model**: Sonnet 4
**Role**: Market scanner
**Responsibilities**:
- Scan FinColl every 5 minutes
- Filter by confidence thresholds
- Create suggested discussion topics
- Trigger coordinator when opportunities found

---

## Agent Communication

### Agent Bus (Event-Driven)

```typescript
// Event Topics
export enum PIMEventTopics {
  // Market Events
  PRICE_CHANGE = 'market:price_change',
  VOLUME_SPIKE = 'market:volume_spike',
  VOLATILITY_ALERT = 'market:volatility',
  NEWS_ALERT = 'market:news',

  // Portfolio Events
  PORTFOLIO_UPDATE = 'portfolio:update',
  TRADE_EXECUTED = 'portfolio:trade_executed',
  POSITION_OPENED = 'portfolio:position_opened',
  POSITION_CLOSED = 'portfolio:position_closed',
  RISK_THRESHOLD_BREACH = 'portfolio:risk_breach',

  // Analysis Events
  PREDICTION_READY = 'analysis:prediction_ready',
  OPPORTUNITIES_DETECTED = 'analysis:opportunities',
  SENTIMENT_UPDATE = 'analysis:sentiment',
  TREND_DETECTED = 'analysis:trend',

  // System Events
  MARKET_OPEN = 'system:market_open',
  MARKET_CLOSE = 'system:market_close',
  AGENT_ERROR = 'system:agent_error'
}

// Publishing
agentBus.publish(PIMEventTopics.PREDICTION_READY, {
  symbol: 'AAPL',
  prediction: 'bullish',
  confidence: 0.85
});

// Subscribing
agentBus.subscribe(PIMEventTopics.PREDICTION_READY, async (event) => {
  await portfolioManager.handlePrediction(event);
});
```

### External Memory (Caelum Integration)

**Storage Layers**:
1. **MongoDB** (10.32.3.27:27017) - Persistent decisions
2. **Redis** (10.32.3.27:6379) - Fast caching (5min TTL)
3. **Qdrant** (10.32.3.27:6333) - Vector search (future)

**Benefits**:
- Shared context across agents
- Reduces LLM context usage (87% reduction)
- Persistent learning
- Historical decision retrieval

---

## Swarm Visualization

### D3.js Force-Directed Graph

The Vue3 frontend includes a real-time visualization of agent communication:

**Features**:
- 9 agent nodes with distinct colors
- Animated message flow between agents
- Real-time WebSocket updates
- Draggable nodes
- Agent statistics cards

**Access**: http://10.32.3.27:5500/swarm

---

## Agent Implementation

### Base Agent Class

```typescript
export class PIMSwarmAgent extends BaseAgent {
  constructor(config: AgentConfig) {
    super(config);
    this.eventTopics = config.eventTopics || [];
  }

  // Handle events from Agent Bus
  protected async handleEvent(topic: string, message: any): Promise<void> {
    // Override in subclass
  }

  // Main execution logic
  async execute(state: PIMSwarmState): Promise<Partial<PIMSwarmState>> {
    // Override in subclass
  }

  // Determine handoffs to other agents
  shouldHandoff(state: PIMSwarmState): Handoff | null {
    // Override in subclass
    return null;
  }

  // Store memory
  async storeMemory(type: string, data: any): Promise<void> {
    await externalMemory.store({
      agentId: this.agentId,
      type,
      data,
      timestamp: new Date()
    });
  }

  // Retrieve memories
  async getRecentMemories(type: string, limit: number = 10): Promise<any[]> {
    return await externalMemory.query({
      agentId: this.agentId,
      type,
      limit
    });
  }
}
```

### Example: Portfolio Manager

```typescript
export class SwarmPortfolioManager extends PIMSwarmAgent {
  constructor(config, dependencies) {
    super({
      ...config,
      name: 'portfolio_manager',
      description: 'Coordinates trading decisions',
      eventTopics: [
        PIMEventTopics.OPPORTUNITIES_DETECTED,
        PIMEventTopics.RISK_THRESHOLD_BREACH,
        PIMEventTopics.MARKET_OPEN
      ]
    });

    this.priceAnalyzer = dependencies.priceAnalyzer;
    this.newsProcessor = dependencies.newsProcessor;
    this.riskManager = dependencies.riskManager;
    this.trendAnalyzer = dependencies.trendAnalyzer;
  }

  protected async handleEvent(topic: string, message: any): Promise<void> {
    if (topic === PIMEventTopics.OPPORTUNITIES_DETECTED) {
      await this.analyzeOpportunities(message);
    } else if (topic === PIMEventTopics.RISK_THRESHOLD_BREACH) {
      await this.handleRiskBreach(message);
    }
  }

  async execute(state: PIMSwarmState): Promise<Partial<PIMSwarmState>> {
    // Main decision logic
    const decision = await this.makeDecision(state);

    // Store in memory
    await this.storeMemory('decision', decision);

    // Update state
    return this.addMessage(state, `Decision: ${decision.action}`, true);
  }

  shouldHandoff(state: PIMSwarmState): Handoff | null {
    // If need price analysis
    if (state.context.needsPriceAnalysis) {
      return this.createHandoff(this.priceAnalyzer, {
        symbol: state.context.symbol,
        reason: 'Need technical analysis'
      });
    }
    return null;
  }
}
```

---

## Committee Voting System

### Vote Weighting

Agents are weighted based on historical performance:

```typescript
interface AgentVote {
  agentId: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;  // 0-1
  reasoning: string;
}

interface CommitteeDecision {
  finalDecision: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  consensus: number;  // % agreement
  votes: AgentVote[];
  synthesis: string;
}

class Committee {
  async aggregateVotes(votes: AgentVote[]): Promise<CommitteeDecision> {
    // Weight by historical accuracy
    const weights = await this.getAgentWeights();

    // Calculate weighted scores
    const scores = {
      BUY: 0,
      SELL: 0,
      HOLD: 0
    };

    for (const vote of votes) {
      const weight = weights[vote.agentId] || 1.0;
      scores[vote.signal] += vote.confidence * weight;
    }

    // Determine winner
    const finalDecision = Object.keys(scores).reduce((a, b) =>
      scores[a] > scores[b] ? a : b
    );

    // Calculate consensus
    const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);
    const consensus = scores[finalDecision] / totalScore;

    return {
      finalDecision,
      confidence: scores[finalDecision] / votes.length,
      consensus,
      votes,
      synthesis: await this.synthesize(votes, finalDecision)
    };
  }
}
```

---

## Configuration

### Agent Settings

Edit via `/agents` page or configuration API:

```typescript
interface AgentSettings {
  status: 'active' | 'training' | 'idle' | 'error';
  model: string;  // 'opus-4', 'sonnet-4', 'haiku-4'
  temperature: number;  // 0-1
  maxTokens: number;
  confidenceThreshold: number;  // Minimum confidence to act
  weight: number;  // Voting weight (0-2)
  eventSubscriptions: string[];  // Topics to subscribe to
}
```

### Training Mode

Agents can operate in training mode:

```typescript
{
  mode: 'training',
  symbols: ['AAPL', 'MSFT', 'GOOGL'],
  timeRange: '30D',
  dryRun: true,  // No actual trades
  logDecisions: true  // Log all decisions for analysis
}
```

---

## Performance Monitoring

### Agent Metrics

Track individual agent performance:

```typescript
interface AgentMetrics {
  agentId: string;
  totalDecisions: number;
  correctDecisions: number;
  accuracy: number;  // correctDecisions / totalDecisions
  avgConfidence: number;
  avgResponseTime: number;  // milliseconds
  profitContribution: number;  // $
  lastActive: Date;
}
```

### Trigger Retraining

Metrics Evaluator monitors performance and triggers retraining:

```typescript
if (metrics.accuracy < 0.60) {
  // Performance degraded
  agentBus.publish(PIMEventTopics.PERFORMANCE_DEGRADED, {
    agentId: metrics.agentId,
    currentAccuracy: metrics.accuracy,
    threshold: 0.60
  });

  // Trigger FinVec retraining
  await axios.post('http://10.32.3.27:8002/api/training/start', {
    reason: 'performance_degraded',
    targetAccuracy: 0.70
  });
}
```

---

## Troubleshooting

### Agent Not Responding

```bash
# Check agent status
curl http://10.32.3.27:5000/api/agents/status | jq

# Check Agent Bus stats
curl http://10.32.3.27:5000/api/agents/bus/stats | jq

# Restart specific agent
curl -X POST http://10.32.3.27:5000/api/agents/portfolio_manager/restart
```

### High Latency

- Check external services (FinColl, SenVec)
- Review agent memory usage
- Check database connection pool
- Monitor WebSocket connections

### Conflicting Decisions

This is normal! Committee voting resolves conflicts:
- Review vote distribution in decision logs
- Check agent confidence levels
- Adjust agent weights if needed

---

## 24/7 Continuous Operation

The PIM system runs continuously, 24 hours a day, 7 days a week - even when markets are closed. This philosophy follows the principle: **"Markets don't wait. Opportunities emerge at 3 AM. Risk materializes on weekends. The system must work like a trader who can't afford to miss anything."**

### Three-Tier Architecture

**Tier 1: Always-On Services (Continuous, Uninterrupted)**
1. **Information Gatherer** - Scans every 5 minutes
   - FinColl predictions, SenVec sentiment, price anomalies
   - Generates suggested topics for team discussion
2. **Risk Monitor** - Checks every 60 seconds
   - Open position monitoring, stop-loss breach detection
   - Pre-market gaps, after-hours news impact
   - Portfolio drawdown and concentration risk
   - **Runs even when market is closed**

**Tier 2: Scheduled Services (Periodic, Critical Timing)**
3. **Daily Self-Evaluator** - Runs daily at 4:00 PM ET (market close)
   - Analyzes ALL agent performance from the day
   - Generates concrete improvement suggestions
   - Auto-implements LOW-RISK improvements
   - Examples: "Cache TechnicalAgent queries (-50% latency)", "Increase PIMV7Agent weight (+3% accuracy)"

**Tier 3: Event-Driven Services (React to Real-Time Events)**
4. **Agent Execution** - On-demand, parallel
   - Spawns 4 subagents when Information Gatherer finds topics
   - Executes immediately (no waiting)

### Self-Improvement Loop

**The most important feature:** The system gets better every single day without human intervention.

**Daily Cycle:**
1. **Trading Day** (9:30 AM - 4:00 PM) - Agents make decisions, execute trades
2. **Data Collection** - Track all agent decisions, outcomes, execution times, errors
3. **Self-Evaluation** (4:00 PM ET) - Analyze performance, find patterns, generate improvements
4. **Risk-Based Decision**:
   - **LOW RISK**: Auto-implement (e.g., caching, new RSS feed)
   - **MEDIUM RISK**: User approval required (e.g., agent weight changes)
   - **HIGH RISK**: A/B test first (e.g., strategy changes)
5. **Next Day** - Improved system with better parameters, new data sources, faster responses

**Compound Effect:** 1% improvement per day = 37x better in a year

### Market Hours Adaptation

The system adapts behavior based on market state:

| Market State | Info Gatherer | Risk Monitor | Actions |
|-------------|---------------|--------------|---------|
| PRE-MARKET (4-9:30 AM) | Every 5 min | Every 60 sec | Gap detection, news monitoring |
| MARKET HOURS (9:30 AM-4 PM) | Every 5 min | Every 60 sec | Full trading, position management |
| AFTER-HOURS (4-8 PM) | Every 5 min | Every 60 sec | News impact, risk checks |
| CLOSED (8 PM-4 AM) | Every 15 min | Every 5 min | Research mode, learning |

**Key Insight:** Even when market is CLOSED, the system:
- Researches new data sources
- Analyzes past performance
- Builds knowledge for tomorrow
- Monitors for overnight gaps

### 24/7 API Endpoints

**Risk Monitoring:**
```bash
GET /api/pim/risk/alerts?limit=10&level=CRITICAL
# Returns recent risk alerts (INFO/WARNING/CRITICAL/EMERGENCY)
```

**Self-Evaluation:**
```bash
GET /api/pim/evolution/report
# Latest daily evaluation with insights and improvements

GET /api/pim/evolution/improvements?days=7
# All improvements from last 7 days
```

**For complete 24/7 architecture details, see `engine/24x7_ARCHITECTURE.md`**

---

## Related Documentation

- **ARCHITECTURE.md** - Overall system design
- **INTEGRATIONS.md** - FinVec, SenVec, Caelum integration
- **TRADING_OPERATIONS.md** - How agents make trading decisions
- **engine/24x7_ARCHITECTURE.md** - Complete 24/7 system documentation (500+ lines)

---

**See ARCHITECTURE.md for agent deployment details**
**See INTEGRATIONS.md for external service configuration**
**See engine/24x7_ARCHITECTURE.md for 24/7 operation details**
