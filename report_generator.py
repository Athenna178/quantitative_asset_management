import os
import json
from datetime import datetime

# Import Quant A logic
try:
    from quant_a_single_asset.engine import fetch_asset_data, apply_strategy, compute_performance_metrics
    QUANT_A_READY = True
except ImportError:
    QUANT_A_READY = False

# Import Quant B logic
from quant_b_portfolio.portfolio_engine import fetch_portfolio_data, simulate_portfolio, get_advanced_metrics
from quant_b_portfolio.data_manager import load_config as load_config_b

# Paths to your config files
CONFIG_A_PATH = "asset_config_a.json"

def generate_report():
    report_lines = [f"=== DAILY QUANT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')} ===", ""]

    # --- PART 1: QUANT A (Single Asset) ---
    if QUANT_A_READY and os.path.exists(CONFIG_A_PATH):
        try:
            with open(CONFIG_A_PATH, "r") as f:
                conf_a = json.load(f)
            
            # Case-insensitivity and data fetching
            ticker = conf_a.get("ticker", "BTC-USD").upper()
            strat_type = conf_a.get("strategy", "Buy and Hold")
            params = conf_a.get("params", {})
            
            prices = fetch_asset_data(ticker)
            if prices is not None:
                strat_ts = apply_strategy(prices, strat_type, params)
                metrics = compute_performance_metrics(strat_ts)
                
                report_lines.append(f"[QUANT A: {ticker}]")
                report_lines.append(f"Strategy: {strat_type}")
                report_lines.append(f"Total Return: {metrics['Total Return']:.2%}")
                report_lines.append(f"Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}")
                report_lines.append(f"Max Drawdown: {metrics['Max Drawdown']:.2%}")
                report_lines.append("-" * 30)
        except Exception as e:
            report_lines.append(f"[QUANT A ERROR]: {str(e)}")
    else:
        report_lines.append("[QUANT A]: No configuration found or module missing. Skipping.")

    # --- PART 2: QUANT B (Portfolio) ---
    conf_b = load_config_b()
    if conf_b:
        try:
            tickers = [t.upper() for t in conf_b.get("tickers", [])]
            weights = conf_b.get("weights", {})
            freq = conf_b.get("freq", "None")
            timeframe = conf_b.get("timeframe", "1y")
            
            prices, normalized = fetch_portfolio_data(tickers, period=timeframe)
            if prices is not None:
                # Re-calculate weights if equal_weights was active
                if conf_b.get("equal_weights"):
                    final_weights = {t: 1.0/len(tickers) for t in tickers}
                else:
                    # Ensure weight keys match uppercase tickers
                    final_weights = {t.upper(): w for t, w in weights.items()}
                
                portfolio_ts = simulate_portfolio(prices, normalized, final_weights, freq)
                metrics = get_advanced_metrics(prices, portfolio_ts, final_weights)
                
                report_lines.append(f"[QUANT B: PORTFOLIO]")
                report_lines.append(f"Assets: {', '.join(tickers)}")
                report_lines.append(f"Total Return: {metrics['Total Return']:.2%}")
                report_lines.append(f"Portfolio Volatility: {metrics['Portfolio Vol']:.2%}")
                report_lines.append(f"Diversification Benefit: {metrics['Diversification Benefit']:.2%}")
                report_lines.append("-" * 30)
        except Exception as e:
            report_lines.append(f"[QUANT B ERROR]: {str(e)}")
    else:
        report_lines.append("[QUANT B]: No portfolio configuration found.")

    # --- SAVE REPORT ---
    report_content = "\n".join(report_lines)
    filename = f"report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w") as f:
        f.write(report_content)
    print(f"Report generated: {filename}")

if __name__ == "__main__":
    generate_report()