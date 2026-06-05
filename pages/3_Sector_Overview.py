import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import STOCK_GROUPS
from processing.merge import get_merged_data

st.title("🏭 Sector Overview")

st.subheader("Market Sentiment Index")
st.caption("Calculated from average sentiment across all tracked stocks. Ranges from -100 (Extreme Fear) to +100 (Extreme Greed).")

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
    # New formula: -100 to +100
    fear_greed_score = int(overall_sentiment * 100)
    fear_greed_score = max(-100, min(100, fear_greed_score))

    if fear_greed_score >= 60:
        label = "Extreme Greed 🤑"
        color = "#00C805"
    elif fear_greed_score >= 20:
        label = "Greed 🟢"
        color = "#8BC34A"
    elif fear_greed_score >= -20:
        label = "Neutral ⚪"
        color = "#888888"
    elif fear_greed_score >= -60:
        label = "Fear 🔴"
        color = "#FF9800"
    else:
        label = "Extreme Fear 😱"
        color = "#FF4444"

    col1, col2 = st.columns([1, 2])
    col1.metric("Market Sentiment", f"{fear_greed_score}/100", label)

    # Gauge with zone labels along the arc
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fear_greed_score,
        title={'text': label, 'font': {'size': 18}},
        number={'font': {'size': 40}},
        gauge={
            'axis': {
                'range': [-100, 100],
                'tickvals': [-100, -60, -20, 20, 60, 100],
                'ticktext': ['-100', '-60', '-20', '20', '60', '100'],
            },
            'bar': {'color': color, 'thickness': 0.3},
            'steps': [
                {'range': [-100, -60], 'color': '#FF4444'},
                {'range': [-60, -20], 'color': '#FF9800'},
                {'range': [-20, 20],  'color': '#888888'},
                {'range': [20, 60],   'color': '#8BC34A'},
                {'range': [60, 100],  'color': '#00C805'},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.8,
                'value': fear_greed_score
            }
        }
    ))

# Add zone labels as annotations outside the arc for clarity
    fig_gauge.add_annotation(
        x=0.02, y=0.05, text="Extreme Fear",
        showarrow=False, font=dict(size=9, color="#FF4444"),
        xref="paper", yref="paper", align="center"
    )
    fig_gauge.add_annotation(
        x=0.18, y=0.42, text="Fear",
        showarrow=False, font=dict(size=9, color="#FF9800"),
        xref="paper", yref="paper", align="center"
    )
    fig_gauge.add_annotation(
        x=0.5, y=0.82, text="Neutral",
        showarrow=False, font=dict(size=9, color="#AAAAAA"),
        xref="paper", yref="paper", align="center"
    )
    fig_gauge.add_annotation(
        x=0.82, y=0.42, text="Greed",
        showarrow=False, font=dict(size=9, color="#8BC34A"),
        xref="paper", yref="paper", align="center"
    )
    fig_gauge.add_annotation(
        x=0.98, y=0.05, text="Extreme Greed",
        showarrow=False, font=dict(size=9, color="#00C805"),
        xref="paper", yref="paper", align="center"
    )

    # Single update_layout — removed duplicate
    fig_gauge.update_layout(
        height=400,
        margin=dict(t=80, b=60, l=80, r=80)
    )
    col2.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# --- Sector breakdown ---
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
        xaxis_title="Average Sentiment Score (-1 to +1)",
        height=300,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_sector, use_container_width=True)