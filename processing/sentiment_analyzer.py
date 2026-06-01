from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from processing.text_cleaner import clean_text
import pandas as pd

analyzer = SentimentIntensityAnalyzer()

def score_text(text):
    cleaned = clean_text(text)
    if not cleaned:
        return None
    return analyzer.polarity_scores(cleaned)['compound']

def analyze_yfinance_news(df):
    """Score yfinance news using title + body combined"""
    df = df.copy()
    df['full_text'] = df['title'] + " " + df['body'].fillna("")
    df['sentiment_score'] = df['full_text'].apply(score_text)
    df = df.dropna(subset=['sentiment_score'])
    return df

def analyze_news_headlines(df):
    """Score NewsAPI headlines"""
    df = df.copy()
    df['sentiment_score'] = df['headline'].apply(score_text)
    df = df.dropna(subset=['sentiment_score'])
    return df

if __name__ == "__main__":
    # Quick test
    sample = pd.DataFrame({
        'title': ['NVDA is going to the moon!', 'Nvidia crashes hard'],
        'body': ['Best stock ever', 'Lost all my money'],
    })
    result = analyze_yfinance_news(sample)
    print(result[['title', 'sentiment_score']])

def compute_daily_sentiment(df, source, date_col, score_col='sentiment_score'):
    """Aggregates sentiment into a daily summary per ticker"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], utc=True).dt.date

    daily = []
    for (date, ticker), group in df.groupby([date_col, 'ticker']):
        daily.append({
            'date': date,
            'ticker': ticker,
            'source': source,
            'avg_sentiment': round(group[score_col].mean(), 4),
            'mention_count': len(group)
        })

    return pd.DataFrame(daily)