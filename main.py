from collectors.yfinance_news_collector import fetch_posts
from collectors.news_collector import fetch_news
from collectors.price_collector import fetch_prices
from database.db import save_dataframe

def collect_all(ticker, company_name):
    print(f"\n=== Collecting data for {ticker} ===")

    print("Fetching yfinance news...")
    yf_news_df = fetch_posts(ticker)
    if not yf_news_df.empty:
        save_dataframe(yf_news_df, "yfinance_news")

    print("Fetching NewsAPI headlines...")
    news_df = fetch_news(ticker, company_name)
    if not news_df.empty:
        save_dataframe(news_df, "news_headlines")

    print("Fetching stock prices...")
    price_df = fetch_prices(ticker)
    if not price_df.empty:
        save_dataframe(price_df, "stock_prices")

    print(f"Done for {ticker}!")

if __name__ == "__main__":
    collect_all("NVDA", "Nvidia")
    collect_all("AAPL", "Apple")
    collect_all("TSLA", "Tesla")