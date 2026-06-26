# dbt Data Transformation Layer — Nusacode DE Beginner

## 📋 Overview

Module ini mencakup **Sesi 5 & 6** dari kursus Data Engineer Beginner. Fokus utama adalah **Data Transformation** menggunakan **dbt (Data Build Tool)** dengan pendekatan **ELT (Extract-Load-Transform)**.

```
┌─────────────────────────────────────────────────────────┐
│              DBT TRANSFORMATION PIPELINE                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  raw_schema (PostgreSQL)                                 │
│    │                                                     │
│    ▼                                                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │  🥉 STAGING LAYER (Bronze/Silver)                │    │
│  │  stg_customers  stg_orders  stg_order_items      │    │
│  │  stg_products   stg_sellers  stg_payments        │    │
│  │  stg_reviews                                      │    │
│  │  → Pembersihan ringan, type casting, renaming     │    │
│  └───────────────────────┬──────────────────────────┘    │
│                          │                                │
│                          ▼                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │  🔷 INTERMEDIATE LAYER (Silver)                   │    │
│  │  int_order_details  int_customer_orders           │    │
│  │  → Join antar staging, agregasi awal              │    │
│  └───────────────────────┬──────────────────────────┘    │
│                          │                                │
│                          ▼                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │  🥇 MARTS LAYER (Gold — Star Schema)             │    │
│  │  dim_customers  dim_products  dim_sellers         │    │
│  │  fct_orders                                       │    │
│  │  → Siap-pakai untuk BI tools & analisis           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ✅ dbt test — data quality otomatis                     │
│  📊 dbt docs — lineage graph & dokumentasi               │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Project Structure

```
pertemuan-05-06-dbt/
├── README.md                         ← Panduan ini
├── dbt_project.yml                   ← Konfigurasi utama dbt
├── profiles.yml                      ← Koneksi database (template)
│
├── PANDUAN_MENGAJAR_SESI_5.md        ← Panduan mengajar sesi 5
├── PANDUAN_MENGAJAR_SESI_6.md        ← Panduan mengajar sesi 6
│
├── models/
│   ├── staging/                      ← Bronze layer
│   │   ├── schema.yml                ← Source & test definitions
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   ├── stg_order_items.sql
│   │   ├── stg_products.sql
│   │   ├── stg_sellers.sql
│   │   ├── stg_payments.sql
│   │   └── stg_reviews.sql
│   │
│   ├── intermediate/                 ← Silver layer
│   │   ├── int_order_details.sql
│   │   └── int_customer_orders.sql
│   │
│   └── marts/                        ← Gold layer (Star Schema)
│       ├── schema.yml                ← Marts test definitions
│       ├── dim_customers.sql
│       ├── dim_products.sql
│       ├── dim_sellers.sql
│       └── fct_orders.sql
│
├── tests/                            ← Singular custom tests
│   └── (buat sendiri sesuai challenge)
│
├── analyses/                         ← Query ad-hoc
├── macros/                           ← Jinja macros
├── snapshots/                        ← SCD type 2
└── seeds/                            ← CSV data
```

---

## ⚙️ Setup Cepat

### Prasyarat

1. **PostgreSQL** — dari Sesi 3 (Docker Compose), database `dw_nusacode` sudah ada dengan data Olist.
2. **Python 3.9+** — untuk instalasi dbt.

### Instalasi dbt

```bash
pip install dbt-core dbt-postgres
dbt --version
```

### Konfigurasi Koneksi

Copy `profiles.yml` ke `~/.dbt/`:

```bash
mkdir -p ~/.dbt
cp profiles.yml ~/.dbt/profiles.yml
# Edit password jika perlu
```

Verifikasi:

```bash
dbt debug
```

### Jalankan Pipeline

```bash
# Run semua model (stg → int → marts)
dbt run

# Run spesifik layer
dbt run --select staging
dbt run --select marts

# Jalankan test data quality
dbt test

# Generate & buka dokumentasi
dbt docs generate
dbt docs serve
```

---

## 🚀 dbt Commands Reference

| Perintah | Fungsi |
|----------|--------|
| `dbt debug` | Cek koneksi database |
| `dbt run` | Jalankan semua model |
| `dbt run --select stg_*` | Jalankan hanya staging |
| `dbt run --select int_*` | Jalankan hanya intermediate |
| `dbt run --select marts` | Jalankan hanya marts |
| `dbt test` | Jalankan semua data test |
| `dbt test --select marts` | Test hanya marts layer |
| `dbt docs generate` | Generate dokumentasi HTML |
| `dbt docs serve` | Buka dokumentasi di browser |
| `dbt ls` | List semua model |
| `dbt source freshness` | Cek umur data source |

---

## 🧪 Data Quality Tests

### Generic Tests (dari schema.yml)

| Test | Fungsi |
|------|--------|
| `unique` | Tidak ada nilai duplikat |
| `not_null` | Tidak ada nilai null |
| `accepted_values` | Nilai harus dari daftar tertentu |
| `relationships` | Foreign key valid |

### Singular Tests (di folder `tests/`)

Buat file `.sql` di folder `tests/`. Jika query mengembalikan baris → test FAIL.

Contoh `tests/assert_positive_revenue.sql`:

```sql
SELECT customer_id, total_revenue
FROM {{ ref('dim_customers') }}
WHERE total_revenue < 0
```

---

## 🧑‍🏫 Untuk Pengajar

### Sesi 5: Introduction to dbt (120 menit)

- **Paradigma ELT vs ETL** — analogi dapur restoran
- **Instalasi dbt Core** — pip install
- **Setup profiles.yml** — koneksi ke PostgreSQL
- **Staging Models** — source → cleaned → select
- **dbt run & dbt test** — eksekusi pertama

📖 Lihat [PANDUAN_MENGAJAR_SESI_5.md](./PANDUAN_MENGAJAR_SESI_5.md)

### Sesi 6: Data Modeling & Star Schema (120 menit)

- **Star Schema** — Fact vs Dimension tables
- **Intermediate Models** — joining staging tables
- **Marts Models** — dim_ & fct_ tables
- **dbt Lineage Graph** — visual DAG
- **Data Testing & Documentation**

📖 Lihat [PANDUAN_MENGAJAR_SESI_6.md](./PANDUAN_MENGAJAR_SESI_6.md)

---

## 💭 Python vs dbt: Sebuah Refleksi untuk Kurikulum

### Apakah perlu membagikan alternatif Python?

**Jawaban singkat: Tidak perlu di sesi 5-6, tapi bisa sebagai referensi/side-note.**

### Kenapa?

| Aspek | dbt (ELT) | Python (ETL) |
|-------|-----------|--------------|
| **Paradigma** | Transform di DB | Transform di aplikasi |
| **Bahasa** | SQL murni | Python (pandas/polars) |
| **Testing** | Bawaan (`dbt test`) | Manual (assert, pytest) |
| **Dokumentasi** | Auto-generate (`dbt docs`) | Manual (docstring, mkdocs) |
| **Lineage** | Auto-track (`ref()`) | Manual tracking |
| **Performance** | Pakai kekuatan DB | Terbatas RAM lokal |
| **Use case** | Data Warehouse | Data Processing / ETL awal |

### Argumen untuk **tidak** mengajarkan Python paralel di sesi 5-6:

1. **Beban kognitif** — Peserta baru belajar SQL di sesi 3-4. dbt adalah SQL dengan Jinja. Menambahkan Python parallel akan membingungkan karena:
   - Python di sesi 1-2 = data ingestion & eksplorasi
   - dbt di sesi 5-6 = transformasi data di DB
   - Keduanya punya *use case berbeda*

2. **Waktu terbatas** — 120 menit per sesi sudah padat:
   - Sesi 5: instalasi, setup, staging, run pertama
   - Sesi 6: star schema, intermediate, marts, lineage, testing
   
   Menambahkan Python comparison akan memakan minimal 30-45 menit.

3. **Konteks sudah dibangun** — Sesi 5 dibuka dengan ETL vs ELT showdown yang menggunakan Python (ETL) sebagai pembanding. Ini sudah cukup.

### Alternatif: side-note di sesi 5

Jika tetap ingin menunjukkan alternatif Python, cukup 5 menit di awal sesi 5:

```python
# "Ini yang akan kita ganti dengan dbt:"
# ETL style (Python) → Transform dulu, baru load
df = pl.read_sql("SELECT * FROM raw_schema.dim_customer", conn)
df_clean = df.with_columns(
    pl.col("customer_city").str.to_titlecase(),
    pl.col("customer_state").str.to_uppercase()
)
df_clean.to_sql("stg_customers", conn)
```

vs

```sql
-- ELT style (dbt) → Load dulu, transform di DB
{{ config(materialized='view') }}
SELECT
    customer_id,
    TRIM(INITCAP(customer_city)) AS customer_city,
    UPPER(TRIM(customer_state)) AS customer_state
FROM {{ source('raw_schema', 'dim_customer') }}
```

> **Kesimpulan:** dbt bukan *pengganti* Python, tapi *evolusi* — dari ETL ke ELT. Python tetap powerful untuk data ingestion, eksplorasi, dan ML pipeline. dbt unggul untuk transformasi terstruktur di Data Warehouse.

---

## 📚 Daftar Source Data (Olist E-Commerce)

Source tables di `raw_schema`:

| Tabel | Isi | Baris |
|-------|-----|-------|
| `dim_customer` | Data pelanggan | ~100rb |
| `dim_product` | Data produk | ~33rb |
| `dim_seller` | Data penjual | ~3rb |
| `dim_product_category` | Kategori produk (PT-EN) | ~70 |
| `fact_order` | Pesanan | ~100rb |
| `fact_order_item` | Item per pesanan | ~115rb |
| `fact_order_payment` | Pembayaran | ~105rb |
| `fact_order_review` | Review | ~100rb |
| `dim_geolocation` | Data geolokasi | ~1jt |

---

## 🏆 Tugas 3: "The Transformation Layer"

> Gunakan dbt untuk mengubah data mentah (raw_schema) menjadi Star Schema yang siap-pakai untuk analisis.

**Langkah:**
1. Jalankan seluruh pipeline: `dbt run`
2. Verifikasi lineage graph: `dbt docs serve`
3. Buat 3 test kustom di folder `tests/`
4. Tulis 2 query analitik di atas `dbt_marts`

**Kriteria Nilai A:**
- ✅ Semua model berjalan sukses
- ✅ Semua test pass
- ✅ Lineage graph lengkap
- ✅ Query menghasilkan insight bisnis
- ✅ Screenshot lineage graph