import nflreadpy as nfl
import sqlite3

def load_game_data():
    import nflreadpy as nfl
    years = [2021, 2022, 2023, 2024, 2025]
    df_games = nfl.load_schedules(years).to_pandas()
    
    conn = sqlite3.connect("sports_data.db")
    df_games.to_sql("historical_games", conn, if_exists="replace", index=False)
    conn.close()
    print("🏟️ Game scores loaded for Spread/Moneyline analysis.")

if __name__ == "__main__":
    load_mega_dataset()