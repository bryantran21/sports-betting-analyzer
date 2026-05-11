import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_fake_data(num_games=500):
    conn = sqlite3.connect("sports_data.db")
    games = []
    
    for i in range(num_games):
        game_id = f"fake_game_{i}"
        # 1. Randomly pick a spread between -1 and -10
        opening_spread = np.random.choice([-3.0, -3.5, -6.0, -7.0, -10.0])
        
        # 2. Decide if this is a "Sharp Move" game (RLM)
        # We'll make RLM happen in 20% of games
        is_rlm = 1 if np.random.random() < 0.20 else 0
        
        if is_rlm:
            # Line moves AGAINST the public (e.g., -7 to -6)
            closing_spread = opening_spread + 1.0
            # Sharps are smart: 58% chance they cover
            win_chance = 0.58
        else:
            # Normal movement or no movement
            closing_spread = opening_spread - 0.5
            win_chance = 0.50
            
        # 3. Determine if they covered based on the win_chance
        covered = 1 if np.random.random() < win_chance else 0
        
        games.append({
            'game_id': game_id,
            'opening_spread': opening_spread,
            'closing_spread': closing_spread,
            'spread_delta': closing_spread - opening_spread,
            'is_rlm': is_rlm,
            'covered_spread': covered,
            'clv': np.random.uniform(-1, 1)
        })

    df = pd.DataFrame(games)
    df.to_sql('game_features', conn, if_exists='append', index=False)
    conn.close()
    print(f"🔥 Success! Generated {num_games} historical games for training.")

if __name__ == "__main__":
    generate_fake_data()