{{ config(materialized='view') }}

SELECT
    transaction_id,
    stock_code,
    description,
    quantity,
    transaction_date,
    amount,
    cardholder_id,
    country
FROM {{ source('raw', 'card_transactions') }}
