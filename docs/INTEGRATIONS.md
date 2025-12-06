# PassiveIncomeMaximizer - External Integrations

**Last Updated**: 2025-11-14
**External Services**: FinVec, SenVec, Caelum, Alpaca, TradeStation, OpenAI, Anthropic

---

## Integration Overview

PIM integrates with multiple external services for predictions, sentiment, trading, and AI models.

```
┌──────────────────────────────────────────────────────────┐
│               PassiveIncomeMaximizer                      │
└────┬─────────┬─────────┬──────────┬─────────┬───────────┘
     │         │         │          │         │
     ▼         ▼         ▼          ▼         ▼
┌────────┐ ┌───────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│FinVec  │ │SenVec │ │Caelum  │ │Alpaca  │ │  OpenAI  │
│V7 API  │ │Sent.  │ │Memory  │ │Trading │ │ /Anthrop.│
└────────┘ └───────┘ └────────┘ └────────┘ └──────────┘
```

---

## System Health Monitoring

**UI**: http://10.32.3.27:5500/health
**API**: http://10.32.3.27:5000/api/health

### Purpose

The `/health` page provides real-time diagnostic information for all infrastructure components. This page exists to help future debugging sessions quickly answer:
- "Is service X running?"
- "What port is it on?"
- "Is it connected?"

This eliminates guesswork and helps identify problems faster.

### Monitored Components

**6 Components** are continuously monitored:

1. **Database (PostgreSQL)** - Port 15433
   - Primary relational database for trades, agents, configurations
   - Docker container: `pim-postgres`

2. **MongoDB** - Port 27117
   - Caelum external memory for agent decisions
   - Docker container: `pim-mongodb`
   - Purpose: Agent decision history, team memory

3. **Qdrant Vector DB** - Port 6333 (10.32.3.27)
   - Vector database for RAG (Retrieval Augmented Generation)
   - Docker container: `caelum-qdrant`
   - Purpose: Team memory sharing across agents
   - **YES, we use this** - required for multi-agent team memory

4. **InfluxDB** - Port 8086
   - Time-series database for metrics
   - Docker container: `caelum-influxdb`
   - Purpose: Account value over time, trades over time, performance metrics
   - **Diagnostic only currently** - full time-series implementation pending

5. **Alpaca API**
   - Trading execution service
   - External service (not local)

6. **Task Scheduler**
   - Internal cron-like scheduler for periodic tasks

### Health Check Commands

```bash
# All components
curl http://10.32.3.27:5000/api/health | jq

# Specific databases
docker ps | grep -E "mongo|postgres|qdrant|influx"

# InfluxDB direct
curl http://10.32.3.27:8086/health
```

### Component Status Meanings

- **healthy** ✅ - Component connected and operational
- **degraded** ⚠️ - Component accessible but experiencing issues
- **unhealthy** ❌ - Component down or unreachable

### Troubleshooting

If a component shows as unhealthy:

1. **Database/MongoDB/Qdrant/InfluxDB**: Check Docker containers are running
   ```bash
   docker ps | grep <container-name>
   docker logs <container-name>
   ```

2. **Alpaca API**: Check API keys in `.env`
   ```bash
   grep ALPACA .env
   ```

3. **Task Scheduler**: Check logs for scheduler errors
   ```bash
   grep scheduler pim-server.log
   ```

---

## FinVec Integration (V7 Predictions)

### FinColl API

**Repository**: `/home/rford/caelum/ss/finvec`
**Port**: 8002
**Purpose**: V7 model predictions

### Starting FinColl

```bash
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server
```

**Health Check**:
```bash
curl http://10.32.3.27:8002/api/health
```

### API Endpoints

#### Get Prediction

```bash
curl -X POST http://10.32.3.27:8002/api/v1/inference/predict \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "provider": "tradestation",
    "interval": "5m",
    "lookback": 100
  }'
```

**Response**:
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-01-14T10:30:00Z",
  "prediction": "bullish",
  "confidence": 0.85,
  "entry_signal": 0.82,
  "exit_signal": 0.15,
  "targets": {
    "t1": 178.50,
    "t2": 180.00,
    "t3": 182.00
  },
  "features": {
    "sentiment_score": 0.72,
    "technical_score": 0.88,
    "momentum": 0.65
  }
}
```

### PIM Integration

```typescript
// server/services/fincoll-client.ts
export class FinCollClient {
  private baseURL = 'http://10.32.3.27:8002';

  async getPrediction(symbol: string): Promise<V7Prediction> {
    const response = await axios.post(
      `${this.baseURL}/api/v1/inference/predict`,
      { symbol }
    );
    return response.data;
  }
}

// Usage in agents
const prediction = await finCollClient.getPrediction('AAPL');
if (prediction.confidence > 0.65 && prediction.entry_signal > 0.65) {
  // High confidence entry
}
```

---

## SenVec Integration (Sentiment)

**Repository**: `/home/rford/caelum/ss/finvec` (senvec module)
**Port**: 18000
**Purpose**: 72D sentiment features

### Starting SenVec

```bash
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
./start_all_services.sh  # Starts 5 microservices
```

**Health Check**:
```bash
curl http://10.32.3.27:18000/health
```

### API Endpoints

#### Get Sentiment Features

```bash
curl http://10.32.3.27:18000/features/AAPL/compact
```

**Response**:
```json
{
  "symbol": "AAPL",
  "timestamp": "2025-01-14T10:30:00Z",
  "features": [0.72, -0.15, 0.43, ...],  // 72D array
  "metadata": {
    "twitter_sentiment": 0.65,
    "reddit_sentiment": 0.70,
    "news_sentiment": 0.75
  }
}
```

### PIM Integration

```typescript
// server/services/senvec-client.ts
export class SenVecClient {
  private baseURL = 'http://10.32.3.27:18000';

  async getSentiment(symbol: string): Promise<SentimentData> {
    const response = await axios.get(
      `${this.baseURL}/features/${symbol}/compact`
    );
    return response.data;
  }
}

// Usage in News Processor agent
const sentiment = await senVecClient.getSentiment('AAPL');
if (sentiment.metadata.news_sentiment < -0.5) {
  // Very negative news
}
```

---

## Caelum Integration (External Memory)

**Purpose**: Agent memory, context storage, vector search
**Components**: MongoDB, Redis, Qdrant

### Services

1. **MongoDB** (10.32.3.27:27017)
   - Persistent decision storage
   - Historical data
   - Agent configurations

2. **Redis** (10.32.3.27:6379)
   - Fast caching (5min TTL)
   - Real-time state
   - Session management

3. **Qdrant** (10.32.3.27:6333)
   - Vector search
   - Semantic similarity
   - Pattern matching

### Configuration

```typescript
// .env
DATABASE_URL=mongodb://10.32.3.27:27017/pim
REDIS_HOST=10.32.3.27
REDIS_PORT=6379
QDRANT_URL=http://10.32.3.27:6333
```

### PIM Integration

```typescript
// engine/pim/caelum_integration.py
class CaelumIntegration:
    def __init__(self):
        self.mongo = MongoClient('mongodb://10.32.3.27:27017')
        self.redis = Redis(host='10.32.3.27', port=6379)
        self.qdrant = QdrantClient(url='http://10.32.3.27:6333')

    async def store_decision(self, decision):
        # Persistent storage
        await self.mongo.decisions.insert_one(decision)

        # Fast cache
        cache_key = f"decision:{decision['symbol']}"
        await self.redis.setex(cache_key, 300, json.dumps(decision))

        # Vector search
        embedding = await self.create_embedding(decision)
        await self.qdrant.upsert(
            collection_name='decisions',
            points=[{
                'id': decision['id'],
                'vector': embedding,
                'payload': decision
            }]
        )
```

---

## Alpaca Integration (Trading)

**Website**: https://alpaca.markets
**Purpose**: Paper and live trading

### Setup

1. Create account at https://alpaca.markets
2. Generate API keys (Paper Trading)
3. Add to `.env`:

```bash
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here
ALPACA_ACCOUNT_ID=your_account_id
ALPACA_PAPER_TRADING=true
```

### Installation

```bash
npm install @alpacahq/alpaca-trade-api
```

### PIM Integration

```typescript
// server/services/alpaca-client.ts
import Alpaca from '@alpacahq/alpaca-trade-api';

export class AlpacaClient {
  private client: Alpaca;

  constructor() {
    this.client = new Alpaca({
      keyId: process.env.ALPACA_API_KEY,
      secretKey: process.env.ALPACA_API_SECRET,
      paper: process.env.ALPACA_PAPER_TRADING === 'true'
    });
  }

  async placeOrder(order: OrderRequest): Promise<Order> {
    return await this.client.createOrder({
      symbol: order.symbol,
      qty: order.quantity,
      side: order.side,
      type: order.type,
      time_in_force: order.timeInForce || 'day'
    });
  }

  async getPositions(): Promise<Position[]> {
    return await this.client.getPositions();
  }

  async getAccount(): Promise<Account> {
    return await this.client.getAccount();
  }
}
```

### Common Operations

```typescript
// Get account info
const account = await alpacaClient.getAccount();
console.log(`Buying power: $${account.buying_power}`);

// Place market order
const order = await alpacaClient.placeOrder({
  symbol: 'AAPL',
  quantity: 50,
  side: 'buy',
  type: 'market'
});

// Get positions
const positions = await alpacaClient.getPositions();
```

---

## TradeStation Integration (Optional)

**Website**: https://www.tradestation.com
**Purpose**: Advanced trading features

### Setup

1. Create TradeStation account
2. Register API application
3. Get OAuth credentials
4. Add to `.env`:

```bash
TRADESTATION_CLIENT_ID=your_client_id
TRADESTATION_CLIENT_SECRET=your_client_secret
TRADESTATION_REDIRECT_URI=http://10.32.3.27:5000/api/tradestation/callback
```

### PIM Integration

```typescript
// server/services/tradestation-client.ts
export class TradeStationClient {
  async authenticate() {
    // OAuth flow
    const authUrl = `https://signin.tradestation.com/authorize?client_id=${this.clientId}&redirect_uri=${this.redirectUri}&response_type=code`;
    // Redirect user to authUrl
  }

  async placeOrder(order: TSOrderRequest): Promise<TSOrder> {
    const response = await axios.post(
      'https://api.tradestation.com/v3/orderexecution/orders',
      order,
      { headers: { Authorization: `Bearer ${this.accessToken}` } }
    );
    return response.data;
  }
}
```

---

## AI Model Integrations

### OpenAI (Primary)

```bash
# .env
OPENAI_API_KEY=sk-...
```

**Models Used**:
- `gpt-4o` - Default for agents
- `gpt-4o-mini` - Fast operations

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const response = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages: [{ role: 'user', content: 'Analyze AAPL trade...' }]
});
```

### Anthropic (Claude)

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
```

**Models Used**:
- `claude-3.7-sonnet` - Financial analysis
- `claude-opus-4` - Complex reasoning

```typescript
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await anthropic.messages.create({
  model: 'claude-3.7-sonnet',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Analyze sentiment...' }]
});
```

### Google Gemini (Optional)

```bash
# .env
GEMINI_API_KEY=...
```

```typescript
import { GoogleGenerativeAI } from '@google/generative-ai';

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

const result = await model.generateContent('Market research...');
```

### Model Routing

```typescript
// Intelligent model selection
export class LLMRouter {
  selectModel(task: TaskType): string {
    switch (task) {
      case 'financial_analysis':
        return 'claude-3.7-sonnet';  // Best for finance
      case 'quick_classification':
        return 'gpt-4o-mini';  // Fast and cheap
      case 'complex_reasoning':
        return 'claude-opus-4';  // Most capable
      case 'market_research':
        return 'gemini-pro';  // Good at search
      default:
        return 'gpt-4o';  // Default
    }
  }
}
```

---

## Data Providers

### Yahoo Finance (via yfinance)

```bash
pip install yfinance
```

```python
# engine/data/providers/yfinance_provider.py
import yfinance as yf

def get_historical_data(symbol, period='1mo'):
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period)

def get_quote(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.info
```

### Alpha Vantage (Optional)

```bash
# .env
ALPHA_VANTAGE_API_KEY=...
```

```typescript
const response = await axios.get(
  `https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=5min&apikey=${process.env.ALPHA_VANTAGE_API_KEY}`
);
```

---

## Troubleshooting

### FinColl Connection Failed

```bash
# Check if running
curl http://10.32.3.27:8002/api/health

# Start if needed
cd /home/rford/caelum/ss/finvec
source .venv/bin/activate
python -m fincoll.api.server
```

### SenVec Connection Failed

```bash
# Check if running
curl http://10.32.3.27:18000/health

# Start all services
cd /home/rford/caelum/ss/finvec
./start_all_services.sh
```

### Alpaca Authentication Failed

- Verify API keys in `.env`
- Check paper trading mode is enabled
- Test with: `curl -H "APCA-API-KEY-ID: ${KEY}" -H "APCA-API-SECRET-KEY: ${SECRET}" https://paper-api.alpaca.markets/v2/account`

### MongoDB Connection Failed

```bash
# Check if running
docker ps | grep caelum-postgres

# Start if needed
docker start caelum-postgres
```

### Redis Connection Failed

```bash
# Test connection
redis-cli -h 10.32.3.27 ping

# Should return: PONG
```

---

## Environment Variables Reference

```bash
# FinVec Integration
FINCOLL_URL=http://10.32.3.27:8002
SENVEC_URL=http://10.32.3.27:18000

# Caelum Infrastructure
DATABASE_URL=postgresql://caelum_user:password@10.32.3.27:15432/caelum_cluster
MONGODB_URL=mongodb://10.32.3.27:27017/pim
REDIS_HOST=10.32.3.27
REDIS_PORT=6379
QDRANT_URL=http://10.32.3.27:6333

# Trading
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
ALPACA_ACCOUNT_ID=...
ALPACA_PAPER_TRADING=true

TRADESTATION_CLIENT_ID=...
TRADESTATION_CLIENT_SECRET=...
TRADESTATION_REDIRECT_URI=...

# AI Models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
MISTRAL_API_KEY=...

# Data Providers
ALPHA_VANTAGE_API_KEY=...
```

---

## Related Documentation

- **ARCHITECTURE.md** - System integration patterns
- **AGENT_SYSTEM.md** - How agents use external services
- **TRADING_OPERATIONS.md** - Trading execution details

---

**For system architecture details, see ARCHITECTURE.md**
**For agent implementation details, see AGENT_SYSTEM.md**
