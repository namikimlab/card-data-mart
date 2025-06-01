{{ config(materialized='view') }}

-- Dimension model for products.
-- Selects latest available product description for each stock_code.

WITH ranked_products AS (
  SELECT
    stock_code,
    description,
    ROW_NUMBER() OVER (
      PARTITION BY stock_code
      ORDER BY transaction_date DESC NULLS LAST
    ) AS row_num
  FROM {{ ref('stg_card_transactions') }}
)

SELECT
  stock_code,
  description
FROM ranked_products
WHERE row_num = 1
