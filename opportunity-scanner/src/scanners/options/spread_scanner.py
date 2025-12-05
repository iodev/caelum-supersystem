"""
Options Spread Scanner

Scans options chains for profitable spread opportunities.
Focus on safety-first: vertical spreads (put credit spreads, call credit spreads)
"""

import httpx
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class OptionsSpreadScanner:
    """Scanner for options spread opportunities"""
    
    def __init__(self, market_data_url: str = "http://localhost:8010"):
        self.market_data_url = market_data_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.close()
    
    async def _get_quote(self, symbol: str) -> Optional[Dict]:
        """Get current quote from market data service"""
        try:
            response = await self.client.get(f"{self.market_data_url}/api/quotes/{symbol}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def _get_options_chain(self, symbol: str, expiration: Optional[str] = None) -> Optional[Dict]:
        """Get options chain from market data service"""
        try:
            url = f"{self.market_data_url}/api/options/chain/{symbol}"
            params = {}
            if expiration:
                params['expiration'] = expiration
            
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return None
    
    async def _get_expirations(self, symbol: str) -> List[str]:
        """Get available expiration dates"""
        try:
            response = await self.client.get(f"{self.market_data_url}/api/options/expirations/{symbol}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Error getting expirations for {symbol}: {e}")
            return []
    
    def _calculate_spread_metrics(self, short_strike: float, long_strike: float,
                                  short_premium: float, long_premium: float,
                                  current_price: float, spread_type: str) -> Dict:
        """
        Calculate metrics for a vertical spread
        
        Args:
            short_strike: Strike price of short option (sold)
            long_strike: Strike price of long option (bought)
            short_premium: Premium received for short option
            long_premium: Premium paid for long option
            current_price: Current stock price
            spread_type: 'put_credit' or 'call_credit'
        """
        net_credit = short_premium - long_premium
        max_profit = net_credit * 100  # Per contract
        spread_width = abs(short_strike - long_strike)
        max_loss = (spread_width - net_credit) * 100
        
        # Calculate probability of profit (simplified)
        if spread_type == 'put_credit':
            # Profit if stock stays above short strike
            distance_to_short = (current_price - short_strike) / current_price
            # Simple estimate: assume ~68% of moves within 1 std dev
            # This is very simplified - real implementation would use IV
            probability = min(0.95, max(0.50, 0.50 + (distance_to_short * 10)))
        else:  # call_credit
            # Profit if stock stays below short strike
            distance_to_short = (short_strike - current_price) / current_price
            probability = min(0.95, max(0.50, 0.50 + (distance_to_short * 10)))
        
        # Risk/reward ratio
        risk_reward = max_profit / max_loss if max_loss > 0 else 0
        
        # Score: higher is better
        # Favor high probability, good risk/reward, and decent premium
        score = (probability * 5) + (risk_reward * 2) + (net_credit * 0.1)
        
        return {
            'net_credit': round(net_credit, 2),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'spread_width': round(spread_width, 2),
            'probability': round(probability, 2),
            'risk_reward': round(risk_reward, 2),
            'score': round(score, 2)
        }
    
    async def scan_put_credit_spreads(self, symbol: str, 
                                      min_dte: int = 20, 
                                      max_dte: int = 45,
                                      min_credit: float = 0.25,
                                      spread_width: float = 5.0) -> List[Dict]:
        """
        Scan for put credit spread opportunities
        
        Strategy: Sell higher strike put, buy lower strike put
        Profit if stock stays above short strike
        
        Args:
            symbol: Stock symbol
            min_dte: Minimum days to expiration
            max_dte: Maximum days to expiration
            min_credit: Minimum net credit to receive
            spread_width: Width between strikes (default $5)
        """
        logger.info(f"Scanning put credit spreads for {symbol}")
        
        # Get current price
        quote = await self._get_quote(symbol)
        if not quote or 'Quotes' not in quote or len(quote['Quotes']) == 0:
            logger.warning(f"No quote data for {symbol}")
            return []
        
        current_price = quote['Quotes'][0]['Last']
        
        # Get expirations
        expirations = await self._get_expirations(symbol)
        if not expirations:
            logger.warning(f"No expirations found for {symbol}")
            return []
        
        # Filter expirations by DTE
        today = datetime.now()
        valid_expirations = []
        for exp_str in expirations:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
            dte = (exp_date - today).days
            if min_dte <= dte <= max_dte:
                valid_expirations.append((exp_str, dte))
        
        if not valid_expirations:
            logger.warning(f"No valid expirations in {min_dte}-{max_dte} DTE range")
            return []
        
        opportunities = []
        
        # Scan each valid expiration
        for exp_str, dte in valid_expirations[:3]:  # Limit to first 3 expirations
            chain = await self._get_options_chain(symbol, exp_str)
            if not chain or 'OptionQuotes' not in chain:
                continue
            
            puts = [opt for opt in chain['OptionQuotes'] if opt['OptionType'] == 'P']
            
            # Sort by strike
            puts.sort(key=lambda x: x['Strike'])
            
            # Look for put credit spread opportunities
            for i, short_put in enumerate(puts):
                short_strike = short_put['Strike']
                
                # Only consider OTM puts (strike below current price)
                if short_strike >= current_price:
                    continue
                
                # Find long put at spread_width below
                long_strike = short_strike - spread_width
                long_put = next((p for p in puts if p['Strike'] == long_strike), None)
                
                if not long_put:
                    continue
                
                # Get mid prices (average of bid/ask)
                short_bid = short_put.get('Bid', 0)
                short_ask = short_put.get('Ask', 0)
                long_bid = long_put.get('Bid', 0)
                long_ask = long_put.get('Ask', 0)
                
                if short_bid == 0 or long_ask == 0:
                    continue
                
                short_premium = (short_bid + short_ask) / 2
                long_premium = (long_bid + long_ask) / 2
                
                net_credit = short_premium - long_premium
                
                if net_credit < min_credit:
                    continue
                
                # Calculate metrics
                metrics = self._calculate_spread_metrics(
                    short_strike, long_strike,
                    short_premium, long_premium,
                    current_price, 'put_credit'
                )
                
                opportunities.append({
                    'symbol': symbol,
                    'strategy': 'put_credit_spread',
                    'expiration': exp_str,
                    'dte': dte,
                    'current_price': round(current_price, 2),
                    'short_strike': short_strike,
                    'long_strike': long_strike,
                    'short_premium': round(short_premium, 2),
                    'long_premium': round(long_premium, 2),
                    **metrics
                })
        
        # Sort by score
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Found {len(opportunities)} put credit spread opportunities for {symbol}")
        return opportunities
    
    async def scan_call_credit_spreads(self, symbol: str,
                                       min_dte: int = 20,
                                       max_dte: int = 45,
                                       min_credit: float = 0.25,
                                       spread_width: float = 5.0) -> List[Dict]:
        """
        Scan for call credit spread opportunities
        
        Strategy: Sell lower strike call, buy higher strike call
        Profit if stock stays below short strike
        """
        logger.info(f"Scanning call credit spreads for {symbol}")
        
        quote = await self._get_quote(symbol)
        if not quote or 'Quotes' not in quote or len(quote['Quotes']) == 0:
            return []
        
        current_price = quote['Quotes'][0]['Last']
        
        expirations = await self._get_expirations(symbol)
        if not expirations:
            return []
        
        today = datetime.now()
        valid_expirations = []
        for exp_str in expirations:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
            dte = (exp_date - today).days
            if min_dte <= dte <= max_dte:
                valid_expirations.append((exp_str, dte))
        
        if not valid_expirations:
            return []
        
        opportunities = []
        
        for exp_str, dte in valid_expirations[:3]:
            chain = await self._get_options_chain(symbol, exp_str)
            if not chain or 'OptionQuotes' not in chain:
                continue
            
            calls = [opt for opt in chain['OptionQuotes'] if opt['OptionType'] == 'C']
            calls.sort(key=lambda x: x['Strike'])
            
            for i, short_call in enumerate(calls):
                short_strike = short_call['Strike']
                
                # Only consider OTM calls (strike above current price)
                if short_strike <= current_price:
                    continue
                
                long_strike = short_strike + spread_width
                long_call = next((c for c in calls if c['Strike'] == long_strike), None)
                
                if not long_call:
                    continue
                
                short_bid = short_call.get('Bid', 0)
                short_ask = short_call.get('Ask', 0)
                long_bid = long_call.get('Bid', 0)
                long_ask = long_call.get('Ask', 0)
                
                if short_bid == 0 or long_ask == 0:
                    continue
                
                short_premium = (short_bid + short_ask) / 2
                long_premium = (long_bid + long_ask) / 2
                
                net_credit = short_premium - long_premium
                
                if net_credit < min_credit:
                    continue
                
                metrics = self._calculate_spread_metrics(
                    short_strike, long_strike,
                    short_premium, long_premium,
                    current_price, 'call_credit'
                )
                
                opportunities.append({
                    'symbol': symbol,
                    'strategy': 'call_credit_spread',
                    'expiration': exp_str,
                    'dte': dte,
                    'current_price': round(current_price, 2),
                    'short_strike': short_strike,
                    'long_strike': long_strike,
                    'short_premium': round(short_premium, 2),
                    'long_premium': round(long_premium, 2),
                    **metrics
                })
        
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Found {len(opportunities)} call credit spread opportunities for {symbol}")
        return opportunities
    
    async def scan_symbol(self, symbol: str) -> Dict:
        """Scan a symbol for all spread opportunities"""
        put_spreads = await self.scan_put_credit_spreads(symbol)
        call_spreads = await self.scan_call_credit_spreads(symbol)
        
        return {
            'symbol': symbol,
            'put_credit_spreads': put_spreads[:10],  # Top 10
            'call_credit_spreads': call_spreads[:10],  # Top 10
            'total_opportunities': len(put_spreads) + len(call_spreads)
        }
