"""
eda.py
------
Exploratory data analysis for the FinRisk Analytics loan portfolio
(real "Give Me Some Credit" consumer credit data, cleaned).
Generates summary statistics and saves charts to outputs/figures/.

Run:
    python src/eda.py
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
TARGET_LABEL = {0: "Not Delinquent", 1: "Serious Delinquency"}

def main():
    df = pd.read_csv(ROOT / "data" / "loan_data_clean.csv")
    df["status"] = df["serious_dlqin_2yrs"].map(TARGET_LABEL)

    print("Shape:", df.shape)
    print("\nMissing values:\n", df.isna().sum())
    print("\nDelinquency rate:\n", df["serious_dlqin_2yrs"].value_counts(normalize=True).round(4))
    print("\nNumeric summary:\n", df.describe().round(2))

    # 1. Delinquency rate by age band
    plt.figure(figsize=(7, 4.5))
    df["age_band"] = (df["age"] // 10) * 10
    rate_by_age = df.groupby("age_band")["serious_dlqin_2yrs"].mean() * 100
    sns.barplot(x=rate_by_age.index, y=rate_by_age.values, color="#2E5EAA")
    plt.title("Serious Delinquency Rate by Age Band")
    plt.ylabel("Delinquency Rate (%)")
    plt.xlabel("Age Band")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "delinquency_rate_by_age.png", dpi=150)
    plt.close()

    # 2. Delinquency rate by revolving utilization band
    plt.figure(figsize=(7, 4.5))
    bins = [0, 0.1, 0.3, 0.5, 0.75, 1.0, df["revol_util"].max() + 1]
    labels = ["0-10%", "10-30%", "30-50%", "50-75%", "75-100%", "100%+"]
    df["util_band"] = pd.cut(df["revol_util"], bins=bins, labels=labels, include_lowest=True)
    rate_by_util = df.groupby("util_band", observed=True)["serious_dlqin_2yrs"].mean() * 100
    sns.barplot(x=rate_by_util.index, y=rate_by_util.values, color="#C0392B")
    plt.title("Serious Delinquency Rate by Revolving Utilization")
    plt.ylabel("Delinquency Rate (%)")
    plt.xlabel("Revolving Utilization Band")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "delinquency_rate_by_utilization.png", dpi=150)
    plt.close()

    # 3. Monthly income distribution by outcome (log scale, capped for readability)
    plt.figure(figsize=(7, 4.5))
    plot_df = df[df["monthly_income"] < df["monthly_income"].quantile(0.98)]
    sns.kdeplot(data=plot_df, x="monthly_income", hue="status", fill=True, alpha=0.4)
    plt.title("Monthly Income Distribution by Delinquency Outcome")
    plt.xlabel("Monthly Income ($)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "income_distribution.png", dpi=150)
    plt.close()

    # 4. Prior late payments vs. delinquency rate
    plt.figure(figsize=(7, 4.5))
    df["any_late_30_59"] = df["n_30_59_days_late"] > 0
    df["any_late_60_89"] = df["n_60_89_days_late"] > 0
    df["any_late_90"] = df["n_90_days_late"] > 0
    late_summary = pd.DataFrame({
        "30-59 days late (any)": [df.loc[df["any_late_30_59"], "serious_dlqin_2yrs"].mean() * 100],
        "60-89 days late (any)": [df.loc[df["any_late_60_89"], "serious_dlqin_2yrs"].mean() * 100],
        "90+ days late (any)": [df.loc[df["any_late_90"], "serious_dlqin_2yrs"].mean() * 100],
        "No prior late payments": [df.loc[
            ~df["any_late_30_59"] & ~df["any_late_60_89"] & ~df["any_late_90"], "serious_dlqin_2yrs"
        ].mean() * 100],
    }).T.reset_index()
    late_summary.columns = ["segment", "delinquency_rate_pct"]
    late_summary = late_summary.sort_values("delinquency_rate_pct")
    sns.barplot(data=late_summary, x="delinquency_rate_pct", y="segment", color="#2E5EAA")
    plt.title("Delinquency Rate by Prior Late-Payment History")
    plt.xlabel("Delinquency Rate (%)")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "delinquency_by_late_history.png", dpi=150)
    plt.close()

    print(f"\nSaved 4 charts to {FIG_DIR}")

if __name__ == "__main__":
    main()
