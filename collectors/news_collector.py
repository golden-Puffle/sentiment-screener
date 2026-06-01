from newsapi import NewsApiClient
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def fetch_news(ticker, company_name, days_back=7):
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    response = newsapi.get_everything(
        q=f"{ticker} OR {company_name}",
        from_param=from_date,
        language='en',
        sort_by='publishedAt'
    )
    articles = []
    for a in response['articles']:
        articles.append({
            "ticker": ticker.upper(),
            "headline": a['title'],
            "source": a['source']['name'],
            "published_at": a['publishedAt'],
            "url": a['url']
        })
    return pd.DataFrame(articles)

if __name__ == "__main__":
    df = fetch_news("NVDA", "Nvidia")
    print(df.head())
    print(f"Fetched {len(df)} articles")