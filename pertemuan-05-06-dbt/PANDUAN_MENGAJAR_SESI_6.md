# Panduan Mengajar Sesi 6: Data Modeling & Star Schema with dbt
**Materi:** Star Schema, Fact & Dimension Tables, dbt Lineage, Testing, & Documentation (120 Menit)

---

## 🎯 1. Tujuan Pembelajaran

Setelah sesi ini, peserta diharapkan mampu:
1. Memahami konsep **Star Schema** dan perbedaan **Fact vs Dimension**.
2. Membuat **Intermediate & Marts Models** (`dim_` & `fct_`) di dbt.
3. Membaca **dbt Lineage Graph** untuk memahami alur data.
4. Menerapkan **data quality tests** (`unique`, `not_null`, `custom`) dan **generate dokumentasi**.

---

## 🗺️ 2. Posisi Sesi 6 dalam Pipeline

```
                    ┌── SESI 5 (dbt Setup & Staging) ──┐
                    │   stg_customers, stg_orders, ...   │
                    └───────────┬────────────────────────┘
                                │
                    ┌───────────▼────────────────────────┐
                    │   SESI 6: DIMENSIONAL MODELING      │
                    │   int_order_details                 │
                    │   int_customer_orders               │
                    │          │                          │
                    │   ┌──────┴──────┐                   │
                    │   │             │                   │
                    │ dim_customers dim_products         │
                    │ dim_sellers   fct_orders            │
                    └────────────────────────────────────┘
```

---

## ⏰ 3. Rencana Alokasi Waktu (120 Menit)

| Durasi | Kegiatan | Metode |
|--------|----------|--------|
| **10 Menit** | **Pembuka: Star Schema Concept** | Slide + Whiteboard |
| **15 Menit** | **Review Sesi 5 + dbt run** | Live Coding |
| **20 Menit** | **Intermediate Models** | Live Code-Along |
| **30 Menit** | **Marts Models (Fact & Dimension)** | Live Code-Along |
| **20 Menit** | **dbt Lineage & Visualisasi** | Demo Interaktif |
| **15 Menit** | **Data Testing & Documentation** | Praktik Mandiri |
| **10 Menit** | **Review & Penutup** | Q&A |

---

## 🛠️ 4. Panduan Setup & Jalur Live Coding

### A. Prasyarat (Ceklist Cepat)

```bash
# 1. Pastikan Sesi 5 sudah completed
dbt ls                      # Harusnya ada 7+ staging models
dbt source freshness        # Cek apakah data masih fresh

# 2. Pastikan PostgreSQL masih berjalan
docker ps | grep postgres
```

### B. Pembuka: Star Schema Concept (10 Menit)

Gunakan analogi **"Perpustakaan"** untuk menjelaskan Star Schema:

```
📚 DIMENSION TABLES (Buku Referensi)
   | Nama Buku | Pengarang | Kategori | Rak |
   |-----------|-----------|----------|-----|
   | HTML 101  | John      | Teknologi| A1  |
   | SQL Guide | Jane      | Teknologi| A2  |

   ✅ Data konteks/atribut — deskriptif
   ✅ Berubah lambat (slow-changing)
   ✅ Tabel kecil — bisa di-cache

📋 FACT TABLE (Katalog Peminjaman)
   | Tgl Pinjam | Buku_ID | Anggota_ID | Durasi |
   |------------|---------|------------|--------|
   | 2024-01-01 | B001    | M001       | 7 hari |
   | 2024-01-02 | B002    | M001       | 3 hari |

   ✅ Data transaksi/metrik — numerik
   ✅ Bertambah terus (append-only)
   ✅ Tabel besar — perlu indexing

⭐ STAR SCHEMA = Fact Table di tengah, Dimension Tables di sekelilingnya
```

**Hubungkan dengan proyek Olist:**
- `dim_customers` → Siapa yang belanja?
- `dim_products` → Apa yang dibeli?
- `dim_sellers` → Siapa yang menjual?
- `fct_orders` → Berapa transaksinya?

> **Pertanyaan Pemantik:** "Kalau kita ingin tahu 'produk apa yang paling laris di kota Bandung' — tabel mana yang kita JOIN?"

### C. Review Sesi 5 + dbt run (15 Menit)

**Langkah 1:** Pastikan semua sudah punya project dbt dari Sesi 5.

**Langkah 2:** Jalankan ulang staging models untuk memastikan semuanya fresh:
```bash
cd nusacode_de
dbt clean       # Hapus target/ lama
dbt run         # Run ulang semua models
dbt test        # Pastikan semua test PASS
```

**Langkah 3:** Cek hasil di database:
```sql
-- Di DBeaver, cek apakah schema dbt_staging sudah ada
SELECT * FROM information_schema.schemata WHERE schema_name LIKE 'dbt_%';
-- Harusnya: dbt_staging, dbt_intermediate, dbt_marts (masih kosong)
```

### D. Intermediate Models (20 Menit)

**Konsep:** Intermediate = **"Dapur tengah"** — tempat menggabungkan beberapa staging models sebelum disajikan ke marts.

#### int_order_details.sql

Buka file `models/intermediate/int_order_details.sql`.

Jelaskan alurnya:

```
stg_orders ──┐
stg_order_items ──┤
stg_payments ──┤──> int_order_details
stg_reviews ──┘
```

```sql
WITH orders AS (SELECT * FROM {{ ref('stg_orders') }}),
items AS (SELECT * FROM {{ ref('stg_order_items') }}),
payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment,
        COUNT(DISTINCT payment_type) AS payment_method_count,
        STRING_AGG(DISTINCT payment_type, ', ') AS payment_types
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id
),
reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS avg_review_score,
        COUNT(review_id) AS review_count
    FROM {{ ref('stg_reviews') }}
    GROUP BY order_id
),
joined AS (
    SELECT
        o.order_id, o.customer_id, ...,
        -- Item summary
        COUNT(DISTINCT i.order_item_id) AS item_count,
        SUM(i.price) AS total_price,
        ...
    FROM orders o
    LEFT JOIN items i ON o.order_id = i.order_id
    LEFT JOIN payments p ON o.order_id = p.order_id
    LEFT JOIN reviews r ON o.order_id = r.order_id
    GROUP BY ...
)
```

**Yang diajarkan:**
1. **Multiple CTEs** — menggunakan 4 CTE sekaligus (`orders`, `items`, `payments`, `reviews`).
2. **LEFT JOIN** — karena tidak semua order punya review.
3. **GROUP BY** — karena ada agregasi (SUM, COUNT, AVG).
4. **`{{ ref('model_name') }}`** — koneksi antar model dbt.

#### int_customer_orders.sql

Buka file `models/intermediate/int_customer_orders.sql`.

```sql
WITH customers AS (SELECT * FROM {{ ref('stg_customers') }}),
order_details AS (SELECT * FROM {{ ref('int_order_details') }}),
customer_summary AS (
    SELECT
        c.customer_id, ...,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(o.total_order_value) AS total_revenue,
        MIN(o.order_purchase_timestamp) AS first_order_date,
        MAX(o.order_purchase_timestamp) AS last_order_date
    FROM customers c
    LEFT JOIN order_details o ON c.customer_id = o.customer_id
    GROUP BY ...
)
```

**Yang diajarkan:**
1. **Ref ke intermediate lain** — `{{ ref('int_order_details') }}`.
2. **Agregasi per customer** — COUNT, SUM, MIN, MAX.
3. Jika waktu lebih, diskusikan: "Kenapa pakai LEFT JOIN bukan INNER JOIN?"

#### dbt run untuk intermediate

Minta peserta menjalankan intermediate models:
```bash
dbt run --select int_*
```

**Output:**
```
1 of 2 START view model dbt_intermediate.int_order_details  [RUN]
2 of 2 START view model dbt_intermediate.int_customer_orders  [RUN]
```

### E. Marts Models: Fact & Dimension Tables (30 Menit)

**Konsep:** Marts = **Gold Layer** — data siap-pakai untuk analisis dan BI tools.

#### dbt_project.yml config

Sebelum membuat model, jelaskan **materialization**:

```yaml
# dbt_project.yml
models:
  nusacode_de:
    staging:
      +materialized: view       # Ringan, data selalu fresh
    intermediate:
      +materialized: view       # Ringan
    marts:
      +materialized: table      # Berat, tapi cepat diquery
```

> **Mengapa marts pakai TABLE?** Karena data di marts akan diquery berulang kali oleh BI tools (Metabase, Grafana). TABLE lebih cepat daripada VIEW yang dihitung ulang setiap kali.

#### dim_customers.sql

Buka `models/marts/dim_customers.sql`:

```sql
WITH source AS (
    SELECT * FROM {{ ref('int_customer_orders') }}
)
SELECT
    customer_id, customer_unique_id,
    customer_city, customer_state,
    total_orders, delivered_orders,
    -- Conversion rate
    CASE WHEN total_orders > 0
        THEN ROUND(delivered_orders::NUMERIC / total_orders, 2)
        ELSE 0
    END AS delivery_rate,
    total_revenue, avg_review_score,
    first_order_date, last_order_date,
    -- Customer tenure
    CASE WHEN first_order_date IS NOT NULL AND last_order_date IS NOT NULL
        THEN EXTRACT(DAY FROM (last_order_date - first_order_date))
        ELSE 0
    END AS customer_tenure_days
FROM source
```

**Yang diajarkan:**
1. **Derived metrics** — `delivery_rate`, `customer_tenure_days`.
2. **CASE WHEN untuk safety** — menghindari division by zero.
3. **Grain: satu baris per customer** — dimension table.

#### dim_products.sql

Buka `models/marts/dim_products.sql`:

```sql
WITH source AS (...),
order_items AS (
    SELECT product_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(price) AS total_revenue
    FROM {{ ref('stg_order_items') }}
    GROUP BY product_id
)
SELECT
    p.product_id, ...,
    COALESCE(oi.total_orders, 0) AS total_orders
FROM source p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
```

**Yang diajarkan:**
1. **COALESCE untuk null handling** — produk yang belum pernah terjual tetap muncul.
2. **LEFT JOIN** — semua produk (termasuk yang 0 penjualan).

#### dim_sellers.sql

Buka `models/marts/dim_sellers.sql`:

```sql
WITH source AS (...),
order_items AS (...),
reviews AS (
    SELECT oi.seller_id,
        ROUND(AVG(r.review_score), 2) AS avg_customer_review
    FROM {{ ref('stg_reviews') }} r
    JOIN {{ ref('stg_order_items') }} oi ON r.order_id = oi.order_id
    GROUP BY oi.seller_id
)
```

**Yang diajarkan:**
1. **JOIN antar staging** — `stg_reviews` JOIN `stg_order_items` untuk mendapatkan seller_id.
2. **AVG + ROUND** — rata-rata review tiap seller.

#### fct_orders.sql

Buka `models/marts/fct_orders.sql`:

```sql
WITH source AS (
    SELECT * FROM {{ ref('int_order_details') }}
)
SELECT ...
WHERE NOT is_canceled  -- Filter data yang valid
```

**Yang diajarkan:**
1. **Fact table** — grain: satu baris per transaksi (order_id).
2. **Filtering** — hanya data valid yang masuk ke marts.

#### Final dbt run + Lineage (20 Menit)

**Jalankan semua models:**
```bash
dbt run
```

Amati output — dbt akan menjalankan model dalam urutan yang benar sesuai DAG:
1. `stg_*` (7 models)
2. `int_*` (2 models)
3. `dim_*` + `fct_*` (4 models)

**Hasil:** Schema `dbt_marts` berisi 4 tabel:
```sql
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'dbt_marts';
```

#### dbt Lineage Graph

Jalankan dokumentasi dan buka lineage:
```bash
dbt docs generate
dbt docs serve
```

Buka browser di `http://localhost:8080`.

**Yang diajarkan:**
1. **Lineage Graph** — panah dari source → staging → intermediate → marts.
2. **Model details** — klik model untuk melihat deskripsi, kolom, dan test.
3. **Ref mapping** — semua `{{ ref() }}` otomatis menjadi koneksi di graph.

```
Contoh lineage untuk dim_customers:
    raw_schema.dim_customer ──> stg_customers ──> int_customer_orders ──> dim_customers
                                                                  ▲
    raw_schema.fact_order ──> stg_orders ──> int_order_details ────┘
```

### F. Data Testing & Documentation (15 Menit)

#### Generic Tests

Buka `models/marts/schema.yml`:

```yaml
models:
  - name: dim_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: total_orders
        tests:
          - not_null
```

**Yang diajarkan:**
1. **Generic tests** — `unique`, `not_null`, `accepted_values`, `relationships`.
2. **Test per model** — setiap model di marts punya test sendiri.

#### Jalankan Tests

```bash
dbt test --select dim_customers
```

Jika semua PASS → data kualitas bagus.
Jika ada FAIL → diskusikan penyebabnya.

#### Custom Test (Jika Waktu Cukup)

Buat file `tests/assert_positive_revenue.sql`:
```sql
-- Tidak boleh ada customer dengan revenue negatif
SELECT customer_id, total_revenue
FROM {{ ref('dim_customers') }}
WHERE total_revenue < 0
```

> **Test ini disebut "singular test"** — test yang ditulis sebagai SQL query. Jika query mengembalikan baris → test FAIL.

### G. dbt Source Freshness (Demo Singkat)

Jika waktu memungkinkan, tambahkan konsep source freshness:
```yaml
# Di schema.yml bagian sources
sources:
  - name: raw_schema
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    loaded_at_field: order_purchase_timestamp
```

Jalankan:
```bash
dbt source freshness
```

> **Konsep:** "Data di raw_schema sudah berapa lama tidak di-update?" — penting untuk staging data pipeline.

---

## 🧪 5. Practical Challenge

### Challenge 1: Eksplorasi Lineage
Minta peserta membuka dbt docs, klik `dim_customers`, dan jawab:
- Source tables apa saja yang menjadi input?
- Ada berapa test yang dijalankan?

### Challenge 2: Buat Test Kustom
```sql
-- tests/assert_valid_review_score.sql
-- Skor review harus antara 1-5
SELECT review_id, review_score
FROM {{ ref('stg_reviews') }}
WHERE review_score < 1 OR review_score > 5
```

---

## 📝 6. Cheat Sheet — Dimensional Modeling

### Star Schema Pattern

```
┌─────────────────────────────────────────────┐
│              fact_table (fct_)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ dim_1    │  │ dim_2    │  │ dim_3    │  │
│  │ (PK)     │  │ (FK)     │  │ (FK)     │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│  │           │  │           │  │           │
│  ▼           ▼  ▼           ▼  ▼           ▼
│  metrics / measures / numbers               │
└─────────────────────────────────────────────┘
```

### dbt Materialization Decision

| Layer | Materialization | Alasan |
|-------|----------------|--------|
| Staging | VIEW | Ringan, data selalu mengikuti source |
| Intermediate | VIEW | Fleksibel untuk transformasi lanjutan |
| Marts | TABLE | Cepat diquery, perlu refresh periodik |

### dbt Test Types

| Test | Fungsi | Contoh |
|------|--------|--------|
| `unique` | Tidak ada duplikat | ID tidak boleh sama |
| `not_null` | Tidak boleh null | Kolom wajib diisi |
| `accepted_values` | Nilai tertentu saja | Status: 'delivered', 'shipped' |
| `relationships` | Referensi valid | FK ke tabel lain |
| Custom (singular) | SQL SELECT | Revenue tidak negatif |

### dbt Commands untuk Sesi 6

```bash
dbt run                    # Run semua model
dbt run --select int_*     # Run intermediate saja
dbt run --select marts     # Run marts saja
dbt test --select marts    # Test marts saja
dbt docs generate          # Generate docs
dbt docs serve             # Buka docs di browser
dbt source freshness       # Cek umur data
```

---

## 📬 7. Penutup

**Recap:**
- ✅ Paham Star Schema (Fact vs Dimension)
- ✅ Intermediate & Marts models berhasil di-run
- ✅ Lineage Graph menunjukkan DAG antar model
- ✅ Data quality test berjalan otomatis

**Preview Sesi 7-8:**
- **Pipeline Orchestration** — bagaimana menjalankan semua ini secara otomatis?
- **GitHub Actions** — CI/CD untuk pipeline data
- **Final Project** — menggabungkan semua yang sudah dipelajari

### Tugas 3: "The Transformation Layer"

```markdown
🚀 **TUGAS 3: DBT TRANSFORMATION LAYER** 🚀

### 📋 Deskripsi
Gunakan dbt untuk mengubah data mentah (raw_schema) menjadi Star Schema
yang siap-pakai untuk analisis.

### ⚙️ Langkah-langkah
1. Jalankan seluruh dbt project (stg → int → marts)
2. Verifikasi lineage graph di dbt docs
3. Tambahkan 3 test kustom:
   - Pastikan tidak ada customer_id null di fct_orders
   - Pastikan total_order_value > 0
   - Pastikan review_score antara 1-5
4. Tulis 2 query analitik di atas dbt_marts:
   - 1 Query dengan CTE (analisis product category performance)
   - 1 Query dengan Window Function (customer ranking per state)

### 🏆 Nilai A
✅ Semua model berjalan (`dbt run` sukses)
✅ Semua test pass (`dbt test` sukses)
✅ Lineage graph lengkap di dbt docs
✅ Query analitik menghasilkan insight bisnis
✅ Ada screenshot lineage graph

"Transform data like a pro. Build, test, and serve!" ⭐
```

> **"Dimensional modeling bukan sekadar teori — ini adalah bahasa universal Data Engineer untuk berkomunikasi dengan stakeholder bisnis."**