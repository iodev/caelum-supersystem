# PIM Living System - Workflow & Modes

## Overview

PIM is a **self-evolving, 24/7 autonomous trading system** that operates continuously, switching between modes based on market hours and account settings. It is NOT a linear progression from "training" to "production" - it is always developing, always learning, always improving.

### Core Principles

1. **Time-Based Mode Switching**: Market hours → Trading mode; Off hours → Research/Backtest mode
2. **Account-Level Control**: Each account independently toggles SIM/LIVE via human UI
3. **Multi-Agent Discussion**: Trade decisions emerge from LLM agent team discussions
4. **Human-in-the-Loop**: Human can observe, vote, override - but system proceeds if no intervention
5. **Autonomous Evolution**: System tests hypotheses off-hours and modifies its own code
6. **Asset Agnostic**: Stocks, Futures, Options, Crypto - agents spawn as needed per account capabilities

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PIM LIVING SYSTEM (24/7)                            │
│                    Always Running • Always Learning                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                           ┌──────────┴──────────┐
                           │   CURRENT TIME &    │
                           │   ACCOUNT SETTINGS  │
                           └──────────┬──────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ↓                           ↓                           ↓
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   TRADING HOURS     │    │   TRANSITION        │    │   OFF HOURS         │
│                     │    │   PERIODS           │    │                     │
│ Regular: 9:30a-4:00p│    │                     │    │ After close until   │
│ Extended: per acct  │    │ • End of day        │    │ pre-market prep     │
│                     │    │   wind-down         │    │                     │
│ Mode: TRADING       │    │ • Pre-market        │    │ Mode: RESEARCH &    │
│                     │    │   preparation       │    │       BACKTEST      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
          │                                                     │
          │                                                     │
          ↓                                                     ↓
┌─────────────────────┐                           ┌─────────────────────┐
│ • Receive           │                           │ • Daily review      │
│   suggestions       │                           │ • Generate          │
│ • Multi-agent       │                           │   hypotheses        │
│   discussions       │                           │ • Run backtests     │
│ • Execute trades    │                           │ • Evolve code       │
│   (SIM or LIVE)     │                           │ • Self-improve      │
└─────────────────────┘                           └─────────────────────┘
          │                                                     │
          └─────────────────────┬───────────────────────────────┘
                                │
                       ┌────────┴────────┐
                       │  CONTINUOUS     │
                       │  LEARNING LOOP  │
                       │  (Forever)      │
                       └─────────────────┘
```

---

## Account Configuration

### Account Settings (Per Account)

Each connected trading account has independent settings controlled via the Web UI:

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Execution Mode** | `SIM` / `LIVE` | `SIM` | Fake money vs real money - **sticky until human changes** |
| **Management Mode** | `MANAGED` / `MANUAL` / `MONITOR` | `MONITOR` | Bot executes / Human only / Observe only |
| **Extended Hours** | `ENABLED` / `DISABLED` | `DISABLED` | Allow pre/after market trading if broker permits |
| **Asset Classes** | `STOCKS` / `OPTIONS` / `FUTURES` / `CRYPTO` | `STOCKS` | What the account can trade (broker-dependent) |
| **Max Position Size** | 1-100% | 10% | Per-position limit |
| **Daily Loss Limit** | 0.5-10% | 2% | Circuit breaker threshold |

### Account States

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCOUNT STATE MATRIX                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Execution     Management     Result                           │
│   ─────────     ──────────     ──────                           │
│   SIM           MANAGED        Bot trades fake money            │
│   SIM           MANUAL         Human trades fake money          │
│   SIM           MONITOR        Bot observes, logs, no trades    │
│   LIVE          MANAGED        ⚠️  Bot trades REAL money         │
│   LIVE          MANUAL         Human trades real money          │
│   LIVE          MONITOR        Bot observes real account        │
│                                                                 │
│   Note: SIM and LIVE are treated identically by the system     │
│         except for the actual order execution endpoint.         │
│         Same caution, same risk management, same logging.       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Trading Hours Mode

### When Active

Trading mode is active when:
- Market is open (9:30am - 4:00pm ET for stocks), OR
- Extended hours enabled AND authorized for account AND within extended window

The transition to off-hours happens when orders are **no longer authorized** on each particular account:
- If extended hours disabled: 4:00pm ET
- If extended hours enabled: 8:00pm ET (post-market close)

### Suggestion Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SUGGESTION SOURCES (Continuous)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────┐                                                     │
│  │   EVENT TRIGGER    │  ← Primary source during market hours               │
│  │                    │                                                     │
│  │  ┌──────────────┐  │                                                     │
│  │  │   RL Layer   │  │  Pre-screens suggestions based on learned           │
│  │  │  (Pre-screen)│  │  experience before surfacing to LLM discussion      │
│  │  └──────────────┘  │                                                     │
│  └─────────┬──────────┘                                                     │
│            │                                                                │
│            ↓                                                                │
│  ┌────────────────────┐    ┌────────────────────┐    ┌──────────────────┐  │
│  │  Research Agent    │    │   News Agent       │    │  Discovery Agent │  │
│  │                    │    │                    │    │                  │  │
│  │  • Correlation     │    │  • Breaking news   │    │  • Find new      │  │
│  │    analysis        │    │  • Earnings calls  │    │    symbols       │  │
│  │  • Pattern         │    │  • SEC filings     │    │  • Sector scans  │  │
│  │    detection       │    │  • Social trends   │    │  • Momentum      │  │
│  └─────────┬──────────┘    └─────────┬──────────┘    └────────┬─────────┘  │
│            │                         │                        │            │
│            └─────────────────────────┴────────────────────────┘            │
│                                      │                                      │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       ↓
                            ┌──────────────────────┐
                            │   SUGGESTION QUEUE   │
                            │  (Prioritized FIFO)  │
                            │                      │
                            │  Each suggestion:    │
                            │  • Symbol            │
                            │  • Direction hint    │
                            │  • Confidence        │
                            │  • Source agent      │
                            │  • Reasoning         │
                            └──────────┬───────────┘
                                       │
                                       ↓
                            ┌──────────────────────┐
                            │  FOR EACH MANAGED    │
                            │  ACCOUNT: Trigger    │
                            │  Inner Discussion    │
                            └──────────────────────┘
```

### Symbol Discovery

When an agent suggests an **unknown symbol** (not in FinColl's database):

```
Unknown Symbol Detected: "XYZ"
        │
        ↓
┌───────────────────────────────────┐
│  1. Auto-add to FinColl watchlist │
│  2. Run historical data backfill  │
│  3. Continue discussion with      │
│     available data                │
└───────────────────────────────────┘
        │
        ↓
(No human approval needed - system
 is allowed to discover new symbols)
```

---

## Multi-Agent Discussion System

### The Inner Discussion

For each suggestion, a discussion is triggered per managed account:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIM INNER DISCUSSION                                     │
│              (Per Account × Per Suggestion)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DISCUSSION PARTICIPANTS:                                                   │
│  ────────────────────────                                                   │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  TradingAgent   │  │   RiskAgent     │  │ SentimentAgent  │             │
│  │                 │  │                 │  │                 │             │
│  │ • Position size │  │ • Portfolio     │  │ • Query FinColl │             │
│  │ • Entry/exit    │  │   exposure      │  │ • Recent data   │             │
│  │ • Stop loss     │  │ • Correlation   │  │ • Trend check   │             │
│  │ • Take profit   │  │ • Sector heat   │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  DYNAMIC PARTICIPANTS (spawn as needed):                                    │
│  ───────────────────────────────────────                                    │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ [FuturesAgent]  │  │ [OptionsAgent]  │  │  [CryptoAgent]  │             │
│  │                 │  │                 │  │                 │             │
│  │ Spawns if       │  │ Spawns if       │  │ Spawns if       │             │
│  │ futures symbol  │  │ options trade   │  │ crypto symbol   │             │
│  │ suggested AND   │  │ suggested AND   │  │ suggested AND   │             │
│  │ account allows  │  │ account allows  │  │ account allows  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  Note: New agent types may spawn if the system encounters asset             │
│        classes it hasn't seen before. They learn from experience.           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Discussion Points

Each discussion covers:

```
DISCUSSION TEMPLATE
═══════════════════

1. SYMBOL
   • Known or new discovery?
   • Asset class: Stock / Future / Option / Crypto
   • Available on this account?

2. DIRECTION
   • LONG / SHORT / HOLD
   • Reasoning from each agent

3. POSITION SIZING
   • % of account (respecting max limit)
   • Scaling: All-in or ladder?

4. ENTRY STRATEGY
   • Market order (immediate)
   • Limit order (price)
   • Conditional (if X happens)

5. EXIT STRATEGY
   • Stop loss level
   • Take profit target
   • Time horizon (day trade? swing? position?)

6. RISK ASSESSMENT
   • Current portfolio heat
   • Correlation with existing positions
   • Sector concentration
   • Account-specific constraints
```

### Voting System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VOTING MECHANISM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Each agent votes: APPROVE │ REJECT │ ABSTAIN                               │
│                                                                             │
│  Vote Weight Factors:                                                       │
│  ────────────────────                                                       │
│  1. REPUTATION SCORE                                                        │
│     • Learned over time based on prediction accuracy                        │
│     • Higher reputation = more weight                                       │
│                                                                             │
│  2. EXPERTISE MATCH                                                         │
│     • Case-dependent: If discussing options, OptionsAgent                   │
│       gets higher weight                                                    │
│     • RiskAgent may get higher weight in volatile markets                   │
│                                                                             │
│  3. CONFIDENCE LEVEL                                                        │
│     • Each agent reports confidence (0-100%)                                │
│     • Low confidence → reduced vote weight                                  │
│                                                                             │
│  Vote Aggregation:                                                          │
│  ─────────────────                                                          │
│  • Weighted sum of votes                                                    │
│  • Threshold for approval: Learned/adaptive (starts at 60%)                 │
│  • Certain agents may have domain-specific veto power                       │
│    (e.g., RiskAgent vetoes if exposure > limit)                             │
│                                                                             │
│  Voting weights themselves are LEARNED:                                     │
│  • After trade outcome known, adjust agent reputation                       │
│  • Winning votes increase reputation                                        │
│  • Losing votes decrease reputation                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Human Override Window

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HUMAN INTERVENTION WINDOW                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DEFAULT WINDOW: 5-10 seconds (human-adjustable setting per account)        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  WEB UI: Discussion Viewer                                            │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │ AAPL Long Discussion (Account: TradeStation-001)                │ │  │
│  │  │                                                                 │ │  │
│  │  │ TradingAgent: "Buy AAPL @ $185, target $195, stop $180"        │ │  │
│  │  │ RiskAgent: "Current exposure 15%, this adds 8%, acceptable"     │ │  │
│  │  │ SentimentAgent: "FinColl shows 72% bullish, news positive"      │ │  │
│  │  │                                                                 │ │  │
│  │  │ VOTE RESULT: 78% APPROVE                                        │ │  │
│  │  │                                                                 │ │  │
│  │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │ │  │
│  │  │ │ APPROVE  │ │  REJECT  │ │  MODIFY  │ │  DEFER   │            │ │  │
│  │  │ │  ✓ 5s    │ │    ✗     │ │    ✎     │ │    ⏸     │            │ │  │
│  │  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │ │  │
│  │  │                                                                 │ │  │
│  │  │ [Auto-proceeding in 5... 4... 3...]                            │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Human Actions:                                                             │
│  ──────────────                                                             │
│  • APPROVE: Execute immediately                                             │
│  • REJECT: Cancel, log reason, add to learning dataset                      │
│  • MODIFY: Adjust parameters (size, stop, etc.) then execute                │
│  • DEFER: Re-queue for later evaluation                                     │
│  • (No action): Auto-proceed with vote result after window expires          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Trade Execution

### Disposition Outcomes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DISPOSITION OUTCOMES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Discussion Complete                                                        │
│         │                                                                   │
│         ↓                                                                   │
│  ┌──────────────┐                                                           │
│  │ Vote Result  │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│         ├──────────────────┬──────────────────┬──────────────────┐          │
│         ↓                  ↓                  ↓                  ↓          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────┐   │
│  │   APPROVED   │   │   REJECTED   │   │   MODIFIED   │   │  DEFERRED  │   │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   └──────┬─────┘   │
│         │                  │                  │                  │          │
│         ↓                  ↓                  ↓                  ↓          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────┐   │
│  │ Execute on   │   │ Log reason   │   │ Apply human  │   │ Re-queue   │   │
│  │ MANAGED      │   │              │   │ modifications│   │ for later  │   │
│  │ accounts     │   │ Add to       │   │              │   │            │   │
│  │              │   │ learning     │   │ Then execute │   │            │   │
│  │ SIM or LIVE  │   │ dataset      │   │              │   │            │   │
│  │ (per acct    │   │              │   │              │   │            │   │
│  │ setting)     │   │ Adjust agent │   │              │   │            │   │
│  │              │   │ reputations  │   │              │   │            │   │
│  └──────┬───────┘   └──────────────┘   └──────┬───────┘   └────────────┘   │
│         │                                     │                             │
│         └─────────────────────────────────────┘                             │
│                          │                                                  │
│                          ↓                                                  │
│                 ┌─────────────────┐                                         │
│                 │  ORDER CREATED  │                                         │
│                 │  (via FinColl)  │                                         │
│                 │  → TradeStation │                                         │
│                 └─────────────────┘                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Market Transitions

### End of Trading Hours (Wind-Down)

Triggered 15 minutes before orders become unauthorized:
- Regular market: 3:45pm ET
- Extended hours enabled: 7:45pm ET

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      WIND-DOWN PROCEDURE                                    │
│                   (15 minutes before close)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FOR EACH MANAGED ACCOUNT:                                                  │
│                                                                             │
│  1. TRIGGER END-OF-DAY DISCUSSION                                           │
│     ─────────────────────────────                                           │
│     For each open position:                                                 │
│                                                                             │
│     TradingAgent: "Position XYZ was flagged as day-trade, recommend close" │
│     RiskAgent: "Overnight gap risk is 2.3% for this symbol"                 │
│     SentimentAgent: "After-hours news pending, volatility expected"         │
│                                                                             │
│     Discussion outcome: CLOSE / HOLD OVERNIGHT                              │
│                                                                             │
│  2. EXECUTE CLOSURES                                                        │
│     ──────────────────                                                      │
│     • Close all day-trade-flagged positions                                 │
│     • Use market orders (prioritize execution over price)                   │
│                                                                             │
│  3. CANCEL UNFILLED ORDERS                                                  │
│     ─────────────────────                                                   │
│     • Cancel all open limit orders                                          │
│     • Cancel all conditional orders                                         │
│     • Log cancellation reasons                                              │
│                                                                             │
│  4. PREPARE OVERNIGHT POSITIONS                                             │
│     ──────────────────────────                                              │
│     • Update stop-loss levels for gap protection                            │
│     • Set alerts for overnight price movements                              │
│                                                                             │
│  5. LOG END-OF-DAY STATE                                                    │
│     ────────────────────                                                    │
│     • Portfolio snapshot                                                    │
│     • Day's P&L                                                             │
│     • All trades executed                                                   │
│     • Discussion transcripts                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Start of Trading Hours (Pre-Market Prep)

Triggered 15 minutes before market open (9:15am ET):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRE-MARKET PREPARATION                                   │
│                   (15 minutes before open)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. VERIFY SYSTEM HEALTH                                                    │
│     ─────────────────────                                                   │
│     □ FinColl API responding (port 8002)                                    │
│     □ SenVec aggregator running (port 18000)                                │
│     □ TradeStation OAuth valid (token not expired)                          │
│     □ Database connections healthy                                          │
│     □ PM2 processes all online                                              │
│                                                                             │
│  2. CHECK OVERNIGHT EVENTS                                                  │
│     ──────────────────────                                                  │
│     • Scan for gap opens on held positions                                  │
│     • Check earnings announcements (before/after market)                    │
│     • Review overnight news for held symbols                                │
│                                                                             │
│  3. REVIEW OPEN POSITIONS                                                   │
│     ───────────────────────                                                 │
│     • Verify stop-loss orders still valid                                   │
│     • Check for any broker-side issues                                      │
│     • Update position tracking from broker data                             │
│                                                                             │
│  4. VERIFY CODE CHANGES                                                     │
│     ───────────────────────                                                 │
│     • If off-hours evolution made changes: Confirm complete                 │
│     • If testing still running: ABORT and revert                            │
│     • Ensure stable code for market open                                    │
│                                                                             │
│  5. CLEAR STALE DATA                                                        │
│     ─────────────────                                                       │
│     • Flush old prediction cache                                            │
│     • Reset intraday counters                                               │
│     • Prepare fresh logging                                                 │
│                                                                             │
│  6. SEND READY NOTIFICATION                                                 │
│     ────────────────────────                                                │
│     • Push notification via caelum-unified                                  │
│     • Log "System ready for market open"                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Off-Hours Mode: Research & Self-Evolution

### When Active

Off-hours mode begins when orders are no longer authorized:
- If extended hours disabled: 4:00pm ET
- If extended hours enabled: 8:00pm ET

Ends at pre-market prep (9:15am ET next trading day).

### The Evolution Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OFF-HOURS: RESEARCH & EVOLUTION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 1: DAILY REVIEW                                                │  │
│  │                                                                       │  │
│  │  • Analyze all trades from today                                      │  │
│  │  • Calculate metrics: win rate, Sharpe, drawdown, profit velocity     │  │
│  │  • Identify: What worked? What didn't?                                │  │
│  │  • Update agent reputation scores based on outcomes                   │  │
│  │  • Compare to previous days' performance                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ↓                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 2: HYPOTHESIS GENERATION                                       │  │
│  │                                                                       │  │
│  │  Team proposes theories for improvement:                              │  │
│  │                                                                       │  │
│  │  TradingAgent: "MACD crossover + high sentiment → 80% win rate today" │  │
│  │  RiskAgent: "We should weight sector exposure more in tech stocks"    │  │
│  │  ResearchAgent: "FinColl output could be biased 1.2x for momentum"    │  │
│  │                                                                       │  │
│  │  Hypotheses are logged and prioritized by potential impact.           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ↓                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 3: BACKTEST SANDBOX                                            │  │
│  │                                                                       │  │
│  │  For each hypothesis:                                                 │  │
│  │  1. Create isolated test environment (sandbox)                        │  │
│  │  2. Modify feature weights / prediction biases / strategy             │  │
│  │  3. Run backtest on recent data (last 30-90 days)                     │  │
│  │  4. Measure: Profit velocity, win rate, max drawdown                  │  │
│  │  5. Compare to baseline (current production settings)                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ↓                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 4: EVALUATION & DECISION                                       │  │
│  │                                                                       │  │
│  │  Improvement Threshold (auto-approve if ALL met):                     │  │
│  │  • Profit velocity increased >10%                                     │  │
│  │  • Win rate improved or maintained                                    │  │
│  │  • Max drawdown stayed <15%                                           │  │
│  │  • No degradation on out-of-sample data                               │  │
│  │                                                                       │  │
│  │  If threshold met: Proceed to code evolution                          │  │
│  │  If not met: Log findings, archive hypothesis, try next               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ↓                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PHASE 5: CODE EVOLUTION (If approved)                                │  │
│  │                                                                       │  │
│  │  1. Modify running code:                                              │  │
│  │     • Feature weights                                                 │  │
│  │     • Bias adjustments                                                │  │
│  │     • Strategy parameters                                             │  │
│  │     • Agent voting weights                                            │  │
│  │                                                                       │  │
│  │  2. Create git commit with explanation:                               │  │
│  │     ┌───────────────────────────────────────────────────────────────┐ │  │
│  │     │ commit abc123                                                 │ │  │
│  │     │ Author: PIM-System <pim@caelum>                               │ │  │
│  │     │                                                               │ │  │
│  │     │ feat: Increase MACD weight 1.2x → 1.5x                        │ │  │
│  │     │                                                               │ │  │
│  │     │ Backtest Results (30 days):                                   │ │  │
│  │     │ - Profit velocity: +12.3%                                     │ │  │
│  │     │ - Win rate: 54% → 57%                                         │ │  │
│  │     │ - Max drawdown: 8.2% (unchanged)                              │ │  │
│  │     │                                                               │ │  │
│  │     │ Hypothesis: Higher MACD weight captures momentum better       │ │  │
│  │     │ in current market regime.                                     │ │  │
│  │     └───────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  3. PM2 restart affected services                                     │  │
│  │                                                                       │  │
│  │  4. Log change in evolution history                                   │  │
│  │                                                                       │  │
│  │  5. Send notification to human (via caelum-unified)                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      ↓                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  TIMING CONSTRAINT                                                    │  │
│  │                                                                       │  │
│  │  ⚠️  ALL TESTING MUST COMPLETE BEFORE 9:00am ET                        │  │
│  │                                                                       │  │
│  │  If test still running at 9:00am:                                     │  │
│  │  1. ABORT immediately                                                 │  │
│  │  2. Revert any uncommitted changes                                    │  │
│  │  3. Ensure stable code for market open                                │  │
│  │  4. Log incomplete test for next off-hours session                    │  │
│  │                                                                       │  │
│  │  The system MUST be ready and stable by 9:15am pre-market prep.       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Emergency Halt System

### Circuit Breaker Triggers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EMERGENCY HALT TRIGGERS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AUTOMATIC TRIGGERS (per account):                                          │
│  ─────────────────────────────────                                          │
│  • Daily loss exceeds limit (default 2%, configurable)                      │
│  • API failures ≥ 3 consecutive                                             │
│  • Position limit breach                                                    │
│  • Broker connection lost                                                   │
│                                                                             │
│  MANUAL TRIGGERS:                                                           │
│  ────────────────                                                           │
│  • Human presses HALT button in Web UI                                      │
│  • Caelum notification command                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Halt Procedure

```
EMERGENCY HALT ACTIVATED
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. IMMEDIATELY: Stop processing new suggestions                │
│                                                                 │
│  2. IMMEDIATELY: Cancel all pending orders                      │
│                                                                 │
│  3. POSITIONS (configurable per account):                       │
│     • Option A: Close all positions (market orders)             │
│     • Option B: Hold positions but stop new trades              │
│                                                                 │
│  4. NOTIFY HUMAN:                                               │
│     • Push notification via caelum-unified                      │
│     • UI shows prominent alert                                  │
│     • Email notification (if configured)                        │
│                                                                 │
│  5. LOG HALT:                                                   │
│     • Timestamp                                                 │
│     • Trigger reason                                            │
│     • Account state at halt                                     │
│     • All recent discussion transcripts                         │
│                                                                 │
│  6. AWAIT HUMAN RESUME:                                         │
│     • System remains halted until human acknowledges            │
│     • Resume requires explicit action in UI                     │
│     • Human must review halt reason before resuming             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Notification System

### Notification Channels

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION SYSTEM                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PRIMARY CHANNEL: caelum-unified (External Tool)                            │
│  ────────────────────────────────────────────────                           │
│  • Real-time push notifications                                             │
│  • Supports email delivery (configurable)                                   │
│  • Available as MCP tool                                                    │
│                                                                             │
│  NOTIFICATION TYPES:                                                        │
│                                                                             │
│  ┌─────────────────┬──────────────────────────────────────────────────────┐ │
│  │ Type            │ Description                                          │ │
│  ├─────────────────┼──────────────────────────────────────────────────────┤ │
│  │ TRADE_EXECUTED  │ Trade placed (symbol, direction, size, price)        │ │
│  │ POSITION_CLOSED │ Position exited (P&L, hold time)                     │ │
│  │ DISCUSSION      │ Summary of agent discussion (on request)             │ │
│  │ DAILY_SUMMARY   │ End of day P&L and metrics                           │ │
│  │ CODE_EVOLVED    │ System modified its own code                         │ │
│  │ CIRCUIT_BREAKER │ Emergency halt triggered (HIGH PRIORITY)             │ │
│  │ SYSTEM_READY    │ Pre-market prep complete                             │ │
│  │ APPROVAL_NEEDED │ Human input requested (rare)                         │ │
│  └─────────────────┴──────────────────────────────────────────────────────┘ │
│                                                                             │
│  WEB UI VISIBILITY:                                                         │
│  ──────────────────                                                         │
│  • All notifications logged and visible in UI                               │
│  • Unread notifications highlighted                                         │
│  • Human returning to UI sees all alerts since last visit                   │
│  • Filter by account, type, time                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: FinColl & SenVec

### Information Sources

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DATA FLOW ARCHITECTURE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FINCOLL (Port 8002) - Primary Data Source                                  │
│  ─────────────────────────────────────────                                  │
│  • OHLCV price data (TradeStation / YFinance)                               │
│  • Technical indicators (MACD, RSI, Bollinger, etc.)                        │
│  • SenVec sentiment data (already integrated)                               │
│  • FinVec continuous predictions (100 horizons)                             │
│  • Sector/market regime features                                            │
│                                                                             │
│  Agents query FinColl for known symbols:                                    │
│  • Efficient: Already aggregated                                            │
│  • Fresh: Updated continuously during market hours                          │
│  • Complete: All features in one call                                       │
│                                                                             │
│  SENVEC (Port 18000) - Sentiment Source                                     │
│  ─────────────────────────────────────────                                  │
│  • Twitter sentiment                                                        │
│  • Reddit sentiment                                                         │
│  • News sentiment                                                           │
│  • Aggregated 72D sentiment vector                                          │
│                                                                             │
│  Agent access:                                                              │
│  • Usually via FinColl (already integrated)                                 │
│  • Direct query if needed for deep sentiment analysis                       │
│  • Can query for unknown symbols before FinColl adds them                   │
│                                                                             │
│  SYMBOL DISCOVERY:                                                          │
│  ─────────────────                                                          │
│  Agents are NOT restricted to known symbols.                                │
│  If an agent discovers a new profitable opportunity:                        │
│  1. System auto-adds to FinColl watchlist                                   │
│  2. Historical backfill runs automatically                                  │
│  3. Discussion continues with available data                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Shared Memory Architecture

### RL Agents ↔ LLM Agents Shared Memory

The RL agent committee and LLM agent committee share a common memory layer for coordination,
learning feedback, and decision context. This enables both committees to learn from each
other's experiences and maintain consistent state.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SHARED MEMORY ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐     ┌─────────────────────────────┐       │
│  │    RL AGENT COMMITTEE       │     │    LLM AGENT COMMITTEE      │       │
│  │    (9 Trained Agents)       │     │    (Specialized Agents)     │       │
│  │                             │     │                             │       │
│  │  • MomentumAgent (40%)      │     │  • TradingAgent             │       │
│  │  • OptionsAgent (30%)       │     │  • RiskAgent                │       │
│  │  • MacroAgent (20%)         │     │  • SentimentAgent           │       │
│  │  • RiskAgent (10%)          │     │  • ResearchAgent            │       │
│  │  • TechnicalAgent (5%)      │     │  • NewsAgent                │       │
│  │  • SentimentAgent (5%)      │     │  • [FuturesAgent]           │       │
│  │  • VolumeAgent (5%)         │     │  • [OptionsAgent]           │       │
│  │  • SectorRotationAgent (3%) │     │  • [CryptoAgent]            │       │
│  │  • MeanReversionAgent (2%)  │     │                             │       │
│  └──────────────┬──────────────┘     └──────────────┬──────────────┘       │
│                 │                                   │                       │
│                 │         SHARED MEMORY             │                       │
│                 │                                   │                       │
│                 ▼                                   ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  STRUCTURED STATE (PostgreSQL)                              │   │   │
│  │  │  • Current positions and P&L                                │   │   │
│  │  │  • Account configurations                                   │   │   │
│  │  │  • Trade history with outcomes                              │   │   │
│  │  │  • Agent reputation scores                                  │   │   │
│  │  │  • Voting weight adjustments                                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  VECTOR MEMORY (Qdrant)                                     │   │   │
│  │  │  • Trade decision embeddings                                │   │   │
│  │  │  • Market pattern embeddings                                │   │   │
│  │  │  • Learned strategy embeddings                              │   │   │
│  │  │  • Discussion transcript embeddings                         │   │   │
│  │  │  • Similar situation retrieval                              │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  REAL-TIME COORDINATION (Redis)                             │   │   │
│  │  │  • Active suggestions queue                                 │   │   │
│  │  │  • Current discussions in progress                          │   │   │
│  │  │  • Agent availability status                                │   │   │
│  │  │  • Human override flags                                     │   │   │
│  │  │  • Circuit breaker state                                    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  ARTIFACT STORAGE (S3/MinIO)                                │   │   │
│  │  │  • Full analysis artifacts (bypass context limits)          │   │   │
│  │  │  • Discussion transcripts                                   │   │   │
│  │  │  • Backtest results                                         │   │   │
│  │  │  • Evolution history                                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Memory Access Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MEMORY ACCESS BY COMMITTEE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RL COMMITTEE WRITES:                                                       │
│  ────────────────────                                                       │
│  • Pre-screening scores (per symbol, per agent)                             │
│  • Confidence levels from learned experience                                │
│  • Pass/reject decisions with reasoning                                     │
│  • Feature importance weights (learned)                                     │
│  • Agent agreement patterns                                                 │
│                                                                             │
│  RL COMMITTEE READS:                                                        │
│  ───────────────────                                                        │
│  • Trade outcomes (to update learning)                                      │
│  • LLM discussion transcripts (for context)                                 │
│  • Human override patterns (to adjust behavior)                             │
│  • Market regime indicators                                                 │
│                                                                             │
│  LLM COMMITTEE WRITES:                                                      │
│  ─────────────────────                                                      │
│  • Discussion transcripts                                                   │
│  • Vote outcomes and reasoning                                              │
│  • Trade execution records                                                  │
│  • Hypothesis proposals (for off-hours testing)                             │
│  • Agent reputation updates                                                 │
│                                                                             │
│  LLM COMMITTEE READS:                                                       │
│  ────────────────────                                                       │
│  • RL pre-screening scores (which suggestions passed)                       │
│  • Historical similar decisions (vector search)                             │
│  • Current portfolio state                                                  │
│  • Agent reputation scores (for vote weighting)                             │
│  • Human preference patterns                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Learning Feedback Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CROSS-COMMITTEE LEARNING                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RL COMMITTEE PRE-SCREENS                                                │
│     └─> Writes: suggestion_scores to shared memory                          │
│         Example: { symbol: "AAPL", rl_confidence: 0.82, passed: true }      │
│                                                                             │
│  2. LLM COMMITTEE DISCUSSES                                                 │
│     └─> Reads: rl_confidence as input context                               │
│     └─> Writes: discussion_transcript, vote_outcome                         │
│         Example: { decision: "BUY", llm_confidence: 0.75, reasoning: [...] }│
│                                                                             │
│  3. TRADE EXECUTED                                                          │
│     └─> Writes: trade_record with entry details                             │
│                                                                             │
│  4. TRADE OUTCOME KNOWN (hours/days later)                                  │
│     └─> Writes: trade_result { pnl: +2.3%, hold_time: 3 days }              │
│                                                                             │
│  5. BOTH COMMITTEES LEARN                                                   │
│                                                                             │
│     RL Committee:                                                           │
│     └─> Reads: trade_result                                                 │
│     └─> Updates: agent weights, feature importance                          │
│     └─> If RL said PASS and trade lost: decrease confidence                 │
│     └─> If RL said REJECT and LLM overrode and won: learn pattern           │
│                                                                             │
│     LLM Committee:                                                          │
│     └─> Reads: trade_result                                                 │
│     └─> Updates: agent reputation scores                                    │
│     └─> Stores: decision embedding for future retrieval                     │
│     └─> If similar pattern in future: retrieve this decision                │
│                                                                             │
│  6. OFF-HOURS EVOLUTION                                                     │
│     └─> Both committees' learnings inform hypothesis generation             │
│     └─> Backtests validate proposed changes                                 │
│     └─> Code evolution incorporates insights from BOTH committees           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementation Reference

The shared memory architecture is detailed in:
- `docs/technical/SHARED_CONTEXT_ARCHITECTURE.md` - Full implementation guide
- `docs/implementation-guides/RL_FILTER_IMPLEMENTATION.md` - RL committee details

Key code locations:
- PostgreSQL schema: `server/db/schema.sql`
- Qdrant vectors: `engine/pim/storage/vector_store.py`
- Redis coordination: `server/services/redis-client.ts`
- Artifact manager: Referenced in SHARED_CONTEXT_ARCHITECTURE.md

---

## Service Health Monitoring

### Health Checks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERVICE HEALTH CHECKS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Checked continuously (every 60 seconds):                                   │
│                                                                             │
│  ┌─────────────────┬───────────────┬─────────────────────────────────────┐  │
│  │ Service         │ Endpoint      │ Critical?                           │  │
│  ├─────────────────┼───────────────┼─────────────────────────────────────┤  │
│  │ FinColl API     │ :8002/health  │ YES - halt if down                  │  │
│  │ SenVec          │ :18000/health │ NO - degrade gracefully             │  │
│  │ TradeStation    │ OAuth status  │ YES - halt if expired               │  │
│  │ PostgreSQL      │ Connection    │ YES - halt if down                  │  │
│  │ PM2 Processes   │ pm2 list      │ Depends on process                  │  │
│  │ caelum-unified  │ :8090/health  │ NO - lose notifications only        │  │
│  └─────────────────┴───────────────┴─────────────────────────────────────┘  │
│                                                                             │
│  Failure Handling:                                                          │
│  ─────────────────                                                          │
│  • Critical service down → Emergency halt                                   │
│  • Non-critical down → Continue with degraded features                      │
│  • All failures logged and notified                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Settings Reference

### Human-Adjustable Settings

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURABLE SETTINGS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TIMING SETTINGS:                                                           │
│  ────────────────                                                           │
│  • human_override_window_seconds: 5-30 (default: 5)                         │
│  • wind_down_minutes_before_close: 5-30 (default: 15)                       │
│  • pre_market_prep_minutes: 5-30 (default: 15)                              │
│                                                                             │
│  RISK SETTINGS (per account):                                               │
│  ─────────────────────────────                                              │
│  • max_position_size_pct: 1-100 (default: 10)                               │
│  • daily_loss_limit_pct: 0.5-10 (default: 2)                                │
│  • max_portfolio_heat_pct: 10-100 (default: 50)                             │
│  • max_sector_concentration_pct: 10-100 (default: 40)                       │
│                                                                             │
│  ACCOUNT SETTINGS:                                                          │
│  ─────────────────                                                          │
│  • execution_mode: SIM / LIVE (default: SIM, sticky)                        │
│  • management_mode: MANAGED / MANUAL / MONITOR (default: MONITOR)           │
│  • extended_hours_enabled: true / false (default: false)                    │
│  • allowed_asset_classes: [STOCKS, OPTIONS, FUTURES, CRYPTO]                │
│                                                                             │
│  EVOLUTION SETTINGS:                                                        │
│  ───────────────────                                                        │
│  • auto_evolve_threshold_profit_pct: 5-50 (default: 10)                     │
│  • auto_evolve_threshold_winrate_delta: 0-20 (default: 0)                   │
│  • max_evolution_changes_per_night: 1-10 (default: 3)                       │
│                                                                             │
│  NOTIFICATION SETTINGS:                                                     │
│  ──────────────────────                                                     │
│  • notify_on_trade: true / false (default: true)                            │
│  • notify_on_evolution: true / false (default: true)                        │
│  • notify_on_halt: true / false (default: true) ← always true               │
│  • email_notifications: true / false (default: false)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### System Philosophy

PIM is a **living, self-evolving trading system** that:

1. **Operates 24/7** - Never stops, only changes mode
2. **Trades or Researches** - Market hours = trade; Off hours = evolve
3. **Discusses Decisions** - Multi-agent LLM teams vote on every trade
4. **Respects Human Authority** - Human can always observe, override, halt
5. **Evolves Autonomously** - Tests hypotheses and improves its own code
6. **Treats SIM/LIVE Equally** - Same caution, same process, different endpoint

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Time-Based Modes** | Market hours vs off-hours, not state progression |
| **Account-Level Control** | SIM/LIVE toggle per account, sticky |
| **Inner Discussion** | LLM agents debate each trade decision |
| **Human Override Window** | 5-10s to intervene, then auto-proceed |
| **Learned Voting** | Agent weights adjust based on track record |
| **Autonomous Evolution** | Off-hours testing and code modification |
| **Symbol Discovery** | Not restricted to known watchlist |
| **Asset Agnostic** | Agents spawn for new asset classes as needed |

### What This Is NOT

- ❌ A linear progression (Training → Paper → Live)
- ❌ A system that needs human approval for every action
- ❌ Limited to stocks only
- ❌ Static code that doesn't improve
- ❌ Different treatment of SIM vs LIVE accounts

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PIM LIVING SYSTEM                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      24/7 CONTINUOUS LOOP                           │   │
│  │                                                                     │   │
│  │   ┌─────────────┐          ┌─────────────┐          ┌───────────┐  │   │
│  │   │   MARKET    │  ──→──   │ TRANSITION  │  ──→──   │ OFF-HOURS │  │   │
│  │   │   HOURS     │          │  PERIODS    │          │   MODE    │  │   │
│  │   │             │          │             │          │           │  │   │
│  │   │ • Suggest   │          │ • Wind-down │          │ • Review  │  │   │
│  │   │ • Discuss   │          │ • Pre-prep  │          │ • Test    │  │   │
│  │   │ • Trade     │          │ • Cleanup   │          │ • Evolve  │  │   │
│  │   └─────────────┘          └─────────────┘          └───────────┘  │   │
│  │         ↑                                                  │       │   │
│  │         └──────────────────────────────────────────────────┘       │   │
│  │                         (Continuous Loop)                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ACCOUNTS                                    │   │
│  │                                                                     │   │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │   │
│  │   │ Account #1   │   │ Account #2   │   │ Account #N   │           │   │
│  │   │ SIM/MANAGED  │   │ LIVE/MANAGED │   │ SIM/MONITOR  │           │   │
│  │   │ Stocks only  │   │ Stocks+Opts  │   │ All assets   │           │   │
│  │   └──────────────┘   └──────────────┘   └──────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         SERVICES                                    │   │
│  │                                                                     │   │
│  │   FinColl (8002)  │  SenVec (18000)  │  TradeStation  │  caelum    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
