# Panduan Mengajar Sesi 4: Advanced SQL for Analytics
**Materi:** Gold Layer (Data Mart), CTE, Window Functions, & Analisis Data Olist (120 Menit)

---

## 🗺️ 1. Arsitektur Medali Data (2 Menit)

Gunakan analogi **Medali Olimpiade 🥉🥈🥇** untuk menjelaskan arsitektur data berlapis:

*   **🥉 Bronze Layer** — Data mentah dari sumber (CSV Olist). Tabel `raw_schema.*` yang kita buat di Sesi 3. Isinya sama persis dengan file CSV, belum ada agregasi.
*   **🥈 Silver Layer** — Data yang sudah dibersihkan, divalidasi, dan dideduplikasi (kita lewati di sesi ini karena data Olist sudah cukup bersih).
*   **🥇 Gold Layer** — **Bintangnya sesi ini!** Tabel agregasi siap-pakai untuk BI tools (Metabase, Looker, Grafana). Di sinilah Data Engineer mengungkapkan nilainya: mengubah data mentah menjadi wawasan bisnis.

> **Kata Kunci:** *Gold Layer* = `CREATE TABLE gold.nama_tabel AS SELECT ...` — satu perintah SQL yang langsung membuat tabel agregat siap-pakai menunggu query analitik selanjutnya!

---

## ⏰ 2. Rencana Alokasi Waktu (120 Menit)

*   **10 Menit — Pembuka & Arsitektur Medali Data**
    *   Memahami posisi Gold Layer dalam pipeline data modern.
*   **15 Menit — Eksekusi Seed Data (Gold Layer)**
    *   Menjalankan script `seed_data.sql` untuk membuat 10 tabel gold layer.
    *   Review struktur tabel yang terbentuk.
*   **45 Menit — Live Code-Along: Query Analitik di Gold Layer**
    *   Menulis query CTE dan Window Functions di atas tabel `gold.*`.
    *   Menjawab pertanyaan bisnis nyata: "Kategori apa paling laris?", "Siapa customer platinum?".
*   **35 Menit — Praktik Mandiri & Optimasi**
    *   Peserta menulis query ranking, running total, dan segmentasi sendiri.
    *   Diskusi hasil query dan perbandingan performa.
*   **15 Menit — Review & Penutup**
    *   Q&A, pembahasan tugas, dan pembagian cheat sheet.

---

## 🛠️ 3. Panduan Setup & Jalur Live Coding

### A. Prasyarat
1.  Pastikan container PostgreSQL Sesi 3 masih berjalan (`docker ps`).
2.  Pastikan tabel `raw_schema.*` sudah terisi data Olist (dari `ingest_to_db.py` Sesi 3).
3.  Buka DBeaver → koneksi ke `dw_nusacode`.

### B. Seed Data: Membangun Gold Layer (15 Menit)
1.  Buka SQL Editor di DBeaver.
2.  Buka file `pertemuan-04-advanced-sql/seed_data.sql`.
3.  Jalankan seluruh script (Alt+X).
4.  **Verifikasi:**
    ```sql
    -- Cek apakah schema gold sudah ada
    SELECT * FROM information_schema.schemata WHERE schema_name = 'gold';

    -- Cek salah satu tabel gold
    SELECT * FROM gold.category_performance ORDER BY total_revenue DESC LIMIT 5;
    ```

### C. Struktur Gold Layer yang Terbentuk

| Tabel Gold | Isi | Penggunaan |
|---|---|---|
| `gold.daily_sales_summary` | Orders, revenue, freight per hari | Tren penjualan |
| `gold.product_performance` | Performa tiap produk + review | Analisis SKU |
| `gold.customer_ltv` | Lifetime value per customer | Segmentasi pelanggan |
| `gold.seller_performance` | Revenue & rating per seller | Evaluasi seller |
| `gold.payment_analysis` | Metode pembayaran & volume | Analisis payment |
| `gold.review_analysis` | Distribusi skor review | Analisis kepuasan |
| `gold.order_fulfillment` | Durasi pengiriman per order | Logistik |
| `gold.category_performance` | Performa per kategori produk | Kategori bisnis |
| `gold.daily_kpi` | KPI harian (siap dashboard) | Metabase/Grafana |

---

### D. Live Code-Along: Query Analitik (45 Menit)

Buka `pertemuan-04-advanced-sql/queries.sql` di DBeaver. Ketik bersama peserta.

#### 🔹 Query 1: Ringkasan Eksekutif (CTE)
```sql
WITH kpi AS (
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(price) AS total_revenue,
        AVG(review_score) AS avg_review_score
    FROM raw_schema.fact_order o
    LEFT JOIN raw_schema.fact_order_item oi USING (order_id)
    LEFT JOIN raw_schema.fact_order_review r USING (order_id)
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
)
SELECT *, total_revenue / total_orders AS revenue_per_order FROM kpi;
```

#### 🔹 Query 2: TOP 3 Produk per Kategori (Window Function: DENSE_RANK)
```sql
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
SELECT * FROM ranked_products
WHERE rank_in_category <= 3
ORDER BY category_english, rank_in_category;
```

#### 🔹 Query 3: Running Total Revenue (Window Function: SUM OVER)
```sql
SELECT
    order_date,
    total_orders,
    total_revenue,
    SUM(total_revenue) OVER (ORDER BY order_date) AS cumulative_revenue,
    AVG(total_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_ma_7d
FROM gold.daily_sales_summary
ORDER BY order_date;
```

#### 🔹 Query 4: Segmentasi Pelanggan (CASE + Window)
```sql
SELECT
    customer_tier,
    COUNT(*) AS total_customers,
    AVG(total_revenue) AS avg_revenue,
    AVG(total_orders) AS avg_orders
FROM (
    SELECT *,
        CASE
            WHEN total_revenue >= 500 THEN 'Platinum'
            WHEN total_revenue >= 200 THEN 'Gold'
            WHEN total_revenue >= 100 THEN 'Silver'
            ELSE 'Bronze'
        END AS customer_tier
    FROM gold.customer_ltv
    WHERE total_orders > 0
) sub
GROUP BY customer_tier
ORDER BY MIN(total_revenue) DESC;
```

---

### E. Praktik Mandiri (35 Menit)

Minta peserta menjawab pertanyaan bisnis berikut dengan query di gold layer:

1. **"Kota mana yang punya customer dengan rata-rata LTV tertinggi?"**
   *Petunjuk: GROUP BY customer_city di gold.customer_ltv*

2. **"Seller mana yang ratingnya di bawah rata-rata?"**
   *Petunjuk: Bandingkan avg_customer_review di gold.seller_performance dengan AVG() di subquery*

3. **"Berapa persen order yang dikirim terlambat?"**
   *Petunjuk: Hitung delivery_status di gold.order_fulfillment*

4. **"Buat perankingan metode pembayaran paling populer per bulan!"**
   *Petunjuk: Gunakan DATE_TRUNC('month', ...) + DENSE_RANK()*

---

## 📝 4. Lembar Contekkan (Cheat Sheet)

### A. Gold Layer Pattern
```sql
-- Membuat tabel gold layer dari raw_schema
CREATE TABLE gold.<nama> AS
SELECT <kolom_agregasi>
FROM raw_schema.<fact/dim>
GROUP BY <dimensi>;
```

### B. CTE (Common Table Expressions)
```sql
WITH <nama_cte> AS (
    SELECT kolom1, kolom2 FROM tabel WHERE kondisi
)
SELECT * FROM <nama_cte>;
```

### C. Window Functions
```sql
<fungsi>() OVER (
    PARTITION BY <kelompok> 
    ORDER BY <urutan>
)
```
| Fungsi | Kegunaan |
|---|---|
| `ROW_NUMBER()` | Nomor baris unik (1,2,3,4) |
| `DENSE_RANK()` | Ranking tanpa lompat (1,2,2,3) |
| `SUM() OVER` | Running total akumulatif |
| `AVG() OVER` | Moving average |
| `LAG() / LEAD()` | Nilai baris sebelumnya/sesudahnya |

### D. Case Study: Bronze → Gold Pipeline
```sql
-- BRONZE (raw)
SELECT * FROM raw_schema.fact_order;

-- GOLD (siap dashboard)
SELECT
    DATE(order_purchase_timestamp) AS date,
    COUNT(*) AS orders,
    SUM(price) AS revenue
FROM raw_schema.fact_order o
JOIN raw_schema.fact_order_item oi ON o.order_id = oi.order_id
WHERE order_status = 'delivered'
GROUP BY date;
```

---

## 📬 5. Template Tugas 2: "Gold Layer Builder"

```markdown
🚨 **TUGAS 2: GOLD LAYER & ADVANCED SQL (DE NUSACODE)** 🚨

### 📋 Deskripsi
Buat **Gold Layer** dari data Olist! Anda akan membuat tabel agregasi dan menulis query analitik di atasnya.

### ⚙️ Langkah-langkah
1. **Jalankan seed_data.sql** di DBeaver untuk membuat 10 gold tables.
2. **Tulis 5 query analitik baru** di file `analysis_gold.sql`:
   - 1 CTE untuk menemukan TOP 5 customer berdasarkan total revenue
   - 1 Window Function ranking seller per state
   - 1 Running total penjualan per bulan
   - 1 Perbandingan `LAG()` revenue week-over-week
   - 1 Query bebas (kreativitas Anda!)

### 🗂️ Output
tugas-02-gold-layer/
├── analysis_gold.sql
└── screenshot_hasil_query.png

### 🏆 Nilai A
✅ Query valid dan bisa dieksekusi
✅ Menggunakan minimal 2 window functions berbeda
✅ Menggunakan CTE minimal di 2 query
✅ Ada insight bisnis yang ditulis sebagai komentar SQL

"Data is the new gold. Refine it!" 🥇
```

---

## 🔗 Referensi Dataset

Dataset: **Olist Brazilian E-Commerce**  
Link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce  
9 CSV files → `raw_schema.*` → `gold.*` (10 analytical tables)