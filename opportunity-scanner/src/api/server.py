"""FastAPI server for Opportunity Scanner"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import logging
import os
from dotenv import load_dotenv
import asyncio

from ..scanners.options.spread_scanner import OptionsSpreadScanner
from ..intelligence.regime_detector import RegimeDetector

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
    title="Opportunity Scanner",
    description="Intelligent scanner for options, futures, and crypto trading opportunities",
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

# Service clients
options_scanner: Optional[OptionsSpreadScanner] = None
regime_detector: Optional[RegimeDetector] = None
market_data_url: str = ""

# Latest scan results (in-memory cache)
latest_regime: Optional[dict] = None
latest_opportunities: Optional[dict] = None
scan_in_progress: bool = False

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global options_scanner, regime_detector, market_data_url
    
    logger.info("Starting Opportunity Scanner...")
    
    market_data_url = os.getenv('MARKET_DATA_SERVICE_URL', 'http://localhost:8010')
    
    options_scanner = OptionsSpreadScanner(market_data_url)
    regime_detector = RegimeDetector(market_data_url)
    
    logger.info(f"Connected to market data service: {market_data_url}")
    logger.info("Opportunity Scanner started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Opportunity Scanner...")
    if options_scanner:
        await options_scanner.close()
    if regime_detector:
        await regime_detector.close()

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "opportunity-scanner",
        "market_data_url": market_data_url,
        "scan_in_progress": scan_in_progress
    }

# ==================== Regime Detection ====================

@app.get("/api/regime")
async def get_regime():
    """Get current market regime"""
    if not regime_detector:
        raise HTTPException(status_code=503, detail="Regime detector not available")
    
    try:
        regime = await regime_detector.detect_regime()
        global latest_regime
        latest_regime = regime
        return regime
    except Exception as e:
        logger.error(f"Error detecting regime: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/regime/symbols")
async def get_scan_symbols():
    """Get recommended symbols for current regime"""
    if not regime_detector:
        raise HTTPException(status_code=503, detail="Regime detector not available")
    
    try:
        symbols = await regime_detector.get_scan_symbols()
        return {"symbols": symbols}
    except Exception as e:
        logger.error(f"Error getting scan symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Options Scanning ====================

@app.get("/api/scan/options/{symbol}")
async def scan_options(
    symbol: str,
    min_dte: int = 20,
    max_dte: int = 45,
    min_credit: float = 0.25,
    spread_width: float = 5.0
):
    """Scan options for a specific symbol"""
    if not options_scanner:
        raise HTTPException(status_code=503, detail="Options scanner not available")
    
    try:
        result = await options_scanner.scan_symbol(symbol)
        return result
    except Exception as e:
        logger.error(f"Error scanning {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan/full")
async def scan_full(background_tasks: BackgroundTasks, symbols: Optional[List[str]] = None):
    """
    Scan multiple symbols for all opportunities
    Runs in background and stores results
    """
    global scan_in_progress
    
    if scan_in_progress:
        return {"status": "scan_already_in_progress", "message": "A scan is already running"}
    
    if not regime_detector or not options_scanner:
        raise HTTPException(status_code=503, detail="Scanners not available")
    
    # Start background scan
    background_tasks.add_task(_run_full_scan, symbols)
    
    return {
        "status": "scan_started",
        "message": "Full scan initiated in background",
        "check_status": "/api/scan/status"
    }

async def _run_full_scan(symbols: Optional[List[str]] = None):
    """Background task for full scan"""
    global scan_in_progress, latest_regime, latest_opportunities
    
    scan_in_progress = True
    logger.info("Starting full opportunity scan...")
    
    try:
        # Detect regime
        regime = await regime_detector.detect_regime()
        latest_regime = regime
        
        # Get symbols to scan
        if not symbols:
            symbols = await regime_detector.get_scan_symbols(regime)
        
        logger.info(f"Scanning {len(symbols)} symbols: {symbols}")
        
        # Scan each symbol
        all_opportunities = {
            'regime': regime,
            'symbols_scanned': [],
            'total_opportunities': 0,
            'put_spreads': [],
            'call_spreads': []
        }
        
        for symbol in symbols:
            try:
                result = await options_scanner.scan_symbol(symbol)
                all_opportunities['symbols_scanned'].append(symbol)
                all_opportunities['put_spreads'].extend(result['put_credit_spreads'])
                all_opportunities['call_spreads'].extend(result['call_credit_spreads'])
                all_opportunities['total_opportunities'] += result['total_opportunities']
                
                logger.info(f"Scanned {symbol}: {result['total_opportunities']} opportunities")
                
                # Small delay to avoid hammering the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by score
        all_opportunities['put_spreads'].sort(key=lambda x: x['score'], reverse=True)
        all_opportunities['call_spreads'].sort(key=lambda x: x['score'], reverse=True)
        
        # Keep top 50
        all_opportunities['put_spreads'] = all_opportunities['put_spreads'][:50]
        all_opportunities['call_spreads'] = all_opportunities['call_spreads'][:50]
        
        latest_opportunities = all_opportunities
        
        logger.info(f"Full scan complete: {all_opportunities['total_opportunities']} total opportunities")
        
    except Exception as e:
        logger.error(f"Error in full scan: {e}")
    finally:
        scan_in_progress = False

@app.get("/api/scan/status")
async def get_scan_status():
    """Get status of latest scan"""
    return {
        "scan_in_progress": scan_in_progress,
        "latest_regime": latest_regime,
        "latest_scan_summary": {
            "total_opportunities": latest_opportunities['total_opportunities'] if latest_opportunities else 0,
            "symbols_scanned": len(latest_opportunities['symbols_scanned']) if latest_opportunities else 0,
            "put_spreads_found": len(latest_opportunities['put_spreads']) if latest_opportunities else 0,
            "call_spreads_found": len(latest_opportunities['call_spreads']) if latest_opportunities else 0
        } if latest_opportunities else None
    }

@app.get("/api/opportunities")
async def get_opportunities(
    strategy: Optional[str] = None,
    min_score: float = 0.0,
    limit: int = 20
):
    """Get latest opportunities from scan"""
    if not latest_opportunities:
        return {
            "message": "No scan results available. Run /api/scan/full first",
            "opportunities": []
        }
    
    opportunities = []
    
    if not strategy or strategy == 'put_credit_spread':
        opportunities.extend(latest_opportunities['put_spreads'])
    
    if not strategy or strategy == 'call_credit_spread':
        opportunities.extend(latest_opportunities['call_spreads'])
    
    # Filter by score
    opportunities = [opp for opp in opportunities if opp['score'] >= min_score]
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        "regime": latest_regime,
        "opportunities": opportunities[:limit],
        "total_available": len(opportunities)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', '8011'))
    uvicorn.run(app, host="0.0.0.0", port=port)
