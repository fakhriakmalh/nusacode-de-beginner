
  create view "dw_nusacode"."public"."stg_customers__dbt_tmp"
    
    
  as (
    -- ============================================================================
-- Staging Model: stg_customers
-- Deskripsi    : Membersihkan dan menstandarisasi data pelanggan dari
--                raw_schema.dim_customer.
-- ============================================================================

WITH source AS (
    SELECT * FROM "dw_nusacode"."public"."dim_customer"
),

cleaned AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        -- Trim whitespace dan standarisasi format kota
        TRIM(INITCAP(customer_city)) AS customer_city,
        -- Standarisasi state ke uppercase
        UPPER(TRIM(customer_state)) AS customer_state
    FROM source
)

SELECT * FROM cleaned
  );