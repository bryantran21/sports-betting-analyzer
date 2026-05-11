import sqlite3
import pandas as pd
import joblib # We'll use this to save our model later
from train_model import run_experiment # Import our logic

def get_player_current_stats(player_name):
    conn = sqlite3.connect("sports_data.db")
    # Get the last game played by this player in 2024
    query = f"""
    SELECT rushing_yards, opponent_team 
    FROM historical_player_stats 
    WHERE player_display_name LIKE '%{player_name}%' 
    ORDER BY season DESC, week DESC LIMIT 1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def grade_prop(model, player_name, sportsbook_line, is_injured=0):
    stats = get_player_current_stats(player_name)
    
    if stats.empty:
        print(f"Could not find stats for {player_name}")
        return

    prev_yards = stats.iloc[0]['rushing_yards']
    # For now, we'll use a neutral defensive value of 100 
    # until we link the live schedule
    avg_def = 100.0 
    
    # Predict using our Linear Model
    # Note: We use [[]] to avoid the warning you saw earlier
    proj_yards = model.predict([[prev_yards, is_injured, avg_def]])[0]
    
    diff = proj_yards - sportsbook_line
    edge = (abs(diff) / sportsbook_line) * 100
    
    print(f"\n--- 🏈 Prop Grade: {player_name} ---")
    print(f"Sportsbook Line: {sportsbook_line} yards")
    print(f"AI Projection:   {proj_yards:.1f} yards")
    print(f"Difference:      {diff:+.1f} yards")
    
    if abs(diff) > 15: # If the AI is more than 15 yards away from the book
        recommendation = "🔥 STRONG VALUE"
    elif abs(diff) > 5:
        recommendation = "✅ VALUE FOUND"
    else:
        recommendation = "❌ NO EDGE (Line is accurate)"
        
    print(f"Recommendation:  {recommendation} on the {'OVER' if diff > 0 else 'UNDER'}")

if __name__ == "__main__":
    # 1. Train the model to get the latest version
    print("Training model...")
    # We'll modify run_experiment to return the Linear Model specifically
    from train_model import prepare_training_data
    from sklearn.linear_model import LinearRegression
    
    df = prepare_training_data()
    model = LinearRegression().fit(df[['prev_week_yards', 'injury_encoded', 'avg_yards_allowed']], df['rushing_yards'])
    
    # 2. Grade a hypothetical bet
    # Example: Saquon Barkley line is 80.5
    grade_prop(model, "Saquon Barkley", 80.5, is_injured=0)