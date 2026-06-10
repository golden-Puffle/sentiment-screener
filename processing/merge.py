import pandas as pd
from database.db import read_table

def get_merged_data(ticker):
    prices = read_table("stock_prices")
    prices = prices[prices['ticker'] == ticker]
    prices['Date'] = pd.to_datetime(prices['Date'], utc=True).dt.date
    
    # Fix duplicate rows bug
    prices = prices.drop_duplicates(subset=['Date'], keep='last')
    prices = prices.sort_values('Date').reset_index(drop=True)
    prices = prices.dropna(subset=['Close'])
    
    sentiment = read_table("daily_sentiment")
    sentiment = sentiment[sentiment['ticker'] == ticker]
    sentiment['date'] = pd.to_datetime(sentiment['date']).dt.date
    
    # Fix duplicate rows bug
    sentiment = sentiment.drop_duplicates(subset=['date'], keep='last')

    daily_avg = sentiment.groupby('date').agg(
        combined_sentiment=('avg_sentiment', 'mean'),
        total_mentions=('mention_count', 'sum')
    ).reset_index()

    merged = pd.merge(
        prices,
        daily_avg,
        left_on='Date',
        right_on='date',
        how='left'
    )
    merged['combined_sentiment'] = merged['combined_sentiment'].fillna(0)
    return merged