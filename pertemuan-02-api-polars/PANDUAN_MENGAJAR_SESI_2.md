# Panduan Mengajar Sesi 2: Modern Local Ingestion (API & Polars)
**Materi:** REST API, Dataframe Engine Polars (Lazy Evaluation), & Ekspor Parquet (120 Menit)

---

## ⚡ 1. Analogi Dunia Nyata (2 Menit)

### A. CSV (Row-based) vs Parquet (Columnar)
*   **CSV (Baris)** = **Daftar Belanjaan Horizontal**. Jika Anda ingin mencari rata-rata harga dari 1 juta barang, Anda terpaksa membaca buku belanjaan tersebut baris-demi-baris, melewati detail yang tidak penting (seperti deskripsi, warna, rating) hanya untuk mencatat harga. Lambat dan memakan memori!
*   **Parquet (Kolom)** = **Laci Obat Apotek**. Kolom harga ditaruh di laci khusus harga, kolom nama di laci nama. Jika Anda hanya ingin menghitung rata-rata harga, Anda cukup membuka **Laci Harga** saja dan mengabaikan laci lainnya. Proses jadi secepat kilat dan ukuran file menyusut drastis!

### B. Eager vs Lazy Evaluation (Polars Robot)
*   **Pandas (Eager)** = **Robot Kurir Kurang Cerdas**. Jika Anda menyuruh: *"Pergi ke toko, beli semua 10 produk kecantikan, bawa pulang, lalu buang yang ratingnya di bawah 4.0."* Si robot akan membeli semua barang, memikulnya pulang (boros tenaga/memori), baru memilahnya di rumah.
*   **Polars (Lazy)** = **Robot Kurir Cerdas**. Ketika diberi perintah yang sama, robot tidak langsung lari. Dia membuat rencana (*Query Plan*) terlebih dahulu: *"Ah, daripada saya memikul 10 barang pulang, lebih baik saya memfilter rating >= 4.0 langsung di rak toko, lalu memikul pulang barang yang lolos saja!"* Optimasi otomatis ini disebut **Predicate Pushdown**.

---

## ⏰ 2. Rencana Alokasi Waktu (120 Menit)

*   **10 Menit — Pembuka & Analogi Belanja**
    *   Mencairkan suasana dengan analogi Laci Apotek (Parquet) & Kurir Cerdas (Lazy Evaluation).
*   **60 Menit — Code-Along Bagian 1: Jupyter Notebook (Eksplorasi - 60%)**
    *   **15 Menit:** Menarik data dari DummyJSON API menggunakan library `requests`.
    *   **20 Menit:** Memuat ke Polars DataFrame, mencoba filter, dan membersihkan nilai `null` (Imputation).
    *   **25 Menit:** Mempelajari Query Optimization menggunakan `.lazy()`, `.explain()`, dan memicu eksekusi menggunakan `.collect()`.
*   **35 Menit — Code-Along Bagian 2: Refactoring ke `ingest.py` (Produksi - 40%)**
    *   Diskusi singkat: Mengapa file `.ipynb` tidak boleh dipakai di server otomasi (scheduler)?
    *   Memindahkan logika pembersihan dari sel notebook ke dalam fungsi modular (`extract`, `transform`, `load`).
    *   Menyimpan hasil akhir ke format `.parquet` via `df.write_parquet()`.
*   **15 Menit — Q&A & Penjelasan Tugas 1**
    *   Review alur ETL.
    *   Penjelasan detail instruksi Tugas 1 "The Local Ingestor".

---

## 💻 3. Code-Along Bagian 1: Jupyter Notebook (60% Porsi Kelas)

Minta peserta membuat/membuka file [notebooks/eksplorasi_polars.ipynb](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-02-api-polars/notebooks/eksplorasi_polars.ipynb) di VS Code. Ikuti langkah ketik bareng berikut:

### Langkah 1: Install & Import Library
```python
import polars as pl
import requests
import json
```

### Langkah 2: Hit API DummyJSON secara Aman
```python
api_url = "https://dummyjson.com/products"
try:
    response = requests.get(api_url, timeout=5)
    response.raise_for_status()
    raw_data = response.json()
    print("✅ API DummyJSON Berhasil Diakses!")
except Exception as e:
    print(f"⚠️ API Offline ({e}). Menggunakan data fallback lokal...")
    with open("../data_dummy.json", "r") as f:
        raw_data = json.load(f)

products_list = raw_data["products"]
```

### Langkah 3: Muat ke Polars (Eager Mode)
```python
df = pl.DataFrame(products_list)
print(df.head(3))
```

### Langkah 4: Aktifkan Mode Lazy & Buat Pipeline Transformasi
Jelaskan bahwa tanda kurung `(...)` digunakan untuk melakukan chaining (menghubungkan operasi) agar kode terlihat bersih.

```python
lazy_df = df.lazy()

cleaned_lazy_df = (
    lazy_df
    # 1. Mengisi missing values (handling nulls)
    .with_columns([
        pl.col("price").fill_null(pl.col("price").median()),
        pl.col("stock").fill_null(0).cast(pl.Int64),
        pl.col("category").fill_null("other"),
        pl.col("rating").fill_null(0.0)
    ])
    # 2. Filter rating tinggi
    .filter(
        pl.col("rating") >= 4.0
    )
    # 3. Rename & Format Huruf Kapital
    .select([
        pl.col("id").alias("id_produk"),
        pl.col("title").str.to_uppercase().alias("nama_produk"),
        pl.col("price").alias("harga"),
        pl.col("stock").alias("stok"),
        pl.col("category").alias("kategori"),
        pl.col("rating").alias("skor_rating")
    ])
)
```

### Langkah 5: Mengintip Optimasi Query Plan
Jalankan perintah berikut untuk melihat bagaimana Rust compiler dari Polars menyusun ulang perintah filter agar data lebih cepat diproses:
```python
print(cleaned_lazy_df.explain())
```

### Langkah 6: Collect Hasil Akhir (Trigger Execution)
```python
final_df = cleaned_lazy_df.collect()
```

#### Output Tabel Akhir yang Dihasilkan (Tampilkan di Proyektor):

| id_produk | nama_produk | harga | stok | kategori | skor_rating |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | ESSENCE MASCARA LASH PRINCESS | 9.99 | 5 | beauty | 4.94 |
| **3** | POWDER CANISTER | 11.49 | 10 | beauty | 4.0 |
| **4** | RED LIPSTICK | 12.99 | 0 | other | 4.8 |

---

## 💻 4. Code-Along Bagian 2: Refactoring ke `ingest.py` (40% Porsi Kelas)

**Narasi Instruktur:**
> *"Logika data cleaning kita sudah berjalan sempurna di Jupyter! Tapi Jupyter Notebook tidak bisa dijalankan secara terjadwal di server produksi (seperti Cron/Airflow). Notebook memakan overhead memori besar dan tidak modular. Sekarang, mari kita lakukan **refactoring**: memindahkan sel-sel kode tadi ke dalam file script Python murni bernama `ingest.py` dengan arsitektur fungsi ETL standar industri."*

Minta peserta membuat dan mengetik bersama file [src/ingest.py](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-02-api-polars/src/ingest.py).

### Penjelasan Baris Kode Penting di `ingest.py`:
1.  **Fungsi `extract()`**: Memisahkan logika penarikan API. Dilengkapi proteksi `try-except` untuk menangani API down dengan mengalihkan data ke file JSON fallback lokal.
2.  **Fungsi `transform()`**: Menampung logika rantai ekspresi Polars. Menggunakan `.lazy()` di awal dan diakhiri `.collect()` di akhir fungsi.
3.  **Fungsi `load()`**: Menyimpan file dengan format `.parquet` menggunakan perintah bawaan Polars:
    ```python
    df.write_parquet(output_path)
    ```
4.  **Menjalankan Script via Terminal:**
    ```bash
    python pertemuan-02-api-polars/src/ingest.py
    ```
    Minta peserta melihat file log `logs/ingest.log` dan file baru `products_cleaned.parquet` yang terbentuk.

---

## 📝 5. Lembar Contekkan (Cheat Sheet) Sesi 2

### A. Polars Expressions (Manipulasi Kolom & Baris)
*   **`pl.col("kolom")`**: Memilih kolom target untuk dimanipulasi.
*   **`.fill_null(nilai)`**: Mengisi nilai kosong (`null`) dengan nilai default.
*   **`.cast(pl.TipeData)`**: Mengubah jenis tipe data (misal: `pl.Int64`, `pl.Float64`, `pl.Utf8`).
*   **`.str.to_uppercase()`**: Mengubah string menjadi huruf kapital semua.
*   **`.alias("nama_baru")`**: Mengubah nama kolom hasil transformasi.

### B. Format Parquet vs CSV
*   Parquet menyimpan data secara **kolom**, CSV secara **baris**.
*   Parquet melakukan kompresi otomatis (ukuran file s/d 90% lebih kecil dibanding CSV).
*   Sangat efisien digunakan pada teknologi Big Data seperti Spark, Snowflake, dan data warehouse modern.

---

## 📬 6. Template Tugas 1: "The Local Ingestor"
*Copy-paste teks di bawah ini untuk dibagikan ke grup belajar peserta:*

```markdown
🚨 **TUGAS 1: THE LOCAL INGESTOR (DE NUSACODE)** 🚨

Halo rekan-rekan calon Data Engineer! 🧑‍💻
Untuk mematangkan pemahaman kalian tentang Python CLI, Git, REST API, dan manipulasi data berkinerja tinggi menggunakan Polars, saatnya kalian mengerjakan tantangan praktis pertama Anda!

### 📋 Deskripsi Tugas & Goal:
Anda diminta untuk membangun sebuah data pipeline lokal mandiri bernama "The Local Ingestor". Tugas pipeline ini adalah menarik data postingan blog dari sebuah API publik, melakukan pembersihan data kotor secara otomatis, menghitung panjang karakter konten, lalu menyimpannya ke dalam format data columnar modern (.parquet).

### ⚙️ Langkah-langkah Pengoperasian (Step-by-Step):
1.  **Repository Setup:** Buat folder proyek lokal baru dan inisialisasi Git (`git init`).
2.  **Extract:** Hubungkan pipeline ke API publik: `https://jsonplaceholder.typicode.com/posts`.
    *   *Mekanisme Pertahanan:* Buat file cadangan lokal `posts_fallback.json` berisi minimal 3 postingan manual. Jika koneksi API gagal/down, script Anda harus otomatis memuat data fallback ini tanpa crash!
3.  **Transform:** Muat data ke Polars Lazy DataFrame dan lakukan transformasi berikut:
    *   Hapus baris data jika kolom `title` atau `body` bernilai kosong (`null`).
    *   Buat kolom baru bernama `body_char_length` yang berisi jumlah karakter teks dari kolom `body`. (Gunakan Polars expression string length).
    *   Filter data: Hanya simpan postingan yang memiliki `body_char_length` lebih dari 50 karakter.
    *   Ubah nama kolom `userId` menjadi `author_id`.
4.  **Load:** Simpan output akhir DataFrame yang sudah bersih ke dalam file format Parquet bernama `fact_posts.parquet`.
5.  **Logging & Resiliency:** 
    *   Gunakan library `logging` untuk mencatat proses penarikan data, sukses/gagal pemrosesan, dan jumlah baris data akhir. Log harus disimpan ke file `logs/pipeline.log`.
    *   Jika proses penulisan Parquet gagal, gunakan catch block untuk membackup data ke format CSV darurat `fact_posts_failed_backup.csv`.

### 🗂️ Struktur Folder Output Akhir (Wajib Diikuti):
tugas-01-local-ingestor/
├── requirements.txt          # Daftar library (polars, requests, pyarrow)
├── ingest_posts.py           # Script utama ETL Anda
├── posts_fallback.json       # Backup data JSON postingan
└── logs/
    └── pipeline.log          # Rekaman aktivitas pipeline Anda

### 🏆 Kriteria Penilaian (Nilai A):
1.  **Clean Code & Modular:** Script `ingest_posts.py` dibagi menjadi fungsi terpisah: `extract()`, `transform()`, dan `load()`.
2.  **Tangguh (Robust):** Dilengkapi penanganan `try-except` menyeluruh (jika API down / data kotor, program tidak crash).
3.  **Audit Track:** File `pipeline.log` terisi lengkap dengan timestamp log.
4.  **Standardisasi Format:** Output akhir berhasil tersimpan sebagai berkas columnar `.parquet` yang valid.

📅 **Batas Pengumpulan:** H-2 Sebelum Pertemuan Sesi 3. Setorkan tautan repositori GitHub Anda ke Google Form kelas!

*"Code early, code robustly!"* 🚀
```
