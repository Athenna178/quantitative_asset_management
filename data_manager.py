import json
import pandas as pd
import os
from datetime import datetime

CONFIG_FILE = "portfolio_config.json"
HISTORY_FILE = "portfolio_history.csv"

def save_config(tickers, weights, freq, timeframe, equal_weights):
    """
    Saves the current configuration to a JSON file.
    """
    config = {
        "tickers": tickers,
        "weights": weights,
        "freq": freq,
        "timeframe": timeframe,
        "equal_weights": equal_weights
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def load_config():
    """
    Loads the configuration from the JSON file if it exists.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    return None

def log_daily_performance(metrics):
    """
    Appends the daily performance metrics to a CSV file.
    """
    row = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Total Return": metrics["Total Return"],
        "Portfolio Volatility": metrics["Portfolio Vol"],
        "Diversification Benefit": metrics["Diversification Benefit"]
    }
    df = pd.DataFrame([row])
    
    try:
        if not os.path.exists(HISTORY_FILE):
            df.to_csv(HISTORY_FILE, index=False)
        else:
            df.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
        return True
    except Exception as e:
        print(f"Error logging history: {e}")
        return False