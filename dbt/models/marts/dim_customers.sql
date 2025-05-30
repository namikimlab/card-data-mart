{{ config(materialized='view') }}

-- Dimension table for customers (cardholders).
-- Each row represents a unique cardholder, including their most frequently associated country.
-- This table is used to join with fact transactions for customer-level analysis.

SELECT
    cardholder_id,

    -- Choose one country per cardholder (e.g., in case of multiple values, use MIN as a deterministic default)
    MIN(country) AS country

FROM {{ ref('stg_card_transactions') }}
WHERE cardholder_id IS NOT NULL
GROUP BY cardholder_id
