{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='order_id'
) }}

-- ============================================================================
-- Staging Model: stg_orders
-- Deskripsi    : Membersihkan data pesanan dan menambahkan kolom flag
--                untuk memudahkan filtering di model selanjutnya.
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ source('public', 'fact_order') }}
),

cleaned AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        -- Flag: Apakah pesanan sudah delivered?
        CASE
            WHEN order_status = 'delivered' THEN TRUE
            ELSE FALSE
        END AS is_delivered,

        -- Flag: Apakah pesanan dibatalkan?
        CASE
            WHEN order_status IN ('canceled', 'unavailable') THEN TRUE
            ELSE FALSE
        END AS is_canceled,

        -- Durasi konfirmasi pesanan (approved - purchase) dalam jam
        EXTRACT(EPOCH FROM (order_approved_at - order_purchase_timestamp)) / 3600
            AS approval_hours
    FROM source
)

SELECT * FROM cleaned