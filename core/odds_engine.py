import requests
from core.config import ODDS_API_KEY

def get_live_events(sport='americanfootball_nfl'):
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
    # --- THE MISSING LINE ---
    url = f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events/{event_id}/odds'
    
    # Switch URL for NBA if needed
    if 'basketball' in event_id or market.startswith('player_points'):
        url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_id}/odds'

    params = {
        'apiKey': ODDS_API_KEY, 
        'regions': 'us', 
        'markets': market
    }
    
    try:
        response = requests.get(url, params=params).json()
        props = []
        seen_players = set() # To prevent duplicate names in your dropdown

        for book in response.get('bookmakers', []):
            for mkt in book.get('markets', []):
                for outcome in mkt.get('outcomes', []):
                    player_name = outcome.get('description')
                    
                    # Only grab the 'Over' outcome to define the line
                    if outcome.get('name') == 'Over' and player_name not in seen_players:
                        props.append({
                            'player': player_name,
                            'line': outcome.get('point'),
                            'book': book.get('title')
                        })
                        seen_players.add(player_name)
        return props
    except Exception as e:
        print(f"❌ Prop API Error: {e}")
        return []