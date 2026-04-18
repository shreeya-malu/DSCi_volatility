# data_collection.py
"""
Real-time data collection module using yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """Handles real-time data collection from Yahoo Finance"""
    
    def __init__(self, tickers: List[str], interval: str = '1m', period: str = '1d'):
        """
        Initialize data collector
        
        Args:
            tickers: List of stock tickers
            interval: Data interval (1m, 5m, 1h, etc.)
            period: Data period (1d, 5d, 1mo, etc.)
        """
        self.tickers = tickers
        self.interval = interval
        self.period = period
        self.cache = {}
        
    def fetch_realtime_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch real-time data for a single ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=self.period, interval=self.interval)
            
            if data.empty:
                logger.warning(f"No data received for {ticker}")
                return None
                
            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            
            logger.info(f"Successfully fetched {len(data)} rows for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def fetch_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch real-time data for all tickers
        
        Returns:
            Dictionary mapping ticker to DataFrame
        """
        all_data = {}
        
        for ticker in self.tickers:
            data = self.fetch_realtime_data(ticker)
            if data is not None:
                all_data[ticker] = data
            time.sleep(0.5)  # Rate limiting
            
        return all_data
    
    def get_latest_price(self, ticker: str) -> Optional[float]:
        """
        Get the latest price for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Latest close price or None
        """
        data = self.fetch_realtime_data(ticker)
        if data is not None and not data.empty:
            return data['close'].iloc[-1]
        return None
    
    def get_historical_data(self, ticker: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for statistical analysis
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days of historical data
            
        Returns:
            DataFrame with historical data
        """
        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = stock.history(start=start_date, end=end_date, interval='1d')
            
            if data.empty:
                logger.warning(f"No historical data for {ticker}")
                return None
                
            data.columns = [col.lower() for col in data.columns]
            logger.info(f"Fetched {len(data)} days of historical data for {ticker}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    collector = DataCollector(['AAPL', 'MSFT'])
    data = collector.fetch_all_data()
    for ticker, df in data.items():
        print(f"\n{ticker} Data:")
        print(df.tail())