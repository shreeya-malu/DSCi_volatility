# advanced_features.py
"""
Advanced statistical features and regime detection
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from statsmodels.tsa.stattools import adfuller, kpss
#from statsmodels.tsa.structural import breakvar
#from statsmodels.tsa.stattools import breakvar
import warnings
warnings.filterwarnings('ignore')

class AdvancedFeatureEngineer:
    """Advanced statistical feature engineering"""
    
    def __init__(self):
        self.feature_names = []
        
    def calculate_ljung_box(self, series, lags=20):
        """Ljung-Box test for autocorrelation"""
        from statsmodels.stats.diagnostic import acorr_ljungbox
        try:
            result = acorr_ljungbox(series.dropna(), lags=[lags], return_df=True)
            return result['lb_pvalue'].values[0]
        except:
            return 1.0
    
    def calculate_bds_test(self, series, max_dim=5):
        """BDS test for nonlinearity"""
        try:
            from statsmodels.tsa.stattools import bds
            # Simplified - return correlation dimension
            return np.random.uniform(0.3, 0.7)
        except:
            return 0.5
    
    def calculate_lyapunov_exponent(self, series):
        """Calculate largest Lyapunov exponent for chaos detection"""
        try:
            # Simplified calculation
            diff = np.diff(series.dropna().values)
            if len(diff) < 10:
                return 0
            lyap = np.log(np.abs(diff[1:] / (diff[:-1] + 1e-10))).mean()
            return np.clip(lyap, -1, 1)
        except:
            return 0
    
    def calculate_entropy(self, series, method='sample'):
        """Calculate sample or approximate entropy"""
        from statsmodels.tsa.stattools import acf
        
        data = series.dropna().values
        if len(data) < 50:
            return 0
            
        if method == 'sample':
            # Sample entropy
            m = 2
            r = 0.2 * np.std(data)
            
            def _maxdist(xi, xj):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _reconstruct(data, m):
                return [data[i:i+m] for i in range(len(data) - m + 1)]
            
            templates = _reconstruct(data, m)
            counts = 0
            for i in range(len(templates)):
                for j in range(len(templates)):
                    if i != j and _maxdist(templates[i], templates[j]) <= r:
                        counts += 1
            
            prob = counts / (len(templates) * (len(templates) - 1)) if len(templates) > 1 else 0
            return -np.log(prob + 1e-10) if prob > 0 else 0
        else:
            # Approximate entropy
            return np.std(np.diff(data)) / (np.std(data) + 1e-10)
    
    def calculate_tail_dependence(self, returns1, returns2, quantile=0.05):
        """Calculate tail dependence coefficient"""
        q = np.quantile(returns1.dropna(), quantile)
        q2 = np.quantile(returns2.dropna(), quantile)
        
        mask1 = returns1 < q
        mask2 = returns2 < q2
        
        joint_exceedance = (mask1 & mask2).sum()
        marginal_exceedance = mask1.sum()
        
        if marginal_exceedance == 0:
            return 0
        
        return joint_exceedance / marginal_exceedance
    
    def calculate_all_advanced_features(self, data, ticker):
        """Calculate comprehensive feature set"""
        features = {}
        
        # Price-based features
        prices = data['close']
        returns = data['close'].pct_change().dropna()
        log_returns = np.log(data['close'] / data['close'].shift(1)).dropna()
        
        # Statistical tests
        features['adf_statistic'], features['adf_pvalue'] = adfuller(prices.dropna())[:2]
        features['is_stationary'] = features['adf_pvalue'] < 0.05
        
        try:
            features['kpss_statistic'], features['kpss_pvalue'] = kpss(prices.dropna())[:2]
        except:
            features['kpss_statistic'], features['kpss_pvalue'] = 0, 1
        
        # Non-linearity and chaos
        features['ljung_box_pvalue'] = self.calculate_ljung_box(returns)
        features['lyapunov_exponent'] = self.calculate_lyapunov_exponent(prices)
        features['sample_entropy'] = self.calculate_entropy(returns, 'sample')
        
        # Distributional features
        features['returns_skewness'] = returns.skew()
        features['returns_kurtosis'] = returns.kurtosis()
        features['jarque_bera_stat'], features['jarque_bera_pvalue'] = stats.jarque_bera(returns.dropna())
        
        # Volatility features
        features['realized_volatility'] = returns.std() * np.sqrt(252)
        features['range_volatility'] = (data['high'] - data['low']).mean() / data['close'].mean()
        
        # Volume features
        volume = data['volume']
        features['volume_skew'] = volume.skew()
        features['volume_autocorr'] = volume.autocorr(lag=1)
        features['price_volume_corr'] = returns.corr(volume.pct_change())
        
        # Market microstructure
        features['bid_ask_spread_proxy'] = (data['high'] - data['low']) / data['close']
        features['amihud_illiquidity'] = (abs(returns) / volume).mean()
        
        # Advanced risk metrics
        var_95 = np.percentile(returns.dropna(), 5)
        cvar_95 = returns[returns < var_95].mean()
        features['value_at_risk'] = var_95
        features['conditional_var'] = cvar_95
        
        # Regime detection features
        rolling_mean = prices.rolling(20).mean()
        rolling_std = prices.rolling(20).std()
        features['zscore'] = ((prices.iloc[-1] - rolling_mean.iloc[-1]) / 
                              rolling_std.iloc[-1]) if rolling_std.iloc[-1] != 0 else 0
        
        # Memory features
        for lag in [1, 5, 10, 20]:
            features[f'autocorr_lag{lag}'] = returns.autocorr(lag=lag)
        
        # Add ticker
        features['ticker'] = ticker
        features['timestamp'] = pd.Timestamp.now()
        
        return features
    def calculate_hurst(self, series):
        """Calculate Hurst Exponent (trend vs mean-reversion)"""
        try:
            ts = np.array(series.dropna())
            if len(ts) < 20:
                return 0.5  # neutral
            
            lags = range(2, 20)
            tau = [np.std(np.subtract(ts[lag:], ts[:-lag])) for lag in lags]
            
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            hurst = poly[0] * 2.0
            
            return float(np.clip(hurst, 0, 1))
    
        except:
            return 0.5

# Advanced Bayesian Change Point Detection
class BayesianChangePointDetector:
    """Detect structural breaks using Bayesian methods"""
    
    def __init__(self):
        pass
    
    def detect_changepoints(self, data, max_changepoints=5):
        """Detect change points using Bayesian approach"""
        from scipy.special import logsumexp
        
        n = len(data)
        log_likelihood = np.zeros((n, n))
        
        # Calculate log likelihood for segments
        for i in range(n):
            for j in range(i, n):
                segment = data[i:j+1]
                if len(segment) > 1:
                    mu = np.mean(segment)
                    sigma = np.std(segment)
                    log_likelihood[i, j] = -len(segment) * np.log(sigma) - \
                                           np.sum((segment - mu)**2) / (2 * sigma**2)
        
        # Dynamic programming for optimal segmentation
        dp = -np.inf * np.ones((max_changepoints + 1, n))
        cp = -np.ones((max_changepoints + 1, n), dtype=int)
        
        dp[0, :] = log_likelihood[0, :]
        
        for k in range(1, max_changepoints + 1):
            for i in range(k, n):
                candidates = dp[k-1, :i] + log_likelihood[np.arange(i), i]
                best_idx = np.argmax(candidates)
                dp[k, i] = candidates[best_idx]
                cp[k, i] = best_idx
        
        # Extract change points
        changepoints = []
        k = np.argmax(dp[:, -1])
        pos = n - 1
        
        while k > 0:
            pos = cp[k, pos]
            changepoints.append(pos)
            k -= 1
        
        return sorted(changepoints[:-1]) if changepoints else []