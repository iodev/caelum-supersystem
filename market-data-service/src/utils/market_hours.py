"""Market hours utility - local time-based logic"""

from datetime import datetime, time
from typing import Tuple
import pytz

class MarketHoursUtil:
    """Utility for checking market hours without API calls"""
    
    # US Stock Market Hours (Eastern Time)
    MARKET_OPEN_TIME = time(9, 30)
    MARKET_CLOSE_TIME = time(16, 0)
    
    # Pre-market and after-hours
    PRE_MARKET_START = time(4, 0)
    AFTER_HOURS_END = time(20, 0)
    
    @staticmethod
    def is_market_open(dt: datetime = None) -> bool:
        """
        Check if market is open using local time
        
        Args:
            dt: DateTime to check (defaults to now in ET)
        """
        if dt is None:
            et = pytz.timezone('US/Eastern')
            dt = datetime.now(et)
        
        # Market is closed on weekends
        if dt.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check if within market hours
        current_time = dt.time()
        return MarketHoursUtil.MARKET_OPEN_TIME <= current_time <= MarketHoursUtil.MARKET_CLOSE_TIME
    
    @staticmethod
    def is_extended_hours(dt: datetime = None) -> bool:
        """Check if in pre-market or after-hours"""
        if dt is None:
            et = pytz.timezone('US/Eastern')
            dt = datetime.now(et)
        
        # Extended hours not available on weekends
        if dt.weekday() >= 5:
            return False
        
        current_time = dt.time()
        
        # Pre-market: 4:00 AM - 9:30 AM
        # After-hours: 4:00 PM - 8:00 PM
        return (
            (MarketHoursUtil.PRE_MARKET_START <= current_time < MarketHoursUtil.MARKET_OPEN_TIME) or
            (MarketHoursUtil.MARKET_CLOSE_TIME < current_time <= MarketHoursUtil.AFTER_HOURS_END)
        )
    
    @staticmethod
    def get_market_status() -> dict:
        """Get current market status"""
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        is_open = MarketHoursUtil.is_market_open(now)
        is_extended = MarketHoursUtil.is_extended_hours(now)
        
        status = "closed"
        if is_open:
            status = "open"
        elif is_extended:
            current_time = now.time()
            if current_time < MarketHoursUtil.MARKET_OPEN_TIME:
                status = "pre_market"
            else:
                status = "after_hours"
        
        return {
            "status": status,
            "is_open": is_open,
            "is_extended_hours": is_extended,
            "current_time_et": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "weekday": now.strftime("%A")
        }
