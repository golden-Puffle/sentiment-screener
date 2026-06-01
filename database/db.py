import sqlite3
import pandas as pd

DB_PATH = "data/screener.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_dataframe(df, table_name):
    conn = get_connection()
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()
    print(f"Saved {len(df)} rows to '{table_name}'")

def read_table(table_name):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df