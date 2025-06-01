{{ config(materialized='view') }}

-- Staging model for the raw card_transactions source table.
-- This model performs data cleansing, standardization, and null handling
-- to prepare for downstream dimension and fact models.

WITH raw_cleaned AS (

    SELECT
        -- transaction_id clean
        CASE 
            WHEN transaction_id IS NULL OR TRIM(transaction_id) = '' OR transaction_id = 'NaN' THEN NULL
            ELSE transaction_id
        END AS transaction_id,

        -- stock_code clean
        CASE 
            WHEN stock_code IS NULL OR TRIM(stock_code) = '' OR stock_code = 'NaN' THEN NULL
            ELSE stock_code
        END AS stock_code,

        -- description clean
        CASE 
            WHEN description IS NULL OR TRIM(description) = '' OR description = 'NaN' THEN NULL
            ELSE description
        END AS description,

        -- quantity clean
        CASE
            WHEN quantity IS NULL OR TRIM(CAST(quantity AS TEXT)) IN ('', 'NaN') OR quantity < 0 THEN NULL
            ELSE quantity
        END AS quantity,

        -- transaction_date clean
        CASE 
            WHEN transaction_date IS NULL OR TRIM(CAST(transaction_date AS TEXT)) IN ('', 'NaN') THEN NULL
            ELSE transaction_date
        END AS transaction_date,

        -- amount clean
        CASE
            WHEN amount IS NULL OR TRIM(CAST(amount AS TEXT)) IN ('', 'NaN') OR amount < 0 THEN NULL
            ELSE amount
        END AS amount,

        -- cardholder_id clean
        CASE 
            WHEN cardholder_id IS NULL OR TRIM(cardholder_id) = '' OR cardholder_id = 'NaN' THEN NULL
            ELSE cardholder_id
        END AS cardholder_id,

        -- country clean
        CASE 
            WHEN country IS NULL OR TRIM(country) = '' OR country = 'NaN' THEN NULL
            ELSE country
        END AS country

    FROM {{ source('raw', 'card_transactions') }}
),

filtered AS (
    SELECT *
    FROM raw_cleaned
    WHERE 
        transaction_id IS NOT NULL
        AND stock_code IS NOT NULL
        AND cardholder_id IS NOT NULL
        AND quantity IS NOT NULL
        AND amount IS NOT NULL
)

SELECT
    -- surrogate key 생성 (unique 보장용)
    ROW_NUMBER() OVER (ORDER BY transaction_date, transaction_id, stock_code) AS transaction_sk,

    transaction_id,
    stock_code,
    description,
    quantity,
    transaction_date,
    amount,
    cardholder_id,
    country

FROM filtered