import sqlite3
import pandas as pd

# Connect to the database you just created
conn = sqlite3.connect("sports_data.db")

# Use Pandas (the data science powerhouse) to read the table
df = pd.read_sql_query("SELECT * FROM nfl_odds LIMIT 5", conn)

# Close the connection
conn.close()

# Show the results
if df.empty:
    print("The database is empty. Something went wrong!")
else:
    print("--- Database Sample ---")
    print(df)