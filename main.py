import subprocess

def run_pipeline():
    print("🚀 Starting Sports Betting Data Pipeline...")
    
    # List of scripts to run in order
    pipeline = [
        "scripts/ingest_odds.py",
        "scripts/import_nfl_history.py",
        "scripts/build_features.py"
    ]
    
    for script in pipeline:
        print(f"--- Running {script} ---")
        result = subprocess.run(["python", script], capture_output=True, text=True)
        print(result.stdout)
        if result.return_code != 0:
            print(f"❌ Error in {script}: {result.stderr}")
            break

if __name__ == "__main__":
    run_pipeline()