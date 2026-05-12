import sqlite3
import pandas as pd
import joblib
import nflreadpy as nfl

def get_automated_injury_status(player_name):
    """
    Fetches the current week's injury report and returns the encoded status.
    0: Healthy, 1: Questionable, 2: Doubtful/Out
    """
    try:
        # Load injuries for the current season
        df_injuries = nfl.load_injuries(seasons=[2026]).to_pandas()
        
        # Filter for the specific player
        player_injury = df_injuries[df_injuries['full_name'].str.contains(player_name, case=False)]
        
        if player_injury.empty:
            return 0  # Assume healthy if not on the report
        
        status = player_injury.iloc[0]['report_status']
        
        # Map to your model's expected inputs
        mapping = {
            'Questionable': 1,
            'Doubtful': 2,
            'Out': 2
        }
        return mapping.get(status, 0)
    except Exception:
        return 0 # Fallback to healthy on API error

# We only import the model function if we are running this file directly
# Otherwise, app.py handles the training to save memory
def get_player_current_stats(player_name):
    conn = sqlite3.connect("sports_data.db")
    query = f"""
    SELECT rushing_yards, passing_yards, opponent_team, recent_team 
    FROM historical_player_stats 
    WHERE player_display_name LIKE '%{player_name}%' 
    ORDER BY season DESC, week DESC LIMIT 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def grade_prop(model, player_name, sportsbook_line, is_injured=0):
    stats = get_player_current_stats(player_name)
    if stats.empty: return

    prev_yards = stats.iloc[0]['rushing_yards']
    current_team = stats.iloc[0]['recent_team']
    
    opp = get_upcoming_opponent(current_team)
    avg_def = get_defensive_rank(opp)
    
    # Matching the Omni-Engine feature names
    input_df = pd.DataFrame([[prev_yards, is_injured, avg_def]], 
                            columns=['prev_perf', 'injury_encoded', 'avg_allowed'])
    
    proj_yards = model.predict(input_df)[0]
    diff = proj_yards - sportsbook_line
    
    print(f"\n--- 🏈 Prop Grade: {player_name} ---")
    print(f"AI Projection:   {proj_yards:.1f} yards")
    print(f"Difference:      {diff:+.1f} yards")
    
    return proj_yards

def get_upcoming_opponent(team_name):
    schedule_2026 = {
        'PHI': 'NYG', 
        'KC': 'BAL', 
        'SF': 'LAR', 
    }
    return schedule_2026.get(team_name, 'AVG')

def get_defensive_rank(opponent_team, mode="Rushing"):
    conn = sqlite3.connect("sports_data.db")
    
    # Switch column based on mode
    col = "passing_yards" if mode == "Passing" else "rushing_yards"
    if mode == "TD": col = "rushing_tds" # Or passing_tds
    
    query = f"""
    SELECT week, SUM({col}) as game_total 
    FROM historical_player_stats 
    WHERE opponent_team = '{opponent_team}' 
    GROUP BY season, week
    ORDER BY season DESC, week DESC
    LIMIT 3
    """
    res = pd.read_sql_query(query, conn)
    conn.close()
    
    if not res.empty:
        return res['game_total'].mean()
    
    # Realistic fallbacks
    return 250.0 if mode == "Passing" else 110.0 if mode == "Rushing" else 1.2

if __name__ == "__main__":
    # If running this file standalone for a quick test
    from core.train_model import train_omni_model
    model = train_omni_model("Rushing")
    grade_prop(model, "Saquon Barkley", 80.5)