import streamlit as st
import pandas as pd
import sys
import os
from core.train_model import train_omni_model
from core.prop_grader import get_player_current_stats, get_upcoming_opponent, get_defensive_rank

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Omni-Betting Analyzer", layout="wide")

# --- Load the Brain ---
@st.cache_resource
def load_model(mode):
    return train_omni_model(mode)

# --- Sidebar Inputs ---
st.sidebar.header("User Input")
player_name = st.sidebar.text_input("Player Name", "Saquon Barkley")
book_line = st.sidebar.number_input("Sportsbook Line", value=80.5, step=0.5)

# Mapping UI selection to Model modes
bet_mapping = {
    "Rushing Yards": "Rushing",
    "Passing Yards": "Passing",
    "Anytime TD": "TD"
}

selection = st.sidebar.selectbox("What are we grading?", list(bet_mapping.keys()))
current_mode = bet_mapping[selection]

is_injured = st.sidebar.selectbox("Injury Status", options=[0, 1, 2], 
                                 format_func=lambda x: ["Healthy", "Questionable", "Doubtful"][x])

# Load the specific model based on selection
model = load_model(current_mode)

tab1, tab2 = st.tabs(["👤 Player Yardage", "🏟️ Game Center (Coming Soon)"])

with tab1:
    if st.button("Grade this Prop"):
        stats = get_player_current_stats(player_name)
        
        if not stats.empty:
            # 1. FIX: Ensure we pull the RIGHT stat for the RIGHT mode
            if current_mode == "Passing":
                prev_val = stats.iloc[0]['passing_yards']
                label = "Yards"
            elif current_mode == "TD":
                # We need to make sure your SQL pulls TD stats too!
                prev_val = stats.iloc[0].get('total_tds', 0) 
                label = "TDs"
            else:
                prev_val = stats.iloc[0]['rushing_yards']
                label = "Yards"

            current_team = stats.iloc[0]['recent_team']
            opp = get_upcoming_opponent(current_team)
            
            # 2. FIX: Ensure the defensive rank matches the mode
            # (Pass 'current_mode' into your defensive rank function)
            avg_def = get_defensive_rank(opp, mode=current_mode)
            
            # Use a DataFrame for prediction to keep feature names consistent
            input_df = pd.DataFrame([[prev_val, is_injured, avg_def]], 
                                    columns=['prev_perf', 'injury_encoded', 'avg_allowed'])
            
            proj_val = model.predict(input_df)[0]
            diff = proj_val - book_line
            
            # Display Results
            col1, col2, col3 = st.columns(3)
            unit = "TDs" if current_mode == "TD" else "yds"
            col1.metric("AI Projection", f"{proj_val:.1f} {unit}")
            col2.metric("Book Line", f"{book_line} {unit}")
            col3.metric("Edge", f"{diff:+.1f} {unit}", delta_color="normal")
            
            if abs(diff) > 15 or (current_mode == "TD" and abs(diff) > 0.3):
                st.success(f"🔥 **Strong Value on the {'OVER' if diff > 0 else 'UNDER'}**")
            elif abs(diff) > 5:
                st.info(f"✅ **Value Found on the {'OVER' if diff > 0 else 'UNDER'}**")
            else:
                st.warning("❌ **No Edge Found (Line is accurate)**")
                
            st.write(f"**Matchup Note:** {current_team} vs {opp} (Recent Defense allowed {avg_def:.1f} {unit}/game)")
        else:
            st.error("Player not found in database. Try a different name.")