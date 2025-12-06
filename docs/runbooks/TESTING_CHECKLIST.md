# Testing Checklist - Option A (Drift Monitoring) & Option D (Trading System)

## Pre-Commit Testing Requirements

### ✅ Phase 1: Syntax Validation
- [x] Python syntax validation (finvec services)
- [x] TypeScript compilation (PIM routes and services)
- [x] Import validation

### Phase 2: Unit Tests (Required)

#### Python Components
- [ ] **Drift Monitor** (`finvec/services/drift_monitor.py`)
  - [ ] Test HTTP API calls to PIM
  - [ ] Test retraining trigger logic
  - [ ] Test drift history tracking

- [ ] **V4Prediction Wrapper** (`finvec/inference/v4_prediction.py`)
  - [ ] Test from_ensemble_prediction conversion
  - [ ] Test to_caelum_format output
  - [ ] Test all required fields present

- [ ] **Trading Service Integration** (`finvec/services/finvec_trading_service.py`)
  - [ ] Test drift_monitor_task execution
  - [ ] Test symbol aggregation (positions + scanner)
  - [ ] Test logging and error handling

#### TypeScript Components
- [ ] **Drift API Endpoint** (`server/routes/finvec-learning-routes.ts:320-377`)
  - [ ] Test POST /api/finvec/drift/monitor with valid data
  - [ ] Test with missing symbols array
  - [ ] Test with invalid lookbackDays
  - [ ] Verify response format matches spec

- [ ] **Drift Detector** (`server/services/finvec/drift-detector.ts`)
  - [ ] Test feature drift detection
  - [ ] Test prediction drift detection
  - [ ] Test concept drift detection
  - [ ] Test monitorDrift with multiple symbols

### Phase 3: Integration Tests (Required)

- [ ] **Python → TypeScript Drift Flow**
  - [ ] Start PIM server
  - [ ] Call drift monitor from Python
  - [ ] Verify HTTP request reaches PIM
  - [ ] Verify drift reports returned correctly
  - [ ] Check error handling (network failures, timeouts)

- [ ] **Trading Cycle Dry Run**
  - [ ] Run `python tests/test_trading_cycle.py --dry-run --symbol AAPL`
  - [ ] Verify scanner executes
  - [ ] Verify data fetching works
  - [ ] Verify inference runs
  - [ ] Verify signal generation logic
  - [ ] Check dry-run order simulation

### Phase 4: TradeStation Connection Tests (Market Hours Required)

- [ ] **Data Fetching**
  - [ ] Verify TradeStation token is valid
  - [ ] Fetch minute bars for test symbol
  - [ ] Fetch daily bars for test symbol
  - [ ] Verify no rate limit errors
  - [ ] Test token refresh mechanism

- [ ] **SIM Account Access**
  - [ ] Verify SIM account is accessible
  - [ ] Check account buying power
  - [ ] Verify market hours detection
  - [ ] Test order validation (without placement)

### Phase 5: Live SIM Trading Tests (Market Hours Required)

⚠️  **ONLY DURING MARKET HOURS: 9:30 AM - 4:00 PM ET**

- [ ] **Single Symbol Test**
  - [ ] Run: `python tests/test_trading_cycle.py --live --symbol AAPL`
  - [ ] Verify order placed on TradeStation SIM
  - [ ] Check order confirmation received
  - [ ] Verify position tracked in PositionManager
  - [ ] Check bracket orders (stop loss, profit target)

- [ ] **Multi-Symbol Test**
  - [ ] Run: `python tests/test_trading_cycle.py --live --limit 3`
  - [ ] Verify max positions limit enforced
  - [ ] Check risk management applied
  - [ ] Verify position sizing calculations
  - [ ] Monitor for order rejections

### Phase 6: End-to-End Validation

- [ ] **Full Service Test** (Run for 30 minutes)
  - [ ] Start FinVec trading service
  - [ ] Monitor continuous scanner operation
  - [ ] Watch for order placements
  - [ ] Check drift monitoring execution (after 6 hours or forced)
  - [ ] Verify position updates
  - [ ] Check P&L tracking

- [ ] **Error Scenarios**
  - [ ] Network failure during API call
  - [ ] Invalid symbol provided
  - [ ] Insufficient buying power
  - [ ] Market closed order attempt
  - [ ] TradeStation API rate limit hit

### Phase 7: Performance Tests

- [ ] **API Response Times**
  - [ ] Drift monitoring API < 5 seconds
  - [ ] Order placement API < 2 seconds
  - [ ] Scanner cycle < 60 seconds (for 50 symbols)

- [ ] **Resource Usage**
  - [ ] Memory usage stable (no leaks)
  - [ ] CPU usage reasonable
  - [ ] No excessive logging

## Test Execution Commands

### Python Tests
```bash
# Syntax validation
python3 -m py_compile services/finvec_trading_service.py
python3 -m py_compile services/drift_monitor.py
python3 -m py_compile inference/v4_prediction.py

# Dry run trading cycle
python tests/test_trading_cycle.py --dry-run --symbol AAPL

# Live SIM test (market hours only)
python tests/test_trading_cycle.py --live --symbol AAPL
```

### TypeScript Tests
```bash
# Type checking
npx tsc --noEmit server/routes/finvec-learning-routes.ts

# Feature tests (requires MongoDB on port 27117)
MONGODB_URL="mongodb://pim_user:pim_password@10.32.3.27:27117/PIM_PROD?authSource=admin" \
  npx jest server/tests/feature/finvec-caelum-integration.feature.test.ts

# API endpoint tests (requires PIM server running)
curl -X POST http://10.32.3.27:3000/api/finvec/drift/monitor \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "lookbackDays": 7}'
```

### Integration Tests
```bash
# Start PIM server
cd PassiveIncomeMaximizer && npm run dev

# In another terminal, test drift monitoring
cd finvec
python -c "
from services.drift_monitor import DriftMonitor
monitor = DriftMonitor()
report = monitor.check_drift(['AAPL', 'MSFT', 'GOOGL'], lookback_days=7)
print(report)
"
```

## Success Criteria

Before committing, ALL of the following must pass:

1. ✅ All Python files pass syntax validation
2. ✅ All TypeScript files compile without errors
3. ✅ Drift monitoring API endpoint accessible and returns valid JSON
4. ✅ Dry-run trading cycle completes without exceptions
5. ⏳ TradeStation connection verified (if testing during market hours)
6. ⏳ At least one successful SIM order placement (if testing during market hours)

## Notes

- **Market Hours**: Many tests require market hours (9:30 AM - 4:00 PM ET)
- **Current Time**: 12:17 AM ET (MARKET CLOSED)
- **Next Market Open**: Tuesday, October 28, 2025 at 9:30 AM ET
- **Test Symbols**: AAPL, MSFT, GOOGL, TSLA, NVDA
- **SIM Account**: TradeStation paper trading account required

## Test Results

### Date: 2025-10-28 00:17 ET

| Test Category | Status | Notes |
|--------------|--------|-------|
| Syntax Validation | ✅ PASS | All Python/TS files valid |
| Unit Tests | ⏳ PENDING | Requires execution |
| Integration Tests | ⏳ PENDING | Requires PIM server |
| TradeStation Connection | ⏳ PENDING | Requires market hours |
| SIM Order Placement | ⏳ PENDING | Requires market hours |
| End-to-End | ⏳ PENDING | Requires market hours |

---

**COMMIT BLOCKED UNTIL**: Minimum tests complete (syntax ✅, dry-run ⏳, integration ⏳)
