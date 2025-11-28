# PIM Workflow Modes & Transitions

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA COLLECTION LAYER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│  │ TradeStation │    │  YFinance    │    │ AlphaVantage │             │
│  │   (Primary)  │    │  (Fallback)  │    │   (Backup)   │             │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘             │
│         │                   │                   │                      │
│         └───────────────────┴───────────────────┘                      │
│                             │                                          │
│                             ↓                                          │
│                    ┌─────────────────┐                                 │
│                    │   FinColl API   │                                 │
│                    │   (Port 8002)   │                                 │
│                    └────────┬────────┘                                 │
└─────────────────────────────┼──────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      FEATURE ENGINEERING LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        FinColl Pipeline                          │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  1. OHLCV Data (from TradeStation/YFinance)                     │  │
│  │     ↓                                                            │  │
│  │  2. SenVec Features (72D sentiment vector)                      │  │
│  │     - Twitter sentiment (port 18000)                            │  │
│  │     - Reddit sentiment                                           │  │
│  │     - News sentiment                                             │  │
│  │     - Aggregated sentiment scores                               │  │
│  │     ↓                                                            │  │
│  │  3. Technical Features (50D)                                     │  │
│  │     - MACD, RSI, Bollinger Bands                                │  │
│  │     - Volume indicators                                          │  │
│  │     - Price momentum                                             │  │
│  │     ↓                                                            │  │
│  │  4. Sector Features (14D)                                        │  │
│  │     - Sector rotation indicators                                │  │
│  │     - Market regime                                              │  │
│  │     ↓                                                            │  │
│  │  5. Options Flow (5D - when available)                          │  │
│  │     ↓                                                            │  │
│  │  6. Combined 336D Feature Vector                                │  │
│  │     ↓                                                            │  │
│  │  7. FinVec Model Inference (GPU on .27 or .44)                  │  │
│  │     - Input: 336D feature vector                                │  │
│  │     - Output: 100 continuous horizon predictions                │  │
│  │     - Model: finvec_continuous_10epoch.pt (107.7M params)       │  │
│  │     ↓                                                            │  │
│  │  8. Prediction Response:                                         │  │
│  │     {                                                            │  │
│  │       "predictions_continuous": [100 values],                   │  │
│  │       "optimal_horizon": 77,                                    │  │
│  │       "optimal_return": 0.176,                                  │  │
│  │       "uncertainty_continuous": [100 values],                   │  │
│  │       "risk_score": 0.465,                                      │  │
│  │       "direction": "LONG"                                        │  │
│  │     }                                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       DECISION & EXECUTION LAYER                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                    PIM Trading Agent                           │    │
│  │                  (PassiveIncomeMaximizer)                      │    │
│  ├────────────────────────────────────────────────────────────────┤    │
│  │                                                                │    │
│  │  1. Extract Continuous Features:                              │    │
│  │     - pred_peak_value (max of 100 predictions)                │    │
│  │     - pred_peak_horizon (day of peak)                         │    │
│  │     - pred_valley_value (min of 100 predictions)              │    │
│  │     - pred_trend_slope (linear fit of first 20 days)          │    │
│  │     - pred_curve_convexity (2nd derivative)                   │    │
│  │     - pred_optimal_exit (90% of peak per Chapter 2)           │    │
│  │     ↓                                                          │    │
│  │  2. Build MarketState (58 features total)                     │    │
│  │     - Continuous prediction features (12)                     │    │
│  │     - Real-time tick data (4)                                 │    │
│  │     - Context (day_of_week, time_of_day, position) (5)        │    │
│  │     - Ray features (13 - optional)                            │    │
│  │     - Derived features (24)                                   │    │
│  │     ↓                                                          │    │
│  │  3. Policy Network Forward Pass                               │    │
│  │     - Input: 58D state tensor                                 │    │
│  │     - Output: {direction_logits, size_logits, value}          │    │
│  │     ↓                                                          │    │
│  │  4. Select Action (TradingAction)                             │    │
│  │     - direction: LONG/SHORT/HOLD                              │    │
│  │     - position_size: 0.0-0.20 (% of portfolio)                │    │
│  │     - stop_loss: calculated from risk_score                   │    │
│  │     - take_profit: optimal_exit horizon                       │    │
│  │     ↓                                                          │    │
│  │  5. Execute Trade (mode-dependent)                            │    │
│  │                                                                │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Modes

### 1. BACKTEST Mode (Current - Training)

**Purpose**: Train RL agent on historical data without risking capital

**Data Flow**:
```
Historical OHLCV (YFinance)
    ↓
YFinanceProvider.get_historical_bars(start_date, end_date)
    ↓
Iterate through bars sequentially (simulated time)
    ↓
For each bar:
    ├─> Call FinColl /predict (uses current bar as "now")
    ├─> Get continuous predictions
    ├─> Agent selects action
    ├─> Simulate execution (update paper positions)
    └─> Calculate reward based on next bar's price
    ↓
Store (state, action, reward) tuples
    ↓
PPO update every N steps
    ↓
Save checkpoint every M episodes
```

**Services Required**:
- ✅ FinColl API (port 8002) - inference only
- ✅ SenVec API (port 18000) - sentiment features
- ✅ YFinance provider - historical data
- ❌ TradeStation - NOT used (live data not needed)
- ❌ PIM Engine - NOT used (no live trading)
- ❌ Database - NOT strictly required (can use in-memory)

**Current Training Script**:
```python
# train_trading_agent_ppo_improved.py
env = ImprovedTradingEnvironment(
    symbols=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
    data_provider=YFinanceProvider(),
    fincoll_url='http://localhost:8002'
)

for episode in range(100):
    state = env.reset()  # Start at random point in history
    
    for step in range(100):
        action = agent.select_action(state)
        next_state, reward, done = env.step(action)
        
        # Store experience
        # Update policy with PPO
```

**Outputs**:
- `checkpoints/trading_agent_continuous_ppo.pt` - trained policy
- `trading_agent_continuous_ppo_training.png` - learning curves
- Training logs with episode returns

---

### 2. PAPER TRADING Mode (Validation)

**Purpose**: Test trained agent on live market data without real money

**Data Flow**:
```
Live Market Data (TradeStation primary, YFinance fallback)
    ↓
Real-time price updates (every 1 min for intraday, daily for swing)
    ↓
For each update:
    ├─> Call FinColl /predict (uses latest OHLCV)
    ├─> Get continuous predictions
    ├─> Agent selects action (using trained policy)
    ├─> Execute in PAPER account (simulated)
    │   - Track positions in memory/database
    │   - Calculate P&L using real market prices
    │   - Log all trades
    └─> Store performance metrics
    ↓
Daily summary reports
    ↓
Compare to benchmarks (S&P 500, buy-and-hold)
```

**Services Required**:
- ✅ FinColl API (port 8002)
- ✅ SenVec API (port 18000)
- ✅ TradeStation OAuth - live prices
- ✅ YFinance - fallback data
- ✅ PIM Engine (port 5005) - paper trading mode
- ✅ PostgreSQL - trade logging
- ✅ Redis - caching

**Configuration**:
```python
# paper_trading.py
account = AccountConfig(
    account_id='paper_trading_001',
    account_type=AccountType.MARGIN,
    broker='paper',  # ← Simulated execution
    initial_capital=100000.0,
    max_position_size=0.20
)

agent = PIMTradingAgent.load('checkpoints/trading_agent_continuous_ppo.pt')
agent.eval()  # Disable exploration

# Run continuously
while True:
    prices = get_live_prices()
    for symbol in watchlist:
        action = agent.decide(symbol, prices)
        execute_paper(action)  # Simulated fill
    sleep(60)  # Wait 1 minute
```

**Metrics Tracked**:
- Total return (%)
- Sharpe ratio
- Max drawdown
- Win rate
- Average profit per trade
- Comparison to S&P 500

---

### 3. LIVE TRADING Mode (Production)

**Purpose**: Execute real trades with real money

**Data Flow**:
```
Live Market Data (TradeStation API)
    ↓
Real-time price updates + Level 2 data
    ↓
For each update:
    ├─> Call FinColl /predict
    ├─> Get continuous predictions
    ├─> Agent selects action
    ├─> Risk checks (position limits, volatility, correlation)
    │   ├─> Max position size: 20% of portfolio
    │   ├─> Max portfolio heat: 50%
    │   ├─> Sector diversification check
    │   └─> Correlation matrix check
    ├─> If checks pass:
    │   └─> Execute via TradeStation API
    │       ├─> Submit market/limit order
    │       ├─> Wait for fill confirmation
    │       ├─> Update positions in database
    │       └─> Log trade in audit trail
    └─> Store all decisions (taken AND rejected)
    ↓
Real-time P&L tracking
    ↓
Alerts on:
    - Large losses (>2% daily drawdown)
    - Position limit breaches
    - API failures
    - Model degradation
```

**Services Required**:
- ✅ ALL services from paper trading, PLUS:
- ✅ TradeStation API - order execution
- ✅ Caelum MCP - notifications
- ✅ Monitoring/alerting system
- ✅ Audit logging to PostgreSQL

**Safety Features**:
```python
# pim_service.py - Production mode
class LiveTradingEngine:
    def execute_action(self, action: TradingAction):
        # 1. Pre-execution checks
        if not self.risk_manager.check_limits(action):
            self.log.warning(f"Action rejected by risk manager: {action}")
            return None
        
        # 2. Circuit breaker (halt if daily loss > 5%)
        if self.portfolio.daily_pnl < -0.05 * self.portfolio.value:
            self.halt_trading("Circuit breaker triggered")
            return None
        
        # 3. Submit order
        order = self.broker.submit_order(action)
        
        # 4. Wait for fill (with timeout)
        fill = self.wait_for_fill(order, timeout=30)
        
        # 5. Update positions
        self.portfolio.update(fill)
        
        # 6. Audit log
        self.db.log_trade(fill)
        
        return fill
```

---

## Mode Transitions

### Transition 1: BACKTEST → PAPER TRADING

**Prerequisites**:
1. ✅ Training complete (100+ episodes)
2. ✅ Learning curve shows improvement
3. ✅ Model checkpoint saved
4. ✅ Validation on held-out historical data shows positive returns

**Checklist**:

```bash
# Step 1: Verify trained model exists
ls -lh checkpoints/trading_agent_continuous_ppo.pt

# Step 2: Check services are running
pm2 list | grep -E "fincoll|senvec"
# Should see:
#   - fincoll-continuous (online)
#   - senvec-aggregator (online)
#   - senvec-news (online)
#   - senvec-social (online)

# Step 3: Test TradeStation OAuth
curl http://localhost:8002/api/v1/providers/tradestation/status
# Should return: {"authenticated": true, ...}

# Step 4: Verify database connection
psql -h localhost -U rford -d pim -c "SELECT COUNT(*) FROM trades;"

# Step 5: Start paper trading
cd PassiveIncomeMaximizer
uv run python engine/paper_trading.py \
    --mode paper \
    --model checkpoints/trading_agent_continuous_ppo.pt \
    --symbols AAPL MSFT GOOGL TSLA NVDA \
    --capital 100000 \
    --max-position-size 0.20

# Step 6: Monitor logs
tail -f logs/paper_trading_$(date +%Y%m%d).log

# Step 7: Check positions in database
psql -d pim -c "SELECT symbol, position, entry_price, current_pnl FROM positions WHERE account_id='paper_trading_001';"

# Step 8: Daily performance check
python engine/scripts/analyze_paper_trading_performance.py --days 7
```

**Validation Period**: Minimum 2 weeks

**Success Criteria**:
- [ ] Positive total return (>0%)
- [ ] Sharpe ratio > 0.5
- [ ] Max drawdown < 15%
- [ ] Win rate > 45%
- [ ] No system crashes or API failures
- [ ] All trades logged correctly

---

### Transition 2: PAPER TRADING → LIVE TRADING

**Prerequisites**:
1. ✅ Paper trading shows consistent profits (2+ weeks)
2. ✅ All validation criteria met
3. ✅ Risk management tested and working
4. ✅ TradeStation account funded
5. ✅ Legal/compliance reviewed

**CRITICAL CHECKLIST** (Must complete in order):

```bash
# ═══════════════════════════════════════════════════════════
# PHASE 1: PRE-FLIGHT CHECKS (30 minutes)
# ═══════════════════════════════════════════════════════════

# 1.1: Verify all services healthy
pm2 list
# ALL must show "online" status

# 1.2: Check TradeStation connection
curl http://localhost:8002/api/v1/providers/tradestation/status
# Must return authenticated=true, expires_in > 3600

# 1.3: Verify account balance
curl http://localhost:8002/api/v1/account/balance
# Confirm: available_cash >= $10,000

# 1.4: Test FinColl predictions
curl -X POST http://localhost:8002/api/v1/inference/predict/AAPL
# Must return predictions_continuous[100], optimal_horizon

# 1.5: Test SenVec sentiment
curl http://localhost:18000/api/sentiment/AAPL
# Must return sentiment scores

# 1.6: Database integrity check
psql -d pim -c "SELECT COUNT(*) FROM trades WHERE account_id='paper_trading_001';"
# Should have 50+ paper trades logged

# 1.7: Verify paper trading performance
python engine/scripts/analyze_paper_trading_performance.py --days 14
# Expected output:
#   Total Return: +5.2%
#   Sharpe Ratio: 0.8
#   Max Drawdown: -3.1%
#   Win Rate: 52%

# 1.8: Backup current configuration
cp config/production.yaml config/production_backup_$(date +%Y%m%d).yaml
pg_dump pim > backups/pim_pre_live_$(date +%Y%m%d).sql

# ═══════════════════════════════════════════════════════════
# PHASE 2: RISK CONFIGURATION (15 minutes)
# ═══════════════════════════════════════════════════════════

# 2.1: Set conservative position limits for first day
cat > config/risk_limits.yaml << EOF
max_position_size: 0.10  # Start at 10% (vs 20% in paper)
max_portfolio_heat: 0.30  # Max 30% of capital at risk
daily_loss_limit: 0.02    # Halt if lose >2% in one day
max_daily_trades: 5       # Limit to 5 trades/day initially
min_time_between_trades: 300  # 5 minutes between trades
max_sector_exposure: 0.40     # Max 40% in one sector
EOF

# 2.2: Enable circuit breakers
cat > config/circuit_breakers.yaml << EOF
enabled: true
triggers:
  - type: daily_loss
    threshold: -0.02
    action: halt_trading
  - type: api_failure
    threshold: 3
    action: halt_trading
  - type: position_limit_breach
    action: close_position
EOF

# 2.3: Configure notifications
cat > config/notifications.yaml << EOF
email: roderick@swdatasci.com
sms: true  # For critical alerts
slack_webhook: <WEBHOOK_URL>
alert_on:
  - trade_executed
  - position_closed
  - daily_pnl_update
  - risk_limit_breach
  - system_error
EOF

# ═══════════════════════════════════════════════════════════
# PHASE 3: DRY RUN (10 minutes)
# ═══════════════════════════════════════════════════════════

# 3.1: Start in SIMULATION mode (live data, no execution)
python engine/pim_service.py \
    --mode simulate \
    --model checkpoints/trading_agent_continuous_ppo.pt \
    --symbols AAPL MSFT GOOGL

# 3.2: Watch logs for 5 minutes
tail -f logs/pim_simulate_$(date +%Y%m%d).log

# 3.3: Verify decisions are being made correctly
# Should see:
#   - Predictions fetched from FinColl
#   - Continuous features extracted
#   - Actions selected
#   - Risk checks performed
#   - Simulated execution (no real orders)

# 3.4: Stop simulation
pkill -f pim_service.py

# ═══════════════════════════════════════════════════════════
# PHASE 4: GO LIVE (5 minutes)
# ═══════════════════════════════════════════════════════════

# 4.1: Create live trading account config
cat > config/live_account.yaml << EOF
account_id: live_production_001
account_type: MARGIN
broker: tradestation
initial_capital: 10000.00
max_position_size: 0.10
allow_short_trades: false  # Start with longs only
EOF

# 4.2: Start PIM Engine in LIVE mode
pm2 start engine/pim_service.py \
    --name pim-live \
    -- \
    --mode live \
    --model checkpoints/trading_agent_continuous_ppo.pt \
    --symbols AAPL MSFT GOOGL \
    --config config/live_account.yaml

# 4.3: Verify it started
pm2 logs pim-live --lines 20

# 4.4: Monitor first trade
tail -f logs/pim_live_$(date +%Y%m%d).log

# Expected first trade within 1-5 minutes

# ═══════════════════════════════════════════════════════════
# PHASE 5: CONTINUOUS MONITORING (Ongoing)
# ═══════════════════════════════════════════════════════════

# 5.1: Real-time position monitoring (run in separate terminal)
watch -n 10 "psql -d pim -c \"SELECT symbol, position, entry_price, current_price, current_pnl FROM positions WHERE account_id='live_production_001' AND position != 0;\""

# 5.2: Daily P&L tracking
watch -n 60 "psql -d pim -c \"SELECT SUM(current_pnl) as total_pnl FROM positions WHERE account_id='live_production_001';\""

# 5.3: Trade log audit
watch -n 30 "psql -d pim -c \"SELECT symbol, action, quantity, price, timestamp FROM trades WHERE account_id='live_production_001' ORDER BY timestamp DESC LIMIT 5;\""

# 5.4: Check for alerts
tail -f logs/alerts_$(date +%Y%m%d).log

# ═══════════════════════════════════════════════════════════
# EMERGENCY PROCEDURES
# ═══════════════════════════════════════════════════════════

# HALT ALL TRADING (if something goes wrong)
python engine/scripts/emergency_halt.py --reason "manual_intervention"

# CLOSE ALL POSITIONS (nuclear option)
python engine/scripts/close_all_positions.py --account live_production_001 --confirm

# ROLLBACK TO PAPER TRADING
pm2 stop pim-live
pm2 start engine/paper_trading.py --name pim-paper
```

**First Day Limits**:
- Max capital deployed: $2,000 (20% of $10K account)
- Max position size: 10% ($1,000 per position)
- Max daily trades: 5
- Allowed symbols: AAPL, MSFT, GOOGL (high liquidity only)
- Trading hours: 10:00 AM - 3:30 PM ET (avoid open/close)

**Gradual Ramp-Up**:
- **Week 1**: Max $2K deployed, 10% position size
- **Week 2**: Max $5K deployed, 15% position size (if Week 1 profitable)
- **Week 3**: Max $7K deployed, 15% position size (if Week 2 profitable)
- **Week 4+**: Full $10K, 20% position size (if all previous weeks profitable)

---

## Service Health Monitoring

**During ALL modes**, monitor these services:

```bash
# Create monitoring script
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash

echo "=== Service Health Check ==="
echo ""

# FinColl API
FINCOLL=$(curl -s -w "%{http_code}" http://localhost:8002/health -o /dev/null)
echo "FinColl API (8002): $([[ $FINCOLL == "200" ]] && echo "✅ OK" || echo "❌ DOWN")"

# SenVec Aggregator
SENVEC=$(curl -s -w "%{http_code}" http://localhost:18000/health -o /dev/null)
echo "SenVec API (18000): $([[ $SENVEC == "200" ]] && echo "✅ OK" || echo "❌ DOWN")"

# PostgreSQL
psql -d pim -c "SELECT 1" > /dev/null 2>&1
echo "PostgreSQL: $([[ $? == "0" ]] && echo "✅ OK" || echo "❌ DOWN")"

# PM2 processes
PM2_COUNT=$(pm2 jlist | jq '[.[] | select(.pm2_env.status=="online")] | length')
echo "PM2 Services: $PM2_COUNT online"

# GPU availability (for inference)
if nvidia-smi > /dev/null 2>&1; then
    GPU_MEM=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    echo "GPU Memory Free: ${GPU_MEM}MB"
else
    echo "GPU: ⚠️  Not available"
fi

echo ""
echo "=== Quick Test ==="
curl -s -X POST http://localhost:8002/api/v1/inference/predict/AAPL | jq -r '"Predictions: \(.predictions_continuous | length) horizons, Optimal: Day \(.optimal_horizon)"'
EOF

chmod +x scripts/health_check.sh

# Run every 5 minutes
crontab -e
# Add: */5 * * * * /path/to/scripts/health_check.sh >> /var/log/pim_health.log 2>&1
```

---

## Summary

**Current State**: BACKTEST MODE
- Training RL agent on historical data
- Services needed: FinColl, SenVec, YFinance
- No real execution
- Output: Trained policy checkpoint

**Next State**: PAPER TRADING MODE
- Validate on live data, paper execution
- Services needed: All backtest + TradeStation + PIM Engine + DB
- Success criteria: 2+ weeks profitable

**Final State**: LIVE TRADING MODE
- Real money, real trades
- Full service stack required
- Strict risk limits
- Gradual ramp-up over 4 weeks
- Emergency halt procedures ready

**Key Principle**: Each mode transition requires FULL validation before proceeding. Never skip paper trading validation.
