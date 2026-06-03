import streamlit as st

st.set_page_config(
    page_title="Stock Sentiment Screener",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Sentiment Screener")
st.markdown("""
Analyze financial news sentiment and correlate it with stock price movements.
Use the sidebar to navigate between pages.
""")

st.info("👈 Select a page from the sidebar to get started")

col1, col2, col3 = st.columns(3)
col1.metric("Data Sources", "2", "yfinance + NewsAPI")
col2.metric("Tickers Available", "12")
col3.metric("Max Comparison", "4 stocks")