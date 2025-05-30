{{ config(materialized='view') }}

-- Fact table for card transactions.
-- Each row represents a single product purchased within a transaction.
-- This table captures detailed sales data and is used for building spending analytics, trends, and aggregations.

-- Lineage enforcement (for documentation only)
-- These do not affect SQL execution but include dim tables in the lineage graph
-- {% do ref('dim_customers') %}
-- {% do ref('dim_products') %}

SELECT
    transaction_id,     -- Unique identifier of the transaction (InvoiceNo)
    cardholder_id,      -- ID of the customer who made the transaction
    stock_code,         -- Product code of the item purchased
    quantity,           -- Number of items purchased
    amount,             -- Unit price at the time of transaction
    transaction_date,   -- Timestamp of the transaction
    country             -- Country where the transaction occurred

FROM {{ ref('stg_card_transactions') }}
WHERE transaction_id IS NOT NULL
