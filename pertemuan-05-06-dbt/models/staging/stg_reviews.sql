{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='review_id'
) }}

-- ============================================================================
-- Staging Model: stg_reviews
-- Deskripsi    : Membersihkan data review, menstandarisasi skor review.
-- ============================================================================

WITH source AS (
    SELECT * FROM {{ source('public', 'fact_order_review') }}
),

cleaned AS (
    SELECT
        review_id,
        order_id,
        -- Skor review: pastikan dalam rentang 1-5
        CASE
            WHEN review_score < 1 THEN 1
            WHEN review_score > 5 THEN 5
            ELSE review_score
        END AS review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    FROM source
)

SELECT * FROM cleaned