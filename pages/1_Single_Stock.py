import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_TICKERS, POSITIVE_THRESHOLD, NEGATIVE_THRESHOLD, BIG_MOVE_THRESHOLD
from processing.merge import get_merged_data
from processing.correlation import compute_correlation
from database.db import read_table

st.title("📊 Single Stock Analysis")

ticker = st.selectbox("Select a stock:", list(ALL_TICKERS.keys()))
company_name = ALL_TICKERS[ticker]

df = get_merged_data(ticker)

if df.empty:
    st.warning(f"No data found for {ticker}. Run main.py first.")
    st.stop()

# --- Summary metrics ---
st.subheader(f"{company_name} ({ticker}) — 30 Day Summary")

first_price = df['Close'].iloc[0]
last_price = df['Close'].iloc[-1]
overall_change = ((last_price - first_price) / first_price) * 100
avg_sentiment = df['combined_sentiment'].mean()

# Color code the 30 day change
if overall_change > 0:
    delta_color = "normal"      # green
elif overall_change < 0:
    delta_color = "inverse"     # red
else:
    delta_color = "off"         # white/grey

col1, col2, col3, col4 = st.columns(4)
col1.metric("Start Price", f"${first_price:.2f}")
col2.metric("Current Price", f"${last_price:.2f}")
col3.metric(
    "30 Day Change",
    f"{overall_change:+.2f}%",
    delta=f"{overall_change:+.2f}%",
    delta_color=delta_color
)
col4.metric(
    "Avg Sentiment",
    f"{avg_sentiment:.3f}",
    help="Sentiment score ranges from -1 (very negative news) to +1 (very positive news). "
         "Above 0.05 = Positive 🟢, Below -0.05 = Negative 🔴, Between = Neutral ⚪. "
         "Calculated using VADER NLP on financial headlines."
)

st.markdown("---")

# --- Price chart (deduplicated) ---
st.subheader("Closing Price")
df_plot = df.drop_duplicates(subset=['Date'])
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=df_plot['Date'], y=df_plot['Close'],
    mode='lines', name='Close Price',
    line=dict(color='#00C805', width=2)
))
fig_price.update_layout(
    xaxis_title="Date", yaxis_title="Price (USD)",
    hovermode="x unified", height=350,
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_price, use_container_width=True)

# --- Sentiment chart ---
st.subheader("Daily News Sentiment")
colors = ['#00C805' if s >= POSITIVE_THRESHOLD
          else '#FF4444' if s <= NEGATIVE_THRESHOLD
          else '#888888'
          for s in df_plot['combined_sentiment']]

fig_sentiment = go.Figure()
fig_sentiment.add_trace(go.Bar(
    x=df_plot['Date'], y=df_plot['combined_sentiment'],
    name='Sentiment', marker_color=colors
))
fig_sentiment.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.4)
fig_sentiment.update_layout(
    xaxis_title="Date", yaxis_title="Sentiment Score",
    height=300,
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_sentiment, use_container_width=True)

# --- Overlay chart ---
st.subheader("Sentiment vs Price (Overlay)")
fig_overlay = go.Figure()
fig_overlay.add_trace(go.Scatter(
    x=df_plot['Date'], y=df_plot['Close'],
    name='Price', line=dict(color='#00C805'), yaxis='y1'
))
fig_overlay.add_trace(go.Bar(
    x=df_plot['Date'], y=df_plot['combined_sentiment'],
    name='Sentiment', marker_color='rgba(100,149,237,0.5)', yaxis='y2'
))
fig_overlay.update_layout(
    yaxis=dict(title='Price (USD)', side='left'),
    yaxis2=dict(title='Sentiment', side='right', overlaying='y'),
    hovermode='x unified', height=400,
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_overlay, use_container_width=True)

# --- Correlation with hover tooltips ---
st.subheader("Sentiment → Next Day Price Correlation")

col1, col2 = st.columns(2)
col1.markdown("**What is Correlation Coefficient?**")
col1.caption(
    "Measures how strongly sentiment today predicts price change tomorrow. "
    "Ranges from -1 to +1. "
    "Above 0.3 = moderate positive relationship. "
    "Below -0.3 = moderate inverse relationship. "
    "Near 0 = no linear relationship."
)
col2.markdown("**What is P-value?**")
col2.caption(
    "Measures statistical significance. "
    "Below 0.05 = result is unlikely to be random chance (significant). "
    "Above 0.05 = result may just be noise (needs more data). "
    "With 30 days of data, p-value is often above 0.05 — this improves as data accumulates."
)

corr, pvalue, corr_df = compute_correlation(df)

if corr is not None:
    col1, col2 = st.columns(2)
    col1.metric("Correlation Coefficient", corr)
    col2.metric("P-value", pvalue)

    if pvalue < 0.05:
        st.success("✅ Statistically significant correlation found")
    else:
        st.info("ℹ️ Correlation not statistically significant yet. Collect more days for stronger results.")

    fig_scatter = px.scatter(
        corr_df, x='combined_sentiment', y='next_day_change',
        trendline='ols',
        labels={
            'combined_sentiment': 'Sentiment Score (Today)',
            'next_day_change': 'Price Change % (Next Day)'
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- Headline explainer ---
st.subheader("📰 Key Price Movements & Possible News Drivers")
st.caption("⚠️ Headlines shown are from the same date range as the price move. Stock prices can lag news by days or weeks — these are possible contributing factors, not guaranteed causes.")

big_moves = df[df['pct_change'].abs() >= BIG_MOVE_THRESHOLD].copy()
big_moves = big_moves.sort_values('pct_change', key=abs, ascending=False).head(5)

if big_moves.empty:
    st.info("No significant price moves found in this period.")
else:
    all_news = read_table("news_headlines")
    all_news = all_news[all_news['ticker'] == ticker]
    all_news['published_at'] = pd.to_datetime(all_news['published_at'], utc=True)

    from processing.sentiment_analyzer import score_text

    for _, move_row in big_moves.iterrows():
        move_date = pd.to_datetime(move_row['Date']).tz_localize('UTC')
        direction = "📈" if move_row['pct_change'] > 0 else "📉"

        with st.expander(
            f"{direction} {move_row['Date']} — {move_row['pct_change']:+.2f}% "
            f"(${move_row['Close']:.2f})"
        ):
            date_from = move_date - pd.Timedelta(days=2)
            date_to = move_date + pd.Timedelta(days=1)

            nearby_headlines = all_news[
                (all_news['published_at'] >= date_from) &
                (all_news['published_at'] <= date_to)
            ].copy()

            if nearby_headlines.empty:
                st.write("No headlines found for this date range.")
            else:
                # Rank by sentiment extremity
                nearby_headlines['sentiment'] = nearby_headlines['headline'].apply(score_text)
                nearby_headlines['sentiment_abs'] = nearby_headlines['sentiment'].abs()
                nearby_headlines = nearby_headlines.sort_values('sentiment_abs', ascending=False).head(5)

                for _, h in nearby_headlines.iterrows():
                    sentiment_label = "🟢" if h['sentiment'] > 0.05 else "🔴" if h['sentiment'] < -0.05 else "⚪"
                    st.markdown(f"{sentiment_label} **{h['headline']}** — *{h['source']}*")