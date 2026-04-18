# alert_system.py
"""
Real-time alert system for market anomalies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity:
    """Alert severity levels"""
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    INFO = "ℹ️ INFO"

@dataclass
class Alert:
    """Represents a market alert"""
    timestamp: datetime
    ticker: str
    severity: str
    message: str
    regime: str
    metrics: Dict[str, float]
    
class AlertSystem:
    """Manages real-time alerts with cooldown"""
    
    def __init__(self, cooldown_minutes: int = 5, log_file: str = 'alerts.csv'):
        """
        Initialize alert system
        
        Args:
            cooldown_minutes: Minutes to wait before sending same alert type
            log_file: File to log alerts
        """
        self.cooldown_minutes = cooldown_minutes
        self.log_file = log_file
        self.last_alerts: Dict[str, datetime] = {}
        self.alerts_history: List[Alert] = []
        
        # Initialize log file
        self._init_log_file()
        
    def _init_log_file(self):
        """Initialize alert log file with headers"""
        try:
            import os
            if not os.path.exists(self.log_file):
                df = pd.DataFrame(columns=['timestamp', 'ticker', 'severity', 'message', 'regime'])
                df.to_csv(self.log_file, index=False)
                logger.info(f"Initialized alert log at {self.log_file}")
        except Exception as e:
            logger.error(f"Error initializing log file: {e}")
    
    def _is_on_cooldown(self, alert_key: str) -> bool:
        """
        Check if alert type is on cooldown
        
        Args:
            alert_key: Unique key for alert type
            
        Returns:
            True if on cooldown, False otherwise
        """
        if alert_key not in self.last_alerts:
            return False
            
        time_since_last = datetime.now() - self.last_alerts[alert_key]
        return time_since_last < timedelta(minutes=self.cooldown_minutes)
    
    def _log_alert(self, alert: Alert):
        """
        Log alert to CSV file
        
        Args:
            alert: Alert object
        """
        try:
            alert_data = {
                'timestamp': alert.timestamp,
                'ticker': alert.ticker,
                'severity': alert.severity,
                'message': alert.message,
                'regime': alert.regime
            }
            
            # Append to CSV
            df = pd.DataFrame([alert_data])
            df.to_csv(self.log_file, mode='a', header=False, index=False)
            
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    def check_alerts(self,
                    ticker: str,
                    regime_result,
                    volume_zscore: float,
                    volatility: float,
                    hurst_exponent: float,
                    is_stationary: bool) -> List[Alert]:
        """
        Check for alert conditions
        
        Args:
            ticker: Stock ticker
            regime_result: Regime detection result
            volume_zscore: Volume Z-score
            volatility: Current volatility
            hurst_exponent: Hurst exponent
            is_stationary: Stationarity status
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # 1. CRITICAL ANOMALY Alert
        if volume_zscore > 3.0 and volatility > 0.04:
            alert_key = f"{ticker}_critical_anomaly"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.CRITICAL,
                    message=f"CRITICAL ANOMALY: Volume Z={volume_zscore:.2f}, Volatility={volatility:.4f}",
                    regime=regime_result.regime.value,
                    metrics={'volume_zscore': volume_zscore, 'volatility': volatility}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] = datetime.now()
                
        # 2. EXTREME VOLATILITY Alert
        elif volatility > 0.05:
            alert_key = f"{ticker}_extreme_volatility"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.HIGH,
                    message=f"EXTREME VOLATILITY: {volatility:.4f} (>{0.05:.2f})",
                    regime=regime_result.regime.value,
                    metrics={'volatility': volatility}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] = datetime.now()
                
        # 3. HIGH VOLATILITY Alert
        elif volatility > 0.03:
            alert_key = f"{ticker}_high_volatility"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.MEDIUM,
                    message=f"HIGH VOLATILITY: {volatility:.4f}",
                    regime=regime_result.regime.value,
                    metrics={'volatility': volatility}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] = datetime.now()
                
        # 4. VOLUME SPIKE Alert
        elif volume_zscore > 2.0:
            alert_key = f"{ticker}_volume_spike"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.MEDIUM,
                    message=f"VOLUME SPIKE: Z={volume_zscore:.2f}",
                    regime=regime_result.regime.value,
                    metrics={'volume_zscore': volume_zscore}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] =datetime.now()
                
        # 5. TRENDING Alert
        elif hurst_exponent > 0.65:
            alert_key = f"{ticker}_trending"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.LOW,
                    message=f"TRENDING MARKET: H={hurst_exponent:.3f}",
                    regime=regime_result.regime.value,
                    metrics={'hurst_exponent': hurst_exponent}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] = datetime.now()
                
        # 6. REGIME CHANGE Alert (based on stationarity)
        if is_stationary != regime_result.is_stationary:
            alert_key = f"{ticker}_regime_change"
            if not self._is_on_cooldown(alert_key):
                alert = Alert(
                    timestamp=datetime.now(),
                    ticker=ticker,
                    severity=AlertSeverity.INFO,
                    message=f"REGIME CHANGE: Stationarity changed to {is_stationary}",
                    regime=regime_result.regime.value,
                    metrics={'is_stationary': is_stationary}
                )
                triggered_alerts.append(alert)
                self.last_alerts[alert_key] = datetime.now()
        
        # Log and store alerts
        for alert in triggered_alerts:
            self.alerts_history.append(alert)
            self._log_alert(alert)
            
            # Print to console with color
            print(f"\n{alert.severity} ALERT [{alert.ticker}] {alert.timestamp.strftime('%H:%M:%S')}")
            print(f"  {alert.message}")
            
        return triggered_alerts
    
    def get_recent_alerts(self, minutes: int = 60) -> List[Alert]:
        """
        Get alerts from the last N minutes
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of recent alerts
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [alert for alert in self.alerts_history if alert.timestamp > cutoff]
    
    def get_alerts_summary(self) -> pd.DataFrame:
        """
        Get summary DataFrame of all alerts
        
        Returns:
            DataFrame with alert history
        """
        if not self.alerts_history:
            return pd.DataFrame()
            
        df = pd.DataFrame([{
            'Timestamp': alert.timestamp,
            'Ticker': alert.ticker,
            'Severity': alert.severity,
            'Message': alert.message,
            'Regime': alert.regime
        } for alert in self.alerts_history])
        
        return df.sort_values('Timestamp', ascending=False)
    
    def clear_cooldowns(self):
        """Clear all alert cooldowns (useful for testing)"""
        self.last_alerts.clear()
        logger.info("Cleared all alert cooldowns")

# Example usage
if __name__ == "__main__":
    from regime_detection import RegimeDetector, MarketRegime, RegimeResult
    
    # Create mock regime result
    mock_regime = RegimeResult(
        regime=MarketRegime.TRENDING,
        confidence=0.8,
        hurst_exponent=0.7,
        volatility=0.035,
        volume_zscore=2.5,
        is_stationary=False,
        alerts=[]
    )
    
    # Initialize alert system
    alert_system = AlertSystem(cooldown_minutes=1)
    
    # Check for alerts
    alerts = alert_system.check_alerts(
        ticker='AAPL',
        regime_result=mock_regime,
        volume_zscore=2.5,
        volatility=0.035,
        hurst_exponent=0.7,
        is_stationary=False
    )
    
    # Get summary
    summary = alert_system.get_alerts_summary()
    print("\nAlert Summary:")
    print(summary.head() if not summary.empty else "No alerts yet")