# 📈 Stock Sentiment Screener

An end-to-end financial news sentiment analysis dashboard that tracks, 
analyzes, and visualizes how news sentiment correlates with stock price movements.

## Features
- Real-time news collection from Yahoo Finance and NewsAPI
- VADER NLP sentiment analysis on financial headlines
- Single stock analysis with price + sentiment overlay
- Multi-stock comparison (up to 4 stocks, intra/inter industry)
- Sector-level sentiment breakdown
- Fear & Greed Index calculated from scratch
- Divergence detection (price vs sentiment disagreement)
- Headlines surfaced for significant price movement dates
- Statistical correlation analysis with p-value
- Designed for easy scaling (add tickers via config.py)

## Tech Stack
Python, Streamlit, Plotly, VADER NLP, yfinance, 
NewsAPI, SQLite, pandas, scipy

## Setup
1. Clone the repo
2. `python -m venv venv`
3. `venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. Create `.env`: `NEWS_API_KEY=your_key_here`
6. `python main.py`
7. `streamlit run app.py`

## Architecture