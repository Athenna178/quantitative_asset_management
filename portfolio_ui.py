import streamlit as st
import plotly.graph_objects as go
from portfolio_engine import fetch_portfolio_data, simulate_portfolio, get_advanced_metrics

def run_portfolio_module():
    st.title("⚖️ Professional Portfolio Analyzer")
    
    # 1. Sidebar Configuration
    st.sidebar.header("Strategy Settings")
    tickers = st.sidebar.multiselect("Assets", ["AAPL", "TSLA", "BTC-USD", "GC=F", "EURUSD=X"], default=["AAPL", "BTC-USD", "GC=F"])
    freq = st.sidebar.selectbox("Rebalancing Frequency", ["None", "Monthly", "Yearly"])
    timeframe = st.sidebar.selectbox("Timeframe", ["1mo", "6mo", "1y", "2y"], index=2)

    if len(tickers) >= 3: # Project requirement: Min 3 assets
        prices, normalized = fetch_portfolio_data(tickers, period=timeframe)
        
        if prices is not None:
            # 2. Dynamic Weight Selection 
            st.subheader("Asset Allocation")
            cols = st.columns(len(tickers))
            weights = {}
            for i, col in enumerate(cols):
                w = col.number_input(f"{tickers[i]} (%)", 0, 100, 100//len(tickers))
                weights[tickers[i]] = w / 100
            
            # 3. Execution
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
            st.dataframe(metrics["Correlation"].style.background_gradient(axis=None))
            
    else:
        st.warning("Please select at least 3 assets to comply with project rules[cite: 41].")

if __name__ == "__main__":
    run_portfolio_module()