-- ============================================================
-- Retail Analytics — Key SQL Queries
-- ============================================================

-- 1. Monthly Revenue & Orders Trend
SELECT
    strftime('%Y-%m', transaction_date) AS month,
    COUNT(*)                            AS total_orders,
    ROUND(SUM(revenue), 2)              AS total_revenue,
    ROUND(AVG(revenue), 2)              AS avg_order_value,
    COUNT(DISTINCT customer_id)         AS unique_customers
FROM transactions
GROUP BY month
ORDER BY month;

-- 2. Top 10 Products by Revenue
SELECT
    p.product_name,
    p.category,
    COUNT(t.transaction_id)    AS orders,
    SUM(t.quantity)            AS units_sold,
    ROUND(SUM(t.revenue), 2)   AS total_revenue,
    ROUND(AVG(t.gross_profit / NULLIF(t.revenue, 0)) * 100, 1) AS margin_pct
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_revenue DESC
LIMIT 10;

-- 3. Revenue by Category
SELECT
    p.category,
    COUNT(t.transaction_id)  AS orders,
    ROUND(SUM(t.revenue), 2) AS total_revenue,
    ROUND(SUM(t.gross_profit), 2) AS total_profit,
    ROUND(SUM(t.gross_profit) / NULLIF(SUM(t.revenue), 0) * 100, 1) AS margin_pct
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 4. Revenue by State (Regional Performance)
SELECT
    c.state,
    COUNT(DISTINCT t.customer_id) AS customers,
    COUNT(t.transaction_id)       AS orders,
    ROUND(SUM(t.revenue), 2)      AS total_revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.state
ORDER BY total_revenue DESC;

-- 5. Channel Performance
SELECT
    channel,
    COUNT(*)                  AS orders,
    ROUND(SUM(revenue), 2)    AS total_revenue,
    ROUND(AVG(revenue), 2)    AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM transactions
GROUP BY channel
ORDER BY total_revenue DESC;

-- 6. Customer Segment Analysis
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)    AS customers,
    COUNT(t.transaction_id)          AS orders,
    ROUND(SUM(t.revenue), 2)         AS total_revenue,
    ROUND(AVG(t.revenue), 2)         AS avg_order_value,
    ROUND(SUM(t.revenue) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_revenue DESC;

-- 7. Repeat vs. New Customers per Month
WITH customer_first_order AS (
    SELECT customer_id, MIN(transaction_date) AS first_order_date
    FROM transactions
    GROUP BY customer_id
),
monthly_orders AS (
    SELECT
        t.customer_id,
        strftime('%Y-%m', t.transaction_date) AS month,
        strftime('%Y-%m', cfo.first_order_date) AS first_month
    FROM transactions t
    JOIN customer_first_order cfo ON t.customer_id = cfo.customer_id
)
SELECT
    month,
    COUNT(DISTINCT CASE WHEN month = first_month THEN customer_id END) AS new_customers,
    COUNT(DISTINCT CASE WHEN month != first_month THEN customer_id END) AS returning_customers
FROM monthly_orders
GROUP BY month
ORDER BY month;

-- 8. RFM Scoring (Recency, Frequency, Monetary)
WITH rfm_base AS (
    SELECT
        customer_id,
        CAST(julianday('2025-12-31') - julianday(MAX(transaction_date)) AS INTEGER) AS recency_days,
        COUNT(transaction_id)    AS frequency,
        ROUND(SUM(revenue), 2)   AS monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM rfm_base
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN (r_score + f_score + m_score) >= 12 THEN 'Champions'
        WHEN (r_score + f_score + m_score) >= 9  THEN 'Loyal Customers'
        WHEN (r_score + f_score + m_score) >= 6  THEN 'At Risk'
        ELSE 'Lost'
    END AS customer_segment
FROM rfm_scores
ORDER BY rfm_total DESC;
