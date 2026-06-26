-- ============================================================================
-- Intermediate Model: int_order_details
-- Deskripsi    : Menggabungkan data pesanan dengan item, pembayaran, dan
--                review untuk menghasilkan detail pesanan yang lengkap.
--                Model ini menjadi dasar untuk fact table di layer marts.
-- ============================================================================

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
),

payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment,
        COUNT(DISTINCT payment_type) AS payment_method_count,
        STRING_AGG(DISTINCT payment_type, ', ') AS payment_types
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id
),

reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS avg_review_score,
        COUNT(review_id) AS review_count
    FROM {{ ref('stg_reviews') }}
    GROUP BY order_id
),

joined AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.is_delivered,
        o.is_canceled,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_customer_date,
        o.approval_hours,

        -- Item summary
        COUNT(DISTINCT i.order_item_id) AS item_count,
        SUM(i.price) AS total_price,
        SUM(i.freight_value) AS total_freight,
        SUM(i.price + i.freight_value) AS total_order_value,
        COUNT(DISTINCT i.product_id) AS unique_products,
        COUNT(DISTINCT i.seller_id) AS unique_sellers,

        -- Payment summary
        COALESCE(p.total_payment, 0) AS total_payment,
        COALESCE(p.payment_method_count, 0) AS payment_method_count,
        p.payment_types,

        -- Review summary
        COALESCE(r.avg_review_score, 0) AS avg_review_score,
        COALESCE(r.review_count, 0) AS review_count

    FROM orders o
    LEFT JOIN items i ON o.order_id = i.order_id
    LEFT JOIN payments p ON o.order_id = p.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    GROUP BY
        o.order_id, o.customer_id, o.order_status,
        o.is_delivered, o.is_canceled,
        o.order_purchase_timestamp, o.order_approved_at,
        o.order_delivered_customer_date, o.approval_hours,
        p.total_payment, p.payment_method_count, p.payment_types,
        r.avg_review_score, r.review_count
)

SELECT * FROM joined