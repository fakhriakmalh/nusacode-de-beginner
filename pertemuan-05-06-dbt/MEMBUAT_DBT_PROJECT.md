# Panduan Membuat dbt Project — NusaCode DE Beginner

Panduan ini menjelaskan cara membuat project dbt dari awal, berdasarkan praktik yang digunakan di folder `pertemuan-05-06-dbt`.

---

## 1. Inisialisasi Project

```bash
# Buat project baru
dbt init nusacode_de

# Masuk ke folder project
cd nusacode_de
```

Struktur yang dihasilkan:

```
nusacode_de/
├── models/            ← SQL models (.sql) + schema definitions (.yml)
├── analyses/          ← Query ad-hoc (tidak di-run oleh dbt)
├── tests/             ← Test kustom (generic + singular)
├── seeds/             ← File CSV statis
├── macros/            ← Jinja macros (fungsi reusable)
├── snapshots/         ← SCD tipe 2 (perubahan data historis)
├── dbt_project.yml    ← Konfigurasi utama proyek
└── target/            ← Hasil kompilasi (di-gitignore)
```

---

## 2. Konfigurasi `dbt_project.yml`

File ini adalah pusat konfigurasi project dbt. Berikut isi file `dbt_project.yml` dari project ini beserta penjelasan tiap field:

```yaml
name: 'nusacode_de'
version: '1.0.0'
config-version: 2
profile: nusacode_de

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  nusacode_de:
    staging:
      +schema: staging

    marts:
      +schema: marts
```

### Field-by-field Explanation

| Field | Value | Fungsi |
|-------|-------|--------|
| `name` | `nusacode_de` | Nama project. **Wajib** cocok dengan key di bagian `models:` (line 30) |
| `version` | `1.0.0` | Versi project (opsional, untuk semver) |
| `config-version` | `2` | Versi format konfigurasi dbt. **Harus 2** untuk dbt v1.0+ |
| `profile` | `nusacode_de` | Nama profile yang harus cocok dengan key di `profiles.yml` (line 11) |
| `model-paths` | `["models"]` | Folder tempat dbt mencari file `.sql` model |
| `analysis-paths` | `["analyses"]` | Folder untuk query analisis (tidak dieksekusi dbt run) |
| `test-paths` | `["tests"]` | Folder untuk singular tests (file `.sql` sendiri) |
| `seed-paths` | `["seeds"]` | Folder untuk file CSV statis (dimuat via `dbt seed`) |
| `macro-paths` | `["macros"]` | Folder untuk file Jinja macro `.sql` |
| `snapshot-paths` | `["snapshots"]` | Folder untuk snapshot SCD Type 2 |
| `target-path` | `"target"` | Folder output kompilasi (di-gitignore) |
| `clean-targets` | `["target", "dbt_packages"]` | Folder yang dihapus saat `dbt clean` |

### Bagian `models:` — Routing Schema per Subfolder

```yaml
models:
  nusacode_de:        # ← HARUS sama dengan `name:` di atas
    staging:          # ← subfolder di dalam models/
      +schema: staging   # → semua file di models/staging/ pakai schema "staging"
    marts:            # ← subfolder di dalam models/
      +schema: marts     # → semua file di models/marts/ pakai schema "marts"
```

- **`+schema: staging`** memberitahu dbt: "semua model di folder `models/staging/` harus dibuat di schema/database bernama `staging`".
- Tanpa macro `generate_schema_name` (lihat bagian 4), dbt akan menggabungkan nama schema misalnya menjadi `public_staging`.
- `materialized`, `engine`, `order_by` dll **tidak diatur di sini** — semuanya di-set via `{{ config() }}` di masing-masing file SQL (lihat bagian 5).

---

## 3. Konfigurasi `profiles.yml` (ClickHouse)

`profiles.yml` adalah jembatan antara dbt dan database. Berikut isi file `profiles.yml` dari project ini:

```yaml
nusacode_de:
  target: dev
  outputs:
    dev:
      type: clickhouse

      host: "{{ env_var('DBT_HOST') }}"
      port: "{{ env_var('DBT_PORT') | int }}"
      user: "{{ env_var('DBT_USER') }}"
      password: "{{ env_var('DBT_PASSWORD') }}"
      schema: "{{ env_var('DBT_SCHEMA') }}"
      secure: {{ env_var('DBT_SECURE', 'false') | lower }}

      threads: "{{ env_var('DBT_THREADS') | int }}"
      connect_timeout: "{{ env_var('DBT_CONNECT_TIMEOUT') | int }}"
      retries: 1
```

### Field-by-field Explanation

| Field | Value | Fungsi |
|-------|-------|--------|
| `nusacode_de` | — | Nama profile. **Wajib cocok** dengan `profile:` di `dbt_project.yml` |
| `target` | `dev` | Environment target yang aktif (bisa `dev`, `prod`, `staging`) |
| `outputs.dev.type` | `clickhouse` | Adapter database. Untuk ClickHouse pakai `clickhouse`, untuk PostgreSQL `postgres` |
| `host` | `{{ env_var('DBT_HOST') }}` | Hostname database (dari env var) |
| `port` | `{{ env_var('DBT_PORT') \| int }}` | Port koneksi. ClickHouse HTTP default: `8123`. Filter `\| int` mengubah string ke integer |
| `user` | `{{ env_var('DBT_USER') }}` | Username database |
| `password` | `{{ env_var('DBT_PASSWORD') }}` | Password database (kosongkan jika default ClickHouse tanpa password) |
| `schema` | `{{ env_var('DBT_SCHEMA') }}` | **Default schema/database** di ClickHouse. Biasanya `default` |
| `secure` | `{{ env_var('DBT_SECURE', 'false') \| lower }}` | HTTPS/TLS. `false` untuk localhost, `true` untuk production. `\| lower` memastikan huruf kecil |
| `threads` | `{{ env_var('DBT_THREADS') \| int }}` | Jumlah thread paralel untuk eksekusi model. Default: `4` |
| `connect_timeout` | `{{ env_var('DBT_CONNECT_TIMEOUT') \| int }}` | Timeout koneksi dalam detik |
| `retries` | `1` | Jumlah percobaan ulang koneksi jika gagal |

### Kenapa pakai `env_var()`?

Semua nilai kredensial menggunakan `{{ env_var('NAMA_VAR') }}` — bukan hardcoded — agar:

1. **Aman** — password tidak tercatat di git
2. **Portabel** — bisa dipakai oleh different user tanpa edit file
3. **Environment-specific** — ganti `DBT_HOST` untuk pindah dari local ke server

Nilai environment variable disimpan di file `.env`:

```ini
DBT_HOST=localhost
DBT_PORT=8123
DBT_USER=default
DBT_PASSWORD=
DBT_SCHEMA=default
DBT_SECURE=false
DBT_THREADS=4
DBT_CONNECT_TIMEOUT=10
DBT_PROFILES_DIR=/home/ffkhr/Documents/nusacode-de-beginner/pertemuan-05-06-dbt
```

### Lokasi `profiles.yml`

Ada dua opsi:

**Opsi A — Default di `~/.dbt/profiles.yml`** (global untuk semua project):

```bash
mkdir -p ~/.dbt
cp /path/to/profiles.yml ~/.dbt/profiles.yml
```

**Opsi B — Custom via `DBT_PROFILES_DIR`** (per project, digunakan di sini):

```bash
export DBT_PROFILES_DIR=/home/ffkhr/Documents/nusacode-de-beginner/pertemuan-05-06-dbt
```

### Verifikasi Koneksi

```bash
dbt debug
```

Output sukses: `All checks passed!`

---

## 4. Macro `generate_schema_name` — Kontrol Naming Schema

### Masalah

Secara default, dbt menggabungkan `target.schema` dengan `custom_schema` yang didefinisikan di `dbt_project.yml`. Contoh: jika `target.schema = public` dan `+schema: staging`, maka tabel akan dibuat di schema `public_staging`.

### Solusi

Override macro `generate_schema_name` di `macros/generate_schema_name.sql`:

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name | default(target.schema) }}
{%- endmacro %}
```

**Cara kerja:**
- Jika model punya `+schema: staging` → `custom_schema_name = 'staging'` → schema tabel `staging`
- Jika model tidak punya `+schema` → `custom_schema_name = None` → fallback ke `target.schema` (biasanya `public`)

Tanpa macro ini, schema akan menjadi `public_staging` dan `public_marts` (kombinasi target + custom). Dengan macro ini, schema menjadi `staging` dan `marts` sesuai yang didefinisikan.

### Cara Penggunaan

1. Buat folder `macros/` di root project
2. Buat file `macros/generate_schema_name.sql` dengan isi di atas
3. Jalankan `dbt run` → tabel akan dibuat di schema sesuai `+schema`

---

## 5. Per-Model `{{ config() }}` Block

Setiap file `.sql` di folder `models/` memiliki block `{{ config(...) }}` di baris pertama. Block ini mendefinisikan bagaimana dbt mengeksekusi dan membuat tabel di ClickHouse.

Berikut contoh isi masing-masing file SQL:

### Staging Models

Semua staging model (`models/staging/stg_*.sql`) menggunakan config yang sama — hanya `order_by` yang berbeda sesuai primary key:

```sql
-- models/staging/stg_customers.sql
{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='customer_id'
) }}

WITH source AS (
    SELECT * FROM {{ source('public', 'dim_customer') }}
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

| File | `order_by` |
|------|------------|
| `stg_customers.sql` | `customer_id` |
| `stg_orders.sql` | `order_id` |
| `stg_order_items.sql` | `(order_id, order_item_id)` — composite key |
| `stg_products.sql` | `product_id` |
| `stg_sellers.sql` | `seller_id` |
| `stg_payments.sql` | `(order_id, payment_sequential)` — composite key |
| `stg_reviews.sql` | `review_id` |

### Dimension Models (Marts)

```sql
-- models/marts/dim_customers.sql
{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='customer_id'
) }}

WITH customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
...
```

| File | `order_by` |
|------|------------|
| `dim_customers.sql` | `customer_id` |
| `dim_products.sql` | `product_id` |
| `dim_sellers.sql` | `seller_id` |

### Fact Model (Marts) — Incremental

```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    engine='ReplacingMergeTree()',
    unique_key='order_id',
    incremental_strategy='delete+insert',
    order_by='order_id',
    partition_by='toYYYYMM(order_purchase_timestamp)'
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
...
```

### Field-by-field Explanation

| Config | Staging / Dim | Fact (fct_orders) |
|--------|---------------|-------------------|
| `materialized` | `'table'` — Dibuat ulang tiap `dbt run` (full refresh) | `'incremental'` — Hanya tambah/update data baru |
| `engine` | `'MergeTree()'` — Engine ClickHouse default | `'ReplacingMergeTree()'` — Otomatis dedup berdasarkan `unique_key` |
| `order_by` | Sesuai primary key (lihat tabel di atas) | `'order_id'` — Sorting key ClickHouse |
| `unique_key` | — | `'order_id'` — Key untuk identifikasi baris unik saat incremental |
| `incremental_strategy` | — | `'delete+insert'` — Hapus dulu baris dengan `unique_key` yang sama, lalu insert baru |
| `partition_by` | — | `'toYYYYMM(order_purchase_timestamp)'` — Partisi per bulan |

### Cara Kerja `{{ config() }}`

Block `{{ config(...) }}` adalah Jinja macro. Saat dbt mengompilasi model:

1. dbt membaca `config()` dan menyimpannya sebagai metadata model
2. Saat eksekusi, dbt menggunakan nilai-nilai ini untuk menentukan:
   - **Bagaimana** membuat tabel (`CREATE TABLE ... ENGINE = MergeTree()`)
   - **Kapan** membuat ulang (`table` = DROP + CREATE; `incremental` = INSERT / DELETE+INSERT)
   - **Dimana** menyimpannya (`+schema` dari `dbt_project.yml` — lihat bagian 2)
3. Config di file SQL **override** config apapun di `dbt_project.yml`

### Tentang `is_incremental()`

Untuk model dengan `materialized='incremental'`, dbt menyediakan variable `is_incremental()` yang bernilai `True` hanya pada **eksekusi kedua dan seterusnya**. Ini berguna untuk memfilter data yang sudah pernah diproses:

```sql
SELECT * FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
  WHERE order_purchase_timestamp > (SELECT max(order_purchase_timestamp) FROM {{ this }})
{% endif %}
```

- **Run pertama**: `is_incremental()` = `False` → semua data diproses
- **Run kedua+**: `is_incremental()` = `True` → hanya data baru yang diproses
- `{{ this }}` merujuk ke tabel yang sedang dibuat (fct_orders itu sendiri)

---

## 6. Cara Menjalankan

```bash
# Setup environment variables (via .env)
python -m dotenv -f .env run -- dbt debug

# Run semua model
dbt run

# Run spesifik layer
dbt run --select staging
dbt run --select marts

# Run spesifik model
dbt run --select stg_customers

# Test data quality
dbt test

# Generate dokumentasi
dbt docs generate
dbt docs serve
```

---

## 7. Ringkasan Alur Membuat dbt Project

```
1. dbt init <project_name>
2. Edit dbt_project.yml
   - nama, profile
   - +schema untuk setiap subfolder (staging, marts, dll)
3. Setup profiles.yml
   - Di ~/.dbt/ atau custom via DBT_PROFILES_DIR
   - Pakai env_var() untuk kredensial
4. Buat macros/generate_schema_name.sql
   - Agar custom schema tidak digabung dengan target schema
5. Buat models/staging/ — pola source → cleaned
   - Tambah {{ config() }} di setiap file (materialized, engine, order_by)
6. Buat models/marts/ — pola ref → agregasi
   - Fact table: materialized='incremental' + partition_by
   - Dimension: materialized='table' + order_by
7. Buat schema.yml di setiap folder untuk source & test definitions
8. dbt run → dbt test ✅
```
