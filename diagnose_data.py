import sqlite3
import pandas as pd

conn = sqlite3.connect("sports_data.db")

print("--- Stats Table Columns ---")
# Let's see all available columns to find a better 'Key'
stats_cols = pd.read_sql_query("PRAGMA table_info(historical_player_stats)", conn)
print(stats_cols['name'].tolist()[:10]) # Looking for 'player_id' or 'gsis_id'

print("\n--- Injury Table Columns ---")
injury_cols = pd.read_sql_query("PRAGMA table_info(historical_injuries)", conn)
print(injury_cols['name'].tolist()[:10])

conn.close()