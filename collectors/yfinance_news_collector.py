import yfinance as yf
import pandas as pd #for data format
from datetime import datetime

def fetch_posts(ticker, limit=100):
    stock = yf.Ticker(ticker)
    news = stock.news

    posts = []
    for article in news[:limit]:
        content = article.get("content", {})
        pub_date = content.get("pubDate", None)

        # Handle date parsing safely
        try:
            if isinstance(pub_date, (int, float)):
                created_at = datetime.fromtimestamp(pub_date)
            elif isinstance(pub_date, str):
                created_at = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            else:
                created_at = datetime.now()
        except:
            created_at = datetime.now()

        posts.append({
            "ticker": ticker.upper(),
            "source": "yfinance_news",
            "title": content.get("title", ""),
            "body": content.get("summary", ""),
            "score": 1,
            "num_comments": 0,
            "created_at": created_at,
            "url": content.get("canonicalUrl", {}).get("url", "")
        })

    return pd.DataFrame(posts)

if __name__ == "__main__":
    df = fetch_posts("NVDA")
    print(df.head())
    print(f"Fetched {len(df)} articles")