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

    col1, col2, col3 = st.columns([1, 2, 1])

    # Left column — score and label
    with col1:
        st.markdown(f"""
        <div style='text-align:center;padding-top:40px'>
            <p style='color:gray;margin-bottom:4px'>Market Sentiment</p>
            <h1 style='margin:0;color:{color}'>{fear_greed_score}</h1>
            <p style='color:{color};font-size:18px;margin-top:8px'>{label}</p>
        </div>
        """, unsafe_allow_html=True)

    # Middle column — gauge (no number displayed)
    with col2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge",  # removed 'number' so score doesn't show inside gauge
            value=fear_greed_score,
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
        fig_gauge.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Right column — legend table
    with col3:
        st.markdown("""
        <div style='padding-top:30px'>
            <p style='color:gray;margin-bottom:8px;font-size:13px'><b>Scale Guide</b></p>
            <p style='margin:4px 0;font-size:12px'><span style='color:#00C805'>●</span> 60 to 100 &nbsp; Extreme Greed</p>
            <p style='margin:4px 0;font-size:12px'><span style='color:#8BC34A'>●</span> 20 to 60 &nbsp;&nbsp; Greed</p>
            <p style='margin:4px 0;font-size:12px'><span style='color:#888888'>●</span> -20 to 20 &nbsp; Neutral</p>
            <p style='margin:4px 0;font-size:12px'><span style='color:#FF9800'>●</span> -60 to -20 &nbsp;Fear</p>
            <p style='margin:4px 0;font-size:12px'><span style='color:#FF4444'>●</span> -100 to -60 Extreme Fear</p>
        </div>
        """, unsafe_allow_html=True)

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