from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd

def test_connection(player_name="Shai Gilgeous-Alexander"):
    print(f"Searching for {player_name}...")
    # 1. Get Player ID
    nba_players = [p for p in players.get_players() if p['full_name'] == player_name]
    if not nba_players:
        print("Player not found.")
        return
    
    p_id = nba_players[0]['id']
    print(f"Found ID: {p_id}. Fetching 2025-26 Season Logs...")

    # 2. Fetch Game Logs
    try:
        log = playergamelog.PlayerGameLog(player_id=p_id, season='2025-26')
        df = log.get_data_frames()[0]
        
        if not df.empty:
            print("✅ Connection Successful!")
            print(f"Last Game Stats for {player_name}:")
            print(df[['GAME_DATE', 'MATCHUP', 'PTS', 'REB', 'AST']].head(1))
        else:
            print("⚠️ Connection worked, but no data found for 2025-26.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()