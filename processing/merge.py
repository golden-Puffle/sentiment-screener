import pandas as pd
from database.db import read_table

def get_merged_data(ticker):
    # Load prices
    prices = read_table("stock_prices")
    prices = prices[prices['ticker'] == ticker]
    prices['Date'] = pd.to_datetime(prices['Date'], utc=True).dt.date

    # Load sentiment, average across sources per day
    sentiment = read_table("daily_sentiment")
    sentiment = sentiment[sentiment['ticker'] == ticker]
    sentiment['date'] = pd.to_datetime(sentiment['date']).dt.date

    daily_avg = sentiment.groupby('date').agg(
        combined_sentiment=('avg_sentiment', 'mean'),
        total_mentions=('mention_count', 'sum')
    ).reset_index()

    # Merge
    merged = pd.merge(
        prices,
        daily_avg,
        left_on='Date',
        right_on='date',
        how='left'
    )
    merged['combined_sentiment'] = merged['combined_sentiment'].fillna(0)
    return merged

if __name__ == "__main__":
    df = get_merged_data("NVDA")
    print(df[['Date', 'Close', 'pct_change', 'combined_sentiment', 'total_mentions']].head(10))