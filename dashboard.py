# # # dashboard.py
# # """
# # Interactive Streamlit dashboard for Market Regime Intelligence System
# # """

# # import streamlit as st
# # import pandas as pd
# # import plotly.graph_objects as go
# # from plotly.subplots import make_subplots
# # import plotly.express as px
# # from datetime import datetime, timedelta
# # import time
# # import logging
# # from typing import List, Dict, Optional, Tuple, Any

# # from config import *
# # from data_collection import DataCollector
# # from preprocessing import DataPreprocessor
# # from feature_engineering import FeatureEngineer
# # from regime_detection import RegimeDetector, MarketRegime
# # from portfolio_manager import PortfolioManager
# # from alert_system import AlertSystem

# # # Configure page
# # st.set_page_config(
# #     page_title="Market Regime Intelligence System",
# #     page_icon="📊",
# #     layout="wide",
# #     initial_sidebar_state="expanded"
# # )

# # # Custom CSS
# # st.markdown("""
# # <style>
# #     .stAlert {
# #         font-family: monospace;
# #     }
# #     .big-font {
# #         font-size:20px !important;
# #         font-weight: bold;
# #     }
# #     .metric-card {
# #         background-color: #1e1e1e;
# #         padding: 15px;
# #         border-radius: 10px;
# #         border-left: 4px solid;
# #     }
# # </style>
# # """, unsafe_allow_html=True)

# # class MarketRegimeDashboard:
# #     """Main dashboard for Market Regime Intelligence System"""
    
# #     def __init__(self):
# #         """Initialize dashboard components"""
# #         self.collector = DataCollector(TICKERS, DATA_INTERVAL, DATA_PERIOD)
# #         self.preprocessor = DataPreprocessor(OUTLIER_SIGMA, EMA_SPAN)
# #         self.engineer = FeatureEngineer(ROLLING_WINDOW)
# #         self.detector = RegimeDetector(
# #             HURST_TRENDING, HURST_MEAN_REVERTING,
# #             VOLUME_Z_THRESHOLD, EXTREME_VOLUME_Z,
# #             VOLATILITY_HIGH, VOLATILITY_EXTREME
# #         )
# #         self.portfolio = PortfolioManager(
# #             initial_capital=100000,
# #             max_position_size=MAX_POSITION_SIZE,
# #             risk_per_trade=RISK_PER_TRADE,
# #             stop_loss_atr_mult=STOP_LOSS_ATR_MULTIPLIER
# #         )
# #         self.alert_system = AlertSystem(ALERT_COOLDOWN_MINUTES, ALERT_LOG_FILE)
        
# #         # Session state for persistence
# #         if 'initialized' not in st.session_state:
# #             st.session_state.initialized = True
# #             st.session_state.last_update = None
# #             st.session_state.cached_data = {}
            
# #     def fetch_and_process_data(self):
# #         """Fetch and process real-time data"""
# #         with st.spinner("Fetching market data..."):
# #             raw_data = self.collector.fetch_all_data()
            
# #         processed_data = {}
# #         features_data = {}
        
# #         for ticker, data in raw_data.items():
# #             if data is not None and not data.empty:
# #                 # Preprocess
# #                 processed = self.preprocessor.preprocess(data)
# #                 processed = self.preprocessor.calculate_returns(processed)
                
# #                 # Calculate features
# #                 features = self.engineer.calculate_all_features(processed)
                
# #                 processed_data[ticker] = processed
# #                 features_data[ticker] = features
                
# #         return processed_data, features_data
    
# #     def analyze_regimes(self, features_data: dict):
# #         """Analyze market regimes for all tickers"""
# #         regime_results = {}
        
# #         for ticker, features in features_data.items():
# #             if len(features) > 0:
# #                 # Get latest values
# #                 latest = features.iloc[-1]
                
# #                 # Calculate Hurst exponent
# #                 hurst = self.engineer.calculate_hurst_exponent(features['close'])
                
# #                 # Get volatility
# #                 volatility = latest.get('volatility', 0.01)
                
# #                 # Get volume Z-score
# #                 volume_z = latest.get('volume_zscore', 0)
                
# #                 # ADF test
# #                 adf_result = self.engineer.adf_test(features['close'])
                
# #                 # Detect regime
# #                 regime = self.detector.detect_regime(
# #                     hurst, volatility, volume_z, adf_result['is_stationary']
# #                 )
                
# #                 regime_results[ticker] = regime
                
# #                 # Check for alerts
# #                 alerts = self.alert_system.check_alerts(
# #                     ticker, regime, volume_z, volatility, hurst, adf_result['is_stationary']
# #                 )
                
# #         return regime_results
    
# #     def render_sidebar(self):
# #         """Render sidebar with controls and metrics"""
# #         st.sidebar.title("🎛️ Controls")
        
# #         # Refresh rate
# #         refresh_rate = st.sidebar.slider(
# #             "Refresh Rate (seconds)",
# #             min_value=10,
# #             max_value=300,
# #             value=DASHBOARD_REFRESH_SECONDS,
# #             step=10
# #         )
        
# #         st.sidebar.markdown("---")
        
# #         # Ticker selection
# #         selected_tickers = st.sidebar.multiselect(
# #             "Select Tickers",
# #             options=TICKERS,
# #             default=TICKERS[:3]
# #         )
        
# #         st.sidebar.markdown("---")
        
# #         # System status
# #         st.sidebar.subheader("📡 System Status")
# #         status_col1, status_col2 = st.sidebar.columns(2)
        
# #         with status_col1:
# #             st.metric("Active Tickers", len(selected_tickers))
            
# #         with status_col2:
# #             st.metric("Alert Cooldown", f"{ALERT_COOLDOWN_MINUTES} min")
            
# #         # Last update time
# #         if st.session_state.last_update:
# #             st.sidebar.info(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")
            
# #         # Auto-refresh checkbox
# #         auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
        
# #         return refresh_rate, selected_tickers, auto_refresh
    
# #     def render_regime_card(self, ticker: str, regime_result):
# #         """Render regime information card"""
# #         actions = self.detector.get_regime_action(regime_result.regime)
        
# #         # Color mapping
# #         colors = {
# #             MarketRegime.TRENDING: "#00ff00",
# #             MarketRegime.MEAN_REVERTING: "#ffff00",
# #             MarketRegime.RANDOM: "#ff8800",
# #             MarketRegime.HIGH_VOLATILITY: "#ff6600",
# #             MarketRegime.EXTREME_VOLATILITY: "#ff0000",
# #             MarketRegime.VOLUME_SPIKE: "#ffaa00",
# #             MarketRegime.ANOMALY: "#ff0000",
# #             MarketRegime.NORMAL: "#00ff88"
# #         }
        
# #         color = colors.get(regime_result.regime, "#ffffff")
        
# #         with st.container():
# #             st.markdown(f"""
# #             <div class="metric-card" style="border-left-color: {color};">
# #                 <h3>{ticker}</h3>
# #                 <p><strong>Regime:</strong> <span style="color: {color};">{regime_result.regime.value}</span></p>
# #                 <p><strong>Confidence:</strong> {regime_result.confidence:.1%}</p>
# #                 <p><strong>Strategy:</strong> {actions['strategy']}</p>
# #                 <p><strong>Risk Level:</strong> {actions['risk_level']}</p>
# #                 <p><strong>Position Size:</strong> {actions['position_size_multiplier']:.0%}</p>
# #             </div>
# #             """, unsafe_allow_html=True)
            
# #             # Metrics
# #             col1, col2, col3 = st.columns(3)
# #             with col1:
# #                 st.metric("Hurst", f"{regime_result.hurst_exponent:.3f}")
# #             with col2:
# #                 st.metric("Volatility", f"{regime_result.volatility:.3f}")
# #             with col3:
# #                 st.metric("Volume Z", f"{regime_result.volume_zscore:.2f}")
                
# #     def render_price_chart(self, ticker: str, data: pd.DataFrame):
# #         """Render interactive price chart"""
# #         if data is None or data.empty:
# #             st.warning(f"No data available for {ticker}")
# #             return
            
# #         fig = make_subplots(
# #             rows=3, cols=1,
# #             shared_xaxes=True,
# #             vertical_spacing=0.05,
# #             subplot_titles=(f"{ticker} Price", "Volume", "Volatility & Z-Score"),
# #             row_heights=[0.5, 0.25, 0.25]
# #         )
        
# #         # Price chart
# #         fig.add_trace(
# #             go.Candlestick(
# #                 x=data.index,
# #                 open=data['open'],
# #                 high=data['high'],
# #                 low=data['low'],
# #                 close=data['close'],
# #                 name="Price"
# #             ),
# #             row=1, col=1
# #         )
        
# #         # Add EMA
# #         if 'close_smoothed' in data.columns:
# #             fig.add_trace(
# #                 go.Scatter(
# #                     x=data.index,
# #                     y=data['close_smoothed'],
# #                     name="EMA",
# #                     line=dict(color='orange', width=1)
# #                 ),
# #                 row=1, col=1
# #             )
            
# #         # Volume chart
# #         colors = ['red' if close < open else 'green' 
# #                   for close, open in zip(data['close'], data['open'])]
# #         fig.add_trace(
# #             go.Bar(x=data.index, y=data['volume'], name="Volume", marker_color=colors),
# #             row=2, col=1
# #         )
        
# #         # Volatility and Z-score
# #         if 'volatility' in data.columns:
# #             fig.add_trace(
# #                 go.Scatter(
# #                     x=data.index,
# #                     y=data['volatility'],
# #                     name="Volatility",
# #                     line=dict(color='red', width=2)
# #                 ),
# #                 row=3, col=1
# #             )
            
# #         if 'volume_zscore' in data.columns:
# #             fig.add_trace(
# #                 go.Scatter(
# #                     x=data.index,
# #                     y=data['volume_zscore'],
# #                     name="Volume Z-Score",
# #                     line=dict(color='blue', width=2, dash='dash')
# #                 ),
# #                 row=3, col=1
# #             )
            
# #             # Add threshold lines
# #             fig.add_hline(y=2, line_dash="dash", line_color="yellow", row=3, col=1)
# #             fig.add_hline(y=3, line_dash="dash", line_color="red", row=3, col=1)
            
# #         # Update layout
# #         fig.update_layout(
# #             title=f"{ticker} - Real-Time Market Analysis",
# #             xaxis_title="Time",
# #             height=800,
# #             showlegend=True,
# #             template="plotly_dark"
# #         )
        
# #         fig.update_xaxes(title_text="Time", row=3, col=1)
# #         fig.update_yaxes(title_text="Price", row=1, col=1)
# #         fig.update_yaxes(title_text="Volume", row=2, col=1)
# #         fig.update_yaxes(title_text="Value", row=3, col=1)
        
# #         st.plotly_chart(fig, use_container_width=True)
        
# #     def render_portfolio_dashboard(self, current_prices: dict):
# #         """Render portfolio performance dashboard"""
# #         st.header("💼 Portfolio Dashboard")
        
# #         # Get portfolio metrics
# #         metrics = self.portfolio.get_portfolio_metrics(current_prices)
        
# #         # Metrics row
# #         col1, col2, col3, col4, col5 = st.columns(5)
        
# #         with col1:
# #             st.metric(
# #                 "Total Value",
# #                 f"${metrics['total_value']:,.2f}",
# #                 delta=f"{metrics['total_return']:.2f}%"
# #             )
# #         with col2:
# #             st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
# #         with col3:
# #             st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
# #         with col4:
# #             st.metric("Open Positions", metrics['open_positions'])
# #         with col5:
# #             st.metric("Total Trades", metrics['total_trades'])
            
# #         # Open positions
# #         if metrics['open_positions'] > 0:
# #             st.subheader("📈 Open Positions")
# #             positions_data = []
# #             for ticker, position in self.portfolio.positions.items():
# #                 current_price = current_prices.get(ticker, position.entry_price)
# #                 pnl = (current_price - position.entry_price) * position.shares
# #                 pnl_pct = (current_price - position.entry_price) / position.entry_price * 100
                
# #                 positions_data.append({
# #                     'Ticker': ticker,
# #                     'Shares': f"{position.shares:.2f}",
# #                     'Entry Price': f"${position.entry_price:.2f}",
# #                     'Current Price': f"${current_price:.2f}",
# #                     'P&L': f"${pnl:.2f}",
# #                     'P&L %': f"{pnl_pct:.2f}%",
# #                     'Stop Loss': f"${position.stop_loss:.2f}",
# #                     'Take Profit': f"${position.take_profit:.2f}"
# #                 })
                
# #             st.dataframe(pd.DataFrame(positions_data), use_container_width=True)
            
# #         # Trade history
# #         trades_df = self.portfolio.get_performance_summary()
# #         if not trades_df.empty:
# #             st.subheader("📊 Trade History")
# #             st.dataframe(trades_df, use_container_width=True)
            
# #     def render_alerts_panel(self):
# #         """Render alerts and notifications panel"""
# #         st.header("🚨 Alerts & Notifications")
        
# #         # Recent alerts
# #         recent_alerts = self.alert_system.get_recent_alerts(minutes=60)
        
# #         if recent_alerts:
# #             for alert in recent_alerts[:10]:  # Show last 10 alerts
# #                 with st.container():
# #                     st.markdown(f"""
# #                     <div style="padding: 10px; margin: 5px 0; border-radius: 5px; background-color: #2e2e2e;">
# #                         <strong>{alert.severity}</strong> [{alert.ticker}] {alert.timestamp.strftime('%H:%M:%S')}<br>
# #                         {alert.message}
# #                     </div>
# #                     """, unsafe_allow_html=True)
# #         else:
# #             st.info("No recent alerts. Market conditions are normal.")
            
# #         # Alert history table
# #         alerts_df = self.alert_system.get_alerts_summary()
# #         if not alerts_df.empty:
# #             with st.expander("📜 Alert History"):
# #                 st.dataframe(alerts_df.head(20), use_container_width=True)
                
# #     def render_correlation_matrix(self, features_data: dict):
# #         """Render correlation matrix of returns"""
# #         st.header("📊 Cross-Asset Correlation")
        
# #         # Calculate returns for all tickers
# #         returns_data = {}
# #         for ticker, features in features_data.items():
# #             if 'returns' in features.columns:
# #                 returns_data[ticker] = features['returns'].iloc[-ROLLING_WINDOW:]
                
# #         if len(returns_data) > 1:
# #             returns_df = pd.DataFrame(returns_data)
# #             corr_matrix = returns_df.corr()
            
# #             fig = px.imshow(
# #                 corr_matrix,
# #                 text_auto=True,
# #                 aspect="auto",
# #                 color_continuous_scale="RdBu",
# #                 title="Returns Correlation Matrix (Last 20 periods)"
# #             )
            
# #             fig.update_layout(height=500)
# #             st.plotly_chart(fig, use_container_width=True)
            
# #     def run(self):
# #         """Main dashboard loop"""
# #         st.title("📈 Market Regime Intelligence System")
# #         st.markdown("*Real-time statistical market analysis and portfolio management*")
        
# #         # Sidebar controls
# #         refresh_rate, selected_tickers, auto_refresh = self.render_sidebar()
        
# #         # Main content tabs
# #         tab1, tab2, tab3, tab4 = st.tabs([
# #             "📊 Market Analysis", 
# #             "💼 Portfolio", 
# #             "🚨 Alerts",
# #             "📈 Correlation"
# #         ])
        
# #         # Auto-refresh logic
# #         if auto_refresh:
# #             time.sleep(refresh_rate)
# #             st.rerun()
            
# #         # Fetch and process data
# #         processed_data, features_data = self.fetch_and_process_data()
        
# #         if not processed_data:
# #             st.error("Failed to fetch market data. Please check your internet connection.")
# #             return
            
# #         # Analyze regimes
# #         regime_results = self.analyze_regimes(features_data)
        
# #         # Update current prices for portfolio
# #         current_prices = {
# #             ticker: features['close'].iloc[-1] 
# #             for ticker, features in features_data.items() 
# #             if not features.empty
# #         }
        
# #         # Tab 1: Market Analysis
# #         with tab1:
# #             st.header("Market Regime Analysis")
            
# #             # Regime summary table
# #             summary_df = self.detector.generate_regime_summary(regime_results)
# #             st.dataframe(summary_df, use_container_width=True)
            
# #             st.markdown("---")
            
# #             # Individual stock analysis
# #             for ticker in selected_tickers:
# #                 if ticker in processed_data and ticker in regime_results:
# #                     st.subheader(f"📊 {ticker} Analysis")
                    
# #                     col1, col2 = st.columns([1, 2])
                    
# #                     with col1:
# #                         self.render_regime_card(ticker, regime_results[ticker])
                        
# #                     with col2:
# #                         # Show regime alerts
# #                         alerts = [a for a in self.alert_system.get_recent_alerts(5) if a.ticker == ticker]
# #                         if alerts:
# #                             st.warning(f"⚠️ Recent Alerts: {len(alerts)}")
# #                             for alert in alerts[:3]:
# #                                 st.caption(f"• {alert.message}")
                                
# #                     # Price chart
# #                     self.render_price_chart(ticker, processed_data[ticker])
                    
# #         # Tab 2: Portfolio
# #         with tab2:
# #             self.render_portfolio_dashboard(current_prices)
            
# #         # Tab 3: Alerts
# #         with tab3:
# #             self.render_alerts_panel()
            
# #         # Tab 4: Correlation
# #         with tab4:
# #             self.render_correlation_matrix(features_data)
            
# #         # Footer
# #         st.markdown("---")
# #         st.caption(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Source: Yahoo Finance | Refresh Rate: {refresh_rate}s")

# # def main():
# #     """Main entry point"""
# #     dashboard = MarketRegimeDashboard()
# #     dashboard.run()

# # if __name__ == "__main__":
# #     main()

# # dashboard_working.py
# """
# Market Regime Intelligence System - Working Version
# """

# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# from datetime import datetime, timedelta
# import yfinance as yf
# import time

# # Page configuration
# st.set_page_config(
#     page_title="Market Regime Intelligence System",
#     page_icon="📈",
#     layout="wide"
# )

# # Custom CSS for better styling
# st.markdown("""
# <style>
#     .stMetric {
#         background-color: #1e1e1e;
#         padding: 10px;
#         border-radius: 10px;
#     }
#     .regime-trending {
#         color: #00ff00;
#         font-weight: bold;
#     }
#     .regime-meanreverting {
#         color: #ffaa00;
#         font-weight: bold;
#     }
#     .regime-random {
#         color: #888888;
#         font-weight: bold;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Title
# st.title("📈 Market Regime Intelligence System")
# st.markdown("*Real-time Statistical Market Analysis Using Hurst Exponent & Z-Scores*")

# # Sidebar
# with st.sidebar:
#     st.header("🎮 Controls")
    
#     # Stock selection
#     default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
#     selected_tickers = st.multiselect(
#         "Select Stocks to Analyze",
#         options=default_tickers,
#         default=['AAPL', 'MSFT']
#     )
    
#     st.markdown("---")
    
#     # Timeframe selection
#     timeframe = st.selectbox(
#         "Data Interval",
#         options=['1m', '5m', '15m', '30m', '1h'],
#         index=0,
#         help="Select the time interval for data"
#     )
    
#     st.markdown("---")
    
#     # Refresh button
#     if st.button("🔄 Refresh Data", use_container_width=True):
#         st.cache_data.clear()
#         st.rerun()
    
#     # Auto-refresh option
#     auto_refresh = st.checkbox("Auto-refresh (30 seconds)", value=False)
    
#     st.markdown("---")
#     st.info("""
#     **Market Regimes:**
#     - 📈 **TRENDING**: H > 0.6
#     - 🔄 **MEAN-REVERTING**: H < 0.4  
#     - 🎲 **RANDOM**: 0.4 ≤ H ≤ 0.6
#     """)

# # Function to fetch data with error handling
# @st.cache_data(ttl=30)
# def fetch_stock_data(ticker, interval='1m', period='1d'):
#     """Fetch stock data with error handling"""
#     try:
#         stock = yf.Ticker(ticker)
        
#         # Map intervals for yfinance
#         interval_map = {
#             '1m': '1m', '5m': '5m', '15m': '15m', 
#             '30m': '30m', '1h': '1h'
#         }
        
#         yf_interval = interval_map.get(interval, '1m')
        
#         # Fetch data
#         data = stock.history(period=period, interval=yf_interval)
        
#         if data.empty:
#             st.warning(f"No data for {ticker}")
#             return None
            
#         # Rename columns to lowercase
#         data.columns = [col.lower() for col in data.columns]
        
#         return data
        
#     except Exception as e:
#         st.error(f"Error fetching {ticker}: {str(e)}")
#         return None

# # Function to calculate Hurst exponent
# def calculate_hurst_exponent(price_series):
#     """Calculate Hurst exponent to determine market regime"""
#     try:
#         # Calculate returns
#         returns = np.diff(np.log(price_series.dropna().values))
        
#         if len(returns) < 20:
#             return 0.5
            
#         max_lag = min(len(returns) // 2, 100)
#         lags = range(2, max_lag)
        
#         # Calculate R/S statistic
#         tau = []
#         for lag in lags:
#             # Split into chunks
#             chunks = [returns[i:i+lag] for i in range(0, len(returns), lag) 
#                      if len(returns[i:i+lag]) == lag]
            
#             if len(chunks) < 2:
#                 continue
                
#             # Calculate R/S for each chunk
#             rs_values = []
#             for chunk in chunks:
#                 chunk_centered = chunk - np.mean(chunk)
#                 cumsum = np.cumsum(chunk_centered)
#                 r = np.max(cumsum) - np.min(cumsum)
#                 s = np.std(chunk)
#                 if s != 0:
#                     rs_values.append(r / s)
            
#             if rs_values:
#                 tau.append(np.mean(rs_values))
        
#         if len(tau) < 2:
#             return 0.5
            
#         # Linear regression on log-log plot
#         tau = np.array(tau)
#         lags = np.array(lags[:len(tau)])
        
#         # Remove invalid values
#         valid = (tau > 0) & np.isfinite(tau)
#         tau = tau[valid]
#         lags = lags[valid]
        
#         if len(tau) < 2:
#             return 0.5
            
#         hurst = np.polyfit(np.log(lags), np.log(tau), 1)[0]
        
#         # Bound between 0 and 1
#         hurst = max(0, min(1, hurst))
        
#         return hurst
        
#     except Exception as e:
#         return 0.5

# # Function to determine regime
# def get_regime(hurst):
#     """Determine market regime based on Hurst exponent"""
#     if hurst > 0.6:
#         return "📈 TRENDING", "#00ff00", "Trend Following", 1.5
#     elif hurst < 0.4:
#         return "🔄 MEAN-REVERTING", "#ffaa00", "Mean Reversion", 0.7
#     else:
#         return "🎲 RANDOM WALK", "#888888", "Wait & See", 0.3

# # Function to create price chart
# def create_price_chart(data, ticker):
#     """Create interactive price chart with indicators"""
    
#     # Calculate indicators
#     data['sma_20'] = data['close'].rolling(window=20).mean()
#     data['returns'] = data['close'].pct_change()
#     data['volatility'] = data['returns'].rolling(window=20).std() * 100
#     data['volume_zscore'] = ((data['volume'] - data['volume'].rolling(window=20).mean()) / 
#                               data['volume'].rolling(window=20).std())
    
#     # Create subplots
#     fig = make_subplots(
#         rows=3, cols=1,
#         shared_xaxes=True,
#         vertical_spacing=0.03,
#         row_heights=[0.5, 0.25, 0.25],
#         subplot_titles=(f"{ticker} - Price", "Volume", "Volume Z-Score")
#     )
    
#     # Price chart with candlesticks
#     fig.add_trace(
#         go.Candlestick(
#             x=data.index,
#             open=data['open'],
#             high=data['high'],
#             low=data['low'],
#             close=data['close'],
#             name="Price"
#         ),
#         row=1, col=1
#     )
    
#     # Add SMA
#     fig.add_trace(
#         go.Scatter(
#             x=data.index,
#             y=data['sma_20'],
#             name="SMA 20",
#             line=dict(color='orange', width=1)
#         ),
#         row=1, col=1
#     )
    
#     # Volume chart
#     colors = ['red' if close < open else 'green' 
#               for close, open in zip(data['close'], data['open'])]
#     fig.add_trace(
#         go.Bar(
#             x=data.index,
#             y=data['volume'],
#             name="Volume",
#             marker_color=colors
#         ),
#         row=2, col=1
#     )
    
#     # Volume Z-score
#     fig.add_trace(
#         go.Scatter(
#             x=data.index,
#             y=data['volume_zscore'],
#             name="Volume Z-Score",
#             line=dict(color='blue', width=2)
#         ),
#         row=3, col=1
#     )
    
#     # Add threshold lines for Z-score
#     fig.add_hline(y=2, line_dash="dash", line_color="yellow", 
#                   annotation_text="Alert", row=3, col=1)
#     fig.add_hline(y=3, line_dash="dash", line_color="red", 
#                   annotation_text="Critical", row=3, col=1)
#     fig.add_hline(y=-2, line_dash="dash", line_color="yellow", row=3, col=1)
    
#     # Update layout
#     fig.update_layout(
#         title=f"{ticker} - Real-Time Market Analysis",
#         xaxis_title="Time",
#         height=800,
#         template="plotly_dark",
#         showlegend=True,
#         xaxis_rangeslider_visible=False
#     )
    
#     fig.update_yaxes(title_text="Price ($)", row=1, col=1)
#     fig.update_yaxes(title_text="Volume", row=2, col=1)
#     fig.update_yaxes(title_text="Z-Score", row=3, col=1)
    
#     return fig

# # Main content
# if not selected_tickers:
#     st.warning("⚠️ Please select at least one stock from the sidebar to begin analysis")
#     st.stop()

# # Create tabs
# tab1, tab2, tab3 = st.tabs(["📊 Market Analysis", "📈 Portfolio Insights", "ℹ️ About"])

# with tab1:
#     # Fetch and display data for each ticker
#     for ticker in selected_tickers:
#         st.markdown("---")
        
#         # Fetch data
#         data = fetch_stock_data(ticker, timeframe)
        
#         if data is None or data.empty:
#             st.error(f"❌ Could not fetch data for {ticker}")
#             continue
        
#         # Calculate metrics
#         hurst = calculate_hurst_exponent(data['close'])
#         regime, color, strategy, pos_mult = get_regime(hurst)
        
#         # Get latest values
#         latest_price = data['close'].iloc[-1]
#         price_change = data['close'].pct_change().iloc[-1] * 100
#         volume = data['volume'].iloc[-1]
#         volume_z = ((volume - data['volume'].rolling(20).mean().iloc[-1]) / 
#                     data['volume'].rolling(20).std().iloc[-1])
#         volatility = data['close'].pct_change().std() * 100
        
#         # Display metrics in columns
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             st.metric(
#                 label=f"📊 {ticker}",
#                 value=f"${latest_price:.2f}",
#                 delta=f"{price_change:.2f}%"
#             )
        
#         with col2:
#             st.markdown(f"""
#             <div style='text-align: center'>
#                 <p style='margin-bottom: 0; color: #888'>Market Regime</p>
#                 <p style='font-size: 24px; font-weight: bold; color: {color}'>{regime}</p>
#             </div>
#             """, unsafe_allow_html=True)
        
#         with col3:
#             st.metric(
#                 label="Hurst Exponent",
#                 value=f"{hurst:.3f}",
#                 help="H > 0.6: Trending | H < 0.4: Mean-reverting"
#             )
        
#         with col4:
#             st.metric(
#                 label="Volume Z-Score",
#                 value=f"{volume_z:.2f}",
#                 delta="Alert" if abs(volume_z) > 2 else "Normal",
#                 delta_color="inverse" if abs(volume_z) > 2 else "normal"
#             )
        
#         # Additional metrics row
#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.metric("Volatility", f"{volatility:.2f}%")
#         with col2:
#             st.metric("Strategy", strategy)
#         with col3:
#             st.metric("Position Size", f"{pos_mult:.0%}")
#         with col4:
#             st.metric("Volume", f"{volume:,.0f}")
        
#         # Alert for abnormal conditions
#         if abs(volume_z) > 2:
#             if abs(volume_z) > 3:
#                 st.error(f"🚨 **CRITICAL ALERT**: {ticker} showing extreme volume spike (Z={volume_z:.2f})!")
#             else:
#                 st.warning(f"⚠️ **Alert**: {ticker} showing unusual volume activity (Z={volume_z:.2f})")
        
#         # Price chart
#         fig = create_price_chart(data, ticker)
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Show recent data table
#         with st.expander(f"📋 Recent Data for {ticker}"):
#             recent_data = data[['open', 'high', 'low', 'close', 'volume']].tail(10)
#             recent_data = recent_data.round(2)
#             st.dataframe(recent_data, use_container_width=True)

# with tab2:
#     st.header("💼 Portfolio Insights")
    
#     # Calculate portfolio metrics
#     if selected_tickers:
#         portfolio_data = {}
#         for ticker in selected_tickers:
#             data = fetch_stock_data(ticker, timeframe)
#             if data is not None and not data.empty:
#                 hurst = calculate_hurst_exponent(data['close'])
#                 regime, _, _, pos_mult = get_regime(hurst)
#                 portfolio_data[ticker] = {
#                     'Price': data['close'].iloc[-1],
#                     'Regime': regime,
#                     'Position Size': f"{pos_mult:.0%}",
#                     'Hurst': hurst
#                 }
        
#         if portfolio_data:
#             df = pd.DataFrame(portfolio_data).T
#             st.dataframe(df, use_container_width=True)
            
#             # Recommendation
#             st.subheader("📝 Recommendations")
#             for ticker, info in portfolio_data.items():
#                 if "TRENDING" in info['Regime']:
#                     st.success(f"✅ **{ticker}**: Trending market - Consider increasing position size")
#                 elif "MEAN-REVERTING" in info['Regime']:
#                     st.warning(f"⚠️ **{ticker}**: Mean-reverting market - Reduce position size")
#                 else:
#                     st.info(f"ℹ️ **{ticker}**: Random walk - Wait for clearer signal")
#     else:
#         st.info("Select stocks to see portfolio insights")

# with tab3:
#     st.header("ℹ️ About This System")
    
#     st.markdown("""
#     ### 🧠 Statistical Market Intelligence System
    
#     This system uses **advanced statistical methods** to analyze market conditions in real-time:
    
#     #### Key Statistical Concepts:
    
#     **1. Hurst Exponent (H)**
#     - Measures long-term memory and trend persistence
#     - H > 0.6: **Trending market** (momentum strategies)
#     - H < 0.4: **Mean-reverting market** (contrarian strategies)
#     - H ≈ 0.5: **Random walk** (avoid trading)
    
#     **2. Volume Z-Score**
#     - Detects abnormal trading activity
#     - |Z| > 2: Unusual activity alert
#     - |Z| > 3: Critical anomaly
    
#     **3. Volatility Analysis**
#     - Rolling standard deviation of returns
#     - Identifies market stress periods
    
#     #### Market Regimes Detected:
#     - 📈 **TRENDING**: Use trend-following strategies
#     - 🔄 **MEAN-REVERTING**: Use mean reversion strategies
#     - 🎲 **RANDOM**: Stay on sidelines
#     - ⚠️ **VOLUME SPIKE**: Potential news/event
#     - 🚨 **ANOMALY**: Extreme conditions - exit positions
    
#     #### Data Source:
#     - Real-time data from Yahoo Finance API
#     - Updates every 30 seconds when auto-refresh is enabled
    
#     #### Built With:
#     - Python 3.11+
#     - Streamlit (Dashboard)
#     - yfinance (Data)
#     - Plotly (Visualizations)
#     - NumPy/Pandas (Calculations)
#     """)

# # Auto-refresh logic
# if auto_refresh:
#     time.sleep(30)
#     st.rerun()

# # Footer
# st.markdown("---")
# col1, col2, col3 = st.columns(3)
# with col2:
#     st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# enhanced_dashboard.py
"""
Enhanced dashboard with ML predictions and XAI
"""
# complete_working_dashboard.py
"""
Complete Market Intelligence System
No external ML libraries needed - Pure statistical analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from scipy import stats
from scipy.signal import find_peaks
from scipy.stats import norm, skew, kurtosis, jarque_bera
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Market Intelligence System",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00ff00, #00aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00aaff;
        margin: 10px 0;
    }
    .insight-box {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 3px solid #ffaa00;
    }
</style>
""", unsafe_allow_html=True)

class MarketIntelligenceSystem:
    """Complete market intelligence system with statistical analysis"""
    
    def __init__(self):
        self.data_cache = {}
        
    def fetch_data(self, tickers, period='1d', interval='1m'):
        """Fetch real-time market data"""
        data_dict = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period=period, interval=interval)
                
                if not data.empty:
                    data.columns = [col.lower() for col in data.columns]
                    
                    # Calculate basic features
                    data['returns'] = data['close'].pct_change()
                    data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
                    data['volatility'] = data['returns'].rolling(20).std() * np.sqrt(252)
                    data['volume_zscore'] = ((data['volume'] - data['volume'].rolling(20).mean()) / 
                                              data['volume'].rolling(20).std())
                    
                    # Moving averages
                    data['sma_20'] = data['close'].rolling(20).mean()
                    data['sma_50'] = data['close'].rolling(50).mean()
                    data['ema_12'] = data['close'].ewm(span=12, adjust=False).mean()
                    data['ema_26'] = data['close'].ewm(span=26, adjust=False).mean()
                    
                    # Technical indicators
                    data['rsi'] = self.calculate_rsi(data['close'])
                    data['bb_upper'], data['bb_middle'], data['bb_lower'] = self.calculate_bollinger_bands(data['close'])
                    
                    # Advanced metrics
                    data['hurst'] = self.calculate_rolling_hurst(data['close'], window=50)
                    data['atr'] = self.calculate_atr(data)
                    
                    data_dict[ticker] = data
                    
            except Exception as e:
                st.warning(f"Could not fetch {ticker}: {str(e)}")
        
        return data_dict
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower
    
    def calculate_atr(self, data, window=14):
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        
        return atr
    
    def calculate_hurst(self, series):
        """Calculate Hurst exponent for regime detection"""
        try:
            prices = series.dropna().values
            if len(prices) < 20:
                return 0.5
            
            # Calculate returns
            returns = np.diff(np.log(prices))
            
            max_lag = min(len(returns) // 2, 100)
            lags = range(2, max_lag)
            tau = []
            
            for lag in lags:
                # Split into chunks
                chunks = [returns[i:i+lag] for i in range(0, len(returns), lag) 
                         if len(returns[i:i+lag]) == lag]
                
                if len(chunks) < 2:
                    continue
                
                # Calculate R/S for each chunk
                rs_values = []
                for chunk in chunks:
                    chunk_centered = chunk - np.mean(chunk)
                    cumsum = np.cumsum(chunk_centered)
                    r = np.max(cumsum) - np.min(cumsum)
                    s = np.std(chunk)
                    if s != 0:
                        rs_values.append(r / s)
                
                if rs_values:
                    tau.append(np.mean(rs_values))
            
            if len(tau) < 2:
                return 0.5
            
            # Linear regression on log-log plot
            hurst = np.polyfit(np.log(lags[:len(tau)]), np.log(tau), 1)[0]
            return np.clip(hurst, 0, 1)
            
        except Exception:
            return 0.5
    
    def calculate_rolling_hurst(self, series, window=50):
        """Calculate rolling Hurst exponent"""
        hurst_values = []
        for i in range(window, len(series) + 1):
            window_data = series.iloc[i-window:i]
            hurst = self.calculate_hurst(window_data)
            hurst_values.append(hurst)
        
        # Pad beginning with NaN
        hurst_values = [np.nan] * (window - 1) + hurst_values
        return pd.Series(hurst_values, index=series.index)
    
    def get_regime(self, hurst):
        """Determine market regime from Hurst exponent"""
        if pd.isna(hurst):
            return "UNKNOWN", "#888888", "Wait", 1.0, "No clear signal"
        elif hurst > 0.65:
            return "TRENDING", "#00ff00", "Trend Following", 1.5, "Strong directional movement - follow the trend"
        elif hurst > 0.55:
            return "WEAK TREND", "#88ff88", "Cautious Trend", 1.2, "Weak trend detected - partial allocation"
        elif hurst < 0.35:
            return "STRONG MEAN-REVERTING", "#ff6600", "Contrarian", 0.5, "Strong reversal signals - fade moves"
        elif hurst < 0.45:
            return "MEAN-REVERTING", "#ffaa00", "Mean Reversion", 0.7, "Range bound - buy dips, sell rips"
        else:
            return "RANDOM", "#888888", "Sideways", 0.4, "No clear direction - reduce exposure"
    
    def calculate_var_cvar(self, returns, confidence_level=0.95):
        """Calculate Value at Risk and Conditional VaR"""
        var = np.percentile(returns, (1 - confidence_level) * 100)
        cvar = returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else var
        return var, cvar
    
    def calculate_max_drawdown(self, prices):
        """Calculate maximum drawdown"""
        cum_returns = (1 + prices.pct_change()).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdown = (cum_returns - rolling_max) / rolling_max
        return drawdown.min(), drawdown
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252
        if returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def calculate_calmar_ratio(self, returns, max_drawdown):
        """Calculate Calmar ratio"""
        annual_return = returns.mean() * 252
        if max_drawdown == 0:
            return 0
        return annual_return / abs(max_drawdown)
    
    def calculate_sortino_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sortino ratio (downside risk)"""
        excess_returns = returns - risk_free_rate / 252
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else returns.std()
        if downside_deviation == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / downside_deviation
    
    def detect_regime_shifts(self, prices, window=20, threshold=2):
        """Detect regime shifts using rolling statistics"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        zscore = (prices - rolling_mean) / rolling_std
        
        # Detect shifts where zscore exceeds threshold
        shifts = np.where(np.abs(zscore) > threshold)[0]
        
        return shifts, zscore
    
    def calculate_volume_profile(self, data, bins=50):
        """Calculate volume profile (VWAP style)"""
        prices = data['close'].values
        volumes = data['volume'].values
        
        # Create price bins
        price_min, price_max = prices.min(), prices.max()
        price_bins = np.linspace(price_min, price_max, bins)
        
        # Calculate volume at each price level
        volume_profile = []
        for i in range(len(price_bins) - 1):
            mask = (prices >= price_bins[i]) & (prices < price_bins[i+1])
            vol_at_level = volumes[mask].sum()
            volume_profile.append(vol_at_level)
        
        return price_bins[:-1], np.array(volume_profile)
    
    def calculate_correlation_matrix(self, data_dict, window=50):
        """Calculate correlation matrix between assets"""
        returns_dict = {}
        for ticker, data in data_dict.items():
            if len(data) >= window:
                returns_dict[ticker] = data['returns'].iloc[-window:]
        
        if len(returns_dict) > 1:
            returns_df = pd.DataFrame(returns_dict)
            return returns_df.corr()
        return None
    
    def optimize_simple_portfolio(self, data_dict, method='risk_parity'):
        """Simple portfolio optimization"""
        if len(data_dict) < 2:
            return None
        
        # Calculate metrics for each asset
        metrics = []
        for ticker, data in data_dict.items():
            returns = data['returns'].dropna()
            if len(returns) > 20:
                vol = returns.std() * np.sqrt(252)
                ret = returns.mean() * 252
                sharpe = ret / vol if vol > 0 else 0
                metrics.append({
                    'ticker': ticker,
                    'return': ret,
                    'volatility': vol,
                    'sharpe': sharpe
                })
        
        if len(metrics) < 2:
            return None
        
        # Calculate weights based on method
        if method == 'risk_parity':
            inv_vol = 1 / np.array([m['volatility'] for m in metrics])
            weights = inv_vol / inv_vol.sum()
        elif method == 'max_sharpe':
            sharpe_vals = np.array([m['sharpe'] for m in metrics])
            weights = np.maximum(sharpe_vals, 0)
            weights = weights / weights.sum() if weights.sum() > 0 else np.ones(len(metrics)) / len(metrics)
        elif method == 'min_variance':
            inv_var = 1 / np.array([m['volatility']**2 for m in metrics])
            weights = inv_var / inv_var.sum()
        else:  # equal weight
            weights = np.ones(len(metrics)) / len(metrics)
        
        # Create allocation
        allocation = {metrics[i]['ticker']: weights[i] for i in range(len(metrics))}
        
        # Calculate portfolio metrics
        portfolio_return = np.sum([metrics[i]['return'] * weights[i] for i in range(len(metrics))])
        portfolio_volatility = np.sqrt(np.sum([(metrics[i]['volatility'] * weights[i])**2 for i in range(len(metrics))]))
        
        return {
            'allocation': allocation,
            'return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe': portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        }

def main():
    st.markdown('<div class="main-title">📈 Market Intelligence System</div>', unsafe_allow_html=True)
    st.markdown("*Statistical Market Analysis + Regime Detection + Risk Management*")
    
    # Initialize system
    system = MarketIntelligenceSystem()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Asset selection
        available_tickers = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'AMZN', 'META', 'JPM', 'V', 'JNJ', 'WMT', 'PG']
        selected_tickers = st.multiselect(
            "Select Assets to Analyze",
            available_tickers,
            default=['AAPL', 'MSFT', 'GOOGL']
        )
        
        st.markdown("---")
        
        # Analysis period
        st.subheader("📊 Analysis Settings")
        analysis_period = st.selectbox(
            "Data Period",
            ['1d', '5d', '1mo', '3mo'],
            index=0,
            help="Amount of historical data to analyze"
        )
        
        st.markdown("---")
        
        # Risk settings
        st.subheader("⚠️ Risk Parameters")
        risk_free_rate = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=10.0, value=2.0) / 100
        var_confidence = st.slider("VaR Confidence Level", 0.90, 0.99, 0.95, 0.01)
        
        st.markdown("---")
        
        # Refresh
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    
    if not selected_tickers:
        st.warning("⚠️ Please select at least one asset from the sidebar")
        return
    
    # Fetch data
    with st.spinner("Fetching market data..."):
        current_data = system.fetch_data(selected_tickers, analysis_period, '5m')
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Analysis", 
        "📈 Risk Analytics", 
        "💼 Portfolio",
        "🔬 Statistical Tests",
        "📉 Correlation Analysis"
    ])
    
    # Tab 1: Market Analysis
    with tab1:
        for ticker, data in current_data.items():
            if data is not None and not data.empty:
                st.markdown(f"### {ticker}")
                
                # Get current metrics
                current_price = data['close'].iloc[-1]
                price_change = data['returns'].iloc[-1] * 100 if not pd.isna(data['returns'].iloc[-1]) else 0
                current_hurst = data['hurst'].iloc[-1] if 'hurst' in data else 0.5
                current_vol = data['volatility'].iloc[-1] * 100 if 'volatility' in data else 0
                volume_z = data['volume_zscore'].iloc[-1] if 'volume_zscore' in data else 0
                current_rsi = data['rsi'].iloc[-1] if 'rsi' in data else 50
                
                # Get regime
                regime, color, strategy, pos_mult, insight = system.get_regime(current_hurst)
                
                # Display metrics row
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Price", f"${current_price:.2f}", f"{price_change:.2f}%")
                with col2:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <small>Market Regime</small>
                        <h3 style='color: {color}; margin:0'>{regime}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.metric("Hurst Exponent", f"{current_hurst:.3f}", 
                             help=">0.65: Trending | 0.45-0.55: Random | <0.35: Mean-reverting")
                with col4:
                    st.metric("Volatility (Ann)", f"{current_vol:.1f}%")
                with col5:
                    delta_color = "inverse" if abs(volume_z) > 2 else "normal"
                    st.metric("Volume Z-Score", f"{volume_z:.2f}", 
                             delta="Alert" if abs(volume_z) > 2 else None, 
                             delta_color=delta_color)
                
                # Additional metrics row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("RSI", f"{current_rsi:.1f}", 
                             help=">70 Overbought, <30 Oversold")
                with col2:
                    st.metric("ATR", f"${data['atr'].iloc[-1]:.2f}" if 'atr' in data else "N/A")
                with col3:
                    st.metric("Position Size", f"{pos_mult:.0%}")
                with col4:
                    st.metric("Strategy", strategy)
                
                # Insight
                st.info(f"💡 **Insight**: {insight}")
                
                # Price chart
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                    row_heights=[0.5, 0.25, 0.25], 
                                    vertical_spacing=0.05,
                                    subplot_titles=("Price & Indicators", "Volume", "Hurst Exponent"))
                
                # Candlestick chart
                fig.add_trace(
                    go.Candlestick(
                        x=data.index,
                        open=data['open'],
                        high=data['high'],
                        low=data['low'],
                        close=data['close'],
                        name="Price"
                    ),
                    row=1, col=1
                )
                
                # Add Bollinger Bands
                if 'bb_upper' in data:
                    fig.add_trace(
                        go.Scatter(x=data.index, y=data['bb_upper'], name="BB Upper", 
                                  line=dict(color='gray', width=1, dash='dash')),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=data.index, y=data['bb_middle'], name="BB Middle", 
                                  line=dict(color='blue', width=1)),
                        row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=data.index, y=data['bb_lower'], name="BB Lower", 
                                  line=dict(color='gray', width=1, dash='dash')),
                        row=1, col=1
                    )
                
                # Volume chart
                colors = ['red' if data['close'].iloc[i] < data['open'].iloc[i] else 'green' 
                          for i in range(len(data))]
                fig.add_trace(
                    go.Bar(x=data.index, y=data['volume'], name="Volume", marker_color=colors),
                    row=2, col=1
                )
                
                # Hurst exponent
                fig.add_trace(
                    go.Scatter(x=data.index, y=data['hurst'], name="Hurst", 
                              line=dict(color='orange', width=2)),
                    row=3, col=1
                )
                
                # Add regime thresholds
                fig.add_hline(y=0.65, line_dash="dash", line_color="green", 
                             annotation_text="Trending", row=3, col=1)
                fig.add_hline(y=0.45, line_dash="dash", line_color="gray", 
                             annotation_text="Random", row=3, col=1)
                fig.add_hline(y=0.35, line_dash="dash", line_color="red", 
                             annotation_text="Mean-Reverting", row=3, col=1)
                
                fig.update_layout(
                    height=700,
                    template="plotly_dark",
                    showlegend=False,
                    xaxis_rangeslider_visible=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Alerts
                if abs(volume_z) > 3:
                    st.error(f"🚨 **CRITICAL**: Extreme volume anomaly (Z={volume_z:.2f}) - Investigate news")
                elif abs(volume_z) > 2:
                    st.warning(f"⚠️ **ALERT**: Unusual volume activity (Z={volume_z:.2f})")
                
                if current_rsi > 80:
                    st.warning(f"⚠️ **RSI ALERT**: Overbought ({current_rsi:.0f}) - Potential reversal")
                elif current_rsi < 20:
                    st.warning(f"⚠️ **RSI ALERT**: Oversold ({current_rsi:.0f}) - Potential bounce")
                
                st.markdown("---")
    
    # Tab 2: Risk Analytics
    with tab2:
        st.markdown("### 📊 Risk Analytics Dashboard")
        
        selected_risk = st.selectbox("Select Asset", selected_tickers, key="risk_select")
        
        if selected_risk in current_data:
            data = current_data[selected_risk]
            returns = data['returns'].dropna()
            prices = data['close']
            
            if len(returns) > 10:
                # Calculate risk metrics
                var_95, cvar_95 = system.calculate_var_cvar(returns, var_confidence)
                var_99, cvar_99 = system.calculate_var_cvar(returns, 0.99)
                max_dd, dd_series = system.calculate_max_drawdown(prices)
                sharpe = system.calculate_sharpe_ratio(returns, risk_free_rate)
                sortino = system.calculate_sortino_ratio(returns, risk_free_rate)
                calmar = system.calculate_calmar_ratio(returns, max_dd)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### Value at Risk")
                    st.metric(f"VaR ({var_confidence:.0%})", f"{var_95:.2%}")
                    st.metric(f"CVaR ({var_confidence:.0%})", f"{cvar_95:.2%}")
                    st.metric(f"VaR (99%)", f"{var_99:.2%}")
                    st.metric(f"CVaR (99%)", f"{cvar_99:.2%}")
                
                with col2:
                    st.markdown("#### Risk Ratios")
                    st.metric("Sharpe Ratio", f"{sharpe:.2f}")
                    st.metric("Sortino Ratio", f"{sortino:.2f}")
                    st.metric("Calmar Ratio", f"{calmar:.2f}")
                    st.metric("Max Drawdown", f"{max_dd:.2%}")
                
                with col3:
                    st.markdown("#### Return Statistics")
                    st.metric("Daily Return", f"{returns.mean():.3%}")
                    st.metric("Annual Return", f"{returns.mean() * 252:.2%}")
                    st.metric("Daily Volatility", f"{returns.std():.3%}")
                    st.metric("Annual Volatility", f"{returns.std() * np.sqrt(252):.2%}")
                
                # Drawdown chart
                st.markdown("#### 📉 Drawdown Analysis")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dd_series.index, y=dd_series * 100, 
                                        name="Drawdown", fill='tozeroy',
                                        line=dict(color='red')))
                fig.update_layout(title="Historical Drawdown", yaxis_title="Drawdown (%)",
                                 template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume profile
                st.markdown("#### 📊 Volume Profile")
                price_levels, volumes = system.calculate_volume_profile(data)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=volumes, y=price_levels, orientation='h',
                                    name="Volume Profile", marker_color='blue'))
                fig.update_layout(title="Volume Profile by Price Level", 
                                 xaxis_title="Volume", yaxis_title="Price",
                                 template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Portfolio
    with tab3:
        st.markdown("### 💼 Portfolio Optimization")
        
        if len(current_data) >= 2:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                optimization_method = st.selectbox(
                    "Optimization Method",
                    ['risk_parity', 'max_sharpe', 'min_variance', 'equal_weight'],
                    format_func=lambda x: {
                        'risk_parity': '🎯 Risk Parity',
                        'max_sharpe': '📈 Maximum Sharpe Ratio',
                        'min_variance': '🛡️ Minimum Variance',
                        'equal_weight': '⚖️ Equal Weight'
                    }.get(x, x)
                )
            
            with col2:
                st.write("")
                st.write("")
                optimize_btn = st.button("🚀 Optimize Portfolio", use_container_width=True)
            
            if optimize_btn:
                portfolio = system.optimize_simple_portfolio(current_data, optimization_method)
                
                if portfolio:
                    st.success("✅ Portfolio optimized successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Expected Annual Return", f"{portfolio['return']:.2%}")
                    with col2:
                        st.metric("Expected Volatility", f"{portfolio['volatility']:.2%}")
                    with col3:
                        st.metric("Sharpe Ratio", f"{portfolio['sharpe']:.2f}")
                    
                    # Allocation table
                    st.markdown("#### 📊 Recommended Allocation")
                    allocation_df = pd.DataFrame([
                        {'Asset': ticker, 'Weight': f"{weight:.1%}", 'Allocation': f"${weight * 100000:,.0f}"}
                        for ticker, weight in portfolio['allocation'].items()
                    ])
                    st.dataframe(allocation_df, use_container_width=True)
                    
                    # Pie chart
                    fig = px.pie(values=list(portfolio['allocation'].values()),
                                names=list(portfolio['allocation'].keys()),
                                title="Portfolio Allocation",
                                color_discrete_sequence=px.colors.qualitative.Set3)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Recommendations
                    st.markdown("#### 💡 Recommendations")
                    for ticker, weight in portfolio['allocation'].items():
                        if weight > 0.3:
                            st.success(f"✅ **{ticker}**: High conviction ({weight:.1%}) - Core holding")
                        elif weight < 0.1:
                            st.warning(f"⚠️ **{ticker}**: Low allocation ({weight:.1%}) - Consider reducing")
        else:
            st.info("Select at least 2 assets for portfolio optimization")
    
    # Tab 4: Statistical Tests
    with tab4:
        st.markdown("### 🔬 Statistical Tests & Distribution Analysis")
        
        selected_stat = st.selectbox("Select Asset", selected_tickers, key="stat_select")
        
        if selected_stat in current_data:
            data = current_data[selected_stat]
            returns = data['returns'].dropna()
            
            if len(returns) > 30:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Normality Tests")
                    
                    # Jarque-Bera test
                    jb_stat, jb_pvalue = jarque_bera(returns)
                    st.write(f"**Jarque-Bera Test**")
                    st.write(f"Statistic: {jb_stat:.4f}")
                    st.write(f"P-value: {jb_pvalue:.4f}")
                    if jb_pvalue < 0.05:
                        st.warning("❌ Returns are NOT normally distributed")
                    else:
                        st.success("✅ Returns appear normally distributed")
                    
                    st.markdown("---")
                    
                    # Skewness and Kurtosis
                    st.markdown("#### 📐 Distribution Moments")
                    st.metric("Skewness", f"{skew(returns):.3f}", 
                             help="Negative = left tail, Positive = right tail")
                    st.metric("Kurtosis", f"{kurtosis(returns):.3f}", 
                             help=">3 = Heavy tails (fat tails)")
                
                with col2:
                    st.markdown("#### 📈 Return Distribution")
                    
                    # Histogram with KDE
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(x=returns, nbinsx=50, name="Returns",
                                              histnorm='probability density'))
                    
                    # Add normal distribution
                    x_norm = np.linspace(returns.min(), returns.max(), 100)
                    y_norm = norm.pdf(x_norm, returns.mean(), returns.std())
                    fig.add_trace(go.Scatter(x=x_norm, y=y_norm, name="Normal Distribution",
                                            line=dict(color='red', dash='dash')))
                    
                    fig.update_layout(title="Return Distribution vs Normal",
                                     xaxis_title="Returns", yaxis_title="Density",
                                     template="plotly_dark", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Q-Q plot
                st.markdown("#### 📊 Q-Q Plot (Quantile-Quantile)")
                from scipy import stats as scipy_stats
                
                fig = go.Figure()
                (osm, osr), (slope, intercept, r) = scipy_stats.probplot(returns, dist="norm", plot=None)
                
                fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name='Sample Quantiles',
                                        marker=dict(color='blue', size=4)))
                fig.add_trace(go.Scatter(x=osm, y=slope * osm + intercept, name='Theoretical Line',
                                        line=dict(color='red', dash='dash')))
                
                fig.update_layout(title="Q-Q Plot for Normality Check",
                                 xaxis_title="Theoretical Quantiles", 
                                 yaxis_title="Sample Quantiles",
                                 template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 5: Correlation Analysis
    with tab5:
        st.markdown("### 📉 Correlation Analysis")
        
        if len(current_data) > 1:
            corr_matrix = system.calculate_correlation_matrix(current_data)
            
            if corr_matrix is not None:
                # Heatmap
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="RdBu",
                    title="Asset Correlation Matrix",
                    zmin=-1, zmax=1
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                # Correlation insights
                st.markdown("#### 💡 Correlation Insights")
                
                # Find highly correlated pairs
                high_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            high_corr.append({
                                'Pair': f"{corr_matrix.columns[i]} - {corr_matrix.columns[j]}",
                                'Correlation': corr_val,
                                'Interpretation': 'Strong positive' if corr_val > 0 else 'Strong negative'
                            })
                
                if high_corr:
                    st.warning("⚠️ **High Correlations Detected** - Potential diversification issues")
                    st.dataframe(pd.DataFrame(high_corr), use_container_width=True)
                else:
                    st.success("✅ No strong correlations - Good diversification")
                
                # Diversification score
                avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                diversification_score = 1 - avg_corr
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Average Correlation", f"{avg_corr:.3f}")
                with col2:
                    st.metric("Diversification Score", f"{diversification_score:.2%}",
                             help="Higher is better for risk reduction")
            else:
                st.warning("Insufficient data for correlation analysis")
        else:
            st.info("Select at least 2 assets for correlation analysis")
    
    # Footer
    st.markdown("---")
    st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("📊 Data Source: Yahoo Finance | Built with Streamlit")
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

if __name__ == "__main__":
    main()