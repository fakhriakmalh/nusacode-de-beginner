-- ============================================================================
-- Marts Model: fct_orders
-- Deskripsi    : Fact table untuk transaksi pesanan. Berisi satu baris per
--                pesanan dengan metrik lengkap (item, payment, review).
--                Grain: satu baris per pesanan (order_id).
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ ref('int_order_details') }}
)

SELECT
    order_id,
    customer_id,
    order_status,
    is_delivered,
    is_canceled,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    approval_hours,
    item_count,
    total_price,
    total_freight,
    total_order_value,
    unique_products,
    unique_sellers,
    total_payment,
    payment_method_count,
    payment_types,
    avg_review_score,
    review_count
FROM source
WHERE NOT is_canceled  -- Hanya pesanan yang tidak dibatalkan