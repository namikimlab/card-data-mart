{{ config(materialized='view') }}

-- This model builds a product dimension table by selecting one
-- representative description per stock_code.
-- It uses the most recent transaction_date to pick the latest description.

WITH ranked_products AS (
  SELECT
    stock_code,
    description,
    
    -- Assigns a row number to each record within the same stock_code group,
    -- ordered by transaction_date in descending order.
    ROW_NUMBER() OVER (
      PARTITION BY stock_code
      ORDER BY transaction_date DESC
    ) AS row_num

  FROM {{ ref('stg_card_transactions') }}
  WHERE stock_code IS NOT NULL
)

-- Select the most recent record per product (row_num = 1)
SELECT
  stock_code,
  description
FROM ranked_products
WHERE row_num = 1
