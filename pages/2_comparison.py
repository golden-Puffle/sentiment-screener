import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_TICKERS, STOCK_GROUPS, STOCK_COLORS, MAX_COMPARISON_STOCKS
from processing.merge import get_merged_data
from database.db import save_custom_groups, load_custom_groups, delete_custom_group

st.title("⚖️ Stock Comparison")

MAX_CUSTOM_GROUPS = 5  # max custom groups per user

# --- Load custom groups from database ---
if 'custom_groups' not in st.session_state:
    st.session_state.custom_groups = load_custom_groups()

# --- Stock selection ---
st.subheader("Select Stocks to Compare")

all_groups = {**STOCK_GROUPS, **st.session_state.custom_groups}
group_options = [g for g in all_groups.keys() if g != "Custom"] + ["Custom Selection"]

mode = st.radio("Selection mode:", ["Preset Groups", "My Custom Groups", "Custom Selection"], horizontal=True)

if mode == "Preset Groups":
    group_name = st.selectbox("Choose a group:", [g for g in STOCK_GROUPS.keys() if g != "Custom"])
    selected_tickers = STOCK_GROUPS[group_name][:MAX_COMPARISON_STOCKS]
    st.info(f"Comparing: {', '.join(selected_tickers)}")

elif mode == "My Custom Groups":
    if not st.session_state.custom_groups:
        st.info("You haven't created any custom groups yet. Use 'Custom Selection' to create one.")
        st.stop()
    else:
        group_name = st.selectbox("Choose your group:", list(st.session_state.custom_groups.keys()))
        selected_tickers = st.session_state.custom_groups[group_name][:MAX_COMPARISON_STOCKS]
        st.info(f"Comparing: {', '.join(selected_tickers)}")

        if st.button(f"🗑️ Delete '{group_name}'"):
            delete_custom_group(group_name)
            del st.session_state.custom_groups[group_name]
            st.rerun()

else:  # Custom Selection
    selected_tickers = st.multiselect(
        f"Select up to {MAX_COMPARISON_STOCKS} stocks:",
        list(ALL_TICKERS.keys()),
        max_selections=MAX_COMPARISON_STOCKS,
        default=["NVDA", "AMD"]
    )

    # Save as custom group
    if selected_tickers and len(selected_tickers) >= 2:
        with st.expander("💾 Save this as a custom group"):
            if len(st.session_state.custom_groups) >= MAX_CUSTOM_GROUPS:
                st.warning(f"You've reached the maximum of {MAX_CUSTOM_GROUPS} custom groups. Delete one to save a new group.")
            else:
                group_name_input = st.text_input("Group name (e.g. 'My Watchlist'):")
                if st.button("Save Group") and group_name_input:
                    st.session_state.custom_groups[group_name_input] = selected_tickers
                    save_custom_groups(st.session_state.custom_groups)
                    st.success(f"Saved '{group_name_input}'!")
                    st.rerun()

if not selected_tickers or len(selected_tickers) < 2:
    st.warning("Please select at least 2 stocks to compare.")
    st.stop()

# --- Load data ---
all_data = {}
for ticker in selected_tickers:
    df = get_merged_data(ticker)
    if not df.empty:
        df = df.drop_duplicates(subset=['Date'])
        all_data[ticker] = df

if len(all_data) < 2:
    st.warning("Not enough data. Run main.py for these tickers first.")
    st.stop()

st.markdown("---")

# --- Chart type toggle (fix point 3) ---
st.subheader("Price Performance")
chart_type = st.radio(
    "Chart mode:",
    ["Normalized (% change from start)", "Raw Price", "Log Scale"],
    horizontal=True
)
st.caption(
    "**Normalized**: All stocks start at 100 — best for comparing % gains fairly. "
    "**Raw Price**: Shows actual dollar values. "
    "**Log Scale**: Best for penny stocks or stocks with very different price ranges."
)

fig_price = go.Figure()
for i, (ticker, df) in enumerate(all_data.items()):
    if chart_type == "Normalized (% change from start)":
        y_values = (df['Close'] / df['Close'].iloc[0]) * 100
        y_title = "Normalized Price (base 100)"
    elif chart_type == "Raw Price":
        y_values = df['Close']
        y_title = "Price (USD)"
    else:  # Log Scale
        y_values = df['Close']
        y_title = "Price (USD) — Log Scale"

    fig_price.add_trace(go.Scatter(
        x=df['Date'], y=y_values,
        mode='lines', name=ticker,
        line=dict(color=STOCK_COLORS[i], width=2)
    ))

if chart_type == "Normalized (% change from start)":
    fig_price.add_hline(y=100, line_dash="dash", line_color="white", opacity=0.3)

fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title=y_title,
    yaxis_type="log" if chart_type == "Log Scale" else "linear",
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

# --- Summary table ---
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
found_divergence = False
for ticker, df in all_data.items():
    if len(df) < 5:
        continue
    recent = df.tail(5)
    price_trend = recent['Close'].iloc[-1] - recent['Close'].iloc[0]
    sentiment_trend = recent['combined_sentiment'].iloc[-1] - recent['combined_sentiment'].iloc[0]
    if price_trend > 0 and sentiment_trend < -0.1:
        st.warning(f"⚠️ **{ticker}**: Price trending UP but sentiment trending DOWN")
        found_divergence = True
    elif price_trend < 0 and sentiment_trend > 0.1:
        st.info(f"💡 **{ticker}**: Price trending DOWN but sentiment trending UP")
        found_divergence = True
if not found_divergence:
    st.success("✅ No significant divergences detected in the last 5 days")