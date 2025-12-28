# Professional Quantitative Portfolio Analyzer

## Project Overview

 This project implements a professional-grade interactive dashboard designed for a quantitative research team in Paris.  The platform continuously retrieves real-time financial data, executes quantitative strategies, and provides portfolio simulations.

 The application is deployed on a **Linux Virtual Machine**, ensuring 24/7 availability with automated data reporting via Cron jobs.

### Key Objectives
*  **Real-time Analysis:** Fetching market data updates every 5 minutes.
*  **Backtesting:** Simulating trading strategies on historical data.
*  **Automation:** Generating daily volatility and drawdown reports automatically.
*  **Collaboration:** Developed using a strict Git flow with separate modules for Single Asset and Portfolio analysis.

---

## Architecture & Features

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

## Automation & Reporting
The system features a robust automated reporting pipeline that operates independently of the web interface.

### Daily Quantitative Report
A standalone automation script, report_generator.py, is executed daily at 12:00 PM via a Linux Cron job.

**State Persistence:** The script reads asset_config_a.json and portfolio_config.json to retrieve the user's latest saved strategies and tickers.

**Cross-Module Execution:** It reuses the core logic from both engine.py (Quant A) and portfolio_engine.py (Quant B) to ensure metric consistency.

**Output:** Generates a timestamped .txt report containing:

**Quant A:** Strategy performance, Sharpe Ratio, and Max Drawdown for the selected asset.

**Quant B:** Portfolio total return, volatility, and diversification benefits.

### Server Configuration
To maintain this automation on the Linux VM, the following crontab configuration is used:

0 12 * * * cd $HOME/quantitative_asset_management && /usr/bin/python3 report_generator.py >> cron_log.txt 2>&1

Ps : The script is designed to be case-insensitive and handles missing configuration files gracefully by skipping the respective module instead of crashing.
