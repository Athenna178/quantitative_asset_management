import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from portfolio_engine import fetch_portfolio_data, simulate_portfolio, get_advanced_metrics
from streamlit_autorefresh import st_autorefresh # for the 5-minute refresh 
from data_manager import save_config, load_config, log_daily_performance

def run_portfolio_module():
    # Auto-refresh every 5 minutes = 300 seconds
    st_autorefresh(interval=5 * 60 * 1000, key="datarefresh")

    # --- Load Saved Configuration ---
    saved_config = load_config()
    
    # Defaults (if no save file exists)
    default_tickers = ["MC.PA", "BTC-USD", "OR.PA"]
    default_freq = "None"
    default_timeframe = "1y"
    default_equal = True
    saved_weights = {}

    if saved_config:
        default_tickers = saved_config.get("tickers", default_tickers)
        default_freq = saved_config.get("freq", default_freq)
        default_timeframe = saved_config.get("timeframe", default_timeframe)
        default_equal = saved_config.get("equal_weights", default_equal)
        saved_weights = saved_config.get("weights", {})

    st.title("Professional Portfolio Analyzer")

    # 1. Asset Dictionaries Configuration
    # Shuffled CAC 40 and Top 50 Cryptos for a diverse selection
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
        ]
    }

    # Flatten list for the multiselect widget
    all_tickers = assets_dict["CAC 40 (France)"] + assets_dict["Crypto 50 (Global)"]

    # --- CSS Injection for Tag Coloring ---
    # French Stocks = Blue (#1f77b4), Cryptos = Red (#d62728)
    css_styles = "<style>"
    for ticker in assets_dict["CAC 40 (France)"]:
        css_styles += f'span[data-baseweb="tag"]:has(span[title*="{ticker}"]) {{ background-color: #1f77b4 !important; color: white !important; }}'
    for ticker in assets_dict["Crypto 50 (Global)"]:
        css_styles += f'span[data-baseweb="tag"]:has(span[title*="{ticker}"]) {{ background-color: #d62728 !important; color: white !important; }}'
    css_styles += "</style>"
    st.markdown(css_styles, unsafe_allow_html=True)

    # 2. Sidebar Configuration
    st.sidebar.header("Strategy Settings")
    
    # Helper to find index for selectbox defaults
    freq_options = ["None", "Monthly", "Yearly"]
    try:
        freq_index = freq_options.index(default_freq)
    except ValueError:
        freq_index = 0

    time_options = ["1mo", "6mo", "1y", "2y"]
    try:
        time_index = time_options.index(default_timeframe)
    except ValueError:
        time_index = 2

    tickers = st.sidebar.multiselect(
        "Assets Selection", 
        all_tickers, 
        default=default_tickers
    )
    
    equal_weight_active = st.sidebar.checkbox("Use Equal Weights", value=default_equal)
    freq = st.sidebar.selectbox("Rebalancing Frequency", freq_options, index=freq_index)
    timeframe = st.sidebar.selectbox("Timeframe", time_options, index=time_index)

    # --- SAVE BUTTON ---
    if st.sidebar.button("Save Configuration"):
        # We save the weights currently in the user_weights dictionary (captured later in code)
        # Note: If equal_weight is active, specific weights matter less, but we save them anyway.
        current_weights_to_save = st.session_state.get('current_user_weights', {})
        if save_config(tickers, current_weights_to_save, freq, timeframe, equal_weight_active):
            st.sidebar.success("Configuration saved successfully!")

    if len(tickers) >= 3: 
        prices, normalized = fetch_portfolio_data(tickers, period=timeframe)
        
        if prices is not None:
            # 3. Dynamic Weight Selection 
            st.subheader("Asset Allocation")
            cols = st.columns(len(tickers))
            user_weights = {}
            auto_w = float(100.0 / len(tickers))
            
            for i, col in enumerate(cols):
                ticker = tickers[i]
                
                # Determine default value for the input
                # If we have a saved weight for this ticker, use it. Otherwise use auto_w.
                if ticker in saved_weights and not equal_weight_active:
                    default_val = float(saved_weights[ticker] * 100)
                else:
                    default_val = auto_w

                # Input for weights
                w = col.number_input(
                    f"{ticker} (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=default_val, 
                    step=0.01,
                    format="%.2f",
                    disabled=equal_weight_active,
                    key=f"weight_{ticker}" 
                )
                user_weights[ticker] = w / 100
                
                # --- Project Requirement: Display current value  ---
                current_price = prices[ticker].iloc[-1]
                col.write(f"Price: **{current_price:,.2f}**")

            # Store weights in session state for the Save button to access
            st.session_state['current_user_weights'] = user_weights

            # Calculation of the total sum entered by the user
            total_sum = sum(user_weights.values())

            # 4. Validation with Tolerance (0.99 to 1.01)
            if not equal_weight_active and not (0.99 <= total_sum <= 1.01):
                st.error(f"**Allocation Error:** Total sum must be between 99% and 101%. Current: **{total_sum*100:.2f}%**")
            else:
                # NORMALIZATION: Force the total to be exactly 1.0 for math precision
                final_weights = {k: v / total_sum for k, v in user_weights.items()}
                
                if equal_weight_active:
                    st.success(f"Equal weighting applied: {100/len(tickers):.2f}% per asset.")
                else:
                    st.success(f"Weights normalized to 100% for calculation accuracy.")
                
                # Run the simulation with final normalized weights
                portfolio_ts = simulate_portfolio(prices, normalized, final_weights, freq)
                metrics = get_advanced_metrics(prices, portfolio_ts, final_weights)
                st.caption("🔄 Data automatically refreshes every 5 minutes")
                
                # --- REPORTING BUTTONS ---
                c1, c2 = st.columns([1, 3])
                with c1:
                    if st.button("Generate Daily Report"):
                        if log_daily_performance(metrics):
                            st.success("Report logged.")
                
                with c2:
                    if st.checkbox("Show Report History"):
                        if os.path.exists("portfolio_history.csv"):
                            history_df = pd.read_csv("portfolio_history.csv")
                            st.dataframe(history_df.sort_index(ascending=False), use_container_width=True)
                        else:
                            st.info("No history found yet.")

                # 5. Performance Chart
                fig = go.Figure()
                for t in tickers:
                    fig.add_trace(go.Scatter(x=normalized.index, y=normalized[t], name=t, line=dict(dash='dot', width=1)))
                fig.add_trace(go.Scatter(x=portfolio_ts.index, y=portfolio_ts, name="PORTFOLIO", line=dict(width=4, color='gold')))
                
                fig.update_layout(
                    title="Cumulative Performance (Base 100)", 
                    yaxis_title="Relative Value", 
                    template="plotly_dark",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                # 6. Metrics Display
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                m2.metric("Portfolio Volatility", f"{metrics['Portfolio Vol']:.2%}")
                m3.metric("Diversification Benefit", f"{metrics['Diversification Benefit']:.2%}")

                st.subheader("Correlation Matrix")
                corr_matrix = metrics["Correlation"]
                heatmap_fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.index,
                    colorscale='RdBu_r',
                    zmin=-1, zmax=1,
                    text=corr_matrix.round(2).values,
                    texttemplate="%{text}",
                    showscale=True
                ))
                heatmap_fig.update_layout(
                    template="plotly_dark",
                    yaxis_autorange='reversed'
                )
                st.plotly_chart(heatmap_fig, use_container_width=True)        
    else:
        st.warning("Please select at least 3 assets to comply with project rules.")

if __name__ == "__main__":
    run_portfolio_module()