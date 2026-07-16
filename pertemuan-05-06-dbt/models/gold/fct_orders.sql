{{ config(
    materialized='incremental',
    engine='ReplacingMergeTree()',
    unique_key='order_id',
    incremental_strategy='delete+insert',
    order_by='order_id',
    partition_by='toYYYYMM(order_purchase_timestamp)',
    settings={'allow_nullable_key': 1}
) }}

WITH orders AS (
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

        COUNT(DISTINCT i.order_item_id) AS item_count,
        SUM(i.price) AS total_price,
        SUM(i.freight_value) AS total_freight,
        SUM(i.price + i.freight_value) AS total_order_value,
        COUNT(DISTINCT i.product_id) AS unique_products,
        COUNT(DISTINCT i.seller_id) AS unique_sellers,

        COALESCE(p.total_payment, 0) AS total_payment,
        COALESCE(p.payment_method_count, 0) AS payment_method_count,
        p.payment_types,

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
FROM joined
WHERE NOT is_canceled
