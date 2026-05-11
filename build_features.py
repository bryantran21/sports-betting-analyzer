import sqlite3
import pandas as pd

def process_game_features():
    conn = sqlite3.connect("sports_data.db")
    
    # 1. Load all raw odds from the database
    df_raw = pd.read_sql_query("SELECT * FROM nfl_odds", conn)
    
    if df_raw.empty:
        print("No data found in nfl_odds table!")
        return

    # 2. Group by game ID to find the first and last recorded odds
    # We sort by timestamp to make sure 'first' is Opening and 'last' is Closing
    df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
    df_raw = df_raw.sort_values(by=['id', 'timestamp'])

    # Create a new empty list to hold our results
    features_list = []

    # Loop through each unique game
    for game_id in df_raw['id'].unique():
        game_data = df_raw[df_raw['id'] == game_id]
        
        opening = game_data.iloc[0] # The earliest row
        closing = game_data.iloc[-1] # The latest row
        
        # Calculate Delta (how much the market moved)
        # Note: In our current data, we have 'home_price'. 
        # For spreads, it would be 'home_spread'.
        delta = closing['home_price'] - opening['home_price']
        
        # Simple RLM Logic for this test:
        # If the price dropped (became more expensive) by more than 0.05
        is_rlm = 1 if delta < -0.05 else 0
        
        features_list.append({
            'game_id': game_id,
            'opening_spread': opening['home_price'],
            'closing_spread': closing['home_price'],
            'spread_delta': delta,
            'is_rlm': is_rlm
        })

    # 3. Save to our new Feature Table
    df_features = pd.DataFrame(features_list)
    df_features.to_sql('game_features', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"✅ Processed {len(df_features)} games into Features!")

if __name__ == "__main__":
    process_game_features()