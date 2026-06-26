-- ============================================================================
-- Marts Model: dim_products
-- Deskripsi    : Dimension table untuk data produk. Menggabungkan produk
--                dengan kategori Bahasa Inggris.
--                Grain: satu baris per produk (product_id).
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ ref('stg_products') }}
),

order_items AS (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(price) AS total_revenue,
        SUM(freight_value) AS total_freight,
        COUNT(DISTINCT seller_id) AS total_sellers
    FROM {{ ref('stg_order_items') }}
    GROUP BY product_id
),

final AS (
    SELECT
        p.product_id,
        p.product_category_name,
        p.product_category_english,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,

        -- Metrik performa
        COALESCE(oi.total_orders, 0) AS total_orders,
        COALESCE(oi.total_revenue, 0) AS total_revenue,
        COALESCE(oi.total_freight, 0) AS total_freight,
        COALESCE(oi.total_sellers, 0) AS total_sellers

    FROM source p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
)

SELECT * FROM final