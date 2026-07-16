# Panduan Mengajar Sesi 5: Introduction to dbt (Data Build Tool)
**Materi:** Paradigma ELT, Setup dbt Core, Staging Models, & Source Freshness (120 Menit)

---

## 🎯 1. Tujuan Pembelajaran

Setelah sesi ini, peserta diharapkan mampu:
1. Memahami perbedaan paradigma **ETL vs ELT** dan mengapa ELT menjadi standar modern.
2. Melakukan instalasi **dbt Core** dan konfigurasi koneksi ke PostgreSQL lokal.
3. Membuat struktur proyek dbt pertama dengan **Staging Models**.
4. Menggunakan perintah `dbt run`, `dbt test`, dan `dbt docs generate`.

---

## 🗺️ 2. Posisi Sesi 5 dalam Pipeline

```
Sesi 1-2 (Python/Polars)  ──>  Sesi 3-4 (PostgreSQL + SQL)  ──>  SESI 5 (dbt: Setup & Staging)
                                                                        │
                                                                    Sesi 6 (dbt: Marts & Testing)
                                                                        │
                                                              Sesi 7-8 (Orchestrasi & Capstone)
```

> **Kata Kunci:** dbt = **d**ata **b**uild **t**ool — transformasi data langsung di dalam database (ELT).

---

## ⏰ 3. Rencana Alokasi Waktu (120 Menit)

| Durasi | Kegiatan | Metode |
|--------|----------|--------|
| **10 Menit** | **Pembuka: ETL vs ELT Showdown** | Slide + Demo |
| **15 Menit** | **Instalasi dbt Core & PostgreSQL Check** | Live Coding |
| **10 Menit** | **dbt init & profiles.yml Setup** | Live Coding |
| **15 Menit** | **Anatomi Proyek dbt** | Eksplorasi Bareh |
| **40 Menit** | **Membuat Staging Models** | Live Code-Along |
| **20 Menit** | **dbt run & dbt test Pertama** | Praktik Mandiri |
| **10 Menit** | **Review & Penutup** | Q&A |

---

## 🛠️ 4. Panduan Setup & Jalur Live Coding

### A. Prasyarat

1. **PostgreSQL masih berjalan** — Cek dengan:
   ```bash
   docker ps | grep postgres
   ```
2. **Database `dw_nusacode` sudah ada** — Dari Sesi 3, tabel `raw_schema.*` sudah terisi data Olist.
3. **Python 3.9+ sudah terinstall** — Cek dengan:
   ```bash
   python --version
   ```

### B. Pembuka: ETL vs ELT Showdown (10 Menit)

Gunakan analogi **"Dapur Restoran"** untuk menjelaskan:

```
🏛️ ETL (Traditional — Python/Polars yang sudah dipelajari)
   Masak (Transform) di dapur luar → Baru bawa ke meja (Load ke DB)
   ❌ Data besar = dapur penuh sesak
   ❌ Testing manual

🏗️ ELT (Modern — dbt)
   Bawa bahan mentah ke gudang (Load ke DB) → Masak di gudang (Transform via SQL)
   ✅ Database yang masak (pakai kekuatan PostgreSQL)
   ✅ Testing otomatis
   ✅ Dokumentasi auto-generate
```

**Demo singkat:** Tunjukkan script `ingest_to_db.py` dari Sesi 3 yang isinya ETL klasik:
```python
# ETL: Python transform dulu baru load
df = pl.read_parquet("data.parquet")
df_clean = df.filter(pl.col("price") > 0)  # Transform di Python
df_clean.to_sql("table")                    # Baru load ke DB
```

Lalu perlihatkan staging model dbt yang akan mereka buat sebentar lagi:
```sql
-- ELT: Load dulu, transform di DB via dbt
SELECT * FROM raw_schema.table WHERE price > 0
```

> **Pertanyaan Pemantik:** "Kalau data 10 juta baris, transform pakai Python di laptop atau SQL di server PostgreSQL — mana yang lebih cepat?"

### C. Instalasi dbt Core (15 Menit)

**Instalasi via pip:**
```bash
# Install dbt-core dengan adapter PostgreSQL
pip install dbt-core dbt-postgres

# Verifikasi instalasi
dbt --version
```

**Output yang diharapkan:**
```
installed version: 1.8.x
   next version: 1.9.x
   Plugin:
    - postgres: 1.8.x
```

> 💡 **Troubleshooting:** Jika error "command not found", pastikan Python bin ada di PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
> ```

### D. dbt init & profiles.yml Setup (10 Menit)

**Buat proyek dbt pertama:**
```bash
# Inisialisasi proyek dbt
dbt init nusacode_de

# Masuk ke folder proyek
cd nusacode_de
```

**Konfigurasi profiles.yml:**

Jelaskan bahwa `profiles.yml` adalah jembatan antara dbt dan database. Gunakan file template yang sudah disediakan di `pertemuan-05-06-dbt/profiles.yml`.

1. Copy `profiles.yml` ke folder `~/.dbt/`:
   ```bash
   mkdir -p ~/.dbt
   cp /path/to/pertemuan-05-06-dbt/profiles.yml ~/.dbt/profiles.yml
   ```
2. Edit jika perlu (sesuaikan password jika berbeda).
3. Verifikasi koneksi:
   ```bash
   dbt debug
   ```

**Output sukses:**
```
All checks passed!
```

**Jika gagal:**
```
Connection:
  host: localhost  [FAIL]
  ...
```
Periksa: Docker berjalan? Port 5432 benar? PostgreSQL bisa diakses?

### E. Anatomi Proyek dbt (15 Menit)

Jelaskan struktur folder yang dihasilkan oleh `dbt init`:

```
nusacode_de/
├── models/          ← SQL models (.sql) + schema definitions (.yml)
├── analyses/        ← Query ad-hoc (tidak di-run oleh dbt)
├── tests/           ← Test kustom (generic + singular)
├── seeds/           ← File CSV statis
├── macros/          ← Jinja macros (fungsi reusable)
├── snapshots/       ← SCD tipe 2 (perubahan data historis)
├── dbt_project.yml  ← Konfigurasi utama proyek
└── target/          ← Hasil kompilasi (di-gitignore)
```

> **Kata Kunci:** Dalam dbt, kita tidak membuat tabel secara manual. Kita **mendefinisikan model** (SQL SELECT), dan dbt yang mengeksekusinya.

### F. Membuat Staging Models (40 Menit)

**Konsep Staging:**
- Staging = **Bronze/Silver Layer** — data mentah yang dibersihkan ringan.
- Gunakan `{{ source() }}` untuk referensi ke tabel di `raw_schema`.
- Gunakan `{{ ref() }}` untuk referensi antar model dbt.

**Buka file yang sudah disediakan di `pertemuan-05-06-dbt/models/silver/`.**

Jelaskan satu per satu:

#### stg_customers.sql
```sql
WITH source AS (
    SELECT * FROM {{ source('raw_schema', 'dim_customer') }}
),
cleaned AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        TRIM(INITCAP(customer_city)) AS customer_city,
        UPPER(TRIM(customer_state)) AS customer_state
    FROM source
)
SELECT * FROM cleaned
```

**Yang diajarkan:**
1. `{{ source('raw_schema', 'dim_customer') }}` — referensi ke tabel sumber.
2. Pembersihan data: `TRIM`, `INITCAP`, `UPPER`.
3. CTE (`source` → `cleaned`) untuk keterbacaan.

#### stg_orders.sql
```sql
WITH source AS (...),
cleaned AS (
    SELECT
        ...,
        CASE WHEN order_status = 'delivered' THEN TRUE ELSE FALSE END AS is_delivered,
        EXTRACT(EPOCH FROM (order_approved_at - order_purchase_timestamp)) / 3600 AS approval_hours
    FROM source
)
```

**Yang diajarkan:**
1. **Flag columns** dengan CASE WHEN.
2. **Date arithmetic** dengan EXTRACT(EPOCH ...).

#### stg_order_items.sql, stg_products.sql, stg_sellers.sql, stg_payments.sql, stg_reviews.sql

Jelaskan sekilas — polanya sama:
- Source → Cleaning → Select.
- Setiap model fokus pada satu tabel sumber.

**Praktik Bersama:** Minta peserta membuka 2-3 file staging dan menjelaskan apa yang terjadi.

### G. dbt run & dbt test Pertama (20 Menit)

#### dbt run

Jalankan semua silver models:
```bash
dbt run
```

**Output:**
```
17:30:00  Running with dbt=1.8.x
17:30:01  Found 12 models, 5 tests, ...
17:30:01
17:30:02  1 of 12 START sql table model silver.stg_customers  [RUN]
17:30:03  1 of 12 OK created sql table model silver.stg_customers  [CREATE TABLE in 0.25s]
17:30:03  2 of 12 START sql table model silver.stg_orders  [RUN]
...
```

**Yang diajarkan:**
1. dbt mengkompilasi SQL Jinja ke SQL murni.
2. Setiap model menjadi TABLE di schema `silver`.
3. Bisa filter model: `dbt run --select stg_customers`.

#### dbt test

Jalankan test dari `schema.yml`:
```bash
dbt test
```

**Output:**
```
17:35:00  1 of 7 PASS source_unique_raw_schema_dim_customer_customer_id  [PASS]
17:35:00  2 of 7 PASS not_null_stg_customers_customer_id  [PASS]
...
```

**Yang diajarkan:**
1. Test otomatis dari deklarasi di `schema.yml`.
2. `unique`, `not_null` adalah **generic tests** bawaan dbt.
3. Jika ada test FAIL — data perlu diperbaiki.

### H. Visualisasi dengan dbt Docs (Demo Singkat)

Jika waktu memungkinkan, demo:
```bash
# Generate dokumentasi
dbt docs generate

# Buka di browser (jalankan di terminal terpisah)
dbt docs serve
```

**Yang diajarkan:**
1. **Lineage Graph** — visual DAG antar model (staging → staging tidak ada koneksi karena masing-masing dari source).
2. **Model documentation** — deskripsi dari `schema.yml`.

---

## 📝 5. Lembar Contekkan (Cheat Sheet)

### dbt Commands

| Perintah | Fungsi |
|----------|--------|
| `dbt debug` | Cek koneksi database |
| `dbt run` | Jalankan semua model |
| `dbt run --select stg_customers` | Jalankan model spesifik |
| `dbt test` | Jalankan semua test |
| `dbt test --select source:raw_schema` | Test hanya source |
| `dbt docs generate` | Generate dokumentasi |
| `dbt docs serve` | Buka dokumentasi di browser |
| `dbt ls` | List semua model |

### Jinja for dbt

```sql
{{ source('schema', 'table') }}      -- Referensi ke tabel sumber
{{ ref('model_name') }}               -- Referensi ke model lain
{{ config(materialized='table') }}    -- Override materialization
```

### Stage Pattern

```sql
WITH source AS (
    SELECT * FROM {{ source('raw_schema', 'table_name') }}
),
cleaned AS (
    SELECT
        -- kolom dengan cleaning
    FROM source
)
SELECT * FROM cleaned
```

---

## 🧪 6. Practical Challenge (Jika Waktu Lebih)

> **Challenge:** Buat staging model baru `stg_order_items_analysis` yang menambahkan kolom `profit_margin` dengan formula `(price - freight_value) / price`.

```sql
SELECT *,
    CASE
        WHEN price > 0 THEN ROUND((price - freight_value) / price, 2)
        ELSE 0
    END AS profit_margin
FROM {{ ref('stg_order_items') }}
```

---

## 📬 7. Penutup

**Recap:**
- ✅ Paham perbedaan ETL vs ELT
- ✅ dbt terinstall dan terkoneksi ke PostgreSQL
- ✅ Staging models berhasil di-run
- ✅ Data quality test berjalan

**Preview Sesi 6:**
- Konsep **Star Schema** (Fact & Dimension Tables)
- Membuat **Marts Models** (`dim_` & `fct_`)
- **dbt Testing & Documentation** yang lebih dalam

> **"dbt bukan tools — dbt adalah paradigma. Data Engineer masa depan adalah yang menguasai ELT."**