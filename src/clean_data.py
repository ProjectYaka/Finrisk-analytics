"""
clean_data.py
-------------
Cleans the raw "Give Me Some Credit" dataset (real consumer credit
data — genuinely messy) and writes an analysis-ready CSV.

Documented data quality issues fixed here:
  - MonthlyIncome missing for ~20% of rows        -> median imputation
  - NumberOfDependents missing for ~2.6% of rows   -> median imputation (0)
  - age has a small number of 0 values (invalid)   -> dropped
  - RevolvingUtilizationOfUnsecuredLines and DebtRatio have extreme
    outliers (values in the thousands, impossible for real ratios)
    -> capped at the 99.5th percentile (winsorized), not dropped,
       so we don't throw away real high-risk borrowers

Run:
    python src/clean_data.py
Output:
    data/loan_data_clean.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "cs-training.csv"
OUT_PATH = ROOT / "data" / "loan_data_clean.csv"

RENAME = {
    "SeriousDlqin2yrs": "serious_dlqin_2yrs",
    "RevolvingUtilizationOfUnsecuredLines": "revol_util",
    "age": "age",
    "NumberOfTime30-59DaysPastDueNotWorse": "n_30_59_days_late",
    "DebtRatio": "debt_ratio",
    "MonthlyIncome": "monthly_income",
    "NumberOfOpenCreditLinesAndLoans": "open_credit_lines",
    "NumberOfTimes90DaysLate": "n_90_days_late",
    "NumberRealEstateLoansOrLines": "real_estate_loans",
    "NumberOfTime60-89DaysPastDueNotWorse": "n_60_89_days_late",
    "NumberOfDependents": "n_dependents",
}

def winsorize(series: pd.Series, upper_pct: float = 0.995) -> pd.Series:
    cap = series.quantile(upper_pct)
    return series.clip(upper=cap)

def main():
    df = pd.read_csv(RAW_PATH, index_col=0)
    df = df.rename(columns=RENAME)
    n_start = len(df)

    # 1. Drop invalid ages (age == 0 is a known data error in this dataset)
    df = df[df["age"] > 0]

    # 2. Impute missing values
    df["monthly_income"] = df["monthly_income"].fillna(df["monthly_income"].median())
    df["n_dependents"] = df["n_dependents"].fillna(0)

    # 3. Winsorize extreme outliers in ratio columns (real data artifact:
    #    a handful of rows report utilization/debt ratios in the thousands)
    df["revol_util"] = winsorize(df["revol_util"])
    df["debt_ratio"] = winsorize(df["debt_ratio"])

    # 4. Cap the "96/98" sentinel values used in this dataset for the
    #    past-due count columns (documented data issue: 96 and 98 are
    #    placeholder codes, not real counts)
    for col in ["n_30_59_days_late", "n_60_89_days_late", "n_90_days_late"]:
        df[col] = df[col].clip(upper=10)

    df = df.reset_index(drop=True)
    df.insert(0, "loan_id", [f"L{100000+i}" for i in range(len(df))])

    df.to_csv(OUT_PATH, index=False)
    print(f"Rows: {n_start} -> {len(df)} after cleaning")
    print(f"Default rate: {df['serious_dlqin_2yrs'].mean():.4f}")
    print(f"Saved -> {OUT_PATH}")

if __name__ == "__main__":
    main()
