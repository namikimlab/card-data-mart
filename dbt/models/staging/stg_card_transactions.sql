{{ config(materialized='view') }}

-- Staging model for the raw card_transactions source table.
-- This model performs basic column selection and aliasing (if needed) without transformations.
-- Used as the base layer for all downstream dimension and fact models.

SELECT
    transaction_id,     -- Transaction ID (originally InvoiceNo)
    stock_code,         -- Product code
    description,        -- Product name or label
    quantity,           -- Number of items purchased
    transaction_date,   -- Timestamp of the transaction
    amount,             -- Unit price at the time of the transaction
    cardholder_id,      -- Unique identifier of the customer
    country             -- Country where the transaction occurred
FROM {{ source('raw', 'card_transactions') }}
