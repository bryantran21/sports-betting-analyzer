import os
import requests
from dotenv import load_dotenv

# 1. Load your secret keys from the .env file
load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY')

# 2. Define the "Endpoint" (The NFL Odds URL)
url = f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?apiKey={API_KEY}&regions=us&markets=h2h'

# 3. Make the request
print("Connecting to The Odds API...")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Success! Found {len(data)} upcoming games.")
    if len(data) > 0:
        print(f"📍 Matchup: {data[0]['home_team']} vs {data[0]['away_team']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Message: {response.text}")