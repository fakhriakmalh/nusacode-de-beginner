{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='product_id'
) }}

-- ============================================================================
-- Staging Model: stg_products
-- Deskripsi    : Menggabungkan data produk dengan terjemahan kategori
--                (Portugis -> Inggris).
-- ============================================================================

WITH source_product AS (
    SELECT * FROM {{ source('public', 'dim_product') }}
),

source_category AS (
    SELECT * FROM {{ source('public', 'dim_product_category') }}
),

joined AS (
    SELECT
        p.product_id,
        p.product_category_name,
        COALESCE(c.product_category_name_english, 'unknown') AS product_category_english,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    FROM source_product p
    LEFT JOIN source_category c
        ON p.product_category_name = c.product_category_name
)

SELECT * FROM joined