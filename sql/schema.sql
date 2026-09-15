-- schema.sql
-- Creates the loans table for the FinRisk Analytics SQLite database,
-- built from the real "Give Me Some Credit" dataset (cleaned).

DROP TABLE IF EXISTS loans;

CREATE TABLE loans (
    loan_id             TEXT PRIMARY KEY,
    serious_dlqin_2yrs  INTEGER,   -- target: 1 = serious delinquency within 2 years
    revol_util          REAL,      -- revolving balance / credit limit
    age                 INTEGER,
    n_30_59_days_late   INTEGER,   -- times 30-59 days past due (not worse), last 2 yrs
    debt_ratio          REAL,
    monthly_income      REAL,
    open_credit_lines   INTEGER,
    n_90_days_late      INTEGER,   -- times 90+ days past due, last 2 yrs
    real_estate_loans   INTEGER,
    n_60_89_days_late   INTEGER,   -- times 60-89 days past due (not worse), last 2 yrs
    n_dependents        REAL
);

CREATE INDEX idx_loans_target ON loans(serious_dlqin_2yrs);
CREATE INDEX idx_loans_age ON loans(age);
