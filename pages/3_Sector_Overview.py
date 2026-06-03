import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STOCK_GROUPS, STOCK_COLORS
from processing.merge import get_merged_data

st.title("🏭 Sector Overview")

# --- Fear & Greed Index ---
st.subheader("Market Sentiment Index")
st.caption("Calculated from average sentiment across all tracked stocks")

all_sentiments = []
for group, tickers in STOCK_GROUPS.items():
    if group == "Custom":
        continue
    for ticker in tickers:
        df = get_merged_data(ticker)
        if not df.empty:
            avg = df['combined_sentiment'].tail(5).mean()
            all_sentiments.append(avg)

if all_sentiments:
    overall_sentiment = sum(all_sentiments) / len(all_sentiments)
    # Normalize from [-1,1] to [0,100]
    fear_greed_score = int((overall_sentiment + 1) * 50)
    fear_greed_score = max(0, min(100, fear_greed_score))

    if fear_greed_score >= 75:
        label = "Extreme Greed 🤑"
        color = "#00C805"
    elif fear_greed_score >= 55:
        label = "Greed 🟢"
        color = "#8BC34A"
    elif fear_greed_score >= 45:
        label = "Neutral ⚪"
        color = "#888888"
    elif fear_greed_score >= 25:
        label = "Fear 🔴"
        color = "#FF9800"
    else:
        label = "Extreme Fear 😱"
        color = "#FF4444"

    col1, col2 = st.columns([1, 2])
    col1.metric("Market Sentiment", f"{fear_greed_score}/100", label)

    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fear_greed_score,
        title={'text': label},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 25], 'color': '#FF4444'},
                {'range': [25, 45], 'color': '#FF9800'},
                {'range': [45, 55], 'color': '#888888'},
                {'range': [55, 75], 'color': '#8BC34A'},
                {'range': [75, 100], 'color': '#00C805'},
            ]
        }
    ))
    fig_gauge.update_layout(height=300)
    col2.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# --- Sector by sector breakdown ---
st.subheader("Sentiment by Sector")

sector_data = []
for group, tickers in STOCK_GROUPS.items():
    if group == "Custom":
        continue
    group_sentiments = []
    for ticker in tickers:
        df = get_merged_data(ticker)
        if not df.empty:
            group_sentiments.append(df['combined_sentiment'].mean())
    if group_sentiments:
        sector_data.append({
            "Sector": group,
            "Avg Sentiment": round(sum(group_sentiments) / len(group_sentiments), 4)
        })

if sector_data:
    sector_df = pd.DataFrame(sector_data).sort_values('Avg Sentiment', ascending=True)
    colors = ['#00C805' if s > 0.05 else '#FF4444' if s < -0.05 else '#888888'
              for s in sector_df['Avg Sentiment']]

    fig_sector = go.Figure(go.Bar(
        x=sector_df['Avg Sentiment'],
        y=sector_df['Sector'],
        orientation='h',
        marker_color=colors
    ))
    fig_sector.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.4)
    fig_sector.update_layout(
        xaxis_title="Average Sentiment Score",
        height=300,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_sector, use_container_width=True)