-- business_queries.sql
-- Analyst-style SQL queries answering real portfolio-risk business
-- questions, run against loans.db built from real consumer credit data.

-- 1. Overall delinquency rate and portfolio size
SELECT
    COUNT(*) AS total_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans;

-- 2. Delinquency rate by age band (younger borrowers = higher risk?)
SELECT
    (age / 10) * 10 AS age_band,
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans
GROUP BY age_band
ORDER BY age_band;

-- 3. Delinquency rate by revolving utilization band
SELECT
    CASE
        WHEN revol_util < 0.1 THEN '0-10%'
        WHEN revol_util < 0.3 THEN '10-30%'
        WHEN revol_util < 0.5 THEN '30-50%'
        WHEN revol_util < 0.75 THEN '50-75%'
        WHEN revol_util < 1.0 THEN '75-100%'
        ELSE '100%+'
    END AS utilization_band,
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans
GROUP BY utilization_band
ORDER BY MIN(revol_util);

-- 4. High-risk segment: any prior 90+ day delinquency
SELECT
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans
WHERE n_90_days_late > 0;

-- 5. Delinquency rate by number of dependents
SELECT
    n_dependents,
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans
GROUP BY n_dependents
ORDER BY n_dependents;

-- 6. Delinquency rate by real-estate loan count (homeowners vs. not, proxy)
SELECT
    CASE WHEN real_estate_loans = 0 THEN 'No real estate loans' ELSE '1+ real estate loans' END AS re_loan_group,
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM loans
GROUP BY re_loan_group;

-- 7. Income quartile vs. delinquency rate
WITH ranked AS (
    SELECT *, NTILE(4) OVER (ORDER BY monthly_income) AS income_quartile
    FROM loans
)
SELECT
    income_quartile,
    ROUND(MIN(monthly_income), 0) AS min_income,
    ROUND(MAX(monthly_income), 0) AS max_income,
    COUNT(*) AS n_borrowers,
    ROUND(100.0 * SUM(serious_dlqin_2yrs) / COUNT(*), 2) AS delinquency_rate_pct
FROM ranked
GROUP BY income_quartile
ORDER BY income_quartile;
