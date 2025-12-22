import streamlit as st
import plotly.graph_objects as go
from portfolio_engine import fetch_portfolio_data, simulate_portfolio, get_advanced_metrics

def run_portfolio_module():
    st.title("Professional Portfolio Analyzer")
    
    # 1. Sidebar Configuration
    st.sidebar.header("Strategy Settings")
    tickers = st.sidebar.multiselect(
        "Assets", 
        ["AAPL", "TSLA", "BTC-USD", "GC=F", "EURUSD=X"], 
        default=["AAPL", "BTC-USD", "GC=F"]
    )
    
    # New Checkbox for Equal Weights Allocation 
    equal_weight_active = st.sidebar.checkbox("Use Equal Weights", value=True)
    
    freq = st.sidebar.selectbox("Rebalancing Frequency", ["None", "Monthly", "Yearly"])
    timeframe = st.sidebar.selectbox("Timeframe", ["1mo", "6mo", "1y", "2y"], index=2)

    if len(tickers) >= 3: 
        prices, normalized = fetch_portfolio_data(tickers, period=timeframe)
        
        if prices is not None:
            # 2. Dynamic Weight Selection 
            st.subheader("Asset Allocation")
            cols = st.columns(len(tickers))
            weights = {}
            
            # Calculate automatic equal weight value
            auto_w = float(100.0 / len(tickers))
            
            for i, col in enumerate(cols):
                # If equal weight is active, inputs are disabled and set to the auto value
                w = col.number_input(
                    f"{tickers[i]} (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=auto_w if equal_weight_active else auto_w, 
                    step=1.0,
                    format="%.2f",
                    disabled=equal_weight_active # Prevents manual changes when equal weight is toggled ON
                )
                weights[tickers[i]] = w / 100

            # Calculate total for validation
            total_weight = round(sum(weights.values()) * 100, 2)

            # 3. Validation and Execution
            if not equal_weight_active and total_weight != 100.0:
                st.error(f"**Allocation Error:** Total sum must be 100%. Current: **{total_weight}%**")
            else:
                if equal_weight_active:
                    st.success(f"Equal weighting applied: {auto_w:.2f}% per asset.")
                
                # Run the simulation
                portfolio_ts = simulate_portfolio(prices, normalized, weights, freq)
                metrics = get_advanced_metrics(prices, portfolio_ts, weights)

                # 4. Main Chart
                fig = go.Figure()
                for t in tickers:
                    fig.add_trace(go.Scatter(x=normalized.index, y=normalized[t], name=t, line=dict(dash='dot', width=1)))
                fig.add_trace(go.Scatter(x=portfolio_ts.index, y=portfolio_ts, name="PORTFOLIO", line=dict(width=4, color='gold')))
                
                fig.update_layout(title="Cumulative Performance (Base 100)", yaxis_title="Relative Value")
                st.plotly_chart(fig, use_container_width=True)

                # 5. Metrics Display
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                m2.metric("Portfolio Volatility", f"{metrics['Portfolio Vol']:.2%}")
                m3.metric("Diversification Benefit", f"{metrics['Diversification Benefit']:.2%}")

                st.subheader("Correlation Matrix")
                st.dataframe(metrics["Correlation"], use_container_width=True)
            
    else:
        st.warning("Please select at least 3 assets to comply with project rules[cite: 41].")

if __name__ == "__main__":
    run_portfolio_module()
