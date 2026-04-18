# portfolio_manager.py
"""
Portfolio management system with risk management
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Represents a trading position"""
    ticker: str
    entry_price: float
    shares: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    position_size: float
    
@dataclass
class Trade:
    """Represents a completed trade"""
    ticker: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    shares: float
    pnl: float
    pnl_percent: float
    regime_at_entry: str
    
class PortfolioManager:
    """Manages portfolio positions and risk"""
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 max_position_size: float = 10000.0,
                 risk_per_trade: float = 0.02,
                 stop_loss_atr_mult: float = 2.0):
        """
        Initialize portfolio manager
        
        Args:
            initial_capital: Starting capital
            max_position_size: Maximum position size in dollars
            risk_per_trade: Risk per trade as percentage of capital
            stop_loss_atr_mult: ATR multiplier for stop loss
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade
        self.stop_loss_atr_mult = stop_loss_atr_mult
        
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        self.timestamps: List[datetime] = [datetime.now()]
        
    def calculate_position_size(self,
                                ticker: str,
                                current_price: float,
                                atr: float,
                                regime_multiplier: float = 1.0) -> float:
        """
        Calculate position size based on risk and regime
        
        Args:
            ticker: Stock ticker
            current_price: Current market price
            atr: Average True Range
            regime_multiplier: Regime-based multiplier
            
        Returns:
            Position size in dollars
        """
        # Calculate risk-based position size
        risk_amount = self.capital * self.risk_per_trade
        stop_distance = atr * self.stop_loss_atr_mult
        risk_based_size = risk_amount / stop_distance * current_price if stop_distance > 0 else 0
        
        # Apply regime multiplier
        adjusted_size = risk_based_size * regime_multiplier
        
        # Apply constraints
        final_size = min(adjusted_size, self.max_position_size, self.capital * 0.25)
        
        # Ensure minimum position
        if final_size < 1000:  # Minimum $1000 position
            final_size = 0
            
        logger.info(f"Position size for {ticker}: ${final_size:.2f} (regime mult: {regime_multiplier})")
        return final_size
    
    def open_position(self,
                     ticker: str,
                     current_price: float,
                     atr: float,
                     regime_multiplier: float = 1.0,
                     regime: str = "NORMAL") -> bool:
        """
        Open a new position
        
        Args:
            ticker: Stock ticker
            current_price: Current price
            atr: Average True Range
            regime_multiplier: Regime-based position multiplier
            regime: Current market regime
            
        Returns:
            True if position opened, False otherwise
        """
        # Check if already have position
        if ticker in self.positions:
            logger.warning(f"Already have position in {ticker}")
            return False
            
        # Calculate position size
        position_size = self.calculate_position_size(ticker, current_price, atr, regime_multiplier)
        
        if position_size == 0:
            logger.info(f"Skipping {ticker} - position size too small")
            return False
            
        # Calculate number of shares
        shares = position_size / current_price
        
        # Set stop loss and take profit
        stop_loss = current_price - (atr * self.stop_loss_atr_mult)
        take_profit = current_price + (atr * self.stop_loss_atr_mult * 2)  # 2:1 reward:risk
        
        # Create position
        position = Position(
            ticker=ticker,
            entry_price=current_price,
            shares=shares,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size
        )
        
        self.positions[ticker] = position
        self.capital -= position_size
        
        logger.info(f"Opened {shares:.2f} shares of {ticker} at ${current_price:.2f}")
        logger.info(f"Stop loss: ${stop_loss:.2f}, Take profit: ${take_profit:.2f}")
        
        return True
    
    def close_position(self, ticker: str, current_price: float, regime: str = "NORMAL") -> Optional[Trade]:
        """
        Close an existing position
        
        Args:
            ticker: Stock ticker
            current_price: Current price
            regime: Current market regime
            
        Returns:
            Trade object if closed, None otherwise
        """
        if ticker not in self.positions:
            return None
            
        position = self.positions[ticker]
        
        # Calculate P&L
        pnl = (current_price - position.entry_price) * position.shares
        pnl_percent = (current_price - position.entry_price) / position.entry_price * 100
        
        # Create trade record
        trade = Trade(
            ticker=ticker,
            entry_time=position.entry_time,
            exit_time=datetime.now(),
            entry_price=position.entry_price,
            exit_price=current_price,
            shares=position.shares,
            pnl=pnl,
            pnl_percent=pnl_percent,
            regime_at_entry=regime
        )
        
        # Update capital
        self.capital += position.position_size + pnl
        self.trades.append(trade)
        
        # Remove position
        del self.positions[ticker]
        
        # Update equity curve
        self.equity_curve.append(self.get_total_value(current_price))
        self.timestamps.append(datetime.now())
        
        logger.info(f"Closed {ticker}: P&L = ${pnl:.2f} ({pnl_percent:.2f}%)")
        
        return trade
    
    def check_stop_loss_take_profit(self, ticker: str, current_price: float, regime: str = "NORMAL") -> bool:
        """
        Check if position should be closed due to stop loss or take profit
        
        Args:
            ticker: Stock ticker
            current_price: Current price
            regime: Current market regime
            
        Returns:
            True if position was closed, False otherwise
        """
        if ticker not in self.positions:
            return False
            
        position = self.positions[ticker]
        
        # Check stop loss
        if current_price <= position.stop_loss:
            logger.info(f"Stop loss triggered for {ticker} at ${current_price:.2f}")
            self.close_position(ticker, current_price, regime)
            return True
            
        # Check take profit
        if current_price >= position.take_profit:
            logger.info(f"Take profit triggered for {ticker} at ${current_price:.2f}")
            self.close_position(ticker, current_price, regime)
            return True
            
        return False
    
    def update_positions(self, ticker: str, current_price: float, atr: float):
        """
        Update trailing stop loss for position
        
        Args:
            ticker: Stock ticker
            current_price: Current price
            atr: Current ATR
        """
        if ticker not in self.positions:
            return
            
        position = self.positions[ticker]
        
        # Trailing stop loss (only move up, never down)
        new_stop = current_price - (atr * self.stop_loss_atr_mult)
        if new_stop > position.stop_loss:
            position.stop_loss = new_stop
            logger.debug(f"Updated stop loss for {ticker} to ${new_stop:.2f}")
    
    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value
        
        Args:
            current_prices: Dictionary mapping ticker to current price
            
        Returns:
            Total portfolio value
        """
        positions_value = 0
        for ticker, position in self.positions.items():
            if ticker in current_prices:
                positions_value += position.shares * current_prices[ticker]
                
        return self.capital + positions_value
    
    def get_portfolio_metrics(self, current_prices: Dict[str, float]) -> Dict[str, any]:
        """
        Calculate portfolio performance metrics
        
        Args:
            current_prices: Current prices for all tickers
            
        Returns:
            Dictionary with portfolio metrics
        """
        total_value = self.get_total_value(current_prices)
        total_return = (total_value - self.initial_capital) / self.initial_capital * 100
        
        # Calculate win rate
        if self.trades:
            winning_trades = sum(1 for trade in self.trades if trade.pnl > 0)
            win_rate = winning_trades / len(self.trades) * 100
            
            # Calculate Sharpe ratio (simplified)
            if len(self.equity_curve) > 1:
                returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
                sharpe = np.mean(returns) / (np.std(returns) + 1e-6) * np.sqrt(252)
            else:
                sharpe = 0
        else:
            win_rate = 0
            sharpe = 0
            
        return {
            'total_value': total_value,
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'open_positions': len(self.positions),
            'total_trades': len(self.trades)
        }
    
    def get_performance_summary(self) -> pd.DataFrame:
        """
        Get performance summary DataFrame
        
        Returns:
            DataFrame with trade history
        """
        if not self.trades:
            return pd.DataFrame()
            
        trades_df = pd.DataFrame([{
            'Ticker': t.ticker,
            'Entry_Time': t.entry_time,
            'Exit_Time': t.exit_time,
            'Entry_Price': t.entry_price,
            'Exit_Price': t.exit_price,
            'P&L': t.pnl,
            'P&L_%': t.pnl_percent,
            'Regime': t.regime_at_entry
        } for t in self.trades])
        
        return trades_df

# Example usage
if __name__ == "__main__":
    # Initialize portfolio
    portfolio = PortfolioManager(initial_capital=100000)
    
    # Simulate opening a position
    portfolio.open_position('AAPL', 150.0, 2.0, regime_multiplier=1.5, regime='TRENDING')
    
    # Simulate price movement
    portfolio.update_positions('AAPL', 155.0, 2.1)
    
    # Check stop loss
    portfolio.check_stop_loss_take_profit('AAPL', 155.0)
    
    # Get metrics
    metrics = portfolio.get_portfolio_metrics({'AAPL': 155.0})
    print(f"Portfolio Metrics: {metrics}")