# Panduan Mengajar Sesi 4: Advanced SQL for Analytics
**Materi:** OLTP vs OLAP, CTE (Common Table Expressions), Window Functions, & Analisis Data Penjualan (120 Menit)

---

## ⚡ 1. Analogi Dunia Nyata (2 Menit)

### A. OLTP (Kasir Cepat) vs OLAP (Manager Analitik)
*   **OLTP (Online Transaction Processing)** = **Kasir Dapur Restoran**. Tugasnya harus secepat kilat melayani pelanggan satu per satu: catat pesanan, terima uang, cetak struk. Dia tidak peduli dengan tren 6 bulan lalu, yang penting transaksi detik ini lancar dan tidak antre.
*   **OLAP (Online Analytical Processing)** = **Manager Restoran di Kantor Pusat**. Dia tidak melayani pembeli langsung. Dia duduk membaca database transaksi selama 1 tahun terakhir untuk menganalisis: *"Menu apa yang paling laku di hari hujan?"* atau *"Jam berapa kita harus memberi diskon?"*. OLAP menangani data yang sangat besar untuk mengambil keputusan bisnis.

### B. Window Functions (Kaca Pembesar Bergerak)
*   **GROUP BY (Agregasi Biasa)** = **Mesin Blender**. Dia memadatkan 10 baris transaksi produk menjadi 1 baris ringkasan (misal: Total Terjual = 15). Kita kehilangan detail transaksi per tanggalnya.
*   **Window Functions (`OVER`)** = **Kaca Pembesar Geser**. 10 baris transaksi kita tetap utuh ditampilkan satu-satu (tidak diblender). Namun, di samping baris tersebut, kita melekatkan kaca pembesar bergerak yang menghitung nilai akumulatif (Running Total) atau peringkat (Rank) per kelompok produk (`PARTITION BY`).

---

## ⏰ 2. Rencana Alokasi Waktu (120 Menit)

*   **10 Menit — Pembuka & Analogi Bisnis**
    *   Pengenalan perbedaan mendasar OLTP vs OLAP serta analogi Kaca Pembesar (Window Functions).
*   **15 Menit — Data Seeding & Review Struktur**
    *   Membimbing peserta membuka DBeaver dan mengeksekusi script [seed_data.sql](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-04-advanced-sql/seed_data.sql) untuk menyuntikkan data transaksi historis.
*   **45 Menit — Live Code-Along SQL: Joins, Aggregations, & CTE**
    *   Menggabungkan tabel produk dan transaksi menggunakan `INNER JOIN`.
    *   Menulis query bertingkat menggunakan CTE (`WITH ... AS`) untuk mempermudah analisis bisnis.
*   **35 Menit — Live Code-Along SQL: Window Functions**
    *   Mempraktikkan `DENSE_RANK()` untuk melihat produk terlaris harian.
    *   Mempraktikkan `SUM() OVER` untuk menghitung akumulasi pendapatan (Running Total).
*   **15 Menit — Penjelasan Tugas 2 & Penutup**
    *   Membagikan instruksi Tugas 2 di grup kelas dan Q&A penutup.

---

## 🛠️ 3. Panduan Jalur Live Coding (DBeaver)

### Langkah 1: Seeding Data (15 Menit)
1.  Buka SQL Editor di DBeaver.
2.  Minta peserta membuka dan meng-copy isi berkas [seed_data.sql](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-04-advanced-sql/seed_data.sql) ke editor SQL DBeaver mereka.
3.  Eksekusi script tersebut (`Alt + X` atau klik tombol run script).
4.  Lakukan verifikasi dengan:
    ```sql
    SELECT * FROM raw_schema.sales;
    ```

---

### Langkah 2: Menulis Query Bersama (80 Menit)

Minta peserta mengetik bersama file [queries.sql](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-04-advanced-sql/queries.sql):

#### A. JOIN & AGGREGATION (Mencari Produk Terlaris secara Finansial)
*   *Poin Pengajaran:* Tunjukkan bagaimana data dihubungkan lewat `id_produk`.
```sql
SELECT 
    p.nama_produk,
    SUM(s.jumlah_terjual) AS total_item_terjual,
    SUM(s.total_bayar) AS total_pendapatan
FROM raw_schema.sales s
INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
GROUP BY p.nama_produk
ORDER BY total_pendapatan DESC;
```

#### B. CTE (Studi Kasus: Filter Agregasi)
*   *Poin Pengajaran:* Jelaskan bahwa kita tidak bisa menggunakan `WHERE` untuk memfilter hasil `SUM()`, dan menggunakan `HAVING` kadang sulit dibaca. CTE adalah solusinya!
```sql
WITH pendapatan_kategori_cte AS (
    SELECT 
        p.kategori,
        SUM(s.total_bayar) AS total_pendapatan
    FROM raw_schema.sales s
    INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
    GROUP BY p.kategori
)
SELECT * FROM pendapatan_kategori_cte WHERE total_pendapatan > 50.00;
```

#### C. Window Function 1: Perankingan Harian (`DENSE_RANK`)
*   *Poin Pengajaran:* Jelaskan fungsi `PARTITION BY` (kelompok pembagi rangking) dan `ORDER BY` (dasar penilaian rangking).
```sql
SELECT 
    s.tanggal_penjualan,
    p.nama_produk,
    SUM(s.jumlah_terjual) AS qty,
    DENSE_RANK() OVER(PARTITION BY s.tanggal_penjualan ORDER BY SUM(s.jumlah_terjual) DESC) AS rank
FROM raw_schema.sales s
INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
GROUP BY s.tanggal_penjualan, p.nama_produk;
```

#### D. Window Function 2: Running Total Pendapatan (`SUM OVER`)
*   *Poin Pengajaran:* Tunjukkan bahwa baris data tidak terkompresi, kita bisa melihat transaksi harian sekaligus akumulasi pendapatannya dari hari ke hari secara mendetail.
```sql
SELECT 
    s.tanggal_penjualan,
    p.nama_produk,
    s.total_bayar AS pendapatan_hari_ini,
    SUM(s.total_bayar) OVER (PARTITION BY s.id_produk ORDER BY s.tanggal_penjualan) AS running_total
FROM raw_schema.sales s
INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk;
```

---

## 📝 4. Lembar Contekkan (Cheat Sheet) Advanced SQL

### A. Format Dasar CTE (Common Table Expressions)
```sql
WITH <nama_cte> AS (
    -- Tulis query SQL standar di sini
    SELECT kolom1, kolom2 FROM tabel
)
SELECT * FROM <nama_cte> WHERE kondisi;
```

### B. Format Window Functions
```sql
<fungsi_window>() OVER (
    PARTITION BY <kolom_pengelompok> 
    ORDER BY <kolom_pengurutan>
)
```
*   `ROW_NUMBER()`: Memberikan nomor urut baris unik (1, 2, 3, 4).
*   `RANK()`: Memberikan rangking. Jika ada nilai kembar, rangking berikutnya akan melompati nomor (1, 2, 2, 4).
*   `DENSE_RANK()`: Memberikan rangking tanpa melompati nomor jika ada nilai kembar (1, 2, 2, 3).
*   `SUM(kolom)`: Menghitung nilai akumulatif dari baris pertama hingga baris aktif saat ini.

---

## 📬 5. Template Tugas 2: "The Warehouse Ingestion & SQL Mastery"
*Copy-paste teks di bawah ini untuk dibagikan ke grup belajar peserta:*

```markdown
🚨 **TUGAS 2: THE WAREHOUSE INGESTION & SQL MASTERY (DE NUSACODE)** 🚨

Halo teman-teman Data Engineer! 🧑‍💻
Kita akan melanjutkan proyek data pipeline kita. Kali ini kita akan naik tingkat: menghubungkan pipeline ke database relasional (PostgreSQL) dan menulis query analitik canggih di atas tabel tersebut.

### 📋 Deskripsi Tugas & Goal:
Anda diminta memodifikasi pipeline Python dari Tugas 1 agar tidak lagi sekadar menyimpan file Parquet lokal. Script harus otomatis memindahkan (*load*) data postingan blog tersebut ke dalam PostgreSQL kontainer Docker di dalam tabel bernama `raw_schema.fact_posts`. Setelah data berhasil masuk, Anda wajib menulis 3 query SQL analitik untuk menjawab kebutuhan divisi bisnis.

### ⚙️ Langkah-langkah Pengerjaan:
1.  **Database Setup:** Jalankan kontainer database PostgreSQL Sesi 3/4 Anda menggunakan Docker.
2.  **Modify Python Script:** Modifikasi script `ingest_posts.py` Anda. Tambahkan fungsi koneksi database dan gunakan Polars `.write_database()` untuk memindahkan data bersih langsung ke tabel `raw_schema.fact_posts` dengan opsi `if_table_exists='replace'`.
3.  **Tulis 3 Query Analitik (Simpan dalam berkas `analysis_queries.sql`):**
    *   **Query 1 (JOIN):** Gabungkan data postingan blog dengan data user (jika ada) untuk memetakan nama penulis dan judul tulisan.
    *   **Query 2 (CTE):** Tulis query menggunakan CTE (`WITH`) untuk menghitung total postingan per `author_id`, lalu tampilkan hanya penulis yang menulis lebih dari 2 postingan.
    *   **Query 3 (Window Functions):** Gunakan fungsi `ROW_NUMBER()` atau `DENSE_RANK()` untuk meranking postingan blog per masing-masing penulis (`author_id`) berdasarkan panjang karakter `body_char_length` dari yang terpanjang ke terpendek.

### 🗂️ Struktur Folder Output Akhir:
tugas-02-warehouse-ingestion/
├── requirements.txt            # Library (polars, requests, psycopg2-binary, sqlalchemy)
├── ingest_posts.py             # Script Python ETL terupdate (Load to Postgres)
├── analysis_queries.sql        # Berkas berisi 3 query SQL analitik Anda
└── logs/
    └── pipeline.log            # Log aktivitas pipeline database Anda

### 🏆 Kriteria Penilaian (Nilai A):
1.  **Database Automation:** Script Python berhasil melakukan penulisan tabel database relasional secara otomatis tanpa crash.
2.  **Valid Advanced SQL:** Ketiga query SQL analitik di file `analysis_queries.sql` lolos uji coba eksekusi (syntactically valid) dan menggunakan format CTE serta Window Functions secara tepat.
3.  **Resiliency (Try-Catch DB):** Jika koneksi database PostgreSQL mati, script Python Anda secara otomatis mencatat error ke log dan melakukan backup darurat ke berkas `.parquet` lokal.

📅 **Batas Pengumpulan:** H-2 Sebelum Pertemuan Sesi 5. Setorkan link repositori GitHub Anda ke Google Form kelas!

*"Let SQL do the heavy lifting in your Warehouse!"* 🚀
```
