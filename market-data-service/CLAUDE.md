# Market Data Service - Claude Code Guide

**Quick reference for AI assistants working on market data integration**

---

## What Is This?

Market Data Service is the **centralized data access layer** for the entire Caelum SuperSystem. It consolidates all market data API calls into one service to eliminate code duplication.

**Key Principle**: READ-ONLY. No order execution. Just market data.

---

## Quick Context

**Purpose**: Single source of truth for market data across all SuperSystem services
**Port**: 8010
**Language**: Python + FastAPI
**Dependencies**: Redis (10.32.3.27:6379), TradeStation API

---

## Service Status

```bash
# Health check
curl http://10.32.3.27:8010/health

# Market status (always works, no auth needed)
curl http://10.32.3.27:8010/api/market/status

# PM2 status
npx pm2 status market-data-service

# View logs
npx pm2 logs market-data-service
```

---

## Architecture

```
Consumers (PIM, opportunity-scanner, finvec)
    ↓ HTTP API calls
Market Data Service (port 8010)
    ├── TradeStation Client (OAuth + token refresh)
    ├── Redis Cache (5s-24h TTL based on data type)
    └── FastAPI Server (async)
        ↓
TradeStation API v3 / Crypto Exchanges
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/clients/tradestation.py` | TradeStation API client with OAuth |
| `src/api/server.py` | FastAPI app with all endpoints |
| `src/cache/redis_cache.py` | Redis caching layer |
| `src/utils/market_hours.py` | Local time-based market hours (no API calls) |
| `ecosystem.config.js` | PM2 configuration |
| `.env` | TradeStation credentials, Redis config |

---

## Common Tasks

### Adding a New Endpoint

1. **Add method to TradeStation client** (`src/clients/tradestation.py`)
```python
async def get_new_data(self, symbol: str) -> Optional[Dict]:
    return await self._make_request('GET', f'/marketdata/new/{symbol}')
```

2. **Add FastAPI endpoint** (`src/api/server.py`)
```python
@app.get("/api/new/{symbol}")
async def get_new_data(symbol: str, use_cache: bool = True):
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    cache_key = f"new:{symbol}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    data = await ts_client.get_new_data(symbol)
    
    if data and cache:
        cache.set(cache_key, data, ttl_seconds=60)
    
    return data or {"error": "Not found"}
```

3. **Test**
```bash
curl http://10.32.3.27:8010/api/new/AAPL
```

### Restarting the Service

```bash
npx pm2 restart market-data-service

# Or delete and re-add
npx pm2 delete market-data-service
npx pm2 start ecosystem.config.js
```

### Debugging

```bash
# Check if port is listening
ss -tlnp | grep 8010

# Manual start (bypasses PM2)
cd /home/rford/caelum/caelum-supersystem/market-data-service
.venv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8010 --reload

# Check Redis
redis-cli -h 10.32.3.27 ping
redis-cli -h 10.32.3.27 keys "quote:*"
```

---

## Caching Strategy

| Data Type | TTL | Why |
|-----------|-----|-----|
| Quotes | 5 seconds | Real-time, changes constantly |
| Bars | 60 seconds | Updates once per bar interval |
| Options chains | 60 seconds | Moderate update frequency |
| Expirations | 24 hours | Rarely changes |
| Strikes | 24 hours | Rarely changes |

Override with `use_cache=false` query parameter for fresh data.

---

## TradeStation Authentication

**Token Storage**: `~/.tradestation_token.json` (shared with PIM/finvec)

**Token Refresh**: Automatic via `_refresh_access_token()` when expired

**OAuth Flow**: Handled by PIM's TradeStation auth controller (user must authenticate there first)

**Status Check**:
```bash
curl http://10.32.3.27:8010/health | jq '.tradestation_authenticated'
```

---

## Integration Examples

### From opportunity-scanner (Python)
```python
import httpx

async def get_options_chain(symbol: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://10.32.3.27:8010/api/options/chain/{symbol}")
        return response.json()
```

### From PIM (TypeScript)
```typescript
const response = await fetch('http://10.32.3.27:8010/api/quotes/AAPL');
const quote = await response.json();
```

---

## Current Limitations

1. **TradeStation only** - Crypto exchanges not yet implemented
2. **No streaming** - REST only, no WebSocket support yet
3. **No account data** - By design (READ-ONLY service)
4. **Single instance** - Not load-balanced (not needed for current scale)

---

## Future Enhancements

- [ ] Crypto exchange clients (Coinbase, Kraken, Binance)
- [ ] WebSocket streaming for real-time quotes
- [ ] Futures contract data
- [ ] Historical data bulk downloads
- [ ] Multi-instance load balancing
- [ ] Prometheus metrics

---

## Related Services

- **opportunity-scanner**: Primary consumer, scans for trading opportunities
- **PassiveIncomeMaximizer**: Could migrate to use this instead of internal client
- **finvec**: Could use for some data instead of yfinance

---

## Development Workflow

```bash
# Make changes
vim src/api/server.py

# Restart service
npx pm2 restart market-data-service

# Test
curl http://10.32.3.27:8010/api/quotes/AAPL

# Check logs for errors
npx pm2 logs market-data-service --lines 20
```

---

## Important Notes

- **Never add order execution** - This is READ-ONLY by design
- **Always use caching** - Respect TradeStation API rate limits
- **Check authentication first** - Most endpoints require valid TradeStation tokens
- **Handle errors gracefully** - Return 503 if TradeStation is unavailable

---

**Updated**: 2025-12-03
