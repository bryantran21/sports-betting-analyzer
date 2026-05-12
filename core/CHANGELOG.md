# 📝 Changelog

All notable changes to the **NFL Sports Betting Analyzer** will be documented in this file. This project adheres to a "feature-first" iteration cycle.

---

## [Unreleased] - 2026-05-11

### 🛠️ Architecture & Core Logic
- **Project Restructuring:** Migrated core modeling and grading scripts into `/core` and ingestion tools into `/data_ingestion`. This prepares the repository for a Streamlit-based web dashboard.
- **Enhanced Schema Alignment:** Updated `get_player_current_stats` to include `recent_team` data, resolving a critical `KeyError` in the prediction pipeline.

### 🧠 Model Optimization (The "Skeptical" Update)
- **Rolling-Window Defensive Feature:** Implemented a new SQL logic in `get_defensive_rank` that calculates a 3-game moving average for opponent rushing yards allowed. This prevents the model from being skewed by season-long averages and captures current defensive trends.
- **Team-Total Defense Correction:** Refactored defensive ranking logic to use `SUM(rushing_yards)` grouped by game. Previously, the model was averaging individual player yardage (~12 yards/game), leading to wildly inaccurate "Under" projections.
- **Temporal Decay Logic (Planned):** Added a conceptual framework for a `sample_weight` function to prioritize 2025/2026 performance over "Peak" historical data (e.g., Saquon Barkley's 2024 season).

### 🔍 Predictive Logic & Sanity Checks
- **Outlier Flagging System:** Added a logic gate to identify "Unprecedented Projections." If the AI projects a number >40% above a player's career baseline, the system triggers a warning to account for natural athletic regression.
- **2026 Matchup Engine:** Integrated a 2026 Week 1 schedule lookup (e.g., PHI vs NYG) to replace hardcoded placeholders with live defensive matchup data.

### 🐛 Bug Fixes
- **Git Repo Recovery:** Fixed a `.gitignore` error where a wildcard `*` was inadvertently ignoring all project files and folders.
- **Linear Regression Stability:** Resolved a `UserWarning` regarding feature names by aligning prediction input lists with DataFrame feature headers.

---

## [0.1.0] - 2026-05-10
### Added
- Initial project setup with SQLite database and `nfl_data_py` integration.
- Baseline Linear Regression model (MAE: 23.54 yards).
- Real-time odds ingestion from The-Odds-API.


## [0.1.1] - 2026-05-11
- Migrated data ingestion pipeline from deprecated nfl_data_py to nflreadpy to resolve 404 errors and ensure compatibility with 2025+ datasets.