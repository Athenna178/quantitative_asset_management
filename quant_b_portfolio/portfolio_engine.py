import yfinance as yf
import pandas as pd
import numpy as np

def fetch_portfolio_data(tickers, period="1y", interval="1d"):
    """
    Retrieves data, cleans it, and normalizes it to start at 100.
    """
    try:
        data = yf.download(tickers, period=period, interval=interval, auto_adjust=True)
        if data.empty: return None
        
        prices = data['Close']
        if len(tickers) == 1:
            prices = prices.to_frame(name=tickers[0])
            
        # Clean Data: Fill gaps so we don't get 'straight lines'
        prices = prices.ffill().bfill()
        
        # Normalization: Start everything at 100 for visual comparison
        normalized = (prices / prices.iloc[0]) * 100
        return prices, normalized
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def simulate_portfolio(prices, normalized_data, weights_dict, rebalance_freq="None"):
    """
    Calculates portfolio value based on weights and rebalancing rules.
    """
    # BUY AND HOLD STRATEGY
    if rebalance_freq == "None":
        portfolio_val = pd.Series(0.0, index=normalized_data.index)
        for ticker, weight in weights_dict.items():
            portfolio_val += normalized_data[ticker] * weight
        return portfolio_val

    # REBALANCING STRATEGY
    else:
        returns = prices.pct_change().fillna(0)
        portfolio_val = pd.Series(100.0, index=returns.index)
        # Initial positions in dollars (starting with $100)
        current_positions = {t: 100.0 * w for t, w in weights_dict.items()}
        
        for i in range(1, len(returns.index)):
            curr_date, prev_date = returns.index[i], returns.index[i-1]
            
            # Trigger Rebalancing
            rebalance = False
            if rebalance_freq == "Monthly" and curr_date.month != prev_date.month: rebalance = True
            elif rebalance_freq == "Yearly" and curr_date.year != prev_date.year: rebalance = True
            
            if rebalance:
                total_current = sum(current_positions.values())
                current_positions = {t: total_current * w for t, w in weights_dict.items()}
            
            # Apply performance
            day_sum = 0
            for t in weights_dict.keys():
                current_positions[t] *= (1 + returns.at[curr_date, t])
                day_sum += current_positions[t]
            portfolio_val.at[curr_date] = day_sum
            
        return portfolio_val

def get_advanced_metrics(prices, portfolio_series, weights_dict):
    """
    Computes diversification effect, volatility, and correlation.
    """
    returns = prices.pct_change().dropna()
    port_rets = portfolio_series.pct_change().dropna()
    
    # Diversification Effect = (Weighted Avg Vol) - (Portfolio Vol)
    indiv_vols = returns.std() * np.sqrt(252)
    weighted_vol = sum(indiv_vols[t] * weights_dict[t] for t in weights_dict.keys())
    port_vol = port_rets.std() * np.sqrt(252)
    
    return {
        "Correlation": returns.corr(),
        "Portfolio Vol": port_vol,
        "Diversification Benefit": weighted_vol - port_vol,
        "Total Return": (portfolio_series.iloc[-1] / 100) - 1
    }