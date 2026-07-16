{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='customer_id',
    settings={'allow_nullable_key': 1}
) }}

WITH customers AS (
    SELECT * FROM {{ ref('silver_dim_customers') }}
),

orders AS (
    SELECT * FROM {{ ref('silver_fact_orders') }}
),

items AS (
    SELECT * FROM {{ ref('silver_fact_order_items') }}
),

payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment,
        COUNT(DISTINCT payment_type) AS payment_method_count,
        STRING_AGG(DISTINCT payment_type, ', ') AS payment_types
    FROM {{ ref('silver_fact_payments') }}
    GROUP BY order_id
),

reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS avg_review_score,
        COUNT(review_id) AS review_count
    FROM {{ ref('silver_fact_reviews') }}
    GROUP BY order_id
),

order_details AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.is_delivered,
        o.is_canceled,
        o.order_purchase_timestamp,
        COALESCE(p.total_payment, 0) AS total_payment,
        COALESCE(r.avg_review_score, 0) AS avg_review_score

    FROM orders o
    LEFT JOIN payments p ON o.order_id = p.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
),

customer_summary AS (
    SELECT
        c.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,

        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT CASE WHEN o.is_delivered THEN o.order_id END) AS delivered_orders,
        COUNT(DISTINCT CASE WHEN o.is_canceled THEN o.order_id END) AS canceled_orders,
        SUM(o.total_payment) AS total_revenue,
        AVG(o.avg_review_score) AS avg_review_score,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date

    FROM customers c
    LEFT JOIN order_details o ON c.customer_id = o.customer_id
    GROUP BY
        c.customer_id, c.customer_unique_id,
        c.customer_city, c.customer_state
)

SELECT
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    total_orders,
    delivered_orders,
    canceled_orders,

    CASE
        WHEN total_orders > 0
        THEN ROUND(delivered_orders::NUMERIC / total_orders, 2)
        ELSE 0
    END AS delivery_rate,

    total_revenue,
    avg_review_score,
    first_order_date,
    last_order_date,

    CASE
        WHEN first_order_date IS NOT NULL AND last_order_date IS NOT NULL
        THEN EXTRACT(DAY FROM (last_order_date - first_order_date))
        ELSE 0
    END AS customer_tenure_days

FROM customer_summary
