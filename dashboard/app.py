"""
app.py
------
Interactive Streamlit dashboard for the FinRisk Analytics project,
built on the real "Give Me Some Credit" consumer credit dataset.
Lets a "credit risk manager" filter the portfolio and see delinquency
rates and risk drivers update live.

Run:
    streamlit run dashboard/app.py
"""

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(page_title="FinRisk Analytics", layout="wide")

MIRROR_URL = (
    "https://raw.githubusercontent.com/JLZml/Credit-Scoring-Data-Sets/"
    "master/3.%20Kaggle/Give%20Me%20Some%20Credit/cs-training.csv"
)

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

def ensure_data(clean_path: Path):
    """Downloads and cleans the real dataset on first run if it isn't
    already present (e.g. on a fresh Streamlit Cloud deploy)."""
    if clean_path.exists():
        return
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "cs-training.csv"
    if not raw_path.exists():
        import urllib.request
        urllib.request.urlretrieve(MIRROR_URL, raw_path)

    raw = pd.read_csv(raw_path, index_col=0).rename(columns=RENAME)
    raw = raw[raw["age"] > 0]
    raw["monthly_income"] = raw["monthly_income"].fillna(raw["monthly_income"].median())
    raw["n_dependents"] = raw["n_dependents"].fillna(0)
    for col in ["revol_util", "debt_ratio"]:
        raw[col] = raw[col].clip(upper=raw[col].quantile(0.995))
    for col in ["n_30_59_days_late", "n_60_89_days_late", "n_90_days_late"]:
        raw[col] = raw[col].clip(upper=10)
    raw = raw.reset_index(drop=True)
    raw.insert(0, "loan_id", [f"L{100000+i}" for i in range(len(raw))])
    raw.to_csv(clean_path, index=False)

@st.cache_data
def load_data():
    clean_path = ROOT / "data" / "loan_data_clean.csv"
    ensure_data(clean_path)
    df = pd.read_csv(clean_path)
    df["status"] = df["serious_dlqin_2yrs"].map({0: "OK", 1: "Delinquent"})
    return df

df = load_data()

st.title("💳 FinRisk Analytics — Consumer Credit Risk Dashboard")
st.caption("Real data: Kaggle 'Give Me Some Credit' (2011) · ~150K anonymized borrowers · built by Michael Mayaka")

# ---- Sidebar filters ----
st.sidebar.header("Filters")
age_range = st.sidebar.slider("Age", int(df["age"].min()), int(df["age"].max()), (20, 90))
util_range = st.sidebar.slider("Revolving Utilization", 0.0, float(df["revol_util"].max()), (0.0, float(df["revol_util"].max())))
dependents = st.sidebar.multiselect(
    "Number of Dependents", sorted(df["n_dependents"].unique()),
    default=sorted(df["n_dependents"].unique())
)
re_loan_filter = st.sidebar.selectbox("Real Estate Loans", ["All", "Has real estate loan(s)", "No real estate loans"])

filtered = df[
    df["age"].between(*age_range)
    & df["revol_util"].between(*util_range)
    & df["n_dependents"].isin(dependents)
]
if re_loan_filter == "Has real estate loan(s)":
    filtered = filtered[filtered["real_estate_loans"] > 0]
elif re_loan_filter == "No real estate loans":
    filtered = filtered[filtered["real_estate_loans"] == 0]

# ---- KPI row ----
col1, col2, col3, col4 = st.columns(4)
total = len(filtered)
delinq_rate = filtered["serious_dlqin_2yrs"].mean() * 100 if total else 0
avg_income = filtered["monthly_income"].median() if total else 0
avg_util = filtered["revol_util"].mean() * 100 if total else 0

col1.metric("Borrowers", f"{total:,}")
col2.metric("Delinquency Rate", f"{delinq_rate:.1f}%")
col3.metric("Median Monthly Income", f"${avg_income:,.0f}")
col4.metric("Avg. Utilization", f"{avg_util:.1f}%")

st.divider()

c1, c2 = st.columns(2)

with c1:
    filtered = filtered.copy()
    filtered["age_band"] = (filtered["age"] // 10) * 10
    age_summary = filtered.groupby("age_band")["serious_dlqin_2yrs"].mean().reset_index()
    age_summary["delinquency_rate_pct"] = age_summary["serious_dlqin_2yrs"] * 100
    fig1 = px.bar(age_summary, x="age_band", y="delinquency_rate_pct",
                  title="Delinquency Rate by Age Band",
                  labels={"delinquency_rate_pct": "Delinquency Rate (%)", "age_band": "Age Band"})
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    bins = [0, 0.1, 0.3, 0.5, 0.75, 1.0, filtered["revol_util"].max() + 1] if total else [0, 1]
    labels = ["0-10%", "10-30%", "30-50%", "50-75%", "75-100%", "100%+"] if total else ["all"]
    filtered["util_band"] = pd.cut(filtered["revol_util"], bins=bins, labels=labels, include_lowest=True)
    util_summary = filtered.groupby("util_band", observed=True)["serious_dlqin_2yrs"].mean().reset_index()
    util_summary["delinquency_rate_pct"] = util_summary["serious_dlqin_2yrs"] * 100
    fig2 = px.bar(util_summary, x="util_band", y="delinquency_rate_pct",
                  title="Delinquency Rate by Revolving Utilization",
                  labels={"delinquency_rate_pct": "Delinquency Rate (%)", "util_band": "Utilization Band"})
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    sample = filtered.sample(min(1500, len(filtered))) if total else filtered
    fig3 = px.scatter(sample, x="debt_ratio", y="revol_util", color="status",
                       title="Debt Ratio vs. Revolving Utilization",
                       labels={"debt_ratio": "Debt Ratio", "revol_util": "Revolving Utilization"},
                       opacity=0.5)
    fig3.update_xaxes(range=[0, 2])
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    late_cols = {
        "30-59 days late": "n_30_59_days_late",
        "60-89 days late": "n_60_89_days_late",
        "90+ days late": "n_90_days_late",
    }
    rows = []
    for label, col in late_cols.items():
        sub = filtered[filtered[col] > 0]
        if len(sub):
            rows.append({"segment": label, "delinquency_rate_pct": sub["serious_dlqin_2yrs"].mean() * 100})
    late_df = pd.DataFrame(rows)
    fig4 = px.bar(late_df, x="delinquency_rate_pct", y="segment", orientation="h",
                  title="Delinquency Rate by Prior Late-Payment History",
                  labels={"delinquency_rate_pct": "Delinquency Rate (%)", "segment": ""})
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("Filtered Borrower Records")
st.dataframe(filtered.drop(columns=["status"], errors="ignore"), use_container_width=True, height=300)
