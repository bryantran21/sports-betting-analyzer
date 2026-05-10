
import os
import sqlite3
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# 1. Setup & Keys
load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY')
DB_NAME = "sports_data.db"

def init_db():
    """Creates the database and table if they don't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfl_odds (
            id TEXT,
            home_team TEXT,
            away_team TEXT,
            commence_time TEXT,
            bookmaker TEXT,
            market TEXT,
            home_price REAL,
            away_price REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_save_odds():
    url = f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?apiKey={API_KEY}&regions=us&markets=h2h'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        conn = sqlite3.connect(DB_NAME)
        
        # We loop through each game and each bookmaker to save the prices
        for game in data:
            for bookmaker in game.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    # We grab the prices (usually [0] is one team, [1] is the other)
                    outcomes = market.get('outcomes', [])
                    
                    # Create a data row
                    row = (
                        game['id'],
                        game['home_team'],
                        game['away_team'],
                        game['commence_time'],
                        bookmaker['key'],
                        market['key'],
                        outcomes[0]['price'],
                        outcomes[1]['price'],
                        datetime.now().isoformat()
                    )
                    
                    conn.execute('INSERT INTO nfl_odds VALUES (?,?,?,?,?,?,?,?,?)', row)
        
        conn.commit()
        conn.close()
        print(f"Successfully saved data to {DB_NAME} at {datetime.now()}")
    else:
        print(f"Failed to fetch: {response.status_code}")

# Run the process
if __name__ == "__main__":
    init_db()
    fetch_and_save_odds()