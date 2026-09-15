"""
load_db.py
----------
Loads data/loan_data.csv into a local SQLite database (loans.db) using
the schema defined in sql/schema.sql, then runs the business queries in
sql/business_queries.sql and prints the results. This mimics a real
analyst workflow: raw data -> relational DB -> SQL-driven insights.

Run:
    python src/load_db.py
"""

import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "loans.db"
CSV_PATH = ROOT / "data" / "loan_data_clean.csv"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
QUERIES_PATH = ROOT / "sql" / "business_queries.sql"

def main():
    df = pd.read_csv(CSV_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())
    df.to_sql("loans", conn, if_exists="append", index=False)
    conn.commit()
    print(f"Loaded {len(df)} rows into {DB_PATH.name}")

    # Strip comment lines first, then split into individual statements
    raw_lines = QUERIES_PATH.read_text().splitlines()
    no_comments = "\n".join(l for l in raw_lines if not l.strip().startswith("--"))
    statements = [q.strip() for q in no_comments.split(";") if q.strip()]

    for i, clean in enumerate(statements, start=1):
        try:
            result = pd.read_sql_query(clean, conn)
            print(f"\n--- Query {i} ---")
            print(result.to_string(index=False))
        except Exception as e:
            print(f"Query {i} failed: {e}")

    conn.close()

if __name__ == "__main__":
    main()
