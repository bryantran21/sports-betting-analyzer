import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor # The new upgrade
from sklearn.metrics import mean_absolute_error

def prepare_training_data():
    conn = sqlite3.connect("sports_data.db")
    
    # 1. Pull stats including the opponent_team
    query = """
    SELECT 
        s.player_id, s.player_display_name, s.week, s.season, s.rushing_yards, 
        s.opponent_team, s.recent_team,
        COALESCE(i.report_status, 'Healthy') as injury_status
    FROM historical_player_stats s
    LEFT JOIN historical_injuries i 
        ON s.player_id = i.gsis_id AND s.week = i.week AND s.season = i.season
    WHERE s.position = 'RB' AND s.season = 2024
    """
    df = pd.read_sql_query(query, conn)
    
    # 2. Calculate Defensive Strength (Avg yards allowed by each team per game)
    # We group by the team that *allowed* the yards (the opponent)
    defense_stats = df.groupby(['opponent_team'])['rushing_yards'].mean().reset_index()
    defense_stats.columns = ['opponent_team', 'avg_yards_allowed']
    
    # 3. Merge that defense data back into our main table
    df = df.merge(defense_stats, on='opponent_team', how='left')
    
    # 4. Standard Encoding (Mapping injuries to numbers)
    status_map = {'Healthy': 0, 'Questionable': 1, 'Doubtful': 2, 'Out': 3}
    df['injury_encoded'] = df['injury_status'].map(status_map).fillna(0)
    
    # 5. Create 'Previous Week' feature
    df = df.sort_values(['player_id', 'week'])
    df['prev_week_yards'] = df.groupby('player_id')['rushing_yards'].shift(1)
    
    df = df.dropna(subset=['prev_week_yards'])
    conn.close()
    return df

def run_experiment():
    df = prepare_training_data()
    X = df[['prev_week_yards', 'injury_encoded', 'avg_yards_allowed']]
    y = df['rushing_yards']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Model 1: The Baseline (Linear) ---
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_mae = mean_absolute_error(y_test, lr_model.predict(X_test))

    # --- Model 2: The Upgrade (Random Forest) ---
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_mae = mean_absolute_error(y_test, rf_model.predict(X_test))

    print(f"\n--- 🧪 Model Comparison ---")
    print(f"Linear Regression MAE: {lr_mae:.2f} yards")
    print(f"Random Forest MAE:     {rf_mae:.2f} yards")
    
    improvement = ((lr_mae - rf_mae) / lr_mae) * 100
    print(f"Improvement:           {improvement:.2f}%")

    # Check which 'clue' was the most powerful
    importances = rf_model.feature_importances_
    feature_names = ['prev_week_yards', 'injury_encoded', 'avg_yards_allowed']
    for name, importance in zip(feature_names, importances):
        print(f"Feature: {name} | Importance: {importance:.4f}")

    return rf_model

if __name__ == "__main__":
    best_model = run_experiment()