-- ============================================================================
-- Marts Model: dim_customers
-- Deskripsi    : Dimension table untuk data pelanggan. Berisi informasi
--                demografis dan metrik agregat tiap customer.
--                Grain: satu baris per pelanggan (customer_id).
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
),

final AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state,
        total_orders,
        delivered_orders,
        canceled_orders,

        -- Conversion rate
        CASE
            WHEN total_orders > 0
            THEN ROUND(delivered_orders::NUMERIC / total_orders, 2)
            ELSE 0
        END AS delivery_rate,

        total_revenue,
        avg_review_score,
        first_order_date,
        last_order_date,

        -- Customer tenure dalam hari
        CASE
            WHEN first_order_date IS NOT NULL AND last_order_date IS NOT NULL
            THEN EXTRACT(DAY FROM (last_order_date - first_order_date))
            ELSE 0
        END AS customer_tenure_days

    FROM source
)

SELECT * FROM final