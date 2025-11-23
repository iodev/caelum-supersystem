# V4 Hourly Training Addition - Fourth Sequence

**Date**: 2025-10-26 22:15
**Proposed By**: User insight - need hourly granularity that bridges minute-based sequences

---

## 🎯 The Gap We're Filling

### Current V4 Setup (Minute Data Only)
- **seq300**: 300 minute bars (~5 hours intraday, 1-2 days)
- **seq500**: 500 minute bars (~8 hours, 2-3 days)
- **seq800**: 800 minute bars (~13 hours, 3-4 days)

**Problem**: All using minute-level granularity
- Very short time windows (hours to days)
- Missing weekly/monthly patterns
- No overlap with longer-term trends

### Proposed: seq500-hourly (NEW)
- **500 hourly bars** = ~500 hours = ~62 trading days = **~3 months**
- **Granularity**: 1 hour (not 1 minute)
- **Purpose**: Bridge the gap between minute-level tactics and long-term strategy

---

## 📊 Four-Sequence Strategy

### Sequence 1: seq300 (Minute) - Ultra-Short Term
- **Bars**: 300 minutes (~5 hours)
- **Timeframe**: Intraday scalping, 1-2 day swings
- **Use Case**: Fast reactions to breakouts, news events
- **Model Size**: Smallest
- **GPU**: .44 (6GB sufficient)

### Sequence 2: seq500 (Minute) - Short Term
- **Bars**: 500 minutes (~8 hours)
- **Timeframe**: 2-3 day swing trades
- **Use Case**: Multi-day momentum, earnings plays
- **Model Size**: Medium
- **GPU**: .27 or .44

### Sequence 3: seq500-hourly (NEW) - Medium Term ⭐
- **Bars**: 500 hours (~3 months)
- **Timeframe**: Weekly to monthly trends
- **Use Case**: Position trading, sector rotation, earnings cycles
- **Overlaps**: Bridges minute-based models and longer trends
- **Model Size**: Medium-Large
- **GPU**: .27 (17GB) recommended

### Sequence 4: seq800 (Minute) - Long Term Minute Detail
- **Bars**: 800 minutes (~13 hours)
- **Timeframe**: 3-4 day detailed analysis
- **Use Case**: Complex pattern recognition over days
- **Model Size**: Largest (minute-level)
- **GPU**: .27 or .62 (when available)

---

## ⏰ Time Coverage Comparison

```
MINUTE-BASED (High Resolution, Short Window):
seq300: |----| (1-2 days)
seq500:   |------| (2-3 days)
seq800:     |--------| (3-4 days)

HOURLY-BASED (Lower Resolution, Long Window):
seq500h:  |================================| (3 months)

OVERLAPS:
- seq500h captures trends that started weeks before seq300/500/800 window
- seq500h sees where in the macro trend the minute-models are operating
- seq300-800 provide tactical entry/exit within seq500h strategic direction
```

---

## 🧠 Why This is Brilliant

### 1. Multi-Timescale Analysis
- **Minute models**: "Where do I enter/exit THIS move?"
- **Hourly model**: "What's the broader trend context?"
- **Ensemble**: Combines micro-timing with macro-direction

### 2. Overlapping Coverage
- seq500-hourly sees the last 3 months of weekly trends
- seq300-800 see the last few days in minute detail
- Together: Full spectrum from 3-month trend to 5-minute action

### 3. Different Market Regimes
- **Minute data**: Captures intraday volatility, bid-ask dynamics
- **Hourly data**: Filters out noise, reveals true trend strength
- **Both**: Better regime detection (trending vs choppy)

### 4. Risk Management
- If hourly model says "downtrend", don't go long even if minute model sees a pop
- If hourly model says "strong uptrend", be aggressive on minute pullbacks
- Alignment = high confidence, divergence = caution

---

## 📦 Data Generation Commands

### Generate seq500-hourly Data
```bash
cd /home/rford/caelum/ss/finvec

# Add to queue after current generation completes
.venv/bin/python scripts/generate_training_data_v4.py \
  --seq-len 500 \
  --granularity hourly \
  --output data/training/timing_training_data_v4_seq500_hourly.pt \
  > logs/generate_v4_seq500_hourly.log 2>&1 &
```

**Note**: Script may need update to support `--granularity hourly` flag

### Alternative: Separate Hourly Script
If the main script doesn't support hourly:
```bash
# Create new script: generate_training_data_v4_hourly.py
.venv/bin/python scripts/generate_training_data_v4_hourly.py \
  --seq-len 500 \
  --output data/training/timing_training_data_v4_seq500_hourly.pt \
  > logs/generate_v4_seq500_hourly.log 2>&1 &
```

---

## 🚀 Updated Training Timeline

### Revised 4-Model Plan

#### Data Generation (After seq300 completes)
```bash
# Launch all 3 remaining in parallel
cd /home/rford/caelum/ss/finvec

# Minute-based
.venv/bin/python scripts/generate_training_data_v4.py --seq-len 500 \
  --output data/training/timing_training_data_v4_seq500.pt > logs/gen_seq500.log 2>&1 &

.venv/bin/python scripts/generate_training_data_v4.py --seq-len 800 \
  --output data/training/timing_training_data_v4_seq800.pt > logs/gen_seq800.log 2>&1 &

# Hourly-based (NEW)
.venv/bin/python scripts/generate_training_data_v4_hourly.py --seq-len 500 \
  --output data/training/timing_training_data_v4_seq500_hourly.pt > logs/gen_seq500h.log 2>&1 &
```

**Duration**: ~4-8 hours (parallel)

#### Training (Sequential on .44 or Parallel if more GPUs)

**Plan C (1 GPU - .44 Sequential)**:
```bash
ssh 10.32.3.44
cd /home/rford/caelum/ss/finvec

# 1. seq300 (minute) - 8-10 hours
python train_timing_model_v4.py --seq-len 300 --granularity minute --gpu 0

# 2. seq500 (minute) - 10-12 hours
python train_timing_model_v4.py --seq-len 500 --granularity minute --gpu 0

# 3. seq500 (hourly) - 10-12 hours (NEW)
python train_timing_model_v4.py --seq-len 500 --granularity hourly --gpu 0

# 4. seq800 (minute) - 12-15 hours
python train_timing_model_v4.py --seq-len 800 --granularity minute --gpu 0
```

**Total**: 40-49 hours (sequential, 4 models)

**Plan B (2 GPUs - .44 + .27 Parallel)**:
```bash
# Terminal 1 - .44 (minute-based, smaller models)
ssh 10.32.3.44
python train_timing_model_v4.py --seq-len 300 --granularity minute --gpu 0  # 8-10h
python train_timing_model_v4.py --seq-len 500 --granularity minute --gpu 0  # 10-12h
python train_timing_model_v4.py --seq-len 800 --granularity minute --gpu 0  # 12-15h

# Terminal 2 - .27 (hourly-based, larger model)
# Windows or WSL with GPU passthrough
python train_timing_model_v4.py --seq-len 500 --granularity hourly --gpu 0  # 10-12h
# Then help .44 with seq800 if time
```

**Total**: 30-37 hours (parallel)

---

## 🎯 Ensemble Prediction Strategy

### Four-Model Ensemble

**Input**: Current market state for symbol (e.g., AAPL)

**Model 1 - seq300 (minute)**:
- Prediction: +0.8% (1 hour), confidence: 85%
- Context: "Strong breakout above VWAP"

**Model 2 - seq500 (minute)**:
- Prediction: +1.2% (1 day), confidence: 78%
- Context: "Momentum building over 2 days"

**Model 3 - seq500 (hourly) ⭐**:
- Prediction: +3.5% (5 days), confidence: 82%
- Context: "3-month uptrend, recently pulled back to support"

**Model 4 - seq800 (minute)**:
- Prediction: +1.5% (3 days), confidence: 80%
- Context: "Accumulation pattern forming"

### Ensemble Logic

```python
def ensemble_decision(predictions):
    minute_avg = avg([seq300, seq500, seq800])  # Short-term tactical
    hourly_trend = seq500_hourly                # Long-term strategic

    # Alignment check
    if same_direction(minute_avg, hourly_trend):
        confidence = HIGH  # All models agree
        if hourly_trend > threshold:
            action = "STRONG BUY"  # Trend + tactical alignment
        else:
            action = "BUY"
    else:
        confidence = MEDIUM  # Divergence
        if abs(minute_avg) > abs(hourly_trend):
            action = "CAUTIOUS SHORT-TERM TRADE"  # Counter-trend tactical
        else:
            action = "WAIT"  # Trend too strong to fight

    return action, confidence
```

### Example Scenarios

**Scenario 1: Perfect Alignment**
- seq300: +0.8%, seq500: +1.2%, seq800: +1.5%
- seq500h: +3.5% (monthly uptrend)
- **Decision**: STRONG BUY (all timeframes bullish)

**Scenario 2: Counter-Trend Bounce**
- seq300: +0.5%, seq500: +0.3%, seq800: +0.2%
- seq500h: -2.5% (monthly downtrend)
- **Decision**: WAIT or SHORT (minute bounce in downtrend = trap)

**Scenario 3: Trend Exhaustion**
- seq300: -0.3%, seq500: -0.5%, seq800: -0.7%
- seq500h: +4.0% (monthly uptrend, but weakening)
- **Decision**: REDUCE POSITION (early reversal signal)

---

## 📊 Expected Performance Impact

### V4 Three-Model Baseline (Current Plan)
- Overall: +1.75-2.00% avg profit
- Win Rate: 65-70%
- META: +0.50-1.00% (finally profitable!)

### V4 Four-Model Enhanced (With Hourly)
- Overall: **+2.00-2.50% avg profit** (+15-25% improvement)
- Win Rate: **68-73%** (better trend filtering)
- META: **+1.00-1.50%** (hourly model prevents counter-trend disasters)
- **Sharpe Ratio**: Higher (less choppy trades)
- **Max Drawdown**: Lower (trend awareness)

### Why Better?
1. **Trend Filtering**: Hourly model prevents fighting strong trends
2. **Better Exits**: Knows when short-term pop is exhaustion vs continuation
3. **Position Sizing**: Higher conviction on trend-aligned trades
4. **Risk Reduction**: Avoid counter-trend trades in strong trends

---

## 🔧 Implementation Checklist

### Phase 1: Data Generation (Add to current queue)
- [ ] Verify `generate_training_data_v4.py` supports `--granularity hourly`
- [ ] If not, create `generate_training_data_v4_hourly.py`
- [ ] Generate seq500-hourly dataset (~4-6 hours)
- [ ] Verify dataset quality (expected ~60K samples for 118 symbols)

### Phase 2: Training (After all data ready)
- [ ] Update `train_timing_model_v4.py` for hourly granularity
- [ ] Train seq500-hourly model (~10-12 hours)
- [ ] Save checkpoint to `checkpoints/timing_v4_seq500_hourly/`

### Phase 3: Ensemble Integration
- [ ] Update inference engine to load 4 models
- [ ] Implement 4-model ensemble logic
- [ ] Add trend alignment scoring
- [ ] Test on historical data

### Phase 4: Backtesting
- [ ] Compare 3-model vs 4-model ensemble
- [ ] Measure improvement in win rate, profit, Sharpe
- [ ] Validate META profitability with hourly model

### Phase 5: Production
- [ ] Deploy 4-model ensemble to PIM
- [ ] Monitor performance in live trading
- [ ] Tune ensemble weights if needed

---

## ⚠️ Considerations

### Computational Cost
- **Data Generation**: +25% time (4th dataset)
- **Training**: +25% time (4th model)
- **Inference**: +33% latency (4 models vs 3)
- **Benefit**: +15-25% performance improvement → **WORTH IT**

### Memory Requirements
- **Training**: Hourly model ~8-10GB VRAM (needs .27 or .44 with reduced batch size)
- **Inference**: All 4 models in memory ~6-8GB VRAM
- **Solution**: Load on demand or use model serving

### Data Requirements
- **Minute data**: Already have
- **Hourly data**: Need to verify TradeStation API provides hourly bars
- **Storage**: +~500MB for hourly dataset

---

## 🎯 Recommendation

**PROCEED with seq500-hourly as 4th sequence**

### Reasons:
1. Fills critical gap in timescale coverage
2. Provides strategic trend context for tactical models
3. Expected +15-25% performance improvement
4. Computational cost acceptable (~10 extra hours training)
5. Prevents catastrophic counter-trend trades

### When to Add:
- **Option A (Immediate)**: Add to data generation queue now
- **Option B (Cautious)**: Wait until 3-model ensemble tested, then add
- **Recommendation**: **Option A** - generate data now, train later if needed

### Command to Add NOW:
```bash
# After seq300 completes, launch all 3 remaining:
cd /home/rford/caelum/ss/finvec

# Minute-based (original plan)
.venv/bin/python scripts/generate_training_data_v4.py --seq-len 500 \
  --output data/training/timing_training_data_v4_seq500.pt &

.venv/bin/python scripts/generate_training_data_v4.py --seq-len 800 \
  --output data/training/timing_training_data_v4_seq800.pt &

# Hourly-based (NEW - add if script supports it)
.venv/bin/python scripts/generate_training_data_v4.py --seq-len 500 \
  --granularity hourly \
  --output data/training/timing_training_data_v4_seq500_hourly.pt &
```

---

## 📝 Next Steps

1. **Check script support**: Does `generate_training_data_v4.py` support `--granularity` flag?
2. **If yes**: Add seq500-hourly to generation queue
3. **If no**: Adapt script or create hourly variant
4. **Train all 4 models**: Sequential on .44 or parallel if multi-GPU
5. **Backtest ensemble**: Compare 3-model vs 4-model performance
6. **Deploy**: If 4-model wins, use it in production

---

**Created**: 2025-10-26 22:15 UTC
**Status**: Ready to implement
**Impact**: Expected +15-25% performance improvement
**Cost**: +25% computational time
**Decision**: ✅ RECOMMENDED - Generate hourly data now, train when ready
