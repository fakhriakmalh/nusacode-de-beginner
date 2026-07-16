{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='(order_id, payment_sequential)'
) }}

-- ============================================================================
-- Staging Model: stg_payments
-- Deskripsi    : Membersihkan data pembayaran per pesanan.
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ source('public', 'fact_order_payment') }}
),

cleaned AS (
    SELECT
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        CASE
            WHEN payment_value IS NULL OR payment_value < 0 THEN 0
            ELSE payment_value
        END AS payment_value
    FROM source
)

SELECT * FROM cleaned