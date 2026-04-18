# preprocessing.py
"""
Data preprocessing module with statistical outlier detection
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging
from typing import List, Dict, Optional, Tuple, Any

import feature_engineering

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles data preprocessing, outlier detection, and noise reduction"""
    
    def __init__(self, outlier_sigma: float = 3.0, ema_span: int = 20):
        """
        Initialize preprocessor
        
        Args:
            outlier_sigma: Number of standard deviations for outlier detection
            ema_span: Span for EMA smoothing
        """
        self.outlier_sigma = outlier_sigma
        self.ema_span = ema_span
        
    def detect_outliers(self, data: pd.Series) -> pd.Series:
        """
        Detect outliers using 3-sigma rule
        
        Args:
            data: Input series
            
        Returns:
            Boolean series where True indicates outlier
        """
        mean = data.mean()
        std = data.std()
        
        if std == 0:
            return pd.Series([False] * len(data), index=data.index)
            
        z_scores = np.abs((data - mean) / std)
        outliers = z_scores > self.outlier_sigma
        
        outlier_count = outliers.sum()
        if outlier_count > 0:
            logger.info(f"Detected {outlier_count} outliers ({outlier_count/len(data)*100:.2f}%)")
            
        return outliers
    
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values using forward/backward fill
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with handled missing values
        """
        initial_missing = data.isnull().sum().sum()
        
        if initial_missing > 0:
            logger.info(f"Initial missing values: {initial_missing}")
            
            # Forward fill then backward fill
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # Fill any remaining NaN with 0 (should be very few)
            data = data.fillna(0)
            
            final_missing = data.isnull().sum().sum()
            logger.info(f"Remaining missing values: {final_missing}")
            
        return data
    
    def apply_ema_smoothing(self, data: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """
        Apply EMA smoothing to reduce noise
        
        Args:
            data: Input DataFrame
            columns: Columns to smooth (default: ['open', 'high', 'low', 'close'])
            
        Returns:
            DataFrame with smoothed values
        """
        if columns is None:
            columns = ['open', 'high', 'low', 'close']
            
        smoothed_data = data.copy()
        
        for col in columns:
            if col in data.columns:
                smoothed_data[f'{col}_smoothed'] = data[col].ewm(span=self.ema_span, adjust=False).mean()
                
        logger.info(f"Applied EMA smoothing with span={self.ema_span}")
        return smoothed_data
    
    def remove_outliers(self, data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        Remove outliers from a specific column
        
        Args:
            data: Input DataFrame
            column: Column to clean
            
        Returns:
            DataFrame with outliers removed
        """
        cleaned_data = data.copy()
        
        # Detect outliers
        outliers = self.detect_outliers(data[column])
        
        # Replace outliers with median
        if outliers.any():
            median_value = data[column].median()
            cleaned_data.loc[outliers, column] = median_value
            logger.info(f"Replaced {outliers.sum()} outliers with median value")
            
        return cleaned_data
    
    def align_timestamps(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Ensure uniform time intervals and sorted timestamps
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with aligned timestamps
        """
        # Sort by index
        data = data.sort_index()
        
        # Check for duplicate indices
        if data.index.duplicated().any():
            logger.warning(f"Found {data.index.duplicated().sum()} duplicate timestamps")
            data = data[~data.index.duplicated()]
            
        # Resample to ensure uniform intervals (for intraday data)
        if len(data) > 1:
            freq = pd.infer_freq(data.index)
            if freq is None:
                logger.info("No uniform frequency detected, keeping original timestamps")
                
        return data
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Complete preprocessing pipeline
        
        Args:
            data: Raw DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting preprocessing pipeline...")
        
        # Make a copy to avoid modifying original
        processed = data.copy()
        
        # Step 1: Handle missing values
        processed = self.handle_missing_values(processed)
        
        # Step 2: Align timestamps
        processed = self.align_timestamps(processed)
        
        # Step 3: Remove outliers from close price
        if 'close' in processed.columns:
            processed = self.remove_outliers(processed, 'close')
            
        # Step 4: Apply EMA smoothing
        processed = self.apply_ema_smoothing(processed)
        
        logger.info("Preprocessing complete!")
        return processed
    
    def calculate_returns(self, data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        Calculate log returns and simple returns
        
        Args:
            data: Input DataFrame
            column: Column to calculate returns from
            
        Returns:
            DataFrame with returns added
        """
        returns_data = data.copy()
        
        # Simple returns
        returns_data['returns_simple'] = returns_data[column].pct_change()
        
        # Log returns
        returns_data['returns_log'] = np.log(returns_data[column] / returns_data[column].shift(1))
        
        # Remove infinite values
        returns_data = returns_data.replace([np.inf, -np.inf], np.nan)
        
        logger.info("Calculated returns")
        return returns_data

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    sample_data = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.randn(100) * 0.1),
        'high': 100 + np.cumsum(np.random.randn(100) * 0.1) + 0.5,
        'low': 100 + np.cumsum(np.random.randn(100) * 0.1) - 0.5,
        'close': 100 + np.cumsum(np.random.randn(100) * 0.1),
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # Add some outliers
    sample_data.iloc[50, 3] = 500  # Extreme outlier
    
    # Preprocess
    preprocessor = DataPreprocessor()
    processed_data = preprocessor.preprocess(sample_data)
    processed_data = preprocessor.calculate_returns(processed_data)
    
    print("Original data shape:", sample_data.shape)
    print("Processed data shape:", processed_data.shape)
    print("\nProcessed data columns:", processed_data.columns.tolist())
    print("\nProcessed data tail:")
    print(processed_data[['close', 'close_smoothed', 'returns_log']].tail())


