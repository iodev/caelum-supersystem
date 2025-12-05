"""FastAPI server for Market Data Service"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging
import os
from dotenv import load_dotenv

from ..clients.tradestation import TradeStationClient
from ..cache.redis_cache import RedisCache
from ..utils.market_hours import MarketHoursUtil

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Market Data Service",
    description="Unified market data access for TradeStation, crypto exchanges, and more",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients and cache
ts_client: Optional[TradeStationClient] = None
cache: Optional[RedisCache] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ts_client, cache
    
    logger.info("Starting Market Data Service...")
    
    # Initialize Redis cache
    redis_host = os.getenv('REDIS_HOST', '10.32.3.27')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    cache = RedisCache(host=redis_host, port=redis_port)
    
    # Initialize TradeStation client
    ts_client_id = os.getenv('TRADESTATION_CLIENT_ID')
    ts_client_secret = os.getenv('TRADESTATION_CLIENT_SECRET')
    
    if ts_client_id and ts_client_secret:
        ts_client = TradeStationClient(ts_client_id, ts_client_secret)
        if ts_client.is_authenticated():
            logger.info("TradeStation client authenticated")
        else:
            logger.warning("TradeStation client not authenticated. OAuth flow needed.")
    else:
        logger.warning("TradeStation credentials not configured")
    
    logger.info("Market Data Service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Market Data Service...")

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "market-data-service",
        "tradestation_authenticated": ts_client.is_authenticated() if ts_client else False,
        "redis_connected": cache.is_connected() if cache else False
    }

# ==================== Market Status ====================

@app.get("/api/market/status")
async def get_market_status():
    """Get current market status"""
    return MarketHoursUtil.get_market_status()

# ==================== TradeStation Endpoints ====================

@app.get("/api/quotes/{symbol}")
async def get_quote(symbol: str, use_cache: bool = True):
    """Get real-time quote for a symbol"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    # Check cache first
    cache_key = f"quote:{symbol}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for quote: {symbol}")
            return cached
    
    # Fetch from API
    try:
        data = await ts_client.get_quote(symbol)
        
        if data and cache:
            # Cache for 5 seconds (quotes change rapidly)
            cache.set(cache_key, data, ttl_seconds=5)
        
        return data or {"error": "Quote not found"}
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bars/{symbol}")
async def get_bars(
    symbol: str,
    interval: str = "1",
    unit: str = "Minute",
    bars_back: int = Query(100, ge=1, le=1000),
    start_date: Optional[str] = None,
    use_cache: bool = True
):
    """Get historical bars"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    # Check cache
    cache_key = f"bars:{symbol}:{interval}:{unit}:{bars_back}:{start_date}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for bars: {symbol}")
            return cached
    
    # Fetch from API
    try:
        data = await ts_client.get_bars(symbol, interval, unit, bars_back, start_date)
        
        if data and cache:
            # Cache for 60 seconds (bars update less frequently)
            cache.set(cache_key, data, ttl_seconds=60)
        
        return data or []
    except Exception as e:
        logger.error(f"Error fetching bars for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/chain/{symbol}")
async def get_options_chain(
    symbol: str,
    expiration: Optional[str] = None,
    use_cache: bool = True
):
    """Get options chain for a symbol"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    # Check cache
    cache_key = f"options_chain:{symbol}:{expiration}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for options chain: {symbol}")
            return cached
    
    # Fetch from API
    try:
        data = await ts_client.get_options_chain(symbol, expiration)
        
        if data and cache:
            # Cache for 60 seconds (options chains update frequently during market hours)
            cache.set(cache_key, data, ttl_seconds=60)
        
        return data or {"error": "Options chain not found"}
    except Exception as e:
        logger.error(f"Error fetching options chain for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/expirations/{symbol}")
async def get_options_expirations(symbol: str, use_cache: bool = True):
    """Get available option expiration dates"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    # Check cache
    cache_key = f"options_expirations:{symbol}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Fetch from API
    try:
        data = await ts_client.get_options_expirations(symbol)
        
        if data and cache:
            # Cache for 24 hours (expirations don't change often)
            cache.set(cache_key, data, ttl_seconds=86400)
        
        return data or []
    except Exception as e:
        logger.error(f"Error fetching expirations for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/options/strikes/{symbol}")
async def get_options_strikes(
    symbol: str,
    expiration: str,
    use_cache: bool = True
):
    """Get available strike prices for an expiration"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    # Check cache
    cache_key = f"options_strikes:{symbol}:{expiration}"
    if use_cache and cache:
        cached = cache.get(cache_key)
        if cached:
            return cached
    
    # Fetch from API
    try:
        data = await ts_client.get_options_strikes(symbol, expiration)
        
        if data and cache:
            # Cache for 24 hours
            cache.set(cache_key, data, ttl_seconds=86400)
        
        return data or []
    except Exception as e:
        logger.error(f"Error fetching strikes for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/symbols/search")
async def search_symbols(
    query: str = Query(..., min_length=1),
    asset_type: str = "STOCK"
):
    """Search for symbols"""
    if not ts_client:
        raise HTTPException(status_code=503, detail="TradeStation client not available")
    
    try:
        data = await ts_client.search_symbols(query, asset_type)
        return data or []
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Cache Management ====================

@app.delete("/api/cache/clear")
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern"""
    if not cache:
        raise HTTPException(status_code=503, detail="Cache not available")
    
    try:
        count = cache.clear_pattern(f"*{pattern}*")
        return {"cleared": count, "pattern": pattern}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', '8010'))
    uvicorn.run(app, host="0.0.0.0", port=port)
