import sqlite3
import pandas as pd
import json

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


def save_custom_groups(groups: dict):
    """Save custom stock groups to a separate table"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_groups 
        (name TEXT PRIMARY KEY, tickers TEXT)
    """)
    for name, tickers in groups.items():
        conn.execute("""
            INSERT OR REPLACE INTO custom_groups (name, tickers) 
            VALUES (?, ?)
        """, (name, json.dumps(tickers)))
    conn.commit()
    conn.close()

def load_custom_groups() -> dict:
    """Load custom stock groups from database"""
    conn = get_connection()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS custom_groups (name TEXT PRIMARY KEY, tickers TEXT)")
        cursor = conn.execute("SELECT name, tickers FROM custom_groups")
        rows = cursor.fetchall()
        conn.close()
        return {row[0]: json.loads(row[1]) for row in rows}
    except:
        conn.close()
        return {}

def delete_custom_group(name: str):
    """Delete a custom group by name"""
    conn = get_connection()
    conn.execute("DELETE FROM custom_groups WHERE name = ?", (name,))
    conn.commit()
    conn.close()