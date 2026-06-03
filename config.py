# config.py
# To scale up, just edit these values — no other code changes needed

MAX_COMPARISON_STOCKS = 4  # change to 10 later if needed

# Predefined stock groups
STOCK_GROUPS = {
    "AI Chips": ["NVDA", "AMD", "INTC", "QCOM"],
    "Big Tech": ["AAPL", "MSFT", "GOOGL", "META"],
    "EV": ["TSLA", "RIVN", "F", "GM"],
    "Custom": []  # user picks manually
}

# All available tickers
ALL_TICKERS = {
    "NVDA": "Nvidia",
    "AMD": "AMD",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "META": "Meta",
    "TSLA": "Tesla",
    "RIVN": "Rivian",
    "F": "Ford",
    "GM": "General Motors"
}

# Color palette for up to 10 stocks on same chart
STOCK_COLORS = [
    "#00C805", "#2196F3", "#FF9800", "#E91E63",
    "#9C27B0", "#00BCD4", "#FF5722", "#8BC34A",
    "#FFC107", "#607D8B"
]

# Sentiment thresholds
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05

# Big price move threshold (for headline explanation feature)
BIG_MOVE_THRESHOLD = 2.0  # percentage