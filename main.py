# main.py
"""
Main entry point for Market Regime Intelligence System
"""

import sys
import logging
from datetime import datetime
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_regime_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_dashboard():
    """Run the Streamlit dashboard"""
    import subprocess
    import os
    
    logger.info("Starting Market Regime Intelligence Dashboard...")
    
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(current_dir, 'dashboard.py')
    
    # Run streamlit
    subprocess.run([
        "streamlit", "run", dashboard_path,
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

def run_backtest():
    """Run a backtest mode"""
    logger.info("Running backtest mode...")
    # This would be implemented for historical testing
    pass

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Market Regime Intelligence System")
    parser.add_argument(
        "--mode",
        choices=["dashboard", "backtest"],
        default="dashboard",
        help="Run mode: dashboard (default) or backtest"
    )
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     MARKET REGIME INTELLIGENCE SYSTEM v1.0                   ║
    ║     Real-Time Statistical Market Analysis                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    logger.info(f"Starting system in {args.mode} mode")
    
    if args.mode == "dashboard":
        run_dashboard()
    elif args.mode == "backtest":
        run_backtest()
    else:
        logger.error(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()