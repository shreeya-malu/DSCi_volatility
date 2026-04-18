# ml_models.py
"""
Machine Learning models for regime prediction with XAI
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import shap
import lime
import lime.lime_tabular
import warnings
warnings.filterwarnings('ignore')

class MLRegimePredictor:
    """ML models for market regime prediction with explainability"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = None
        
    def prepare_features(self, features_df):
        """Prepare features for ML models"""
        # Select numeric features
        exclude_cols = ['ticker', 'timestamp', 'date']
        feature_cols = [col for col in features_df.columns 
                       if col not in exclude_cols and features_df[col].dtype in ['float64', 'int64']]
        
        X = features_df[feature_cols].fillna(0)
        y = features_df['regime_encoded'] if 'regime_encoded' in features_df.columns else None
        
        self.feature_names = feature_cols
        return X, y, feature_cols
    
    def train_random_forest(self, X_train, y_train):
        """Train Random Forest classifier"""
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        rf.fit(X_train, y_train)
        self.models['random_forest'] = rf
        return rf
    
    def train_xgboost(self, X_train, y_train):
        """Train XGBoost classifier"""
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
        xgb_model.fit(X_train, y_train)
        self.models['xgboost'] = xgb_model
        return xgb_model
    
    def train_ensemble(self, X_train, y_train):
        """Train ensemble of models"""
        self.train_random_forest(X_train, y_train)
        self.train_xgboost(X_train, y_train)
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        gb.fit(X_train, y_train)
        self.models['gradient_boosting'] = gb
        
        return self.models
    
    def predict_ensemble(self, X):
        """Ensemble prediction with soft voting"""
        predictions = []
        probabilities = []
        
        for name, model in self.models.items():
            pred = model.predict(X)
            proba = model.predict_proba(X)
            predictions.append(pred)
            probabilities.append(proba)
        
        # Average probabilities
        avg_proba = np.mean(probabilities, axis=0)
        final_pred = np.argmax(avg_proba, axis=1)
        
        return final_pred, avg_proba
    
    def explain_with_shap(self, model, X_sample, model_name='random_forest'):
        """Explain predictions using SHAP values"""
        # Create SHAP explainer
        if model_name == 'xgboost':
            self.shap_explainer = shap.TreeExplainer(model)
        else:
            self.shap_explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        shap_values = self.shap_explainer.shap_values(X_sample)
        
        # Create explanation summary
        explanation = {
            'shap_values': shap_values,
            'base_value': self.shap_explainer.expected_value,
            'feature_names': self.feature_names
        }
        
        return explanation
    
    def explain_with_lime(self, model, X_train, X_sample, sample_idx=0):
        """Explain predictions using LIME"""
        # Create LIME explainer
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train,
            feature_names=self.feature_names,
            class_names=['Normal', 'Trending', 'MeanReverting', 'Volatile'],
            mode='classification',
            discretize_continuous=True
        )
        
        # Explain prediction
        exp = self.lime_explainer.explain_instance(
            X_sample[sample_idx],
            model.predict_proba,
            num_features=10
        )
        
        return exp
    
    def get_feature_importance(self, model, model_name='random_forest'):
        """Get feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_imp = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            return feature_imp
        return None
    
    def cross_validate_timeseries(self, X, y, n_splits=5):
        """Time series cross-validation"""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train model
            model = xgb.XGBClassifier(random_state=42, use_label_encoder=False)
            model.fit(X_train, y_train)
            
            # Evaluate
            score = model.score(X_val, y_val)
            cv_scores.append(score)
        
        return {
            'mean_score': np.mean(cv_scores),
            'std_score': np.std(cv_scores),
            'scores': cv_scores
        }

# Reinforcement Learning Portfolio Optimizer
class RLPortfolioOptimizer:
    """Reinforcement learning for dynamic portfolio allocation"""
    
    def __init__(self, n_assets=5, initial_capital=100000):
        self.n_assets = n_assets
        self.capital = initial_capital
        self.state_dim = n_assets * 10  # Features per asset
        self.action_dim = n_assets  # Allocation weights
        
    def get_state(self, market_data):
        """Extract state from market data"""
        state = []
        for ticker, data in market_data.items():
            # Extract features for each asset
            features = [
                data['close'].iloc[-1] / data['close'].mean(),  # Normalized price
                data['returns'].iloc[-1],  # Latest return
                data['volatility'].iloc[-1],  # Current volatility
                data['volume_zscore'].iloc[-1],  # Volume anomaly
                data['hurst'].iloc[-1] if 'hurst' in data else 0.5,  # Trend strength
                data['returns'].rolling(5).mean().iloc[-1],  # Short-term momentum
                data['returns'].rolling(20).mean().iloc[-1],  # Long-term momentum
                data['high'].iloc[-1] / data['low'].iloc[-1],  # Daily range
                data['volume'].iloc[-1] / data['volume'].mean(),  # Relative volume
                data['close'].iloc[-1] / data['close'].iloc[-5] - 1  # 5-day return
            ]
            state.extend(features)
        
        return np.array(state)
    
    def calculate_reward(self, portfolio_return, volatility, sharpe_ratio, drawdown):
        """Calculate reward function for RL agent"""
        # Reward components
        return_reward = portfolio_return * 100
        risk_penalty = -volatility * 10
        sharpe_reward = sharpe_ratio * 20
        drawdown_penalty = -drawdown * 50
        
        # Combined reward
        reward = return_reward + risk_penalty + sharpe_reward + drawdown_penalty
        
        return reward
    
    def optimize_allocation(self, market_data, risk_tolerance=0.5):
        """Optimize portfolio allocation using RL principles"""
        n_assets = len(market_data)
        
        # Calculate key metrics
        returns = []
        volatilities = []
        correlations = []
        
        for ticker, data in market_data.items():
            ret = data['returns'].iloc[-20:].mean()
            vol = data['volatility'].iloc[-1]
            returns.append(ret)
            volatilities.append(vol)
        
        # Calculate correlation matrix
        returns_df = pd.DataFrame({
            ticker: data['returns'].iloc[-50:] 
            for ticker, data in market_data.items()
        })
        corr_matrix = returns_df.corr()
        
        # Mean-variance optimization with risk adjustment
        inv_vol = 1 / np.array(volatilities)
        risk_adjusted_returns = np.array(returns) * (1 - risk_tolerance) + inv_vol * risk_tolerance
        
        # Normalize to get weights
        weights = risk_adjusted_returns / risk_adjusted_returns.sum()
        
        # Apply constraints
        weights = np.clip(weights, 0, 0.4)  # Max 40% per asset
        weights = weights / weights.sum()  # Renormalize
        
        # Create allocation dictionary
        allocation = {
            ticker: weight 
            for ticker, weight in zip(market_data.keys(), weights)
        }
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(returns * weights)
        portfolio_volatility = np.sqrt(
            np.dot(weights.T, np.dot(corr_matrix.values, weights))
        )
        sharpe = portfolio_return / (portfolio_volatility + 1e-6)
        
        return {
            'allocation': allocation,
            'portfolio_return': portfolio_return,
            'portfolio_volatility': portfolio_volatility,
            'sharpe_ratio': sharpe,
            'weights': weights
        }