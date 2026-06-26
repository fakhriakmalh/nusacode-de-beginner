-- ============================================================================
-- Marts Model: dim_sellers
-- Deskripsi    : Dimension table untuk data penjual. Berisi informasi
--                demografis dan metrik performa tiap seller.
--                Grain: satu baris per penjual (seller_id).
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ ref('stg_sellers') }}
),

order_items AS (
    SELECT
        seller_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(price) AS total_revenue,
        SUM(freight_value) AS total_freight,
        COUNT(DISTINCT product_id) AS unique_products
    FROM {{ ref('stg_order_items') }}
    GROUP BY seller_id
),

reviews AS (
    SELECT
        oi.seller_id,
        ROUND(AVG(r.review_score), 2) AS avg_customer_review,
        COUNT(r.review_id) AS total_reviews
    FROM {{ ref('stg_reviews') }} r
    JOIN {{ ref('stg_order_items') }} oi
        ON r.order_id = oi.order_id
    GROUP BY oi.seller_id
),

final AS (
    SELECT
        s.seller_id,
        s.seller_city,
        s.seller_state,

        -- Metrik performa
        COALESCE(oi.total_orders, 0) AS total_orders,
        COALESCE(oi.total_revenue, 0) AS total_revenue,
        COALESCE(oi.total_freight, 0) AS total_freight,
        COALESCE(oi.unique_products, 0) AS unique_products,

        -- Metrik review
        COALESCE(r.avg_customer_review, 0) AS avg_customer_review,
        COALESCE(r.total_reviews, 0) AS total_reviews

    FROM source s
    LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
    LEFT JOIN reviews r ON s.seller_id = r.seller_id
)

SELECT * FROM final