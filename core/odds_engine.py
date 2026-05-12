import requests
from core.config import ODDS_API_KEY

def get_live_events(sport='americanfootball_nfl'):
    """
    sport options: 'americanfootball_nfl' or 'americanfootball_ncaaf'
    """
    url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds'
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        events = response.json()
        return {e['id']: f"{e['home_team']} vs {e['away_team']}" for e in events}
    except Exception as e:
        print(f"❌ Odds API Error: {e}")
        return {}

def get_player_props(event_id, market='player_rush_yds'):
    url = f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events/{event_id}/odds'
    params = {'apiKey': ODDS_API_KEY, 'regions': 'us', 'markets': market}
    
    response = requests.get(url, params=params).json()
    props = []
    
    # Logic to parse the nested bookmaker outcomes
    for book in response.get('bookmakers', []):
        for mkt in book.get('markets', []):
            for outcome in mkt.get('outcomes', []):
                if outcome.get('name') == 'Over':
                    props.append({
                        'player': outcome.get('description'),
                        'line': outcome.get('point'),
                        'book': book.get('title')
                    })
    return props