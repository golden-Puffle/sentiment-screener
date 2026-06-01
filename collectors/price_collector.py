import yfinance as yf
import pandas as pd

def fetch_prices(ticker, period="1mo"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df['ticker'] = ticker.upper()
    df['pct_change'] = df['Close'].pct_change() * 100
    df.reset_index(inplace=True)
    return df

if __name__ == "__main__":
    df = fetch_prices("NVDA")
    print(df.head())