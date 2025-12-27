import streamlit as st

# 1. Attempt to import Quant B (already exists)
try:
    from quant_b_portfolio.portfolio_ui import run_portfolio_module
    QUANT_B_AVAILABLE = True
except ImportError:
    QUANT_B_AVAILABLE = False

# 2. Attempt to import Quant A (may be missing)
try:
    from quant_a_single_asset.ui import run_single_asset_module
    QUANT_A_AVAILABLE = True
except ImportError:
    QUANT_A_AVAILABLE = False

# --- Page Configuration ---
st.set_page_config(
    layout="wide", 
    page_title="Finance Quant Dashboard"
)

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
selection = st.sidebar.radio(
    "Go to:", 
    ["Portfolio Management (Quant B)", "Single Asset Analysis (Quant A)"]
)

# --- Main Logic ---
if selection == "Portfolio Management (Quant B)":
    if QUANT_B_AVAILABLE:
        run_portfolio_module()
    else:
        st.error("Error: Portfolio module files not found in 'quant_b_portfolio' folder.")

elif selection == "Single Asset Analysis (Quant A)":
    if QUANT_A_AVAILABLE:
        run_single_asset_module()
    else:
        # User-friendly message if the folder/module isn't there yet
        st.info("### 🚧 Under Construction")
        st.write("The **Single Asset Analysis (Quant A)** module is currently being developed and will be available soon.")
        st.markdown("---")
        st.subheader("Upcoming Features:")
        st.write("* Real-time price tracking for individual stocks.")
        st.write("* Moving Average Crossover backtesting.")
        st.write("* Daily volatility and drawdown reports.")