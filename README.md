# 📈 Stock Sentiment Screener

A full-stack data pipeline and interactive dashboard that tracks financial news sentiment across 12 stocks and correlates it with real stock price movements. Built entirely in Python, this project collects live financial news from Yahoo Finance and NewsAPI, runs NLP sentiment analysis using the VADER algorithm, stores everything in a local SQLite database, and visualizes it all through a multi-page Streamlit dashboard with interactive Plotly charts.

---

## 🌟 Features

### 📊 Single Stock Analysis
- Interactive closing price chart over the last 30 days
- Daily sentiment score chart with green/red color coding
- Overlay chart showing price and sentiment on the same graph
- Pearson correlation coefficient with p-value measuring whether sentiment predicts next-day price movement
- Automatic detection of significant price moves (>2%) with nearby headlines surfaced as possible explanations

### ⚖️ Multi-Stock Comparison
- Compare up to 4 stocks simultaneously
- Normalized price chart (all stocks start at 100) for fair % performance comparison regardless of absolute price
- Side-by-side sentiment score overlay across all selected stocks
- Summary table with 30-day return, average sentiment, and sentiment label per stock
- Preset industry groups (AI Chips, Big Tech, EV) for instant intra-industry comparison
- Custom selection mode for cross-industry comparisons

### 🏭 Sector Overview
- Fear & Greed Index calculated from scratch using average sentiment across all tracked stocks, displayed as an interactive gauge from 0 (Extreme Fear) to 100 (Extreme Greed)
- Sector-level sentiment breakdown showing which industries have the most positive or negative news coverage
- Divergence detection that flags stocks where price and sentiment are moving in opposite directions — a signal that analysts actively look for

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data Collection | yfinance, NewsAPI | Free APIs with reliable financial data |
| NLP | VADER Sentiment | Built for short text, no API cost, explainable scores |
| Storage | SQLite | Lightweight, zero setup, perfect for single-user scale |
| Data Processing | pandas, scipy | Industry standard for tabular data and statistics |
| Dashboard | Streamlit | Python-native, fast to build, free deployment |
| Charts | Plotly | Interactive charts with hover, zoom, and dual-axis support |
| Environment | python-dotenv, venv | Professional secrets management and dependency isolation |

---

## 📁 Project Structure
sentiment_screener/
├── app.py                          # Main entry point
├── main.py                         # Full data pipeline runner
├── config.py                       # All settings (tickers, thresholds, colors)
├── run_daily.bat                   # Windows automation script
├── requirements.txt
├── .env                            # API keys (not committed to git)
├── .gitignore
│
├── collectors/
│   ├── yfinance_news_collector.py  # Fetches news from Yahoo Finance
│   ├── news_collector.py           # Fetches headlines from NewsAPI
│   └── price_collector.py          # Fetches OHLCV price data
│
├── processing/
│   ├── text_cleaner.py             # Removes URLs and noise from text
│   ├── sentiment_analyzer.py       # VADER scoring and daily aggregation
│   ├── run_sentiment.py            # Runs sentiment pipeline for a ticker
│   ├── merge.py                    # Joins sentiment and price data
│   └── correlation.py              # Pearson correlation with p-value
│
├── database/
│   └── db.py                       # SQLite read/write helpers
│
├── pages/
│   ├── 1_Single_Stock.py           # Single ticker analysis page
│   ├── 2_Comparison.py             # Multi-stock comparison page
│   └── 3_Sector_Overview.py        # Sector sentiment and Fear & Greed
│
└── data/
└── screener.db                 # SQLite database (not committed to git)

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A free [NewsAPI](https://newsapi.org) account

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/golden-Puffle/sentiment-screener.git
cd sentiment-screener
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your API key**

Create a `.env` file in the root folder:
NEWS_API_KEY=your_newsapi_key_here

**5. Run the data pipeline**
```bash
python main.py
```
This collects news and price data for all 12 tracked stocks. Takes about 2 minutes on first run.

**6. Launch the dashboard**
```bash
streamlit run app.py
```

---

## 📈 How It Works
Yahoo Finance ──►
Text Cleaning → VADER Scoring → Daily Aggregation
NewsAPI       ──►                                        │
▼
yfinance Prices ──────────────────────────────► Merge with Sentiment
│
▼
Streamlit Dashboard
(Charts, Correlation, Alerts)

1. **Collection** — News articles and stock prices are fetched from two sources and saved to SQLite
2. **Cleaning** — URLs and noise are stripped from article text
3. **Scoring** — VADER assigns each article a compound sentiment score from -1 (very negative) to +1 (very positive)
4. **Aggregation** — Scores are averaged per day per ticker
5. **Merging** — Daily sentiment is joined with price data on date
6. **Visualization** — The dashboard renders charts, detects patterns, and surfaces insights

---

## 🔧 Configuration & Scaling

All project settings live in `config.py`. To scale the project up, only this file needs to change:

```python
MAX_COMPARISON_STOCKS = 4    # change to 10 to allow more simultaneous comparisons

ALL_TICKERS = {
    "NVDA": "Nvidia",        # add any ticker here to start tracking it
    "AAPL": "Apple",
    ...
}
```

Adding a new ticker requires exactly one line in `config.py`. No other files need to be modified.

---

## ⚠️ Known Limitations & Honest Observations

- **NewsAPI free tier** is limited to 30 days of history, which constrains the correlation analysis. Running the daily automation script over several weeks builds up more meaningful data
- **Headlines do not always explain price moves** — stock prices can lag news by days or weeks due to delayed market reactions, macro policy effects, or sentiment already being priced in. The headline explainer feature surfaces possible contributing factors, not guaranteed causes
- **Correlation significance** — with 30 days of data, the p-value will often be above 0.05, meaning the correlation may not be statistically significant. This is an honest finding rather than a flaw — more data improves reliability
- **VADER limitations** — VADER is a rule-based model that may misread financial sarcasm or complex context. A transformer-based model like FinBERT would improve accuracy at the cost of API fees

---

## 🚀 Future Improvements

- [ ] Migrate to Supabase PostgreSQL for cloud-hosted persistent storage
- [ ] Replace VADER with FinBERT for finance-specific NLP
- [ ] Add email/Telegram alerts when divergence is detected
- [ ] Expand to 50+ tickers with sector auto-classification
- [ ] Add options chain data (implied volatility as a fear indicator)
- [ ] Build a backtesting module to formally test sentiment-based trading signals

---

## 📄 License

MIT License — feel free to use, modify, and distribute this project.