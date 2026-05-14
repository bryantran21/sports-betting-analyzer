from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import pandas as pd

def get_nba_player_stats(player_name):
    # Find ID (Case-insensitive)
    all_players = players.get_players()
    nba_player = [p for p in all_players if p['full_name'].lower() == player_name.lower()]
    
    if not nba_player:
        return pd.DataFrame()
    
    # timeout=30 helps prevent random hang-ups
    log = playergamelog.PlayerGameLog(player_id=nba_player[0]['id'], season='2025-26', timeout=30)
    df = log.get_data_frames()[0]
    
    # Rename to match your Omni-Model's "Feature Names"
    return df.rename(columns={
        'PTS': 'pts',
        'REB': 'reb',
        'AST': 'ast'
    }).head(1)