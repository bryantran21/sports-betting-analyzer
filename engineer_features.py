import os
import requests
from dotenv import load_dotenv

load_dotenv()
CFBD_KEY = os.getenv('CFBD_API_KEY')

def test_cfbd_connection():
    headers = {
        'Authorization': f'Bearer {CFBD_KEY}',
        'accept': 'application/json'
    }
    
    # Let's grab Week 1 of the 2025 Regular Season
    url = 'https://api.collegefootballdata.com/games?year=2025&seasonType=regular&week=1'
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            game = data[0]
            # Match the exact keys from your RAW DATA DEBUG:
            home = game.get('homeTeam')
            away = game.get('awayTeam')
            h_pts = game.get('homePoints')
            a_pts = game.get('awayPoints')
            venue = game.get('venue')
            
            print(f"✅ Matchup Found: {home} vs {away}")
            print(f"🏟️  Venue: {venue}")
            print(f"📊 Final Score: {home} ({h_pts}) - {away} ({a_pts})")

if __name__ == "__main__":
    test_cfbd_connection()


def detect_rlm(public_pct, opening_spread, closing_spread):
    """
    Identifies if 'Reverse Line Movement' occurred.
    """
    # Is the public heavy on the favorite?
    heavy_public = public_pct > 65
    
    # Did the line move TOWARD the underdog despite public pressure?
    # (e.g., Opening -7, Closing -6)
    line_moved_against_public = closing_spread > opening_spread 
    
    if heavy_public and line_moved_against_public:
        return 1 # RLM Detected!
    return 0 # Normal movement