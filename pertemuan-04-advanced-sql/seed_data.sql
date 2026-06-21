-- seed_data.sql
-- Script untuk membuat Gold Layer (Data Mart) dari raw_schema Olist
-- Gold Layer = tabel agregasi yang siap pakai untuk dashboard / BI tools
--
-- Prinsip: SELECT dari tabel fact + dim di raw_schema, lalu transformasi
-- menjadi agregasi bisnis yang langsung bisa dikonsumsi stakeholder.
--
-- Jalankan di DBeaver secara berurutan (satu per satu atau full script)

-- =====================================================================
-- 1. BUAT SCHEMA GOLD LAYER
-- =====================================================================
CREATE SCHEMA IF NOT EXISTS gold;

-- =====================================================================
-- 2. GOLD: Ringkasan Penjualan Harian
--    Daily aggregated sales: total orders, revenue, items sold
-- =====================================================================
DROP TABLE IF EXISTS gold.daily_sales_summary CASCADE;
CREATE TABLE gold.daily_sales_summary AS
SELECT
    DATE(o.order_purchase_timestamp) AS order_date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    COUNT(oi.order_item_id) AS total_items_sold,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(SUM(oi.freight_value)::numeric, 2) AS total_freight,
    ROUND((SUM(oi.price) + SUM(oi.freight_value))::numeric, 2) AS total_gross,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_item_price,
    ROUND(AVG(oi.freight_value)::numeric, 2) AS avg_freight
FROM raw_schema.fact_order o
LEFT JOIN raw_schema.fact_order_item oi ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY DATE(o.order_purchase_timestamp)
ORDER BY order_date;

-- =====================================================================
-- 3. GOLD: Performa Produk (terlaris & paling menguntungkan)
-- =====================================================================
DROP TABLE IF EXISTS gold.product_performance CASCADE;
CREATE TABLE gold.product_performance AS
WITH product_base AS (
    SELECT
        p.product_id,
        p.product_category_name,
        p.product_weight_g,
        (p.product_length_cm * p.product_height_cm * p.product_width_cm) AS product_volume_cm3
    FROM raw_schema.dim_product p
)
SELECT
    pb.product_id,
    COALESCE(pc.product_category_name_english, pb.product_category_name, 'Unknown') AS category_english,
    pb.product_weight_g,
    pb.product_volume_cm3,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COALESCE(SUM(oi.order_item_id), 0) AS total_units_sold,
    COALESCE(ROUND(SUM(oi.price)::numeric, 2), 0) AS total_revenue,
    COALESCE(ROUND(AVG(oi.price)::numeric, 2), 0) AS avg_unit_price,
    COALESCE(ROUND(SUM(oi.freight_value)::numeric, 2), 0) AS total_freight_paid,
    COALESCE(ROUND(AVG(r.review_score)::numeric, 2), 0) AS avg_review_score
FROM product_base pb
LEFT JOIN raw_schema.dim_product_category pc ON pb.product_category_name = pc.product_category_name
LEFT JOIN raw_schema.fact_order_item oi ON pb.product_id = oi.product_id
LEFT JOIN raw_schema.fact_order o ON oi.order_id = o.order_id AND o.order_status NOT IN ('canceled', 'unavailable')
LEFT JOIN raw_schema.fact_order_review r ON o.order_id = r.order_id
GROUP BY pb.product_id, pb.product_category_name, pc.product_category_name_english, pb.product_weight_g, pb.product_volume_cm3
ORDER BY total_revenue DESC;

-- =====================================================================
-- 4. GOLD: Customer Lifetime Value (LTV)
-- =====================================================================
DROP TABLE IF EXISTS gold.customer_ltv CASCADE;
CREATE TABLE gold.customer_ltv AS
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    MIN(o.order_purchase_timestamp) AS first_order_date,
    MAX(o.order_purchase_timestamp) AS last_order_date,
    EXTRACT(DAY FROM (MAX(o.order_purchase_timestamp) - MIN(o.order_purchase_timestamp))) AS customer_lifetime_days,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_order_value,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_given
FROM raw_schema.dim_customer c
LEFT JOIN raw_schema.fact_order o ON c.customer_id = o.customer_id AND o.order_status NOT IN ('canceled', 'unavailable')
LEFT JOIN raw_schema.fact_order_item oi ON o.order_id = oi.order_id
LEFT JOIN raw_schema.fact_order_review r ON o.order_id = r.order_id
GROUP BY c.customer_id, c.customer_unique_id, c.customer_city, c.customer_state
ORDER BY total_revenue DESC;

-- =====================================================================
-- 5. GOLD: Performa Seller / Penjual
-- =====================================================================
DROP TABLE IF EXISTS gold.seller_performance CASCADE;
CREATE TABLE gold.seller_performance AS
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS total_orders_served,
    COUNT(DISTINCT oi.product_id) AS unique_products_sold,
    SUM(oi.order_item_id) AS total_units_sold,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_sale_price,
    ROUND(SUM(oi.freight_value)::numeric, 2) AS total_freight_charged,
    ROUND(AVG(r.review_score)::numeric, 2) AS avg_customer_review
FROM raw_schema.dim_seller s
LEFT JOIN raw_schema.fact_order_item oi ON s.seller_id = oi.seller_id
LEFT JOIN raw_schema.fact_order o ON oi.order_id = o.order_id AND o.order_status NOT IN ('canceled', 'unavailable')
LEFT JOIN raw_schema.fact_order_review r ON o.order_id = r.order_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC;

-- =====================================================================
-- 6. GOLD: Analisis Pembayaran
-- =====================================================================
DROP TABLE IF EXISTS gold.payment_analysis CASCADE;
CREATE TABLE gold.payment_analysis AS
SELECT
    op.payment_type,
    COUNT(DISTINCT op.order_id) AS total_orders,
    COUNT(*) AS total_transactions,
    ROUND(SUM(op.payment_value)::numeric, 2) AS total_payment_volume,
    ROUND(AVG(op.payment_value)::numeric, 2) AS avg_payment_value,
    ROUND(AVG(op.payment_installments)::numeric, 2) AS avg_installments,
    MIN(op.payment_value) AS min_payment,
    MAX(op.payment_value) AS max_payment
FROM raw_schema.fact_order_payment op
LEFT JOIN raw_schema.fact_order o ON op.order_id = o.order_id AND o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY op.payment_type
ORDER BY total_payment_volume DESC;

-- =====================================================================
-- 7. GOLD: Analisis Review / Kepuasan Pelanggan
-- =====================================================================
DROP TABLE IF EXISTS gold.review_analysis CASCADE;
CREATE TABLE gold.review_analysis AS
SELECT
    r.review_score,
    COUNT(*) AS total_reviews,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    COUNT(DISTINCT r.order_id) AS unique_orders,
    COUNT(r.review_comment_message) AS reviews_with_comment,
    COUNT(r.review_comment_title) AS reviews_with_title
FROM raw_schema.fact_order_review r
GROUP BY r.review_score
ORDER BY r.review_score DESC;

-- =====================================================================
-- 8. GOLD: Order Fulfillment / Pengiriman
-- =====================================================================
DROP TABLE IF EXISTS gold.order_fulfillment CASCADE;
CREATE TABLE gold.order_fulfillment AS
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    -- Durasi dalam jam
    EXTRACT(EPOCH FROM (o.order_approved_at - o.order_purchase_timestamp)) / 3600 AS approval_hours,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 3600 AS fulfillment_hours,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_estimated_delivery_date)) / 3600 AS delivery_vs_estimate_hours,
    -- Flag keterlambatan
    CASE
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late'
        WHEN o.order_delivered_customer_date IS NOT NULL THEN 'On Time'
        ELSE 'Not Delivered'
    END AS delivery_status,
    -- Geolokasi
    c.customer_city,
    c.customer_state,
    s.seller_city AS seller_city,
    s.seller_state AS seller_state
FROM raw_schema.fact_order o
LEFT JOIN raw_schema.dim_customer c ON o.customer_id = c.customer_id
LEFT JOIN raw_schema.fact_order_item oi ON o.order_id = oi.order_id
LEFT JOIN raw_schema.dim_seller s ON oi.seller_id = s.seller_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

-- =====================================================================
-- 9. GOLD: Performa Kategori Produk
-- =====================================================================
DROP TABLE IF EXISTS gold.category_performance CASCADE;
CREATE TABLE gold.category_performance AS
SELECT
    COALESCE(pc.product_category_name_english, p.product_category_name, 'Unknown') AS category_name,
    COUNT(DISTINCT p.product_id) AS total_products,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COALESCE(SUM(oi.order_item_id), 0) AS total_units_sold,
    COALESCE(ROUND(SUM(oi.price)::numeric, 2), 0) AS total_revenue,
    COALESCE(ROUND(AVG(oi.price)::numeric, 2), 0) AS avg_price,
    COALESCE(ROUND(SUM(oi.freight_value)::numeric, 2), 0) AS total_freight,
    COALESCE(ROUND(AVG(r.review_score)::numeric, 2), 0) AS avg_review_score
FROM raw_schema.dim_product p
LEFT JOIN raw_schema.dim_product_category pc ON p.product_category_name = pc.product_category_name
LEFT JOIN raw_schema.fact_order_item oi ON p.product_id = oi.product_id
LEFT JOIN raw_schema.fact_order o ON oi.order_id = o.order_id AND o.order_status NOT IN ('canceled', 'unavailable')
LEFT JOIN raw_schema.fact_order_review r ON o.order_id = r.order_id
GROUP BY COALESCE(pc.product_category_name_english, p.product_category_name, 'Unknown')
ORDER BY total_revenue DESC;

-- =====================================================================
-- 10. GOLD: KPI Harian (Dashboard Ready)
--     Satu baris per hari dengan metrik-metrik utama
-- =====================================================================
DROP TABLE IF EXISTS gold.daily_kpi CASCADE;
CREATE TABLE gold.daily_kpi AS
WITH daily_orders AS (
    SELECT
        DATE(o.order_purchase_timestamp) AS order_date,
        COUNT(DISTINCT o.order_id) AS orders,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        ROUND(SUM(oi.price)::numeric, 2) AS revenue,
        ROUND(SUM(oi.freight_value)::numeric, 2) AS freight,
        COUNT(oi.order_item_id) AS items_sold,
        COUNT(DISTINCT oi.product_id) AS unique_products
    FROM raw_schema.fact_order o
    LEFT JOIN raw_schema.fact_order_item oi ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY DATE(o.order_purchase_timestamp)
),
daily_review AS (
    SELECT
        DATE(r.review_creation_date) AS review_date,
        ROUND(AVG(r.review_score)::numeric, 2) AS avg_daily_score,
        COUNT(*) AS total_reviews
    FROM raw_schema.fact_order_review r
    GROUP BY DATE(r.review_creation_date)
)
SELECT
    COALESCE(d.order_date, dr.review_date) AS date,
    d.orders,
    d.unique_customers,
    d.revenue,
    d.freight,
    d.items_sold,
    d.unique_products,
    ROUND((d.revenue / NULLIF(d.orders, 0))::numeric, 2) AS revenue_per_order,
    ROUND((d.items_sold / NULLIF(d.orders, 0))::numeric, 2) AS items_per_order,
    dr.avg_daily_score,
    dr.total_reviews
FROM daily_orders d
FULL OUTER JOIN daily_review dr ON d.order_date = dr.review_date
ORDER BY date;