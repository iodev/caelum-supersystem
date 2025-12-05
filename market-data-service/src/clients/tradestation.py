"""
TradeStation API Client - READ-ONLY market data access

This client handles authentication and market data retrieval from TradeStation API.
No order execution functionality to keep this service safe and stateless.
"""

import httpx
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class TradeStationClient:
    """TradeStation API client for market data retrieval"""
    
    BASE_URL = "https://api.tradestation.com/v3"
    TOKEN_URL = "https://signin.tradestation.com/oauth/token"
    
    def __init__(self, client_id: str, client_secret: str, token_storage_path: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_storage_path = token_storage_path or str(Path.home() / ".tradestation_token.json")
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Load existing tokens if available
        self._load_tokens()
    
    def _load_tokens(self):
        """Load tokens from storage file"""
        try:
            if os.path.exists(self.token_storage_path):
                with open(self.token_storage_path, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.refresh_token = data.get('refresh_token')
                    
                    expires_str = data.get('expires_at')
                    if expires_str:
                        self.token_expires_at = datetime.fromisoformat(expires_str)
                    
                logger.info("Loaded TradeStation tokens from storage")
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to storage file"""
        try:
            data = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
            }
            
            with open(self.token_storage_path, 'w') as f:
                json.dump(data, f)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(self.token_storage_path, 0o600)
            
            logger.info("Saved TradeStation tokens to storage")
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
    
    async def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        'grant_type': 'refresh_token',
                        'refresh_token': self.refresh_token,
                        'client_id': self.client_id,
                        'client_secret': self.client_secret
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data['access_token']
                    
                    # Update refresh token if provided
                    if 'refresh_token' in data:
                        self.refresh_token = data['refresh_token']
                    
                    # Calculate expiration time
                    expires_in = data.get('expires_in', 1200)  # Default 20 minutes
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    self._save_tokens()
                    logger.info("Successfully refreshed access token")
                    return True
                else:
                    logger.error(f"Token refresh failed: {response.status_code} {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token"""
        # Check if token is expired or will expire in next 60 seconds
        if self.token_expires_at and datetime.now() >= (self.token_expires_at - timedelta(seconds=60)):
            logger.info("Token expired or expiring soon, refreshing...")
            return await self._refresh_access_token()
        
        # Check if we have a token
        if not self.access_token:
            logger.error("No access token available. Please authenticate via OAuth flow first.")
            return False
        
        return True
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make an authenticated API request"""
        if not await self.ensure_authenticated():
            raise Exception("Authentication failed")
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                if response.status_code == 401:
                    # Token expired, try refreshing
                    logger.info("Got 401, attempting token refresh...")
                    if await self._refresh_access_token():
                        # Retry the request with new token
                        headers['Authorization'] = f'Bearer {self.access_token}'
                        response = await client.get(url, headers=headers, params=params)
                    else:
                        raise Exception("Token refresh failed")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    # ==================== Market Data Methods ====================
    
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a symbol"""
        try:
            data = await self._make_request('GET', f'/marketdata/quotes/{symbol}')
            return data
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return None
    
    async def get_bars(self, symbol: str, interval: str = '1', unit: str = 'Minute', 
                       bars_back: int = 100, start_date: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Get historical bars
        
        Args:
            symbol: Trading symbol
            interval: Bar interval (1, 5, 15, 30, 60, etc.)
            unit: Time unit (Minute, Daily, Weekly, Monthly)
            bars_back: Number of bars to retrieve
            start_date: Optional start date (YYYY-MM-DD)
        """
        params = {
            'interval': interval,
            'unit': unit,
            'barsback': bars_back
        }
        
        if start_date:
            params['firstdate'] = start_date
        
        try:
            data = await self._make_request('GET', f'/marketdata/barcharts/{symbol}', params=params)
            
            if data and 'Bars' in data:
                return data['Bars']
            return []
            
        except Exception as e:
            logger.error(f"Error getting bars for {symbol}: {e}")
            return None
    
    async def get_options_chain(self, symbol: str, expiration: Optional[str] = None) -> Optional[Dict]:
        """
        Get options chain for a symbol
        
        Args:
            symbol: Underlying symbol (e.g., 'AAPL')
            expiration: Optional expiration date (YYYY-MM-DD)
        """
        params = {}
        if expiration:
            params['expiration'] = expiration
        
        try:
            data = await self._make_request('GET', f'/marketdata/options/chains/{symbol}', params=params)
            return data
        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return None
    
    async def get_options_expirations(self, symbol: str) -> Optional[List[str]]:
        """Get available option expiration dates for a symbol"""
        try:
            data = await self._make_request('GET', f'/marketdata/options/expirations/{symbol}')
            
            if data and 'Expirations' in data:
                return data['Expirations']
            return []
            
        except Exception as e:
            logger.error(f"Error getting option expirations for {symbol}: {e}")
            return None
    
    async def get_options_strikes(self, symbol: str, expiration: str) -> Optional[List[float]]:
        """Get available strike prices for a symbol and expiration"""
        try:
            data = await self._make_request('GET', 
                f'/marketdata/options/strikes/{symbol}',
                params={'expiration': expiration}
            )
            
            if data and 'Strikes' in data:
                return data['Strikes']
            return []
            
        except Exception as e:
            logger.error(f"Error getting strikes for {symbol}: {e}")
            return None
    
    async def search_symbols(self, query: str, asset_type: str = 'STOCK') -> Optional[List[Dict]]:
        """
        Search for symbols
        
        Args:
            query: Search query
            asset_type: STOCK, FUTURES, OPTIONS, etc.
        """
        try:
            data = await self._make_request('GET', 
                '/marketdata/symbollookup',
                params={'search': query, 'assettype': asset_type}
            )
            return data
        except Exception as e:
            logger.error(f"Error searching symbols for {query}: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.access_token is not None
