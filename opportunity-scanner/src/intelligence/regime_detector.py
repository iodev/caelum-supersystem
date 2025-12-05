"""
Market Regime Detector

Determines current market regime to guide scanning strategy.
Uses VIX + trend analysis to classify market conditions.
"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RegimeDetector:
    """Detect current market regime"""
    
    # Regime thresholds
    VIX_LOW = 15
    VIX_MEDIUM = 20
    VIX_HIGH = 30
    
    def __init__(self, market_data_url: str = "http://localhost:8010"):
        self.market_data_url = market_data_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.close()
    
    async def _get_quote(self, symbol: str) -> Optional[Dict]:
        """Get quote from market data service"""
        try:
            response = await self.client.get(f"{self.market_data_url}/api/quotes/{symbol}")
            if response.status_code == 200:
                data = response.json()
                if 'Quotes' in data and len(data['Quotes']) > 0:
                    return data['Quotes'][0]
            return None
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def _get_bars(self, symbol: str, bars_back: int = 20) -> Optional[list]:
        """Get historical bars"""
        try:
            response = await self.client.get(
                f"{self.market_data_url}/api/bars/{symbol}",
                params={'interval': '1', 'unit': 'Daily', 'bars_back': bars_back}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting bars for {symbol}: {e}")
            return None
    
    async def detect_regime(self) -> Dict:
        """
        Detect current market regime
        
        Returns dict with:
        - regime: str ('low_vol_bullish', 'high_vol_bearish', etc.)
        - volatility: str ('low', 'medium', 'high', 'extreme')
        - trend: str ('bullish', 'bearish', 'neutral')
        - vix: float
        - spy_price: float
        - recommended_strategies: list
        - confidence: float
        """
        logger.info("Detecting market regime...")
        
        # Get VIX (volatility indicator)
        vix_quote = await self._get_quote('VIX')
        vix_level = vix_quote['Last'] if vix_quote else 20.0  # Default to medium
        
        # Classify volatility
        if vix_level < self.VIX_LOW:
            volatility = 'low'
        elif vix_level < self.VIX_MEDIUM:
            volatility = 'medium'
        elif vix_level < self.VIX_HIGH:
            volatility = 'high'
        else:
            volatility = 'extreme'
        
        # Get SPY for trend
        spy_quote = await self._get_quote('SPY')
        spy_price = spy_quote['Last'] if spy_quote else None
        
        # Get recent SPY bars for trend analysis
        spy_bars = await self._get_bars('SPY', bars_back=20)
        
        trend = 'neutral'
        if spy_bars and len(spy_bars) >= 10:
            # Simple trend: compare current price to 10-day average
            closes = [bar['Close'] for bar in spy_bars[-10:]]
            avg_close = sum(closes) / len(closes)
            
            if spy_price:
                if spy_price > avg_close * 1.02:  # 2% above average
                    trend = 'bullish'
                elif spy_price < avg_close * 0.98:  # 2% below average
                    trend = 'bearish'
        
        # Determine regime
        regime = f"{volatility}_vol_{trend}"
        
        # Recommend strategies based on regime
        strategies = self._get_recommended_strategies(volatility, trend)
        
        # Calculate confidence (simplified)
        confidence = 0.75  # Default medium confidence
        if vix_quote and spy_quote and spy_bars:
            confidence = 0.85  # Higher confidence with all data
        
        result = {
            'regime': regime,
            'volatility': volatility,
            'trend': trend,
            'vix': round(vix_level, 2) if vix_level else None,
            'spy_price': round(spy_price, 2) if spy_price else None,
            'recommended_strategies': strategies,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Detected regime: {regime} (confidence: {confidence})")
        return result
    
    def _get_recommended_strategies(self, volatility: str, trend: str) -> list:
        """Get recommended strategies for current regime"""
        strategies = []
        
        if volatility == 'low':
            # Low volatility: premium is cheap, avoid selling
            strategies.append({
                'name': 'Long options',
                'rationale': 'Low IV makes options cheap to buy'
            })
        
        elif volatility in ['medium', 'high']:
            # Medium/high volatility: good for selling premium
            if trend == 'bullish':
                strategies.append({
                    'name': 'Put credit spreads',
                    'rationale': 'Sell puts in uptrend, high premium'
                })
            elif trend == 'bearish':
                strategies.append({
                    'name': 'Call credit spreads',
                    'rationale': 'Sell calls in downtrend, high premium'
                })
            else:  # neutral
                strategies.append({
                    'name': 'Iron condors',
                    'rationale': 'Sideways market, sell both sides'
                })
                strategies.append({
                    'name': 'Put credit spreads',
                    'rationale': 'Conservative premium collection'
                })
        
        elif volatility == 'extreme':
            # Extreme volatility: be cautious
            strategies.append({
                'name': 'Put credit spreads (wide)',
                'rationale': 'High premium but use wider spreads for safety'
            })
            strategies.append({
                'name': 'Wait for calm',
                'rationale': 'Extreme volatility increases risk'
            })
        
        return strategies
    
    async def get_scan_symbols(self, regime: Optional[Dict] = None) -> list:
        """
        Get recommended symbols to scan based on regime
        
        Returns list of symbols prioritized for current market conditions
        """
        if regime is None:
            regime = await self.detect_regime()
        
        # Default symbol list (high liquidity options)
        symbols = [
            'SPY',   # S&P 500 ETF
            'QQQ',   # Nasdaq 100 ETF
            'IWM',   # Russell 2000 ETF
            'AAPL',  # Tech blue chip
            'MSFT',  # Tech blue chip
            'NVDA',  # High IV tech
            'TSLA',  # High IV growth
            'AMD',   # Semiconductor
            'AMZN',  # E-commerce
            'GOOGL', # Search/cloud
        ]
        
        # Prioritize based on volatility
        if regime['volatility'] in ['high', 'extreme']:
            # High volatility: favor ETFs over individual stocks
            symbols = ['SPY', 'QQQ', 'IWM'] + [s for s in symbols if s not in ['SPY', 'QQQ', 'IWM']]
        
        return symbols[:10]  # Return top 10
