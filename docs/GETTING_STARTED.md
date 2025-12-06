# PassiveIncomeMaximizer - Getting Started Guide

**Last Updated**: 2025-11-14
**System**: Prediction-to-Execution Trading Engine
**Architecture**: Vue3/React Frontend | Flask/Express API | Python PIM Engine

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Starting the System](#starting-the-system)
5. [Accessing the Application](#accessing-the-application)
6. [Configuration](#configuration)
7. [Health Checks](#health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference](#quick-reference)

---

## System Overview

PassiveIncomeMaximizer (PIM) is a multi-agent trading system that combines machine learning predictions with autonomous trading execution.

### System Components

```
┌──────────────────────────────────────────────────────────┐
│  FinVec V7 (Prediction Model)                            │
│  → http://10.32.3.27:8002                                 │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  PIM Engine (Python)                                     │
│  → http://10.32.3.27:5002 (REST API)                      │
│  Information Gatherer → Coordinator → 9 Subagents        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Backend APIs                                            │
│  ├── Flask API (Python) → http://10.32.3.27:5000          │
│  └── Express API (TypeScript) → http://10.32.3.27:5000    │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Frontends                                               │
│  ├── Vue3 Dashboard → http://10.32.3.27:5500              │
│  └── React Dashboard → http://10.32.3.27:5000             │
└──────────────────────────────────────────────────────────┘
```

### Key Features

- **9 AI Agents**: Portfolio Manager, Price Analyzer, Risk Manager, News Processor, Trend Analyzer, and more
- **24/7 Continuous Operation**: Risk monitoring every 60 seconds, daily self-improvement at 4PM ET
- **Self-Improvement Loop**: System gets better every day, auto-implements LOW-RISK improvements
- **Multi-Model Orchestration**: OpenAI, Anthropic, Google Gemini, Mistral
- **Real-Time Trading**: Integration with Alpaca and TradeStation
- **Advanced Backtesting**: Signal-based exits, risk management
- **Swarm Visualization**: D3.js force-directed graph of agent communication
- **External Memory**: Caelum integration with MongoDB, Redis, Qdrant

---

## Prerequisites

### Required Services

1. **Node.js** 20 or later
2. **Python** 3.11 or later
3. **PostgreSQL** database (port 15432)
4. **Redis** server (10.32.3.27:6379 or 10.32.3.27:6379)
5. **Docker** (for PostgreSQL container)

### Optional Services

- **Qdrant** vector database (10.32.3.27:6333) - for enhanced agent memory
- **MongoDB** (10.32.3.27:27017) - for PIM Engine decision storage
- **FinColl API** (10.32.3.27:8002) - for V7 predictions
- **SenVec API** (10.32.3.27:18000) - for sentiment analysis

### API Keys Required

- **Alpaca Trading Account** (for paper trading)
  - `ALPACA_API_KEY`
  - `ALPACA_API_SECRET`
  - `ALPACA_ACCOUNT_ID`

- **OpenAI** (primary AI model)
  - `OPENAI_API_KEY`

- **Optional AI Models**
  - `ANTHROPIC_API_KEY` (Claude models)
  - `GEMINI_API_KEY` (Google Gemini)
  - `MISTRAL_API_KEY` (Mistral AI)

- **Optional Trading**
  - `TRADESTATION_CLIENT_ID`
  - `TRADESTATION_CLIENT_SECRET`

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/passive-income-maximizer.git
cd passive-income-maximizer
```

### 2. Install Dependencies

#### TypeScript/JavaScript Dependencies
```bash
npm install
```

#### Python Dependencies (PIM Engine)
```bash
cd engine
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

#### Flask API Dependencies (if using Flask backend)
```bash
# In project root
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
```

### 3. Set Up Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

#### Essential .env Configuration

```bash
# Database
DATABASE_URL=postgresql://caelum_user:caelum_secure_password_change_me@10.32.3.27:15432/caelum_cluster

# Alpaca Trading
ALPACA_API_KEY=your_alpaca_key
ALPACA_API_SECRET=your_alpaca_secret
ALPACA_ACCOUNT_ID=your_account_id
ALPACA_PAPER_TRADING=true

# AI Models
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  # optional
GEMINI_API_KEY=your_gemini_key        # optional
MISTRAL_API_KEY=your_mistral_key      # optional

# Redis & Caching
REDIS_HOST=10.32.3.27
REDIS_PORT=6379
REDIS_PASSWORD=                        # if authentication enabled

# Optional Vector Database
QDRANT_URL=http://10.32.3.27:6333
QDRANT_API_KEY=                        # if authentication enabled

# Server Configuration
PIM_SERVER_PORT=5000                   # Backend API port
```

### 4. Initialize Database

```bash
# Start PostgreSQL container (if not already running)
docker ps | grep caelum-postgres

# If not running, check docker-compose.yml and start:
docker-compose up -d postgres

# Initialize database schema
npm run db:push
```

---

## Starting the System

### Quick Start (All Services)

#### Option A: Using npm Scripts (Recommended)

```bash
# Terminal 1: Start TypeScript Express API + React Frontend
npm run dev

# Terminal 2: Start Vue3 Frontend
npm run vue

# Terminal 3: Start PIM Engine (Python)
cd engine
source .venv/bin/activate
python pim_service.py
```

#### Option B: Using Flask API

```bash
# Terminal 1: Start Flask API
source venv/bin/activate
python api/app.py

# Terminal 2: Start Vue3 Dashboard
npm run vue
```

### Service-by-Service Startup

#### 1. Start PostgreSQL (Docker)

```bash
docker start caelum-postgres
# or
docker-compose up -d postgres

# Verify
docker ps | grep caelum-postgres
```

#### 2. Start Express API + React Frontend

```bash
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run dev
```

**Started**: http://10.32.3.27:5000

#### 3. Start Vue3 Frontend

```bash
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run vue
```

**Started**: http://10.32.3.27:5500

#### 4. Start PIM Engine (Python)

```bash
cd /home/rford/caelum/ss/PassiveIncomeMaximizer/engine
source .venv/bin/activate
python pim_service.py
```

**Started**: http://10.32.3.27:5002

**What runs automatically:**
- ✅ Information Gatherer (scans every 5 minutes)
- ✅ 24/7 Risk Monitor (checks every 60 seconds)
- ✅ Daily Self-Evaluator (runs at 4:00 PM ET)

**Expected startup log:**
```
🚀 PIM Service starting up...
✅ PIM Engine initialized
✅ 24/7 Risk Monitor started
✅ Daily Self-Evaluator scheduled (runs at 4PM ET)
🎯 PIM Service FULLY OPERATIONAL - 24/7 Mode Active
```

#### 5. Start FinColl API (Optional - for V7 predictions)

```bash
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server
```

**Started**: http://10.32.3.27:8002

### Auto-Start on System Boot (systemd)

The PIM server can auto-start on reboot:

```bash
# Enable auto-start
systemctl --user enable pim-server.service

# Start now
systemctl --user start pim-server.service

# Check status
systemctl --user status pim-server.service

# View logs
journalctl --user -u pim-server.service -f
```

---

## Accessing the Application

### Frontend URLs

| Frontend | URL | Description |
|----------|-----|-------------|
| **React Dashboard** | http://10.32.3.27:5000 | Full-featured dashboard with all existing functionality |
| **Vue3 Dashboard** | http://10.32.3.27:5500 | Modern UI with Vuetify, D3.js swarm visualization |

### API Endpoints

| API | URL | Description |
|-----|-----|-------------|
| **Express API** | http://10.32.3.27:5000/api | TypeScript backend |
| **Flask API** | http://10.32.3.27:5000/api | Python backend (alternative) |
| **PIM Engine** | http://10.32.3.27:5002/api/pim | Python RL engine |
| **FinColl API** | http://10.32.3.27:8002/api/v1 | V7 predictions |

### Key Pages

#### Vue3 Dashboard

- **Monitor** (`/`) - Real-time positions, P/L, predictions
- **Swarm Network** (`/swarm`) - Animated agent communication graph
- **Backtest** (`/backtest`) - Signal-based backtesting with charts
- **Insights** (`/insights`) - Trading analytics + LLM evaluations
- **History** (`/history`) - Trade history + account management
- **Scheduler** (`/scheduler`) - Cron & event-based automation

#### React Dashboard

- **Trading Dashboard** (`/trading-dashboard`) - Main trading interface
- **Agent Status** - Monitor all 9 agents
- **Performance** - Portfolio metrics and charts
- **Backtest Results** - Historical testing results
- **Configuration** - System settings

---

## Configuration

### Trading Parameters

Edit via Configuration page or `.env` file:

```bash
# Position Sizing
MAX_TRADE_AMOUNT=5000              # Max per trade ($)
RISK_PERCENTAGE=1.5                # Risk per position (%)

# Trading Hours
TRADING_HOURS_START=09:30          # Market open
TRADING_HOURS_END=16:00            # Market close

# Risk Management
MAX_CONCURRENT_POSITIONS=10        # Max open positions
MAX_DAILY_LOSS=1000                # Daily loss limit ($)
```

### Agent Configuration

Each agent can be configured through the UI:

- **Status**: Active, Training, Idle, Error
- **Training Mode**: Analysis or Backtest
- **Symbol Sets**: Specific symbols to monitor
- **Time Ranges**: 1D, 7D, 30D, 90D

### Multi-Model Orchestration

Configure AI model selection:

```bash
# Default models
TEXT_GENERATION_MODEL=gpt-4o       # OpenAI
FINANCIAL_ANALYSIS_MODEL=claude-3.7-sonnet  # Anthropic
MARKET_RESEARCH_MODEL=gemini-pro   # Google
```

---

## Health Checks

### Quick Health Check

```bash
# Express API
curl http://10.32.3.27:5000/api/health | jq

# Flask API
curl http://10.32.3.27:5000/api/health | jq

# PIM Engine
curl http://10.32.3.27:5002/api/pim/status | jq
```

### Expected Response

```json
{
  "status": "healthy",
  "components": [
    {"name": "Database", "status": "healthy"},
    {"name": "Alpaca API", "status": "healthy"},
    {"name": "Qdrant Vector DB", "status": "healthy"},
    {"name": "Task Scheduler", "status": "healthy"}
  ]
}
```

### Check All Services

```bash
#!/bin/bash
echo "=== Service Health Check ==="

echo -e "\n1. PIM Server (Express):"
curl -s http://10.32.3.27:5000/api/health | jq '.status' || echo "unavailable"

echo -e "\n2. PIM Engine (Python):"
curl -s http://10.32.3.27:5002/api/pim/status | jq '.status' || echo "unavailable"

echo -e "\n3. PostgreSQL:"
docker ps | grep caelum-postgres | awk '{print $7}' || echo "not running"

echo -e "\n4. Redis:"
redis-cli -h 10.32.3.27 ping 2>&1 || echo "unavailable"

echo -e "\n5. Qdrant:"
curl -s http://10.32.3.27:6333/health | jq '.status' 2>/dev/null || echo "unavailable"

echo -e "\n6. FinColl API:"
curl -s http://10.32.3.27:8002/api/health | jq '.status' 2>/dev/null || echo "unavailable"
```

---

## Troubleshooting

### Common Issues

#### 1. Server Not Starting

**Problem**: Port already in use

```bash
# Check what's using port 5000
lsof -i :5000
# or
ss -tlnp | grep :5000

# Kill existing process
pkill -f "tsx server/index.ts"
# or
kill -9 <PID>
```

#### 2. Database Connection Errors

**Problem**: Cannot connect to PostgreSQL

```bash
# Check if container is running
docker ps | grep caelum-postgres

# Start container
docker start caelum-postgres

# Test connection
docker exec caelum-postgres psql -U caelum_user -d caelum_cluster -c "SELECT version();"

# Check credentials in .env
grep DATABASE_URL .env
```

#### 3. Redis Connection Failed

**Problem**: Cannot connect to Redis

```bash
# Test connection
redis-cli -h 10.32.3.27 ping

# If using 10.32.3.27
redis-cli ping

# Check if Redis is running
ps aux | grep redis
```

#### 4. Agent System Not Starting

**Checklist**:
- ✅ PostgreSQL running
- ✅ Alpaca API keys valid
- ✅ OpenAI API key valid
- ✅ Redis connection working

```bash
# Verify API keys
npm run verify-keys  # if script exists

# Check logs
tail -100 pim-server.log
```

#### 5. PIM Engine Errors

**Problem**: Module not found or connection refused

```bash
# Install dependencies
cd engine
source .venv/bin/activate
pip install -r requirements.txt

# Start FinColl API (if needed)
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server
```

#### 6. Vue3 Frontend Not Loading

**Problem**: Vite dev server errors

```bash
# Clear cache and reinstall
rm -rf node_modules
npm install

# Check Vite config
cat vite.config.ts

# Restart Vite
npm run vue
```

### Port Reference

| Service | Default Port | Configurable Via |
|---------|--------------|------------------|
| Express API + React | 5000 | `PIM_SERVER_PORT` |
| Vue3 Frontend | 5500 | vite.config.ts |
| PIM Engine (Python) | 5002 | pim_service.py |
| Flask API | 5000 | FLASK_PORT |
| PostgreSQL | 15432 | docker-compose.yml |
| Redis | 6379 | REDIS_PORT |
| Qdrant | 6333 | QDRANT_URL |
| FinColl API | 8002 | fincoll config |
| SenVec API | 18000 | senvec config |
| Caelum Service | 8080 | - |
| Caelum Daemon | 8090 | - |

---

## Quick Reference

### Daily Startup Commands

```bash
# 1. Start PostgreSQL (if not auto-started)
docker start caelum-postgres

# 2. Start main backend + React frontend
cd /home/rford/caelum/ss/PassiveIncomeMaximizer
npm run dev

# 3. (Optional) Start Vue3 frontend
npm run vue

# 4. (Optional) Start PIM Engine
cd engine && source .venv/bin/activate && python pim_service.py
```

### Useful Commands

```bash
# Restart everything
pkill -f "tsx server/index.ts"
pkill -f "python pim_service.py"
./start-pim-server.sh

# View logs
tail -f pim-server.log
journalctl --user -u pim-server.service -f

# Database operations
npm run db:push          # Initialize schema
npm run db:generate      # Generate migrations

# Run tests
npm run test             # All tests
npm run test:unit        # Unit tests only
npm run test:integration # Integration tests
```

### Environment Variables Quick Copy

```bash
# Copy to .env file
DATABASE_URL=postgresql://caelum_user:caelum_secure_password_change_me@10.32.3.27:15432/caelum_cluster
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret
ALPACA_ACCOUNT_ID=your_account_id
ALPACA_PAPER_TRADING=true
OPENAI_API_KEY=your_openai_key
REDIS_HOST=10.32.3.27
REDIS_PORT=6379
MAX_TRADE_AMOUNT=5000
RISK_PERCENTAGE=1.5
PIM_SERVER_PORT=5000
```

---

## Next Steps

Once the system is running:

1. ✅ Access the dashboard at http://10.32.3.27:5000 or http://10.32.3.27:5500
2. ✅ Configure agents via **Agent Status** page
3. ✅ Set up trading parameters in **Configuration**
4. ✅ Review **ARCHITECTURE.md** for system design
5. ✅ See **AGENT_SYSTEM.md** for agent details
6. ✅ Check **TRADING_OPERATIONS.md** for backtesting
7. ✅ Read **INTEGRATIONS.md** for external services
8. ✅ Consult **DEVELOPMENT_GUIDE.md** for development workflow

---

**For detailed architecture and system design, see ARCHITECTURE.md**
**For agent configuration and swarm details, see AGENT_SYSTEM.md**
**For trading operations and backtesting, see TRADING_OPERATIONS.md**
