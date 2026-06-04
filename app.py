import os
import streamlit as st
from config import ALL_TICKERS

st.set_page_config(
    page_title="Stock Sentiment Screener",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Sentiment Screener")
st.markdown("Analyze financial news sentiment and correlate it with stock price movements.")

col1, col2, col3 = st.columns(3)
col1.metric("Data Sources", "2", "yfinance + NewsAPI")
col2.metric("Tickers Available", str(len(ALL_TICKERS)))
col3.metric("Max Stocks Comparable Simultaneously", "4")