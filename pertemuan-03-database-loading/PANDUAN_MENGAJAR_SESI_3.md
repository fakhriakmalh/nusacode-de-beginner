# Panduan Mengajar Sesi 3: Database & Data Loading
**Materi:** PostgreSQL di Docker, SQL DDL/DML Basics, & Ingesti Parquet ke DB (120 Menit)

---

## 🗄️ 1. Analogi Dunia Nyata (2 Menit)

Gunakan analogi **"Lemari Arsip Kantor yang Disiplin Ketat"** untuk memahamkan database relasional ke pemula:

*   Di Sesi 2, kita menyimpan data ke file Parquet/CSV. Ini seperti menulis data di tumpukan kertas hvs lalu meletakkannya begitu saja di meja. Fleksibel, tapi rawan hilang, teracak, atau tertumpuk.
*   **Database Relasional (PostgreSQL)** = **Lemari Arsip Besi Terkunci**. Lemari ini memiliki sekat-sekat laci dengan aturan yang kaku (Tabel). Laci tersebut hanya menerima map dengan ukuran dan format kolom yang sama (Skema & Tipe Data).
*   Jika Anda mencoba memasukkan data nomor telepon ke kolom yang didesain khusus untuk tanggal lahir, penjaga arsip (Database Engine) akan menolaknya secara tegas. Hal ini memastikan data kita selalu rapi, aman, dan tidak berantakan.

---

## ⏰ 2. Rencana Alokasi Waktu (120 Menit)

*   **10 Menit — Pembuka & Analogi Lemari Arsip**
    *   Membahas pentingnya database relasional dibanding file mentah lokal.
*   **20 Menit — Setup Docker & DBeaver (SQL Client)**
    *   Menjalankan container PostgreSQL Sesi 3 lewat terminal VS Code.
    *   Panduan menghubungkan database lokal ke tools visual seperti DBeaver.
*   **45 Menit — Live Code-Along SQL: DDL & DML**
    *   Peserta mempraktikkan DDL (`CREATE TABLE`, `DROP TABLE`) untuk mendesain struktur tabel.
    *   Peserta mempraktikkan DML (`INSERT`, `UPDATE`, `DELETE`) untuk mengubah data di dalam tabel.
*   **35 Menit — Live Code-Along Python: Ingestion Pipeline**
    *   Peserta mengetik bersama file `ingest_to_db.py`.
    *   Menghubungkan koneksi Python Polars ke PostgreSQL dan memindahkan data dari berkas Parquet Sesi 2 ke database target.
*   **10 Menit — Q&A & Penutup**
    *   Diskusi seputar anomali load data dan pembagian Cheat Sheet.

---

## 🛠️ 3. Panduan Setup & Jalur Live Coding

### A. Docker Setup (Sesi 3) (20 Menit)
1.  Minta peserta membuka folder `pertemuan-03-database-loading`.
2.  Jalankan perintah berikut di terminal untuk menyalakan PostgreSQL:
    ```bash
    docker-compose up -d
    ```
3.  Jelaskan bahwa container ini membaca [init.sql](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-03-database-loading/init.sql) secara otomatis untuk membuat schema `raw_schema` saat pertama kali dihidupkan.
4.  **Menghubungkan ke DBeaver:**
    *   Buka aplikasi DBeaver.
    *   Pilih **New Connection** -> **PostgreSQL**.
    *   Isi parameter koneksi berikut:
        *   **Host:** `localhost`
        *   **Port:** `5432`
        *   **Database:** `dw_nusacode`
        *   **Username:** `postgres`
        *   **Password:** `admindwpass`
    *   Klik **Test Connection**. Jika sukses, klik **Finish**.

---

### B. Praktek Live SQL: DDL & DML (45 Menit)

Minta peserta membuka SQL Editor di DBeaver (klik kanan pada koneksi -> **SQL Editor**) dan ketik perintah berikut langkah-demi-langkah bersama Anda:

#### 1. DDL (Data Definition Language) - Membuat Lemari Arsip
```sql
-- Membuat tabel baru secara manual di raw_schema untuk barang diskon
CREATE TABLE raw_schema.manual_products (
    id_produk INT PRIMARY KEY,
    nama_produk VARCHAR(100) NOT NULL,
    harga DECIMAL(12, 2) DEFAULT 0.0,
    stok INT NOT NULL,
    tanggal_ditambahkan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cek apakah tabel sudah terbuat
SELECT * FROM raw_schema.manual_products;
```

#### 2. DML (Data Manipulation Language) - Mengisi & Memanipulasi Arsip
```sql
-- Memasukkan data baru (INSERT)
INSERT INTO raw_schema.manual_products (id_produk, nama_produk, harga, stok)
VALUES (101, 'MECHANICAL KEYBOARD PRO', 850000.00, 15);

-- Memasukkan beberapa data sekaligus
INSERT INTO raw_schema.manual_products (id_produk, nama_produk, harga, stok)
VALUES 
(102, 'WIRELESS MOUSE ERGONOMIC', 350000.00, 8),
(103, 'RGB DESKMAT LARGE', 120000.00, 0);

-- Mengubah data yang salah (UPDATE)
UPDATE raw_schema.manual_products
SET stok = 10, harga = 320000.00
WHERE id_produk = 102;

-- Menghapus data (DELETE)
DELETE FROM raw_schema.manual_products
WHERE id_produk = 103;
```

---

### C. Praktek Ingesti Parquet ke Postgres (35 Menit)

**Narasi Instruktur:**
> *"Rekan-rekan, kita sudah bisa membuat tabel secara manual di DBeaver. Tapi di dunia nyata, Data Engineer tidak mungkin mengetik data transaksi pelanggan satu-satu pake SQL! Kita akan mengotomatiskan hal ini. Kita akan menulis script Python `ingest_to_db.py` yang membaca data Parquet bersih hasil olahan kita di Sesi 2, lalu langsung mengirimkannya ke PostgreSQL secara instan!"*

1.  Pastikan library database terinstal di terminal virtual env peserta:
    ```bash
    pip install psycopg2-binary sqlalchemy
    ```
2.  Minta peserta mengetik dan menyimpan file [ingest_to_db.py](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-03-database-loading/ingest_to_db.py).
3.  Jalankan script lewat terminal:
    ```bash
    python pertemuan-03-database-loading/ingest_to_db.py
    ```
4.  **Verifikasi Sukses:** Minta peserta membuka DBeaver kembali, lakukan klik kanan pada schema `raw_schema` -> **Refresh**. Tunjukkan bahwa tabel baru bernama `products` sekarang sudah terisi otomatis oleh program!

---

## 📝 4. Lembar Contekkan (Cheat Sheet) SQL & Database

### A. SQL DDL & DML Dasar
```sql
-- MEMBUAT TABEL
CREATE TABLE <nama_skema>.<nama_tabel> (
    <nama_kolom> <tipe_data> <constraint>
);

-- MENGHAPUS TABEL
DROP TABLE <nama_skema>.<nama_tabel>;

-- MENAMBAH BARIS DATA
INSERT INTO <nama_tabel> (kolom1, kolom2) VALUES (nilai1, nilai2);

-- MEMPERBARUI NILAI KOLOM (Penting: Selalu gunakan WHERE agar tidak mengubah seluruh isi tabel!)
UPDATE <nama_tabel> SET kolom1 = nilai_baru WHERE kondisi;

-- MENGHAPUS DATA (Penting: Selalu gunakan WHERE agar tidak mengosongkan tabel!)
DELETE FROM <nama_tabel> WHERE kondisi;
```

### B. Python Connection Parameters
Konektor standard PostgreSQL di Python menggunakan format string URI:
```text
postgresql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE_NAME>
```
*   Polars DataFrame menggunakan koneksi URI ini secara langsung di dalam `.write_database()` untuk memetakan data dengan kecepatan tinggi.
