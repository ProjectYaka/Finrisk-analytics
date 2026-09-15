# 💳 FinRisk Analytics — Consumer Credit Delinquency Risk

An end-to-end data analytics project on **real consumer credit data**:
raw data → cleaning → SQL database → exploratory analysis → predictive
modeling → interactive business dashboard.

**Author:** Michael Mayaka — [LinkedIn](https://www.linkedin.com/in/michaelmayaka/) · [GitHub](https://github.com/ProjectYaka)

---

## Business Problem

Lenders need to identify, ahead of time, which borrowers are likely to
become seriously delinquent (90+ days past due) so they can price risk
appropriately and monitor the riskiest segments of an existing portfolio.

This project builds a small but complete analytics pipeline that answers:

1. **Which borrower attributes predict serious delinquency** within the
   next two years?
2. **Which segments of the portfolio carry the most risk**, so a risk or
   collections team can prioritize monitoring?

---

## The Data

This project uses the real **["Give Me Some Credit"](https://www.kaggle.com/c/GiveMeSomeCredit/data)**
dataset — a 2011 Kaggle credit-scoring competition built on anonymized,
real consumer credit records (~150,000 borrowers, ~6.7% experienced
serious delinquency).

- **Target:** `SeriousDlqin2yrs` — did the borrower become 90+ days past
  due within two years?
- **Features:** revolving credit utilization, age, prior late-payment
  counts (30–59, 60–89, 90+ days), debt ratio, monthly income, number of
  open credit lines, real estate loans, and number of dependents.
- **Real-world data quality issues handled in `src/clean_data.py`:**
  ~20% of rows missing `MonthlyIncome`, ~2.6% missing `NumberOfDependents`,
  a small number of invalid `age == 0` rows, and extreme outlier values in
  the utilization/debt-ratio columns — all documented and fixed rather
  than silently dropped.
- The raw file isn't committed to this repo (7+ MB and best practice for
  competition-sourced data); `data/download_data.py` fetches it from a
  public GitHub mirror of the dataset on first run.

---

## What This Project Demonstrates

| Skill | Where |
|---|---|
| Real-world data cleaning (missing data, outliers, invalid values) | `src/clean_data.py` |
| SQL (schema design, aggregate & window-function queries) | `sql/schema.sql`, `sql/business_queries.sql` |
| Python data wrangling & EDA | `src/eda.py` |
| Handling class-imbalanced classification (~6.7% positive rate) | `src/risk_model.py` |
| ML modeling (Logistic Regression, Random Forest) & evaluation (ROC-AUC, precision/recall) | `src/risk_model.py` |
| Data visualization (Matplotlib/Seaborn, Plotly) | `outputs/figures/`, `dashboard/app.py` |
| Interactive dashboarding (Streamlit) | `dashboard/app.py` |

---

## Project Structure

```
finrisk-analytics/
├── data/
│   ├── download_data.py       # fetches the real dataset (GitHub mirror)
│   └── raw/                   # cs-training.csv (gitignored, downloaded)
├── sql/
│   ├── schema.sql             # loans table DDL
│   └── business_queries.sql   # 7 analyst-style business questions
├── src/
│   ├── clean_data.py          # cleans raw data -> loan_data_clean.csv
│   ├── load_db.py             # CSV -> SQLite, runs business_queries.sql
│   ├── eda.py                 # exploratory analysis + charts
│   └── risk_model.py          # trains & compares 2 classifiers
├── dashboard/
│   └── app.py                 # Streamlit interactive dashboard
├── outputs/
│   ├── figures/                # saved PNG charts
│   └── model_metrics.json      # model performance metrics
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
git clone https://github.com/ProjectYaka/finrisk-analytics.git
cd finrisk-analytics
pip install -r requirements.txt

# 1. Download the real dataset (~7 MB, cached in data/raw/)
python data/download_data.py

# 2. Clean it (handles missing data, outliers, invalid values)
python src/clean_data.py

# 3. Load into SQLite and run business queries
python src/load_db.py

# 4. Run EDA (saves charts to outputs/figures/)
python src/eda.py

# 5. Train risk models (saves metrics + charts)
python src/risk_model.py

# 6. Launch the interactive dashboard
streamlit run dashboard/app.py
```

---

## Key Findings

- **Utilization is the strongest single risk driver.** Delinquency rises
  from ~1.8% for borrowers using under 10% of their revolving credit to
  ~37% for borrowers over 100% utilization (i.e., over their limit).
- **Prior late payments are a very strong signal**: any history of 90+
  day lateness is associated with a ~42% delinquency rate, vs. ~6.7%
  portfolio-wide.
- **Risk decreases steadily with age** — from ~12% delinquency in the
  20s to under 2% by the 70s and 80s, a pattern consistent with real
  credit-scoring literature.
- **Lower-income borrowers are meaningfully higher risk**: the bottom
  income quartile delinquency rate (~9.1%) is nearly double the top
  quartile's (~4.8%).
- Having a real estate loan is associated with *lower* delinquency
  (~5.7% vs. ~8.3%), likely acting as a proxy for financial stability.
- A **Random Forest classifier** (with `class_weight="balanced"` to
  handle the 6.7% positive rate) achieves an **ROC-AUC of ~0.86–0.87**
  on held-out data, slightly outperforming logistic regression (~0.86).
  Revolving utilization, prior 90-day lateness, and prior 30–59 day
  lateness are the top three features by importance — see
  `outputs/figures/feature_importance.png`.

*(Exact numbers vary slightly run to run due to the train/test split —
see `outputs/model_metrics.json` for current values after running
`risk_model.py`.)*

---

## Dashboard Preview

The Streamlit dashboard (`dashboard/app.py`) lets a user filter the
portfolio by age, revolving utilization, dependents, and real-estate-loan
status, with KPIs (borrower count, delinquency rate, income, utilization)
and four charts updating live. This is the kind of self-serve tool a
risk or BI team would use to monitor a real portfolio.

---

## Possible Extensions

- Add a cost-sensitive decision threshold (a missed delinquent borrower
  costs more than a false alarm) and report expected-loss reduction.
- Add SHAP values for per-borrower explainability.
- Compare against the `cs-test.csv` holdout file from the same Kaggle
  competition (unlabeled — used for competition leaderboard scoring).
- Deploy the dashboard on Streamlit Community Cloud for a live demo link.

---

## Tech Stack

Python · Pandas · NumPy · SQLite · scikit-learn · Matplotlib/Seaborn ·
Plotly · Streamlit

---

## Data Source & License

Dataset: ["Give Me Some Credit"](https://www.kaggle.com/c/GiveMeSomeCredit/data),
a Kaggle credit-scoring competition (2011). Used here for educational /
portfolio purposes. See the Kaggle competition page for full terms.
