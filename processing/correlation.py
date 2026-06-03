import pandas as pd
from scipy import stats

def compute_correlation(df):
    df = df.copy()
    df['next_day_change'] = df['pct_change'].shift(-1)
    df = df.dropna(subset=['combined_sentiment', 'next_day_change'])

    if len(df) < 5:
        return None, None, None

    corr, pvalue = stats.pearsonr(df['combined_sentiment'], df['next_day_change'])
    return round(corr, 4), round(pvalue, 4), df