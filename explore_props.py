import sqlite3
import pandas as pd

conn = sqlite3.connect("sports_data.db")

# We join on the IDs now: player_id = gsis_id
query = """
SELECT 
    s.player_display_name, 
    s.recent_team, 
    s.week, 
    s.passing_yards, 
    s.rushing_yards,
    i.report_status,
    i.report_primary_injury
FROM historical_player_stats s
JOIN historical_injuries i 
    ON s.player_id = i.gsis_id 
    AND s.week = i.week 
    AND s.season = i.season
WHERE s.season = 2024 
    AND i.report_status NOT IN ('None', 'Active')
    AND (s.passing_yards > 200 OR s.rushing_yards > 50)
LIMIT 15;
"""

df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print("❌ Still empty. We might need to check if Week 1 Injuries align with Week 1 Stats.")
else:
    print("--- 🎯 SUCCESS: Found Injured Players with Big Stats (2024) ---")
    print(df)