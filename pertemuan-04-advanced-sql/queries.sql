-- queries.sql
-- Kumpulan query analitik lanjutan (Sesi 4) — Gold Layer
-- Diketik bersama instruktur di DBeaver!
--
-- Prasyarat: Jalankan seed_data.sql terlebih dahulu untuk membuat gold layer tables.
--
-- Dataset: Olist Brazilian E-Commerce (raw_schema -> gold layer)
-- 
-- Medali Data:
--   🥉 Bronze Layer = raw_schema (tabel mentah)
--   🥈 Silver Layer = (transformasi ringan, dilewati di sesi ini)
--   🥇 Gold Layer   = gold schema (agregasi siap-pakai untuk BI)

-- =====================================================================
-- 1. RINGKASAN EKSEKUTIF: KPI Utama Bisnis
-- Menggunakan CTE untuk menghitung angka-angka kunci dari gold layer
-- =====================================================================
WITH kpi AS (
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        ROUND(SUM(price)::numeric, 2) AS total_revenue,
        ROUND(AVG(review_score)::numeric, 2) AS avg_review_score
    FROM raw_schema.fact_order o
    LEFT JOIN raw_schema.fact_order_item oi USING (order_id)
    LEFT JOIN raw_schema.fact_order_review r USING (order_id)
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
)
SELECT *,
    ROUND((total_revenue / NULLIF(total_orders, 0))::numeric, 2) AS revenue_per_order
FROM kpi;

-- =====================================================================
-- 2. TOP 10 PRODUK TERLARIS (dari gold.product_performance)
-- Menggabungkan performa produk dengan rata-rata review
-- =====================================================================
SELECT
    product_id,
    category_english,
    total_units_sold,
    total_revenue,
    total_orders,
    avg_unit_price,
    avg_review_score,
    -- Rasio pendapatan terhadap unit: makin tinggi makin premium
    ROUND((total_revenue / NULLIF(total_units_sold, 0))::numeric, 2) AS revenue_per_unit
FROM gold.product_performance
ORDER BY total_revenue DESC
LIMIT 10;

-- =====================================================================
-- 3. KATEGORI PRODUK PALING LARIS (dari gold.category_performance)
-- Siapa yang paling banyak menghasilkan uang?
-- =====================================================================
SELECT
    category_name,
    total_products,
    total_orders,
    total_units_sold,
    total_revenue,
    avg_review_score,
    -- Persentase kontribusi terhadap total revenue
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) AS revenue_share_pct
FROM gold.category_performance
ORDER BY total_revenue DESC;

-- =====================================================================
-- 4. WINDOW FUNCTION: RANKING PRODUK PER KATEGORI
-- Di setiap kategori, produk mana yang paling laris?
-- =====================================================================
WITH ranked_products AS (
    SELECT
        category_english,
        product_id,
        total_units_sold,
        total_revenue,
        DENSE_RANK() OVER (
            PARTITION BY category_english
            ORDER BY total_revenue DESC
        ) AS rank_in_category
    FROM gold.product_performance
    WHERE total_units_sold > 0
)
SELECT *
FROM ranked_products
WHERE rank_in_category <= 3  -- TOP 3 per kategori
ORDER BY category_english, rank_in_category;

-- =====================================================================
-- 5. WINDOW FUNCTION: CUSTOMER SEGMENTASI BERDASARKAN LTV
-- Analisis distribusi customer: siapa yang high-value?
-- =====================================================================
WITH customer_segments AS (
    SELECT
        customer_id,
        customer_city,
        customer_state,
        total_orders,
        total_revenue,
        customer_lifetime_days,
        -- Klasifikasi segmentasi pelanggan
        CASE
            WHEN total_revenue >= 500 THEN 'Platinum 💎'
            WHEN total_revenue >= 200 THEN 'Gold 🥇'
            WHEN total_revenue >= 100 THEN 'Silver 🥈'
            ELSE 'Bronze 🥉'
        END AS customer_tier,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank
    FROM gold.customer_ltv
    WHERE total_orders > 0
)
SELECT
    customer_tier,
    COUNT(*) AS total_customers,
    ROUND(AVG(total_revenue)::numeric, 2) AS avg_revenue,
    ROUND(AVG(total_orders)::numeric, 2) AS avg_orders,
    ROUND(AVG(customer_lifetime_days)::numeric, 2) AS avg_lifetime_days
FROM customer_segments
GROUP BY customer_tier
ORDER BY MIN(total_revenue) DESC;

-- =====================================================================
-- 6. WINDOW FUNCTION: TREN PENJUALAN HARIAN (RUNNING TOTAL)
-- Akumulasi revenue dari hari ke hari
-- =====================================================================
SELECT
    order_date,
    total_orders,
    total_revenue,
    SUM(total_revenue) OVER (ORDER BY order_date) AS cumulative_revenue,
    AVG(total_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_ma_7d,
    ROUND(
        (total_revenue - LAG(total_revenue, 1) OVER (ORDER BY order_date))::numeric
        / NULLIF(LAG(total_revenue, 1) OVER (ORDER BY order_date), 0) * 100,
        2
    ) AS revenue_dod_change_pct  -- Day-over-Day change
FROM gold.daily_sales_summary
ORDER BY order_date;

-- =====================================================================
-- 7. ANALISIS PENGIRIMAN: PERSENTASE TEPAT WAKTU vs TERLAMBAT
-- Dari gold.order_fulfillment, berapa persen yang on time?
-- =====================================================================
SELECT
    delivery_status,
    COUNT(*) AS total_orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    ROUND(AVG(approval_hours)::numeric, 2) AS avg_approval_hours,
    ROUND(AVG(fulfillment_hours)::numeric, 2) AS avg_fulfillment_hours,
    ROUND(AVG(delivery_vs_estimate_hours)::numeric, 2) AS avg_delay_hours
FROM gold.order_fulfillment
WHERE delivery_status IN ('On Time', 'Late')
GROUP BY delivery_status;

-- =====================================================================
-- 8. METODE PEMBAYARAN: ANALISIS TRANSAKSI
-- Dari gold.payment_analysis
-- =====================================================================
SELECT
    payment_type,
    total_transactions,
    total_payment_volume,
    avg_payment_value,
    avg_installments,
    -- Hitung persentase penggunaan metode
    ROUND(100.0 * total_transactions / SUM(total_transactions) OVER (), 2) AS usage_pct
FROM gold.payment_analysis
ORDER BY total_payment_volume DESC;

-- =====================================================================
-- 9. CTE + WINDOW: PERSENTASE REVIEW SCORE
-- Dari gold.review_analysis
-- =====================================================================
WITH review_stats AS (
    SELECT
        review_score,
        total_reviews,
        pct_of_total,
        CASE
            WHEN review_score >= 4 THEN 'Positive ✅'
            WHEN review_score = 3 THEN 'Neutral ➖'
            ELSE 'Negative ❌'
        END AS sentiment
    FROM gold.review_analysis
)
SELECT
    sentiment,
    SUM(total_reviews) AS total_reviews,
    ROUND(SUM(pct_of_total)::numeric, 2) AS pct_of_total
FROM review_stats
GROUP BY sentiment
ORDER BY SUM(total_reviews) DESC;

-- =====================================================================
-- 10. DASHBOARD KPI: 7 HARI TERAKHIR
--     Siap untuk di-export ke Metabase / Grafana
-- =====================================================================
SELECT
    date,
    orders,
    unique_customers,
    revenue,
    items_sold,
    revenue_per_order,
    avg_daily_score,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY date))::numeric
        / NULLIF(LAG(revenue, 1) OVER (ORDER BY date), 0) * 100,
        2
    ) AS revenue_growth_pct
FROM gold.daily_kpi
WHERE date >= (SELECT MAX(date) - INTERVAL '7 days' FROM gold.daily_kpi)
ORDER BY date DESC;