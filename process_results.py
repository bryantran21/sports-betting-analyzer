import sqlite3
import pandas as pd

# 1. The Mapper (This handles the 'Ole Miss' vs 'Mississippi' problem)
# Add to this list whenever you find a mismatch!
TEAM_MAP = {
    "Ole Miss": "Mississippi",
    "Pitt": "Pittsburgh",
    "NC State": "North Carolina State",
    "UConn": "Connecticut"
}

def clean_name(name):
    return TEAM_MAP.get(name, name)

def calculate_spread_winner(home_pts, away_pts, home_spread):
    """
    Returns 1 if the Home Team covered, 0 if they didn't.
    Formula: (Home Score - Away Score) + Home Spread
    If the result > 0, the Home team covered.
    """
    margin = home_pts - away_pts
    if (margin + home_spread) > 0:
        return 1 # Home Covered
    elif (margin + home_spread) < 0:
        return 0 # Away Covered
    else:
        return 0.5 # Push (Tie)

# For now, let's just print a manual test of our logic
print("--- Testing Feature Logic ---")
h_score, a_score = 21, 24
spread = -4.5 # Kansas State was favored by 4.5
result = calculate_spread_winner(h_score, a_score, spread)

print(f"Game: K-State {h_score}, Iowa St {a_score}")
print(f"Spread: K-State {spread}")
print(f"Did K-State Cover? {'✅ Yes' if result == 1 else '❌ No'}")