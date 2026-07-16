{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='(order_id, order_item_id)'
) }}

-- ============================================================================
-- Staging Model: stg_order_items
-- Deskripsi    : Membersihkan data item pesanan, memastikan harga dan
--                freight bernilai positif.
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ source('public', 'fact_order_item') }}
),

cleaned AS (
    SELECT
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        -- Harga: null -> 0, negatif -> 0
        CASE
            WHEN price IS NULL OR price < 0 THEN 0
            ELSE price
        END AS price,
        -- Freight: null -> 0, negatif -> 0
        CASE
            WHEN freight_value IS NULL OR freight_value < 0 THEN 0
            ELSE freight_value
        END AS freight_value
    FROM source
)

SELECT * FROM cleaned