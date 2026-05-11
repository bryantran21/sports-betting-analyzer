import nfl_data_py as nfl
import sqlite3
import pandas as pd

def fetch_historical_nfl_data():
    years = [2023, 2024]
    conn = sqlite3.connect("sports_data.db")
    
    print("Fetching Schedules and Spreads...")
    # This includes 'spread_line' and 'total_line' (the betting odds!)
    schedules = nfl.import_schedules(years)
    schedules.to_sql('historical_schedules', conn, if_exists='replace', index=False)
    
    print("Fetching Injury Reports...")
    injuries = nfl.import_injuries(years)
    injuries.to_sql('historical_injuries', conn, if_exists='replace', index=False)
    
    print("Fetching Player Stats (Weekly)...")
    # This is huge data - it's where player props are born
    player_stats = nfl.import_weekly_data(years)
    player_stats.to_sql('historical_player_stats', conn, if_exists='replace', index=False)
    
    conn.close()
    print("✅ Real NFL History successfully loaded into your database!")

if __name__ == "__main__":
    fetch_historical_nfl_data()