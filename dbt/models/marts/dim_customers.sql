{{ config(materialized='view') }}

-- Dimension table for customers (cardholders).
-- Each row represents a unique cardholder, including their most frequently associated country.
-- This table is used to join with fact transactions for customer-level analysis.

SELECT
    cardholder_id,
    MIN(country) AS country
FROM {{ ref('stg_card_transactions') }}
GROUP BY cardholder_id
