import streamlit as st
import pandas as pd
import sys
import os

# 1. Setup Pathing and Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ODDS_API_KEY, CFBD_API_KEY
from core.odds_engine import get_live_events, get_player_props
from core.train_model import train_omni_model
from core.prop_grader import get_player_current_stats, get_upcoming_opponent, get_defensive_rank

st.set_page_config(page_title="Omni-Betting Analyzer", layout="wide")

# --- 2. Sidebar Configuration ---
st.sidebar.title("🏈 Omni-Config")
league = st.sidebar.selectbox("Select League", ["NFL", "NCAAF"])

# Display API Status based on .env
if league == "NCAAF":
    st.sidebar.success("✅ CFBD API Active")
else:
    st.sidebar.success("✅ Odds API Active")

st.sidebar.markdown("---")
st.sidebar.header("Targeting System")

# --- 3. Live Market Feed ---
sport_key = 'americanfootball_nfl' if league == "NFL" else 'americanfootball_ncaaf'
live_games = get_live_events(sport=sport_key)

if live_games:
    game_id = st.sidebar.selectbox(
        "Select Matchup", 
        options=list(live_games.keys()), 
        format_func=lambda x: live_games[x]
    )
    
    market_selection = st.sidebar.selectbox(
        "Market Type", 
        ["Rushing Yards", "Passing Yards", "Anytime TD"]
    )
    
    # Map UI to API and Model keys
    BET_MODES = {
        "Rushing Yards": {"mode": "Rushing", "unit": "Yds", "col": "rushing_yards", "api": "player_rush_yds"},
        "Passing Yards": {"mode": "Passing", "unit": "Yds", "col": "passing_yards", "api": "player_pass_yds"},
        "Anytime TD":    {"mode": "TD",      "unit": "Prob", "col": "total_tds",    "api": "player_anytime_td"}
    }
    config = BET_MODES[market_selection]

    # Fetch live players from The Odds API
    live_props = get_player_props(game_id, market=config['api'])
    
    if live_props:
        player_names = [p['player'] for p in live_props]
        target_player = st.sidebar.selectbox("Select Player", player_names)
        
        # Extract live line
        selected_prop = next(p for p in live_props if p['player'] == target_player)
        book_line = selected_prop['line']
        st.sidebar.info(f"Market Line: {book_line} {config['unit']} (via {selected_prop['book']})")
    else:
        st.sidebar.warning("No live props for this matchup yet.")
        target_player = None
        book_line = 0.5
else:
    st.sidebar.error(f"No active {league} games found.")
    target_player = None

# 1. Fetch the automated injury status from nflverse
from core.prop_grader import get_automated_injury_status
auto_status = get_automated_injury_status(target_player)

# 2. Use that status as the 'index' (default choice)
# If auto_status is 0, 'Healthy' is pre-selected.
# If auto_status is 1, 'Questionable' is pre-selected.
is_injured = st.sidebar.selectbox(
    "Health Status", 
    options=[0, 1, 2], 
    index=auto_status, 
    format_func=lambda x: ["Healthy", "Questionable", "Doubtful/Out"][x],
    help="Automatically updated from official injury reports."
)
# --- 4. Model Loading ---
@st.cache_resource
def load_omni_model(mode):
    return train_omni_model(mode)

model = load_omni_model(config['mode'])

# --- 5. Main UI Tabs ---
tab1, tab2 = st.tabs(["👤 Player Props", "🏟️ Game Center"])

with tab1:
    if target_player:
        st.subheader(f"Analysis: {target_player} ({market_selection})")
        
        if st.button(f"Grade {target_player}"):
            stats = get_player_current_stats(target_player)
            
            if not stats.empty:
                # Use correct stat column for prediction input
                prev_val = stats.iloc[0].get(config['col'], 0)
                current_team = stats.iloc[0]['recent_team']
                opp = get_upcoming_opponent(current_team)
                
                # Fetch defensive rank based on current mode
                avg_def = get_defensive_rank(opp, mode=config['mode'])
                
                # Predict
                input_df = pd.DataFrame([[prev_val, is_injured, avg_def]], 
                                        columns=['prev_perf', 'injury_encoded', 'avg_allowed'])
                proj_val = model.predict(input_df)[0]
                
                # Display Metrics
                col1, col2, col3 = st.columns(3)
                
                # Handle TD Probability vs Yards
                if config['mode'] == "TD":
                    col1.metric("Scoring Prob", f"{proj_val*100:.1f}%")
                    col2.metric("Market Line", f"{book_line}")
                    # Edge calculation for TDs (Projection vs Implied Probability)
                    edge = proj_val - 0.5 # Basic threshold
                    col3.metric("Edge", f"{edge:+.2f}")
                else:
                    col1.metric("AI Projection", f"{proj_val:.1f} {config['unit']}")
                    col2.metric("Market Line", f"{book_line} {config['unit']}")
                    diff = proj_val - book_line
                    col3.metric("Edge", f"{diff:+.1f} {config['unit']}", delta_color="normal")
                
                st.write(f"**Matchup Note:** {current_team} vs {opp} (Defense allows avg {avg_def:.1f} {config['unit']}/game)")
            else:
                st.error("Player data missing from historical database.")
    else:
        st.write("Select a matchup and player in the sidebar to begin.")

with tab2:
    st.header("🏟️ Game Center")
    if live_games and game_id in live_games:
        st.write(f"Analyzing: **{live_games[game_id]}**")
        st.info("Spread and Moneyline models are initializing using historical team EPA data.")
    else:
        st.write("Please select a game in the sidebar.")