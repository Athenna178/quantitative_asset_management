# Quantitative Asset Management Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Platform](https://img.shields.io/badge/Platform-Linux%20VM-black)
![License](https://img.shields.io/badge/License-MIT-green)

## 📖 Project Overview

 This project implements a professional-grade interactive dashboard designed for a quantitative research team in Paris.  The platform continuously retrieves real-time financial data, executes quantitative strategies, and provides portfolio simulations.

 The application is deployed on a **Linux Virtual Machine**, ensuring 24/7 availability with automated data reporting via Cron jobs.

### Key Objectives
*  **Real-time Analysis:** Fetching market data updates every 5 minutes.
*  **Backtesting:** Simulating trading strategies on historical data.
*  **Automation:** Generating daily volatility and drawdown reports automatically.
*  **Collaboration:** Developed using a strict Git flow with separate modules for Single Asset and Portfolio analysis.

---

## 🏗 Architecture & Features

 The project is divided into two core quantitative modules integrated into a single Streamlit interface.

###  1. Quant A: Univariate Analysis Module
Focused on the deep analysis of single assets (Stocks, Forex, Commodities).
*  **Real-time Ticker:** Displays current price and daily variation.
* **Strategy Backtesting:**
    *  *Buy & Hold* vs. *Momentum/Moving Average Crossover*.
    *  Customizable parameters (periodicity, window sizes).
*  **Performance Metrics:** Sharpe Ratio, Max Drawdown, Annualized Return.
*  **Visualization:** Dual-curve plotting (Raw Price vs. Strategy Cumulative Return).
*  *(Optional)* **Forecasting:** ML-based price prediction models.

###  2. Quant B: Multi-Asset Portfolio Module
 Focused on diversification and portfolio construction (minimum 3 assets).
*  **Allocation Simulation:** Custom weight distribution vs. Equal weighting.
*  **Risk Analysis:** Computation of the Correlation Matrix and Diversification Benefits.
*  **Rebalancing:** Options for Monthly or Yearly rebalancing frequencies.
*  **Benchmarking:** Visual comparison of Portfolio performance vs. Individual Assets.
