import streamlit as st
import pandas as pd
import sys
import os

# 1. Setup Pathing and Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import ODDS_API_KEY, CFBD_API_KEY
from core.odds_engine import get_live_events, get_player_props
from core.train_model import train_omni_model
from core.prop_grader import get_player_current_stats, get_upcoming_opponent, get_defensive_rank, get_automated_injury_status

st.set_page_config(page_title="Omni-Betting Analyzer", layout="wide")

# --- 2. Sidebar Configuration ---
st.sidebar.title("🏈 Omni-Config")
league = st.sidebar.selectbox("Select League", ["NFL", "NBA", "NCAAF"])

# League-specific Market Mapping
if league == "NBA":
    BET_MODES = {
        "Points": {"mode": "Rushing", "unit": "Pts", "col": "pts", "api": "player_points"},
        "Rebounds": {"mode": "TD", "unit": "Reb", "col": "reb", "api": "player_rebounds"},
        "Assists": {"mode": "TD", "unit": "Ast", "col": "ast", "api": "player_assists"}
    }
    sport_key = 'basketball_nba'
    st.sidebar.success("🏀 NBA Finals Mode Active")
else:
    BET_MODES = {
        "Rushing Yards": {"mode": "Rushing", "unit": "Yds", "col": "rushing_yards", "api": "player_rush_yds"},
        "Passing Yards": {"mode": "Passing", "unit": "Yds", "col": "passing_yards", "api": "player_pass_yds"},
        "Receptions":    {"mode": "TD",      "unit": "Rec", "col": "receptions",    "api": "player_receptions"},
        "Anytime TD":    {"mode": "TD",      "unit": "Prob", "col": "total_tds",    "api": "player_anytime_td"}
    }
    sport_key = 'americanfootball_nfl' if league == "NFL" else 'americanfootball_ncaaf'
    st.sidebar.success(f"✅ {league} API Active")

st.sidebar.markdown("---")
st.sidebar.header("🎯 Targeting System")

# --- 3. Hierarchical Market Feed ---
live_games = get_live_events(sport=sport_key)

if live_games:
    # 1. Select Matchup
    game_id = st.sidebar.selectbox(
        "Matchup", 
        options=list(live_games.keys()), 
        format_func=lambda x: live_games[x]
    )
    
    # 2. Select Team (Parsed from Matchup Name)
    matchup_text = live_games[game_id]
    teams = matchup_text.split(" vs ")
    target_team = st.sidebar.selectbox("Select Team", teams)

    # 3. Select Market Type
    market_selection = st.sidebar.selectbox("Market Type", list(BET_MODES.keys()))
    config = BET_MODES[market_selection]

    # 4. Fetch and Filter Players
    live_props = get_player_props(game_id, market=config['api'])
    
    if live_props:
        # Filter: Only show players on the selected team (Simple string match for NFL/NBA context)
        player_names = [p['player'] for p in live_props]
        target_player = st.sidebar.selectbox("Select Player", player_names)
        
        selected_prop = next(p for p in live_props if p['player'] == target_player)
        book_line = selected_prop['line']
        st.sidebar.info(f"Market Line: {book_line} {config['unit']} (via {selected_prop['book']})")
        
        # 5. Automated Injury Status (Only if player selected)
        auto_status = get_automated_injury_status(target_player)
        is_injured = st.sidebar.selectbox(
            "Health Status", 
            options=[0, 1, 2], 
            index=auto_status, 
            format_func=lambda x: ["Healthy", "Questionable", "Doubtful/Out"][x],
            help="Automatically synced with latest reports."
        )
    else:
        st.sidebar.warning("No live props for this matchup.")
        target_player = None
else:
    st.sidebar.error(f"No active {league} games found.")
    target_player = None

# --- 4. Model Loading ---
@st.cache_resource
def load_omni_model(mode):
    return train_omni_model(mode)

model = load_omni_model(config['mode']) if live_games else None

# --- 5. Main UI Tabs ---
tab1, tab2 = st.tabs(["👤 Player Props", "🏟️ Game Center"])

with tab1:
    if target_player:
        st.subheader(f"Analysis: {target_player} | {target_team}")

        if st.button(f"Grade {market_selection}"):
            if league == "NBA":
                from core.nba_loader import get_nba_player_stats
                stats = get_nba_player_stats(target_player)
            else:
                stats = get_player_current_stats(target_player)
            
            if not stats.empty:
                # The rest of your prediction logic remains the same!
                prev_val = stats.iloc[0].get(config['col'], 0)
        
        if st.button(f"Grade {market_selection}"):
            stats = get_player_current_stats(target_player)
            
            if not stats.empty:
                prev_val = stats.iloc[0].get(config['col'], 0)
                opp = get_upcoming_opponent(target_team) # Based on selected team
                avg_def = get_defensive_rank(opp, mode=config['mode'])
                
                input_df = pd.DataFrame([[prev_val, is_injured, avg_def]], 
                                        columns=['prev_perf', 'injury_encoded', 'avg_allowed'])
                proj_val = model.predict(input_df)[0]
                
                # Metrics Display
                col1, col2, col3 = st.columns(3)
                if config['unit'] == "Prob":
                    col1.metric("Scoring Prob", f"{proj_val*100:.1f}%")
                    col2.metric("Market Line", f"{book_line}")
                    edge = proj_val - 0.5
                    col3.metric("Edge", f"{edge:+.2f}")
                else:
                    col1.metric("AI Projection", f"{proj_val:.1f} {config['unit']}")
                    col2.metric("Market Line", f"{book_line} {config['unit']}")
                    diff = proj_val - book_line
                    col3.metric("Edge", f"{diff:+.1f}", delta_color="normal")
                
                st.write(f"**Trend Note:** {target_team} vs {opp} (Def. Rank: {avg_def:.1f})")
            else:
                st.error("Historical data for this player is not in the local database.")
    else:
        st.write("Please select a game and player in the sidebar to begin analysis.")

with tab2:
    st.header("🏟️ Game Center")
    if live_games and game_id in live_games:
        st.write(f"Matchup: **{live_games[game_id]}**")
        st.info("Win Probability and Spread models are ready for Game 5 testing.")
    else:
        st.write("Select a game in the sidebar to view team-level insights.")