# feature_engineering.py
"""
Feature engineering module with statistical tests (Z-score, ADF, Hurst)
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Calculates statistical features and market indicators"""
    
    def __init__(self, rolling_window: int = 20):
        """
        Initialize feature engineer
        
        Args:
            rolling_window: Window size for rolling statistics
        """
        self.rolling_window = rolling_window
        
    def calculate_zscore(self, data: pd.Series) -> pd.Series:
        """
        Calculate Z-score for anomaly detection
        
        Args:
            data: Input series
            
        Returns:
            Z-score series
        """
        mean = data.rolling(window=self.rolling_window).mean()
        std = data.rolling(window=self.rolling_window).std()
        
        zscore = (data - mean) / std
        return zscore.fillna(0)
    
    def calculate_hurst_exponent(self, data: pd.Series, max_lag: int = 100) -> float:
        """
        Calculate Hurst exponent to determine market regime
        
        Args:
            data: Time series data
            max_lag: Maximum lag for calculation
            
        Returns:
            Hurst exponent (H)
            H > 0.5: Trending
            H = 0.5: Random walk
            H < 0.5: Mean-reverting
        """
        try:
            # Calculate returns
            returns = data.dropna().values
            
            if len(returns) < max_lag:
                max_lag = len(returns) // 2
                
            if max_lag < 2:
                return 0.5
                
            # Calculate R/S statistic for different lags
            lags = range(2, max_lag)
            tau = []
            
            for lag in lags:
                # Split into chunks
                chunks = [returns[i:i+lag] for i in range(0, len(returns), lag) if len(returns[i:i+lag]) == lag]
                
                if len(chunks) < 2:
                    continue
                    
                # Calculate R/S for each chunk
                rs_values = []
                for chunk in chunks:
                    # Mean center
                    chunk = chunk - np.mean(chunk)
                    # Cumulative sum
                    cumsum = np.cumsum(chunk)
                    # Range
                    r = np.max(cumsum) - np.min(cumsum)
                    # Standard deviation
                    s = np.std(chunk)
                    if s != 0:
                        rs_values.append(r / s)
                
                if rs_values:
                    tau.append(np.mean(rs_values))
                else:
                    tau.append(0)
            
            # Remove zeros
            tau = np.array(tau)
            lags = np.array(lags[:len(tau)])
            
            # Remove invalid values
            valid = (tau > 0) & np.isfinite(tau)
            tau = tau[valid]
            lags = lags[valid]
            
            if len(tau) < 2:
                return 0.5
                
            # Calculate Hurst exponent via linear regression
            hurst = np.polyfit(np.log(lags), np.log(tau), 1)[0]
            
            # Bound between 0 and 1
            hurst = max(0, min(1, hurst))
            
            return hurst
            
        except Exception as e:
            logger.error(f"Error calculating Hurst exponent: {e}")
            return 0.5
    
    def adf_test(self, data: pd.Series) -> Dict[str, any]:
        """
        Perform Augmented Dickey-Fuller test for stationarity
        
        Args:
            data: Time series data
            
        Returns:
            Dictionary with test results
        """
        try:
            # Remove NaN values
            clean_data = data.dropna()
            
            if len(clean_data) < 10:
                return {'is_stationary': False, 'p_value': 1.0, 'statistic': 0}
                
            # Perform ADF test
            result = adfuller(clean_data, autolag='AIC')
            
            adf_statistic = result[0]
            p_value = result[1]
            is_stationary = p_value < 0.05
            
            return {
                'is_stationary': is_stationary,
                'p_value': p_value,
                'statistic': adf_statistic,
                'critical_values': result[4]
            }
            
        except Exception as e:
            logger.error(f"Error in ADF test: {e}")
            return {'is_stationary': False, 'p_value': 1.0, 'statistic': 0}
    
    def t_test_regime_change(self, recent_data: pd.Series, historical_data: pd.Series) -> Dict[str, any]:
        """
        Perform t-test to detect regime changes
        
        Args:
            recent_data: Recent returns
            historical_data: Historical returns
            
        Returns:
            Dictionary with t-test results
        """
        try:
            # Remove NaN values
            recent_clean = recent_data.dropna()
            historical_clean = historical_data.dropna()
            
            if len(recent_clean) < 2 or len(historical_clean) < 2:
                return {'has_changed': False, 'p_value': 1.0, 't_statistic': 0}
                
            # Perform independent t-test
            t_statistic, p_value = stats.ttest_ind(recent_clean, historical_clean, equal_var=False)
            
            has_changed = p_value < 0.05
            
            return {
                'has_changed': has_changed,
                'p_value': p_value,
                't_statistic': t_statistic
            }
            
        except Exception as e:
            logger.error(f"Error in t-test: {e}")
            return {'has_changed': False, 'p_value': 1.0, 't_statistic': 0}
    
    def calculate_volatility(self, data: pd.Series) -> pd.Series:
        """
        Calculate rolling volatility (standard deviation of returns)
        
        Args:
            data: Price series
            
        Returns:
            Rolling volatility series
        """
        returns = data.pct_change()
        volatility = returns.rolling(window=self.rolling_window).std()
        return volatility.fillna(0)
    
    def calculate_atr(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Average True Range for volatility measurement
        
        Args:
            data: DataFrame with OHLC data
            
        Returns:
            ATR series
        """
        high = data['high']
        low = data['low']
        close = data['close']
        
        true_range = pd.DataFrame({
            'hl': high - low,
            'hc': abs(high - close.shift()),
            'lc': abs(low - close.shift())
        }).max(axis=1)
        
        atr = true_range.rolling(window=self.rolling_window).mean()
        return atr.fillna(0)
    
    def calculate_all_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all statistical features
        
        Args:
            data: Preprocessed DataFrame with OHLCV
            
        Returns:
            DataFrame with all features added
        """
        logger.info("Calculating all features...")
        
        features = data.copy()
        
        # Price-based features
        if 'close' in features.columns:
            # Returns
            features['returns'] = features['close'].pct_change()
            features['log_returns'] = np.log(features['close'] / features['close'].shift(1))
            
            # Rolling statistics
            features['rolling_mean'] = features['close'].rolling(window=self.rolling_window).mean()
            features['rolling_std'] = features['close'].rolling(window=self.rolling_window).std()
            
            # Volatility
            features['volatility'] = self.calculate_volatility(features['close'])
            
        # Volume-based features
        if 'volume' in features.columns:
            features['volume_zscore'] = self.calculate_zscore(features['volume'])
            features['volume_ma'] = features['volume'].rolling(window=self.rolling_window).mean()
            
        # Technical indicators
        if all(col in features.columns for col in ['high', 'low', 'close']):
            features['atr'] = self.calculate_atr(features)
            
        # Fill NaN values
        features = features.fillna(0)
        
        logger.info(f"Created {len(features.columns)} features")
        return features

# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1min')
    np.random.seed(42)
    
    # Generate trending data (Hurst > 0.5)
    trend = np.cumsum(np.random.randn(1000) * 0.1) + np.linspace(0, 5, 1000)
    
    sample_data = pd.DataFrame({
        'close': 100 + trend,
        'high': 100 + trend + 0.5,
        'low': 100 + trend - 0.5,
        'volume': np.random.randint(1000, 10000, 1000)
    }, index=dates)
    
    # Calculate features
    engineer = FeatureEngineer(rolling_window=20)
    features = engineer.calculate_all_features(sample_data)
    
    # Calculate Hurst exponent
    hurst = engineer.calculate_hurst_exponent(sample_data['close'])
    
    # Perform ADF test
    adf_result = engineer.adf_test(sample_data['close'])
    
    # Calculate volume Z-score
    volume_zscore = engineer.calculate_zscore(sample_data['volume'])
    
    print(f"Hurst Exponent: {hurst:.3f}")
    print(f"ADF Test - Stationary: {adf_result['is_stationary']}")
    print(f"ADF Test - P-value: {adf_result['p_value']:.4f}")
    print(f"Latest Volume Z-score: {volume_zscore.iloc[-1]:.2f}")
    print(f"\nFeatures shape: {features.shape}")
    print(f"Features columns: {features.columns.tolist()}")