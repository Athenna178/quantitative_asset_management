import streamlit as st
from quant_a_single_asset.ui import run_single_asset_module
from quant_b_portfolio.portfolio_ui import run_portfolio_module

st.set_page_config(layout="wide", page_title="Finance Quant Dashboard")

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to:", ["Single Asset Analysis (Quant A)", "Portfolio Management (Quant B)"])

if selection == "Single Asset Analysis (Quant A)":
    run_single_asset_module()
else:
    run_portfolio_module() 
