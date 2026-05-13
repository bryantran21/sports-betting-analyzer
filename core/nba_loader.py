from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd
import time

def get_nba_player_stats(player_name):
    # Find player ID
    nba_player = [p for p in players.get_players() if p['full_name'].lower() == player_name.lower()]
    if not nba_player:
        return pd.DataFrame()
    
    player_id = nba_player[0]['id']
    
    # Fetch game logs for the 2025-26 season
    # Note: Using 2025-26 for current Finals context
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2025-26')
    df = gamelog.get_data_frames()[0]
    
    # Map NBA columns to your model's expected "Omni" names
    df = df.rename(columns={
        'PTS': 'pts',
        'REB': 'reb',
        'AST': 'ast',
        'MATCHUP': 'opponent_team'
    })
    
    # Return the most recent game for the 'prev_perf' feature
    return df.head(1)