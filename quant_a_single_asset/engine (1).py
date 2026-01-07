import yfinance as yf
import pandas as pd
import numpy as np

def fetch_asset_data(ticker, period="1y"):
    """
    Retrieves historical price data for a single asset.
    """
    try:
        data = yf.download(ticker, period=period, interval="1d", auto_adjust=True)
        if data.empty: return None
        return data['Close'].squeeze() 
    except Exception as e:
        print(f"Error: {e}")
        return None

def apply_strategy(prices, strategy_type="Buy and Hold", params=None):
    """
    Calculates cumulative strategy performance based on selected logic.
    """
    returns = prices.pct_change().fillna(0)
    
    if strategy_type == "Momentum (SMA Crossover)":
        short_w = params.get('short_window', 20)
        long_w = params.get('long_window', 50)
        short_sma = prices.rolling(window=short_w).mean()
        long_sma = prices.rolling(window=long_w).mean()
        # Signal: Long when Short SMA is above Long SMA
        position = (short_sma > long_sma).astype(int).shift(1).fillna(0)
        
    elif strategy_type == "RSI Strategy":
        window = params.get('rsi_period', 14)
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # Signal: Buy under 30 (Oversold), Sell over 70 (Overbought)
        position = pd.Series(index=prices.index, data=np.nan)
        position.loc[rsi < 30] = 1
        position.loc[rsi > 70] = 0
        position = position.ffill().fillna(0).shift(1)

    elif strategy_type == "Bollinger Bands":
        window = params.get('bb_window', 20)
        num_std = params.get('bb_std', 2)
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        # Signal: Buy if price < lower band, Sell if price > upper band
        position = pd.Series(index=prices.index, data=np.nan)
        position.loc[prices < lower_band] = 1
        position.loc[prices > upper_band] = 0
        position = position.ffill().fillna(0).shift(1)
    
    else: # Buy and Hold
        return (1 + returns).cumprod() * 100

    strat_returns = returns * position
    return (1 + strat_returns).cumprod() * 100

def compute_performance_metrics(strategy_series):
    """
    Computes standard risk/return metrics for the strategy.
    """
    if strategy_series.empty or strategy_series.std() == 0:
        return {"Sharpe Ratio": 0, "Max Drawdown": 0, "Total Return": 0, "Volatility": 0}

    returns = strategy_series.pct_change().dropna()
    vol = float(returns.std() * np.sqrt(252))
    sharpe = float((returns.mean() * 252) / vol) if vol > 0 else 0
    
    cum_max = strategy_series.cummax()
    drawdown = (strategy_series - cum_max) / cum_max
    max_dd = float(drawdown.min())
    
    return {
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
        "Total Return": float((strategy_series.iloc[-1] / 100) - 1),
        "Volatility": vol
    }