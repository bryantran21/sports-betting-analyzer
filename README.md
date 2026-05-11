# 🏈 NFL Sports Betting Analyzer

A machine learning pipeline designed to identify market inefficiencies and predict NFL player performance.

## 🚀 Phase 3 Update: The "Prop Grader"
We have successfully transitioned from data ingestion to predictive modeling. After conducting an **Ablation Study**, we determined that a **Linear Regression** model currently outperforms complex Ensemble methods for our specific dataset size.

### 📊 Model Performance (RBs - 2024 Season)
| Metric | Value |
| :--- | :--- |
| **Baseline MAE** | 23.54 Yards |
| **Data Samples** | 1,273 Games |
| **Top Feature** | `prev_week_yards` (65.6% Importance) |

### 🔍 Key Engineering Insights
* **The Injury Paradox:** Statistical analysis shows that "Questionable" tags for RBs have a negligible impact (-0.57 yards) on final output, suggesting these designations are often tactical rather than performance-limiting.
* **Simplicity vs. Complexity:** Linear models Generalized better than Random Forests, which showed a -11.60% decrease in accuracy due to overfitting on noise in defensive averages.

---

## 🛠 Project Structure
* `/scripts`: Data ingestion and cleaning.
* `train_model.py`: Model training and comparison logic.
* `prop_grader.py`: Final logic for comparing AI projections against sportsbook lines.

---

## 🏗 Setup & Installation
1. `pip install -r requirements.txt`
2. Configure `.env` with your `ODDS_API_KEY`.
3. Run `python scripts/import_nfl_history.py` to seed the database.