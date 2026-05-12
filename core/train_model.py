import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def prepare_omni_data(mode="Rushing"):
    conn = sqlite3.connect("sports_data.db")
    
    # Selecting all relevant stat columns for QBs, RBs, and WRs
    query = """
    SELECT 
        s.player_id, s.player_display_name, s.position, s.recent_team, s.opponent_team,
        s.season, s.week, s.rushing_yards, s.passing_yards, s.rushing_tds, s.passing_tds,
        s.carries, s.attempts,
        COALESCE(i.report_status, 'Healthy') as injury_status
    FROM historical_player_stats s
    LEFT JOIN historical_injuries i 
        ON s.player_id = i.gsis_id AND s.week = i.week AND s.season = i.season
    WHERE s.position IN ('QB', 'RB', 'WR', 'TE')
    """
    df = pd.read_sql_query(query, conn)
    
    # --- Dynamic Target Logic ---
    if mode == "Passing":
        df['target'] = df['passing_yards']
        defense_col = 'passing_yards'
    elif mode == "TD":
        df['target'] = df['rushing_tds'] + df['passing_tds']
        defense_col = 'rushing_yards'
    else: # Rushing
        df['target'] = df['rushing_yards']
        defense_col = 'rushing_yards'

    # --- Defensive Strength Calculation ---
    defense_agg = df.groupby(['opponent_team', 'season', 'week'])[defense_col].sum().reset_index()
    defense_agg['avg_allowed'] = defense_agg.groupby('opponent_team')[defense_col].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    
    df = df.merge(defense_agg[['opponent_team', 'season', 'week', 'avg_allowed']], on=['opponent_team', 'season', 'week'], how='left')

    # --- Features ---
    status_map = {'Healthy': 0, 'Questionable': 1, 'Doubtful': 2, 'Out': 3}
    df['injury_encoded'] = df['injury_status'].map(status_map).fillna(0)
    df = df.sort_values(['player_id', 'season', 'week'])
    df['prev_perf'] = df.groupby('player_id')['target'].shift(1)
    
    conn.close()
    return df.dropna(subset=['prev_perf', 'avg_allowed'])

# This is the function your app.py is looking for!
def train_omni_model(mode="Rushing"):
    df = prepare_omni_data(mode)
    df['sample_weight'] = df['season'].apply(lambda x: 1.0 if x >= 2025 else 0.5)
    
    X = df[['prev_perf', 'injury_encoded', 'avg_allowed']]
    y = df['target']
    
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y, df['sample_weight'], test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train, sample_weight=w_train)
    
    return model

if __name__ == "__main__":
    train_omni_model("Rushing")