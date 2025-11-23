# FinVec V4 Training Strategy - 3 GPU Setup

**Date**: 2025-10-26
**Context**: Training V4 models across 3 machines with NFS shared filesystem

---

## 🖥️ GPU Infrastructure

### Host 1: 10.32.3.27 (caelum) - RTX 5060 Ti
- **VRAM**: 17.1 GB
- **OS**: Windows 11 + WSL2
- **Status**: ⚠️ GPU not visible in WSL (Windows-hosted)
- **Access**: Need to run training on Windows or configure WSL GPU passthrough
- **Ollama**: 4 models loaded (qwen3-coder:30b, qwen3:30b, llama3.1:8b, nomic-embed-text)
- **Mount**: `/home/rford/caelum/ss` (NFS shared)

### Host 2: 10.32.3.44 - GTX 1660 Ti
- **VRAM**: 6 GB
- **OS**: Windows 11
- **Status**: ✅ ACCESSIBLE via SSH
- **GPU Command**: `ssh 10.32.3.44 nvidia-smi` works
- **Ollama**: 4 models loaded (gemma3:1b, qwen3:4b, qwen3:8b, llama3.1:8b)
- **Mount**: `/home/rford/caelum/ss` (NFS shared)

### Host 3: 10.32.3.62 - GPU #2
- **VRAM**: 8 GB (estimated)
- **OS**: Windows 11
- **Status**: ❌ DOWN (confirmed since Oct 24)
- **Action**: Physical investigation needed
- **Mount**: `/home/rford/caelum/ss` (NFS shared when up)

---

## 📊 V4 Training Configuration

### Three Sequence Lengths (Parallel Training)

**Why 3 sequences?**
- Different context windows capture different market patterns
- Shorter sequences: Fast reactions to recent moves
- Longer sequences: Better trend recognition

### seq300 - Short Context (Smallest Model)
- **Sequence Length**: 300 bars (~1-2 weeks of minute data)
- **Expected Samples**: ~70K (118 symbols × ~600 avg)
- **Training Time**: 8-10 hours
- **Best GPU**: **.44 (GTX 1660 Ti)** - 6GB sufficient
- **Model Size**: Smallest (fits in 6GB)
- **Use Case**: Fast intraday predictions

### seq500 - Medium Context
- **Sequence Length**: 500 bars (~2-3 weeks)
- **Expected Samples**: ~60K (118 symbols × ~500 avg)
- **Training Time**: 10-12 hours
- **Best GPU**: **.27 (RTX 5060 Ti)** - Most powerful
- **Model Size**: Medium
- **Use Case**: Swing trading, multi-day forecasts

### seq800 - Long Context (Largest Model)
- **Sequence Length**: 800 bars (~4 weeks)
- **Expected Samples**: ~47K (118 symbols × ~400 avg)
- **Training Time**: 12-15 hours
- **Best GPU**: **.62 (8GB)** - When available, or **.27**
- **Model Size**: Largest (needs 8GB+)
- **Use Case**: Long-term trend analysis

---

## 🚀 Training Execution Plans

### Plan A: All 3 GPUs Available (Ideal)
**Status**: Blocked by .62 being down

```bash
# Terminal 1 - .44 (seq300)
ssh 10.32.3.44
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python train_timing_model_v4.py --seq-len 300 --gpu 0 &

# Terminal 2 - .27 (seq500)
# Run on Windows or via WSL GPU passthrough
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python train_timing_model_v4.py --seq-len 500 --gpu 0 &

# Terminal 3 - .62 (seq800)
ssh 10.32.3.62
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python train_timing_model_v4.py --seq-len 800 --gpu 0 &
```

**Estimated Time**: 12-15 hours (parallel)
**Checkpoints**: Auto-saved every N iterations
**Logs**: `logs/train_v4_seq{300,500,800}.log`

### Plan B: 2 GPUs Available (Current - .62 Down)
**Status**: ✅ Feasible now

**Option B1: Sequential on .44 (Safe, Slower)**
```bash
ssh 10.32.3.44

# Train seq300 first (8-10 hours)
cd /home/rford/caelum/ss/finvec && .venv/bin/python train_timing_model_v4.py --seq-len 300 --gpu 0
# Wait for completion, then:

# Train seq500 (10-12 hours)
.venv/bin/python train_timing_model_v4.py --seq-len 500 --gpu 0
# Wait for completion, then:

# Train seq800 (12-15 hours)
.venv/bin/python train_timing_model_v4.py --seq-len 800 --gpu 0
```

**Total Time**: 30-37 hours (sequential)
**Risk**: Low - simple and safe

**Option B2: Parallel .44 + .27 (Faster, Requires .27 GPU Access)**
```bash
# Terminal 1 - .44 (seq300 + seq800)
ssh 10.32.3.44
cd /home/rford/caelum/ss/finvec && .venv/bin/python train_timing_model_v4.py --seq-len 300 --gpu 0
# After completion:
.venv/bin/python train_timing_model_v4.py --seq-len 800 --gpu 0

# Terminal 2 - .27 (seq500) - IF GPU accessible
# Either: Windows native Python, or WSL GPU passthrough
cd /home/rford/caelum/ss/finvec && .venv/bin/python train_timing_model_v4.py --seq-len 500 --gpu 0
```

**Total Time**: ~20-22 hours (parallel + sequential)
**Risk**: Medium - requires .27 GPU configuration

### Plan C: 1 GPU Only (.44)
**Status**: ✅ Always works as fallback

```bash
# Sequential training on .44 only
ssh 10.32.3.44
cd /home/rford/caelum/ss/finvec

# seq300 (8-10 hours)
.venv/bin/python train_timing_model_v4.py --seq-len 300 --gpu 0 &> logs/train_v4_seq300.log

# seq500 (10-12 hours)
.venv/bin/python train_timing_model_v4.py --seq-len 500 --gpu 0 &> logs/train_v4_seq500.log

# seq800 (12-15 hours)
.venv/bin/python train_timing_model_v4.py --seq-len 800 --gpu 0 &> logs/train_v4_seq800.log
```

**Total Time**: 30-37 hours
**Advantage**: Simple, reliable, no dependencies

---

## 📦 Data Access via NFS

### NFS Benefits
- All hosts mount `/home/rford/caelum/ss` from .27
- Training data generated on ANY host is visible to ALL hosts
- Models saved on ANY host are visible to ALL hosts
- No data copying needed!

### File Locations
```
/home/rford/caelum/ss/finvec/
├── data/training/
│   ├── timing_training_data_v4_seq300.pt (generated on .27, visible everywhere)
│   ├── timing_training_data_v4_seq500.pt (to be generated)
│   └── timing_training_data_v4_seq800.pt (to be generated)
├── checkpoints/
│   ├── timing_v4_seq300/best_model.pt (trained on .44, visible everywhere)
│   ├── timing_v4_seq500/best_model.pt
│   └── timing_v4_seq800/best_model.pt
└── logs/
    ├── train_v4_seq300.log
    ├── train_v4_seq500.log
    └── train_v4_seq800.log
```

---

## 📝 Training Command Reference

### Basic Training Command
```bash
python train_timing_model_v4.py \
  --seq-len 300 \
  --gpu 0 \
  --epochs 100 \
  --batch-size 32 \
  --learning-rate 0.0001 \
  --checkpoint-dir checkpoints/timing_v4_seq300 \
  --log-file logs/train_v4_seq300.log
```

### Resume from Checkpoint
```bash
python train_timing_model_v4.py \
  --seq-len 300 \
  --resume checkpoints/timing_v4_seq300/checkpoint_epoch_50.pt
```

### Monitor Training
```bash
# Watch logs in real-time
tail -f logs/train_v4_seq300.log

# Check GPU usage
nvidia-smi -l 1

# Check process
ps aux | grep train_timing_model_v4
```

---

## ⚠️ Known Issues & Solutions

### Issue 1: .27 GPU Not Visible in WSL
**Problem**: RTX 5060 Ti not accessible from WSL
**Solutions**:
1. **WSL GPU Passthrough** (Recommended):
   ```bash
   # In WSL, check if GPU visible:
   nvidia-smi
   # If not, configure WSL GPU passthrough (Windows 11 required)
   ```

2. **Native Windows Training**:
   ```powershell
   # Run training directly in Windows PowerShell
   cd D:\swdatasci\caelum\ss\finvec
   .\.venv\Scripts\activate
   python train_timing_model_v4.py --seq-len 500 --gpu 0
   ```

3. **Skip .27** (Easiest):
   - Use Plan C (only .44)
   - Acceptable since .44 is powerful enough

### Issue 2: .62 Host Down
**Problem**: Third GPU unavailable
**Solutions**:
1. Physical investigation (check power, network, boot)
2. Use 2-GPU strategy (Plans B1 or B2)
3. Fix later - not blocking (can use .44 alone)

### Issue 3: VRAM Insufficient
**Problem**: seq800 model too large for 6GB
**Solutions**:
1. Reduce batch size: `--batch-size 16` or `--batch-size 8`
2. Reduce model size: `--d-model 512` (instead of 768)
3. Use gradient checkpointing: `--gradient-checkpointing`
4. Train seq800 on .27 (17GB VRAM) instead

---

## 🎯 Recommended Strategy (NOW)

**Given Current State**:
- ✅ .44 GPU accessible (6GB)
- ⚠️ .27 GPU not accessible from WSL
- ❌ .62 GPU down

**Best Approach**: **Plan C** (Sequential on .44)

### Step-by-Step Execution:

1. **Wait for Data Generation** (Currently 35/118, ~30%)
   - ETA: ~1.5-2 hours to complete seq300 data
   - Do NOT start training until data complete

2. **Generate Remaining Data** (After seq300 completes)
   ```bash
   # seq500 data
   .venv/bin/python scripts/generate_training_data_v4.py \
     --seq-len 500 \
     --output data/training/timing_training_data_v4_seq500.pt &

   # seq800 data
   .venv/bin/python scripts/generate_training_data_v4.py \
     --seq-len 800 \
     --output data/training/timing_training_data_v4_seq800.pt &
   ```
   - ETA: 4-6 hours (parallel)

3. **Start Training on .44** (After ALL data ready)
   ```bash
   ssh 10.32.3.44
   cd /home/rford/caelum/ss/finvec

   # Train all 3 models sequentially
   # seq300 (8-10 hours)
   .venv/bin/python train_timing_model_v4.py --seq-len 300 --gpu 0

   # seq500 (10-12 hours)
   .venv/bin/python train_timing_model_v4.py --seq-len 500 --gpu 0

   # seq800 (12-15 hours)
   .venv/bin/python train_timing_model_v4.py --seq-len 800 --gpu 0
   ```

4. **Total Timeline**:
   - Data generation: 2 + 6 = 8 hours
   - Training: 30-37 hours
   - **Total**: 38-45 hours (~2 days)

---

## 📊 Expected V4 Results

### Performance Improvements (vs V3)
- **META**: -0.32% → +0.50-1.00% (PROFITABLE!)
- **MU**: +2.51% → +3.00-3.50%
- **AMD**: +3.48% → +4.00-4.50%
- **Overall**: +1.34% → +1.75-2.00% (+30-50%)

### New Features (81D vs 50D)
- Velocity features (1st derivative)
- Acceleration features (2nd derivative)
- Jerk features (3rd derivative)
- Regime detection (plateau, compression, breakout)
- Pre-move pattern indicators
- Improved temporal dynamics

---

## 🔄 Future: When All 3 GPUs Work

**Ideal Setup** (Plan A):
```bash
# Launch all 3 training jobs simultaneously
# .44: seq300 (8-10 hours)
# .27: seq500 (10-12 hours)
# .62: seq800 (12-15 hours)
# Total time: 12-15 hours (all parallel!)
```

**Requires**:
- [ ] .27 GPU accessible from WSL or Windows
- [ ] .62 host repaired and online
- [ ] All NFS mounts verified

**Benefit**: 67% time savings (15 hours vs 45 hours)

---

## 📝 Monitoring & Validation

### During Training
```bash
# GPU utilization
watch -n 1 nvidia-smi

# Training logs
tail -f logs/train_v4_seq*.log

# Checkpoint progress
ls -lh checkpoints/timing_v4_seq*/checkpoint_epoch_*.pt

# Training metrics
grep "Epoch" logs/train_v4_seq300.log | tail -5
```

### After Training
```bash
# Backtest V4 vs V3
python scripts/backtest_v4_ensemble.py

# Compare models
python scripts/compare_v3_v4_performance.py

# Visualize improvements
python scripts/visualize_v4_results.py
```

---

**Created**: 2025-10-26 21:55 UTC
**Status**: Ready to execute Plan C when data generation completes
**Timeline**: 38-45 hours total (data + training)
**Priority**: Let data generation complete first (35/118, ~2 hours remaining)
