import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_TICKERS, STOCK_GROUPS, STOCK_COLORS, MAX_COMPARISON_STOCKS
from processing.merge import get_merged_data

st.title("⚖️ Stock Comparison")

# --- Stock selection ---
st.subheader("Select Stocks to Compare")

mode = st.radio("Selection mode:", ["Preset Groups", "Custom Selection"], horizontal=True)

if mode == "Preset Groups":
    group_name = st.selectbox("Choose a group:", 
                               [g for g in STOCK_GROUPS.keys() if g != "Custom"])
    selected_tickers = STOCK_GROUPS[group_name][:MAX_COMPARISON_STOCKS]
    st.info(f"Comparing: {', '.join(selected_tickers)}")
else:
    selected_tickers = st.multiselect(
        f"Select up to {MAX_COMPARISON_STOCKS} stocks:",
        list(ALL_TICKERS.keys()),
        max_selections=MAX_COMPARISON_STOCKS,
        default=["NVDA", "AMD"]
    )

if len(selected_tickers) < 2:
    st.warning("Please select at least 2 stocks to compare.")
    st.stop()

# --- Load data for all selected tickers ---
all_data = {}
for ticker in selected_tickers:
    df = get_merged_data(ticker)
    if not df.empty:
        all_data[ticker] = df

if len(all_data) < 2:
    st.warning("Not enough data. Run main.py for these tickers first.")
    st.stop()

st.markdown("---")

# --- Normalized price comparison ---
st.subheader("Price Performance (Normalized to 100)")
st.caption("All stocks start at 100 so you can compare % performance regardless of absolute price")

fig_price = go.Figure()
for i, (ticker, df) in enumerate(all_data.items()):
    normalized = (df['Close'] / df['Close'].iloc[0]) * 100
    fig_price.add_trace(go.Scatter(
        x=df['Date'], y=normalized,
        mode='lines', name=ticker,
        line=dict(color=STOCK_COLORS[i], width=2)
    ))

fig_price.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.3)
fig_price.update_layout(
    xaxis_title="Date", yaxis_title="Normalized Price",
    hovermode="x unified", height=400,
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_price, use_container_width=True)

# --- Sentiment comparison ---
st.subheader("Sentiment Score Comparison")

fig_sentiment = go.Figure()
for i, (ticker, df) in enumerate(all_data.items()):
    fig_sentiment.add_trace(go.Scatter(
        x=df['Date'], y=df['combined_sentiment'],
        mode='lines+markers', name=ticker,
        line=dict(color=STOCK_COLORS[i], width=2)
    ))

fig_sentiment.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.4)
fig_sentiment.update_layout(
    xaxis_title="Date", yaxis_title="Sentiment Score",
    hovermode="x unified", height=350,
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_sentiment, use_container_width=True)

# --- Summary metrics table ---
st.subheader("Summary Comparison")

summary_rows = []
for ticker, df in all_data.items():
    first = df['Close'].iloc[0]
    last = df['Close'].iloc[-1]
    change = ((last - first) / first) * 100
    avg_sentiment = df['combined_sentiment'].mean()
    
    summary_rows.append({
        "Ticker": ticker,
        "Start Price": f"${first:.2f}",
        "Current Price": f"${last:.2f}",
        "30D Change": f"{change:+.2f}%",
        "Avg Sentiment": f"{avg_sentiment:.3f}",
        "Sentiment Label": "Positive 🟢" if avg_sentiment > 0.05 
                          else "Negative 🔴" if avg_sentiment < -0.05 
                          else "Neutral ⚪"
    })

st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

# --- Divergence detector ---
st.subheader("⚡ Divergence Detection")
st.caption("Flags stocks where price and sentiment are moving in opposite directions")

for ticker, df in all_data.items():
    if len(df) < 5:
        continue

    recent = df.tail(5)
    price_trend = recent['Close'].iloc[-1] - recent['Close'].iloc[0]
    sentiment_trend = recent['combined_sentiment'].iloc[-1] - recent['combined_sentiment'].iloc[0]

    # Divergence = price up but sentiment down, or vice versa
    if price_trend > 0 and sentiment_trend < -0.1:
        st.warning(f"⚠️ **{ticker}**: Price trending UP but sentiment trending DOWN — "
                  f"news may not support current price momentum")
    elif price_trend < 0 and sentiment_trend > 0.1:
        st.info(f"💡 **{ticker}**: Price trending DOWN but sentiment trending UP — "
               f"news may be more positive than price suggests")