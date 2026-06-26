-- ============================================================================
-- Intermediate Model: int_customer_orders
-- Deskripsi    : Menggabungkan data pelanggan dengan ringkasan pesanan
--                mereka. Model ini menjadi dasar untuk dim_customers
--                di layer marts.
-- ============================================================================

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

order_details AS (
    SELECT * FROM {{ ref('int_order_details') }}
),

customer_summary AS (
    SELECT
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,

        -- Metrik agregat
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT CASE WHEN o.is_delivered THEN o.order_id END) AS delivered_orders,
        COUNT(DISTINCT CASE WHEN o.is_canceled THEN o.order_id END) AS canceled_orders,
        SUM(o.total_order_value) AS total_revenue,
        AVG(o.avg_review_score) AS avg_review_score,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date

    FROM customers c
    LEFT JOIN order_details o ON c.customer_id = o.customer_id
    GROUP BY
        c.customer_id, c.customer_unique_id,
        c.customer_city, c.customer_state
)

SELECT * FROM customer_summary