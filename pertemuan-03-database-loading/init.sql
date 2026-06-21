-- init.sql
-- Script inisialisasi awal database
-- Dijalankan otomatis oleh Docker Entrypoint saat database pertama kali dibangun.
--
-- Dataset: Olist Brazilian E-commerce (Kaggle)
-- Link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
--
-- Klasifikasi Tabel:
--   Fact Tables  : fact_order, fact_order_item, fact_order_payment, fact_order_review
--   Dim Tables   : dim_customer, dim_geolocation, dim_product, dim_product_category, dim_seller

CREATE SCHEMA IF NOT EXISTS raw_schema;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- 1. dim_customer: Data pelanggan
CREATE TABLE IF NOT EXISTS raw_schema.dim_customer (
    customer_id          TEXT NOT NULL,
    customer_unique_id   TEXT,
    customer_zip_code_prefix TEXT,
    customer_city        TEXT,
    customer_state       TEXT,
    PRIMARY KEY (customer_id)
);

-- 2. dim_geolocation: Data lokasi kode pos
CREATE TABLE IF NOT EXISTS raw_schema.dim_geolocation (
    geolocation_zip_code_prefix TEXT NOT NULL,
    geolocation_lat            DOUBLE PRECISION,
    geolocation_lng            DOUBLE PRECISION,
    geolocation_city           TEXT,
    geolocation_state          TEXT
);

-- 3. dim_product: Data produk
CREATE TABLE IF NOT EXISTS raw_schema.dim_product (
    product_id               TEXT NOT NULL,
    product_category_name    TEXT,
    product_name_lenght      INT,
    product_description_lenght INT,
    product_photos_qty       INT,
    product_weight_g         DOUBLE PRECISION,
    product_length_cm        DOUBLE PRECISION,
    product_height_cm        DOUBLE PRECISION,
    product_width_cm         DOUBLE PRECISION,
    PRIMARY KEY (product_id)
);

-- 4. dim_product_category: Terjemahan kategori produk (Portugis -> Inggris)
CREATE TABLE IF NOT EXISTS raw_schema.dim_product_category (
    product_category_name          TEXT NOT NULL,
    product_category_name_english  TEXT,
    PRIMARY KEY (product_category_name)
);

-- 5. dim_seller: Data penjual
CREATE TABLE IF NOT EXISTS raw_schema.dim_seller (
    seller_id               TEXT NOT NULL,
    seller_zip_code_prefix  TEXT,
    seller_city             TEXT,
    seller_state            TEXT,
    PRIMARY KEY (seller_id)
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 6. fact_order: Data pesanan / transaksi utama
CREATE TABLE IF NOT EXISTS raw_schema.fact_order (
    order_id                       TEXT NOT NULL,
    customer_id                    TEXT,
    order_status                   TEXT,
    order_purchase_timestamp       TIMESTAMP,
    order_approved_at              TIMESTAMP,
    order_delivered_carrier_date   TIMESTAMP,
    order_delivered_customer_date  TIMESTAMP,
    order_estimated_delivery_date  TIMESTAMP,
    PRIMARY KEY (order_id)
);

-- 7. fact_order_item: Item detail dalam setiap pesanan
CREATE TABLE IF NOT EXISTS raw_schema.fact_order_item (
    order_id            TEXT NOT NULL,
    order_item_id       INT NOT NULL,
    product_id          TEXT,
    seller_id           TEXT,
    shipping_limit_date TIMESTAMP,
    price               DOUBLE PRECISION,
    freight_value       DOUBLE PRECISION,
    PRIMARY KEY (order_id, order_item_id)
);

-- 8. fact_order_payment: Metode pembayaran per pesanan
CREATE TABLE IF NOT EXISTS raw_schema.fact_order_payment (
    order_id            TEXT NOT NULL,
    payment_sequential  INT NOT NULL,
    payment_type        TEXT,
    payment_installments INT,
    payment_value       DOUBLE PRECISION,
    PRIMARY KEY (order_id, payment_sequential)
);

-- 9. fact_order_review: Ulasan / review per pesanan
CREATE TABLE IF NOT EXISTS raw_schema.fact_order_review (
    review_id                  TEXT NOT NULL,
    order_id                   TEXT,
    review_score               INT,
    review_comment_title       TEXT,
    review_comment_message     TEXT,
    review_creation_date       TIMESTAMP,
    review_answer_timestamp    TIMESTAMP,
    PRIMARY KEY (review_id)
);