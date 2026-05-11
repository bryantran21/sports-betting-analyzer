import sqlite3

def setup_feature_table():
    conn = sqlite3.connect("sports_data.db")
    cursor = conn.cursor()
    
    # This table stores the "Processed" data your ML model will actually read
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_features (
            game_id TEXT PRIMARY KEY,
            opening_spread REAL,
            closing_spread REAL,
            spread_delta REAL,
            is_rlm INTEGER,
            covered_spread INTEGER,
            clv REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Feature table is ready for Phase 2!")

if __name__ == "__main__":
    setup_feature_table()