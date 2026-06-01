from collectors.yfinance_news_collector import fetch_posts
from collectors.news_collector import fetch_news
from collectors.price_collector import fetch_prices
from database.db import save_dataframe
from processing.run_sentiment import run_for_ticker

def full_pipeline(ticker, company_name):
    print(f"\n=== Running full pipeline for {ticker} ===")
    save_dataframe(fetch_posts(ticker), "yfinance_news")
    save_dataframe(fetch_news(ticker, company_name), "news_headlines")
    save_dataframe(fetch_prices(ticker), "stock_prices")
    run_for_ticker(ticker)

if __name__ == "__main__":
    full_pipeline("NVDA", "Nvidia")
    full_pipeline("AAPL", "Apple")
    full_pipeline("TSLA", "Tesla")