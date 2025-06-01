{{ config(
    materialized='table'
) }}

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', transaction_date) AS month,
        COUNT(*) AS num_orders,
        SUM(amount * quantity) AS total_revenue,
        SUM(quantity) AS total_quantity,
        COUNT(DISTINCT cardholder_id) AS unique_customers,
        AVG(amount * quantity) AS avg_order_value
    FROM {{ ref('fct_transactions') }}
    GROUP BY 1
)

SELECT
    month,
    num_orders,
    total_quantity,
    total_revenue,
    avg_order_value,
    unique_customers
FROM monthly_sales
ORDER BY month
