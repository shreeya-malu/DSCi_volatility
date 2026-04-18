# advanced_portfolio.py
"""
Advanced portfolio management with GARCH and Copulas
"""

import numpy as np
import pandas as pd
from arch import arch_model
from scipy import stats
from copulas.multivariate import GaussianMultivariate
import warnings
warnings.filterwarnings('ignore')

class AdvancedPortfolioManager:
    """Portfolio with advanced risk models"""
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.risk_models = {}
        
    def fit_garch_model(self, returns, ticker):
        """Fit GARCH(1,1) model for volatility forecasting"""
        try:
            # Fit GARCH model
            model = arch_model(returns * 100, vol='Garch', p=1, q=1)
            result = model.fit(update_freq=5, disp='off')
            
            # Store model
            self.risk_models[ticker] = {
                'model': result,
                'forecast_volatility': result.forecast(horizon=5).variance.iloc[-1].values / 100
            }
            
            return result
        except Exception as e:
            print(f"GARCH fitting failed for {ticker}: {e}")
            return None
    
    def calculate_copula_correlation(self, returns_dict):
        """Calculate copula-based correlation"""
        try:
            # Create DataFrame
            returns_df = pd.DataFrame(returns_dict)
            
            # Fit Gaussian copula
            copula = GaussianMultivariate()
            copula.fit(returns_df)
            
            # Get correlation matrix
            corr_matrix = copula.get_parameters()['correlation']
            
            return corr_matrix
        except Exception as e:
            print(f"Copula calculation failed: {e}")
            return None
    
    def calculate_cvar(self, returns, confidence_level=0.95):
        """Calculate Conditional Value at Risk (CVaR)"""
        var = np.percentile(returns, (1 - confidence_level) * 100)
        cvar = returns[returns <= var].mean()
        return cvar
    
    def calculate_expected_shortfall(self, returns, alpha=0.05):
        """Calculate Expected Shortfall"""
        sorted_returns = np.sort(returns)
        index = int(alpha * len(sorted_returns))
        es = np.mean(sorted_returns[:index])
        return es
    
    def optimize_with_constraints(self, returns_dict, target_return=None):
        """Optimize portfolio with constraints using scipy"""
        from scipy.optimize import minimize
        
        returns_df = pd.DataFrame(returns_dict)
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()
        n_assets = len(returns_df.columns)
        
        # Objective: minimize volatility
        def objective(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Constraints
        constraints = []
        if target_return:
            constraints.append({
                'type': 'eq',
                'fun': lambda w: np.sum(mean_returns * w) - target_return
            })
        
        constraints.append({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        
        # Bounds
        bounds = tuple((0, 0.3) for _ in range(n_assets))
        
        # Initial guess
        init_weights = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(
            objective,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            return result.x
        else:
            return init_weights
    
    def calculate_black_litterman(self, market_weights, views, confidence):
        """Black-Litterman model for views-based allocation"""
        # Simplified Black-Litterman
        tau = 0.05  # Uncertainty parameter
        delta = 2.5  # Risk aversion coefficient
        
        # Equilibrium returns
        pi = delta * market_weights
        
        # Combine with views
        if views:
            adjusted_returns = pi * (1 - confidence) + np.array(views) * confidence
        else:
            adjusted_returns = pi
        
        return adjusted_returns
    
    def generate_portfolio_insights(self, portfolio_data):
        """Generate comprehensive portfolio insights"""
        insights = {
            'diversification_ratio': None,
            'concentration_score': None,
            'tail_risk': None,
            'stress_test_results': {}
        }
        
        # Diversification ratio
        if len(portfolio_data) > 1:
            weights = np.array([d['weight'] for d in portfolio_data.values()])
            vols = np.array([d['volatility'] for d in portfolio_data.values()])
            portfolio_vol = np.sqrt(np.sum((weights * vols)**2))
            weighted_vol = np.sum(weights * vols)
            insights['diversification_ratio'] = weighted_vol / (portfolio_vol + 1e-6)
        
        # Concentration (Herfindahl index)
        insights['concentration_score'] = np.sum(weights**2) if weights is not None else 1
        
        # Tail risk (Average of CVaRs)
        tail_risks = [d.get('cvar', 0.05) for d in portfolio_data.values()]
        insights['tail_risk'] = np.mean(tail_risks)
        
        # Stress tests
        scenarios = {
            'Market_Crash_-20%': -0.20,
            'Moderate_Downturn_-10%': -0.10,
            'Volatility_Spike_+50%': 'vol_up',
            'Liquidity_Crisis': 'spread_widen'
        }
        
        for scenario, shock in scenarios.items():
            if isinstance(shock, float):
                impact = np.sum(weights * shock)
            else:
                impact = -0.15  # Default impact for non-linear shocks
            insights['stress_test_results'][scenario] = impact
        
        return insights