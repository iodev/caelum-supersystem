# Market Data Service

**Unified market data access layer for the Caelum SuperSystem**

## Overview

Market Data Service is a centralized API service that provides read-only access to market data from multiple sources. It eliminates code duplication across the SuperSystem by consolidating all market data access into a single, reusable service.

## Features

- **TradeStation API Integration**: Stocks, options chains, futures data
- **Crypto Exchange Support**: (Planned) Coinbase, Kraken, Binance
- **Redis Caching**: Intelligent caching with configurable TTL per data type
- **FastAPI**: High-performance async API
- **Zero Duplication**: Single source of truth for market data across all services

## Architecture

```
market-data-service (Port 8010)
    ├── TradeStation Client (OAuth, token refresh)
    ├── Redis Cache (10.32.3.27:6379)
    └── FastAPI Server
        ├── /health - Service health check
        ├── /api/market/status - Market hours status
        ├── /api/quotes/{symbol} - Real-time quotes
        ├── /api/bars/{symbol} - Historical bars
        ├── /api/options/chain/{symbol} - Options chains
        ├── /api/options/expirations/{symbol} - Available expirations
        └── /api/options/strikes/{symbol} - Available strikes
```

## Quick Start

### Installation

```bash
# Install dependencies with uv
uv venv .venv
uv pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your TradeStation credentials
```

### Running the Service

```bash
# With PM2 (recommended)
npx pm2 start ecosystem.config.js

# Manual start
.venv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8010
```

### Testing

```bash
# Health check
curl http://10.32.3.27:8010/health

# Market status
curl http://10.32.3.27:8010/api/market/status

# Get quote (requires TradeStation authentication)
curl http://10.32.3.27:8010/api/quotes/AAPL

# Get options chain
curl http://10.32.3.27:8010/api/options/chain/AAPL
```

## Configuration

### Environment Variables

```bash
# TradeStation API
TRADESTATION_CLIENT_ID=your_client_id
TRADESTATION_CLIENT_SECRET=your_client_secret

# Redis
REDIS_HOST=10.32.3.27
REDIS_PORT=6379

# Service
PORT=8010
LOG_LEVEL=INFO
```

### Token Management

TradeStation tokens are stored in `~/.tradestation_token.json` and automatically refreshed. The service shares tokens with other SuperSystem services (PIM, finvec).

## Caching Strategy

| Data Type | TTL | Reasoning |
|-----------|-----|-----------|
| Quotes | 5s | High-frequency updates during market hours |
| Bars | 60s | Updates once per bar interval |
| Options Chains | 60s | Moderate update frequency |
| Expirations | 24h | Rarely changes |
| Strikes | 24h | Rarely changes |

## Used By

- **opportunity-scanner**: Scans options/futures for trading opportunities
- **PassiveIncomeMaximizer**: (Future) Replace internal TradeStation client
- **finvec**: (Future) Replace yfinance for some data sources

## API Endpoints

### Health & Status

#### GET /health
```json
{
  "status": "healthy",
  "service": "market-data-service",
  "tradestation_authenticated": true,
  "redis_connected": true
}
```

#### GET /api/market/status
```json
{
  "status": "open",
  "is_open": true,
  "is_extended_hours": false,
  "current_time_et": "2025-12-03 09:35:00 EST",
  "weekday": "Wednesday"
}
```

### Market Data

#### GET /api/quotes/{symbol}
Query Parameters:
- `use_cache` (bool, default: true) - Use cached data

#### GET /api/bars/{symbol}
Query Parameters:
- `interval` (str, default: "1") - Bar interval
- `unit` (str, default: "Minute") - Time unit
- `bars_back` (int, default: 100) - Number of bars
- `start_date` (str, optional) - Start date (YYYY-MM-DD)
- `use_cache` (bool, default: true)

#### GET /api/options/chain/{symbol}
Query Parameters:
- `expiration` (str, optional) - Filter by expiration (YYYY-MM-DD)
- `use_cache` (bool, default: true)

#### GET /api/options/expirations/{symbol}
Returns list of available expiration dates

#### GET /api/options/strikes/{symbol}
Query Parameters:
- `expiration` (str, required) - Expiration date

### Cache Management

#### DELETE /api/cache/clear
Query Parameters:
- `pattern` (str, default: "*") - Pattern to match for clearing

## Development

### Project Structure

```
market-data-service/
├── src/
│   ├── clients/
│   │   └── tradestation.py      # TradeStation API client
│   ├── api/
│   │   └── server.py            # FastAPI application
│   ├── cache/
│   │   └── redis_cache.py       # Redis caching layer
│   └── utils/
│       └── market_hours.py      # Market hours utilities
├── tests/                       # (Future) Test suite
├── requirements.txt             # Python dependencies
├── ecosystem.config.js          # PM2 configuration
└── README.md
```

### Adding New Data Sources

1. Create client in `src/clients/{provider}.py`
2. Add endpoints in `src/api/server.py`
3. Configure caching strategy
4. Update documentation

## Monitoring

```bash
# PM2 status
npx pm2 status market-data-service

# View logs
npx pm2 logs market-data-service

# Monitor resource usage
npx pm2 monit
```

## Troubleshooting

### Service not starting
```bash
# Check logs
npx pm2 logs market-data-service --lines 50

# Verify venv
ls -la .venv/bin/uvicorn

# Test manually
.venv/bin/uvicorn src.api.server:app --host 0.0.0.0 --port 8010
```

### TradeStation authentication failed
- Verify credentials in `.env`
- Check token file: `~/.tradestation_token.json`
- Token sharing with PIM/finvec should work automatically

### Redis connection failed
- Verify Redis is running: `redis-cli -h 10.32.3.27 ping`
- Service will work without Redis but won't cache

## License

Part of the Caelum SuperSystem
