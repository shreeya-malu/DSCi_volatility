# config.py
"""
Configuration file for Market Regime Intelligence System
"""

# Data Collection Settings
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
DATA_INTERVAL = '1m'  # 1-minute intervals
DATA_PERIOD = '1d'    # 1 day of data for real-time
LOOKBACK_DAYS = 30    # For statistical analysis

# Preprocessing Settings
OUTLIER_SIGMA = 3      # 3-sigma rule for outlier detection
EMA_SPAN = 20          # EMA smoothing span
ROLLING_WINDOW = 20    # Rolling statistics window

# Statistical Test Thresholds
HURST_TRENDING = 0.6
HURST_MEAN_REVERTING = 0.4
VOLUME_Z_THRESHOLD = 2.0
EXTREME_VOLUME_Z = 3.0
VOLATILITY_HIGH = 0.02   # 2% daily volatility
VOLATILITY_EXTREME = 0.05 # 5% daily volatility

# Alert Settings
ALERT_COOLDOWN_MINUTES = 5
ALERT_LOG_FILE = 'alerts.csv'

# Portfolio Settings
MAX_POSITION_SIZE = 10000  # $10,000 max per position
RISK_PER_TRADE = 0.02      # 2% risk per trade
STOP_LOSS_ATR_MULTIPLIER = 2.0

# Dashboard Settings
DASHBOARD_REFRESH_SECONDS = 60
DASHBOARD_THEME = 'dark'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE = 'system.log'