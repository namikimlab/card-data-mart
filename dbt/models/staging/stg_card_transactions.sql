{{ config(materialized='view') }}

-- Staging model for the raw card_transactions source table.
-- This model performs data cleansing, standardization, and null handling
-- to prepare for downstream dimension and fact models.

SELECT
    -- Clean transaction_id
    CASE 
        WHEN transaction_id IS NULL OR TRIM(transaction_id) = '' OR transaction_id = 'NaN' THEN NULL
        ELSE transaction_id
    END AS transaction_id,

    -- Clean stock_code
    CASE 
        WHEN stock_code IS NULL OR TRIM(stock_code) = '' OR stock_code = 'NaN' THEN NULL
        ELSE stock_code
    END AS stock_code,

    -- Cleaned product description (convert 'NaN' or empty strings to NULL)
    CASE 
        WHEN description IS NULL OR TRIM(description) = '' OR description = 'NaN' THEN NULL
        ELSE description
    END AS description,

    -- Quantity 
    CASE
        WHEN quantity IS NULL 
        OR TRIM(CAST(quantity AS TEXT)) IN ('', 'NaN')
        OR quantity < 0
        THEN NULL
        ELSE quantity
    END AS quantity,

    -- Transaction date (timestamp stays as-is)
    CASE 
        WHEN transaction_date IS NULL 
        OR TRIM(CAST(transaction_date AS TEXT)) IN ('', 'NaN')
        THEN NULL
        ELSE transaction_date
    END AS transaction_date,

    -- Unit price
    CASE
        WHEN amount IS NULL 
        OR TRIM(CAST(amount AS TEXT)) IN ('', 'NaN')
        OR amount < 0
        THEN NULL
        ELSE amount
    END AS amount,

    -- Cleaned cardholder_id (convert 'NaN' or empty strings to NULL)
    CASE 
        WHEN cardholder_id IS NULL OR TRIM(cardholder_id) = '' OR cardholder_id = 'NaN' THEN NULL
        ELSE cardholder_id
    END AS cardholder_id,

    -- Cleaned country (optional)
    CASE 
        WHEN country IS NULL OR TRIM(country) = '' OR country = 'NaN' THEN NULL
        ELSE country
    END AS country

FROM {{ source('raw', 'card_transactions') }}

-- Remove rows where key columns are missing (invalid transactions)
WHERE 
    transaction_id IS NOT NULL
    AND stock_code IS NOT NULL
    AND cardholder_id IS NOT NULL
