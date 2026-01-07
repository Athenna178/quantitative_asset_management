import streamlit as st
import plotly.graph_objects as go
import json
import os
from .engine import fetch_asset_data, apply_strategy, compute_performance_metrics

CONFIG_A_FILE = "asset_config_a.json"

def save_config_a(ticker, strategy, params):
    """Saves the configuration for Quant A and the future Report Generator."""
    config = {"ticker": ticker, "strategy": strategy, "params": params}
    with open(CONFIG_A_FILE, "w") as f:
        json.dump(config, f)

def load_config_a():
    """Loads the previously saved configuration."""
    if os.path.exists(CONFIG_A_FILE):
        try:
            with open(CONFIG_A_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"ticker": "MC.PA", "strategy": "Buy and Hold", "params": {}}

def run_single_asset_module():
    st.title("Single Asset Analysis (Quant A)")
    conf = load_config_a()

    # 1. Asset Dictionaries (Mirrors Quant B for consistency)
    assets_dict = {
        "CAC 40 (France)": [
            "AI.PA", "AIR.PA", "ALO.PA", "MT.AS", "AXA.PA", "BNP.PA", "EN.PA", "CAP.PA", 
            "CA.PA", "ACA.PA", "BN.PA", "DSY.PA", "ENGI.PA", "EL.PA", "ERF.PA", "RMS.PA", 
            "KER.PA", "OR.PA", "LR.PA", "MC.PA", "ML.PA", "ORA.PA", "PUB.PA", "RNO.PA", 
            "SAF.PA", "SGO.PA", "SAN.PA", "SU.PA", "GLE.PA", "STLA.PA", "STM.PA", "TEP.PA", 
            "HO.PA", "TTE.PA", "URW.AS", "VIE.PA", "VIV.PA", "WLN.PA", "DG.PA", "EDEN.PA"
        ],
        "Crypto 50 (Global)": [
            "BTC-USD", "ETH-USD", "USDT-USD", "BNB-USD", "SOL-USD", "XRP-USD", "USDC-USD", 
            "ADA-USD", "DOGE-USD", "TRX-USD", "DOT-USD", "LINK-USD", "MATIC-USD", "SHIB-USD", 
            "DAI-USD", "LTC-USD", "BCH-USD", "UNI-USD", "AVAX-USD", "XLM-USD", "ATOM-USD", 
            "XMR-USD", "ETC-USD", "FIL-USD", "HBAR-USD", "APT-USD", "NEAR-USD", "VET-USD", 
            "OP-USD", "ARB-USD", "RNDR-USD", "INJ-USD", "STX-USD", "GRT-USD", "KAS-USD", 
            "THETA-USD", "MKR-USD", "LDO-USD", "BSV-USD", "AAVE-USD", "EGLD-USD", "TIA-USD", 
            "QNT-USD", "FLOW-USD", "SUI-USD", "SEI-USD", "ALGO-USD", "FTM-USD", "GALA-USD", "DYDX-USD"
        ],
        "Manual Input": []
    }

    # --- Sidebar: Asset Selection ---
    st.sidebar.header("Asset Selection")
    
    # Determine default category for the selectbox
    default_cat = "CAC 40 (France)"
    for cat, tickers in assets_dict.items():
        if conf['ticker'] in tickers:
            default_cat = cat
            break
    
    market_cat = st.sidebar.selectbox("Market Category", list(assets_dict.keys()), index=list(assets_dict.keys()).index(default_cat))
    
    if market_cat == "Manual Input":
        ticker = st.sidebar.text_input("Enter Ticker (Yahoo Finance)", value=conf['ticker']).upper()
    else:
        available_tickers = assets_dict[market_cat]
        try:
            default_idx = available_tickers.index(conf['ticker'])
        except ValueError:
            default_idx = 0
        ticker = st.sidebar.selectbox("Select Asset", available_tickers, index=default_idx)

    # --- Sidebar: Strategy ---
    strat_list = ["Buy and Hold", "Momentum (SMA Crossover)", "RSI Strategy", "Bollinger Bands"]
    try:
        strat_idx = strat_list.index(conf['strategy'])
    except: strat_idx = 0
    strategy_type = st.sidebar.radio("Strategy", strat_list, index=strat_idx)
    
    params = {}
    if strategy_type == "Momentum (SMA Crossover)":
        params['short_window'] = st.sidebar.slider("Short SMA", 5, 50, conf['params'].get('short_window', 20))
        params['long_window'] = st.sidebar.slider("Long SMA", 20, 200, conf['params'].get('long_window', 50))
    elif strategy_type == "RSI Strategy":
        params['rsi_period'] = st.sidebar.slider("RSI Period", 5, 30, conf['params'].get('rsi_period', 14))
    elif strategy_type == "Bollinger Bands":
        params['bb_window'] = st.sidebar.slider("BB Window", 10, 50, conf['params'].get('bb_window', 20))
        params['bb_std'] = st.sidebar.slider("Std Dev", 1.0, 3.0, conf['params'].get('bb_std', 2.0))

    if st.sidebar.button("Save & Analyze"):
        save_config_a(ticker, strategy_type, params)

    # --- Calculation & Display ---
    prices = fetch_asset_data(ticker)
    
    if prices is not None:
        strategy_val = apply_strategy(prices, strategy_type, params)
        metrics = compute_performance_metrics(strategy_val)
        
        # --- Title and Asset Price ---
        st.subheader(f"Backtest {ticker}: {strategy_type}")
        current_price = prices.iloc[-1]
        st.markdown(f"#### Current Price: `{current_price:,.2f}`") 
        
        # --- Performance Chart ---
        fig = go.Figure()
        norm_p = (prices / prices.iloc[0]) * 100
        fig.add_trace(go.Scatter(x=prices.index, y=norm_p, name="Asset (Base 100)", line=dict(color='gray', dash='dot')))
        fig.add_trace(go.Scatter(x=strategy_val.index, y=strategy_val, name="Strategy Path", line=dict(color='gold', width=3)))
        
        fig.update_layout(template="plotly_dark", hovermode="x unified", margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Metrics Display ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
        m2.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
        m3.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
        m4.metric("Volatility", f"{metrics['Volatility']:.2%}")
    else:
        st.error("No data found for this ticker. Please check the symbol.")
