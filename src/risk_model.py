"""
risk_model.py
-------------
Trains and compares two classifiers to predict serious delinquency
within 2 years, using the real "Give Me Some Credit" dataset (cleaned).

The target is highly imbalanced (~6.7% positive class), which is a
realistic and common challenge in credit-risk modeling, so both models
use class_weight="balanced" and are evaluated with ROC-AUC and
precision/recall rather than raw accuracy.

Saves:
  outputs/model_metrics.json
  outputs/figures/feature_importance.png
  outputs/figures/roc_curve.png
  outputs/figures/confusion_matrix.png

Run:
    python src/risk_model.py
"""

import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, roc_curve, classification_report, confusion_matrix
)

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "revol_util", "age", "n_30_59_days_late", "debt_ratio",
    "monthly_income", "open_credit_lines", "n_90_days_late",
    "real_estate_loans", "n_60_89_days_late", "n_dependents",
]
TARGET = "serious_dlqin_2yrs"

def main():
    df = pd.read_csv(ROOT / "data" / "loan_data_clean.csv")
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    results = {}

    # ---- Logistic Regression (class-balanced) ----
    logreg = Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    logreg.fit(X_train, y_train)
    lr_proba = logreg.predict_proba(X_test)[:, 1]
    lr_pred = logreg.predict(X_test)
    results["logistic_regression"] = {
        "roc_auc": round(roc_auc_score(y_test, lr_proba), 4),
        "classification_report": classification_report(y_test, lr_pred, output_dict=True),
    }

    # ---- Random Forest (class-balanced) ----
    rf = Pipeline([
        ("clf", RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=25,
            class_weight="balanced", random_state=42, n_jobs=-1
        )),
    ])
    rf.fit(X_train, y_train)
    rf_proba = rf.predict_proba(X_test)[:, 1]
    rf_pred = rf.predict(X_test)
    results["random_forest"] = {
        "roc_auc": round(roc_auc_score(y_test, rf_proba), 4),
        "classification_report": classification_report(y_test, rf_pred, output_dict=True),
    }

    print("Logistic Regression ROC-AUC:", results["logistic_regression"]["roc_auc"])
    print("Random Forest ROC-AUC:", results["random_forest"]["roc_auc"])

    cm = confusion_matrix(y_test, rf_pred)
    print("\nRandom Forest confusion matrix:\n", cm)

    # ---- ROC curves ----
    plt.figure(figsize=(6, 6))
    for name, proba in [("Logistic Regression", lr_proba), ("Random Forest", rf_proba)]:
        fpr, tpr, _ = roc_curve(y_test, proba)
        auc = roc_auc_score(y_test, proba)
        plt.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve: Serious Delinquency Prediction")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "roc_curve.png", dpi=150)
    plt.close()

    # ---- Confusion matrix heatmap ----
    plt.figure(figsize=(5, 4.5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Predicted: OK", "Predicted: Delinquent"],
                yticklabels=["Actual: OK", "Actual: Delinquent"])
    plt.title("Random Forest Confusion Matrix (test set)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "confusion_matrix.png", dpi=150)
    plt.close()

    # ---- Feature importance (Random Forest) ----
    importances = rf.named_steps["clf"].feature_importances_
    imp_df = pd.DataFrame({"feature": FEATURES, "importance": importances})
    imp_df = imp_df.sort_values("importance", ascending=False)

    plt.figure(figsize=(7, 5))
    plt.barh(imp_df["feature"][::-1], imp_df["importance"][::-1], color="#2E5EAA")
    plt.title("Feature Importances (Random Forest)")
    plt.xlabel("Importance")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "feature_importance.png", dpi=150)
    plt.close()

    with open(ROOT / "outputs" / "model_metrics.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved metrics to outputs/model_metrics.json")
    print(f"Saved charts to {FIG_DIR}")

if __name__ == "__main__":
    main()
