from database.db import read_table, save_dataframe
from processing.sentiment_analyzer import (
    analyze_yfinance_news,
    analyze_news_headlines,
    compute_daily_sentiment
)

def run_for_ticker(ticker):
    print(f"\nRunning sentiment for {ticker}...")

    # --- yfinance news ---
    yf_df = read_table("yfinance_news")
    yf_df = yf_df[yf_df['ticker'] == ticker]

    if not yf_df.empty:
        yf_scored = analyze_yfinance_news(yf_df)
        yf_daily = compute_daily_sentiment(
            yf_scored,
            source='yfinance_news',
            date_col='created_at'
        )
        save_dataframe(yf_daily, "daily_sentiment")
        print(f"yfinance news: {len(yf_daily)} daily rows saved")

    # --- NewsAPI ---
    news_df = read_table("news_headlines")
    news_df = news_df[news_df['ticker'] == ticker]

    if not news_df.empty:
        news_scored = analyze_news_headlines(news_df)
        news_daily = compute_daily_sentiment(
            news_scored,
            source='newsapi',
            date_col='published_at'
        )
        save_dataframe(news_daily, "daily_sentiment")
        print(f"NewsAPI: {len(news_daily)} daily rows saved")

if __name__ == "__main__":
    run_for_ticker("NVDA")
    run_for_ticker("AAPL")
    run_for_ticker("TSLA")