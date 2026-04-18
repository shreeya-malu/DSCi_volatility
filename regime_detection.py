# regime_detection.py
"""
Market regime detection using statistical rules
"""

import pandas as pd
import numpy as np
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Market regime types"""
    TRENDING = "TRENDING"
    MEAN_REVERTING = "MEAN-REVERTING"
    RANDOM = "RANDOM"
    HIGH_VOLATILITY = "HIGH-VOLATILITY"
    EXTREME_VOLATILITY = "EXTREME-VOLATILITY"
    VOLUME_SPIKE = "VOLUME-SPIKE"
    ANOMALY = "ANOMALY"
    NORMAL = "NORMAL"

@dataclass
class RegimeResult:
    """Container for regime detection results"""
    regime: MarketRegime
    confidence: float
    hurst_exponent: float
    volatility: float
    volume_zscore: float
    is_stationary: bool
    alerts: List[str]
    
class RegimeDetector:
    """Detects market regimes using statistical rules"""
    
    def __init__(self, 
                 hurst_trending: float = 0.6,
                 hurst_mean_reverting: float = 0.4,
                 volume_z_threshold: float = 2.0,
                 extreme_volume_z: float = 3.0,
                 volatility_high: float = 0.02,
                 volatility_extreme: float = 0.05):
        """
        Initialize regime detector
        
        Args:
            hurst_trending: Hurst threshold for trending regime
            hurst_mean_reverting: Hurst threshold for mean-reverting
            volume_z_threshold: Z-score threshold for volume spike
            extreme_volume_z: Z-score threshold for extreme volume
            volatility_high: High volatility threshold
            volatility_extreme: Extreme volatility threshold
        """
        self.hurst_trending = hurst_trending
        self.hurst_mean_reverting = hurst_mean_reverting
        self.volume_z_threshold = volume_z_threshold
        self.extreme_volume_z = extreme_volume_z
        self.volatility_high = volatility_high
        self.volatility_extreme = volatility_extreme
        
    def detect_regime(self, 
                     hurst_exponent: float,
                     volatility: float,
                     volume_zscore: float,
                     is_stationary: bool,
                     additional_metrics: Optional[Dict] = None) -> RegimeResult:
        """
        Detect current market regime based on statistical metrics
        
        Args:
            hurst_exponent: Calculated Hurst exponent
            volatility: Current volatility (standard deviation of returns)
            volume_zscore: Volume Z-score for anomaly detection
            is_stationary: Whether the series is stationary (ADF test)
            additional_metrics: Additional metrics for decision making
            
        Returns:
            RegimeResult object with regime classification
        """
        alerts = []
        regime = MarketRegime.NORMAL
        confidence = 0.5
        
        # Priority 1: Check for anomalies (extreme conditions)
        if volume_zscore > self.extreme_volume_z and volatility > self.volatility_high:
            regime = MarketRegime.ANOMALY
            confidence = 0.95
            alerts.append(f"CRITICAL: Extreme volume spike (Z={volume_zscore:.2f}) with high volatility")
            
        # Priority 2: Check for volume spikes
        elif volume_zscore > self.volume_z_threshold:
            regime = MarketRegime.VOLUME_SPIKE
            confidence = 0.8
            alerts.append(f"Volume spike detected (Z={volume_zscore:.2f})")
            
        # Priority 3: Check volatility conditions
        elif volatility > self.volatility_extreme:
            regime = MarketRegime.EXTREME_VOLATILITY
            confidence = 0.9
            alerts.append(f"Extreme volatility: {volatility:.4f}")
            
        elif volatility > self.volatility_high:
            regime = MarketRegime.HIGH_VOLATILITY
            confidence = 0.7
            alerts.append(f"High volatility: {volatility:.4f}")
            
        # Priority 4: Check trend conditions (Hurst exponent)
        elif hurst_exponent > self.hurst_trending:
            regime = MarketRegime.TRENDING
            confidence = min(0.9, (hurst_exponent - self.hurst_trending) / 0.4 + 0.6)
            alerts.append(f"Trending market detected (H={hurst_exponent:.3f})")
            
        elif hurst_exponent < self.hurst_mean_reverting:
            regime = MarketRegime.MEAN_REVERTING
            confidence = min(0.9, (self.hurst_mean_reverting - hurst_exponent) / 0.4 + 0.6)
            alerts.append(f"Mean-reverting market (H={hurst_exponent:.3f})")
            
        elif abs(hurst_exponent - 0.5) < 0.1:
            regime = MarketRegime.RANDOM
            confidence = 0.6
            alerts.append(f"Random walk market (H={hurst_exponent:.3f})")
            
        # Additional logic based on stationarity
        if is_stationary and regime == MarketRegime.TRENDING:
            # Contradiction: Trending but stationary - might be false signal
            confidence *= 0.8
            alerts.append("Warning: Trending but stationary - low confidence")
            
        # Add timestamp
        result = RegimeResult(
            regime=regime,
            confidence=confidence,
            hurst_exponent=hurst_exponent,
            volatility=volatility,
            volume_zscore=volume_zscore,
            is_stationary=is_stationary,
            alerts=alerts
        )
        
        logger.info(f"Regime detected: {regime.value} (confidence: {confidence:.2f})")
        return result
    
    def get_regime_action(self, regime: MarketRegime) -> Dict[str, any]:
        """
        Get recommended actions based on regime
        
        Args:
            regime: Detected market regime
            
        Returns:
            Dictionary with recommended actions
        """
        actions = {
            'position_size_multiplier': 1.0,
            'risk_level': 'MODERATE',
            'strategy': 'STANDARD',
            'color': '#ffffff'
        }
        
        if regime == MarketRegime.TRENDING:
            actions.update({
                'position_size_multiplier': 1.5,
                'risk_level': 'AGGRESSIVE',
                'strategy': 'TREND_FOLLOWING',
                'color': '#00ff00'
            })
        elif regime == MarketRegime.MEAN_REVERTING:
            actions.update({
                'position_size_multiplier': 0.7,
                'risk_level': 'MODERATE',
                'strategy': 'MEAN_REVERSION',
                'color': '#ffff00'
            })
        elif regime == MarketRegime.RANDOM:
            actions.update({
                'position_size_multiplier': 0.3,
                'risk_level': 'CONSERVATIVE',
                'strategy': 'WAIT_AND_SEE',
                'color': '#ff8800'
            })
        elif regime == MarketRegime.HIGH_VOLATILITY:
            actions.update({
                'position_size_multiplier': 0.5,
                'risk_level': 'CONSERVATIVE',
                'strategy': 'REDUCED_RISK',
                'color': '#ff6600'
            })
        elif regime == MarketRegime.EXTREME_VOLATILITY:
            actions.update({
                'position_size_multiplier': 0.2,
                'risk_level': 'DEFENSIVE',
                'strategy': 'HEDGE',
                'color': '#ff0000'
            })
        elif regime == MarketRegime.VOLUME_SPIKE:
            actions.update({
                'position_size_multiplier': 0.4,
                'risk_level': 'CAUTIOUS',
                'strategy': 'MONITOR_ONLY',
                'color': '#ffaa00'
            })
        elif regime == MarketRegime.ANOMALY:
            actions.update({
                'position_size_multiplier': 0.0,
                'risk_level': 'EXIT',
                'strategy': 'FLAT',
                'color': '#ff0000'
            })
            
        return actions
    
    def generate_regime_summary(self, results: Dict[str, RegimeResult]) -> pd.DataFrame:
        """
        Generate summary DataFrame of regimes for multiple tickers
        
        Args:
            results: Dictionary mapping ticker to RegimeResult
            
        Returns:
            DataFrame with regime summary
        """
        summary_data = []
        
        for ticker, result in results.items():
            actions = self.get_regime_action(result.regime)
            
            summary_data.append({
                'Ticker': ticker,
                'Regime': result.regime.value,
                'Confidence': f"{result.confidence:.2%}",
                'Hurst': f"{result.hurst_exponent:.3f}",
                'Volatility': f"{result.volatility:.4f}",
                'Volume_Z': f"{result.volume_zscore:.2f}",
                'Stationary': result.is_stationary,
                'Position_Multiplier': actions['position_size_multiplier'],
                'Risk_Level': actions['risk_level'],
                'Strategy': actions['strategy']
            })
            
        return pd.DataFrame(summary_data)

# Example usage
if __name__ == "__main__":
    # Test different regimes
    detector = RegimeDetector()
    
    # Test cases
    test_cases = [
        (0.75, 0.01, 1.0, False),   # Trending
        (0.25, 0.01, 1.0, True),    # Mean-reverting
        (0.52, 0.01, 1.0, False),   # Random
        (0.65, 0.03, 1.0, False),   # High volatility
        (0.60, 0.06, 1.0, False),   # Extreme volatility
        (0.55, 0.01, 2.5, False),   # Volume spike
        (0.55, 0.04, 3.5, False),   # Anomaly
    ]
    
    for hurst, vol, zscore, stationary in test_cases:
        result = detector.detect_regime(hurst, vol, zscore, stationary)
        actions = detector.get_regime_action(result.regime)
        
        print(f"\nH={hurst:.2f}, Vol={vol:.3f}, Z={zscore:.1f}")
        print(f"Regime: {result.regime.value}")
        print(f"Action: {actions['strategy']}")
        print(f"Alerts: {result.alerts}")