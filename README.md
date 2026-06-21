# Kurikulum Data Engineering Nusacode: Sesi 1 & Sesi 2 (Revisi)

Selamat datang di repositori materi ajar **Data Engineering (DE) Nusacode**. Repositori ini didesain dengan prinsip **"Minimal Theory, Maximum Hands-on, Fast Onboarding"** untuk membantu pemula melompati batasan mental terhadap tools dasar DE dan langsung mempraktikkan proses ETL secara mandiri.

---

## 📂 Struktur Folder Proyek

Semua file dikelompokkan secara rapi agar Anda langsung mengenali materi untuk setiap pertemuan:

```text
.
├── README.md                              # Panduan utama repositori ini
├── pertemuan-01-python-core/             # Sesi 1: The DE Environment & Python Core (120 Menit)
│   ├── PANDUAN_MENGAJAR_SESI_1.md         # Silabus, rundown, naskah live-coding & cheat sheet Sesi 1
│   ├── docker-compose.yml                 # Setup database PostgreSQL super simpel (1-click run)
│   └── app.py                             # Script core Python (try-except & logging)
└── pertemuan-02-api-polars/              # Sesi 2: Modern Local Ingestion (120 Menit)
    ├── PANDUAN_MENGAJAR_SESI_2.md         # Silabus, rundown, naskah, cheat sheet & Tugas 1
    ├── data_dummy.json                    # Backup data produk JSON jika API publik down
    ├── notebooks/
    │   └── eksplorasi_polars.ipynb        # 60% Sesi: Eksplorasi data & Polars di Jupyter Notebook
    └── src/
        └── ingest.py                      # 40% Sesi: Script produksi hasil refactor (Save to Parquet)
```

---

## 🎯 Ringkasan Sesi

### **Pertemuan 1: The DE Environment & Python Core (120 Menit)**
*   **Tujuan:** Mematahkan ketakutan pemula terhadap Terminal (layar hitam), mengenalkan Docker dengan cara paling instan, serta melatih *production mindset* menggunakan error handling dan logging sistematis di Python.
*   **Aktivitas Utama:** 
    *   Mencoba `docker-compose.yml` untuk PostgreSQL.
    *   Membangun script `app.py` yang sengaja dibuat error lalu diperbaiki dengan `try-except`.
    *   Mengganti `print()` dengan library `logging` bawaan Python.

### **Pertemuan 2: Modern Local Ingestion (API & Polars) (120 Menit)**
*   **Tujuan:** Melakukan transisi mulus dari eksplorasi data visual di Jupyter Notebook menuju otomatisasi script produksi. Peserta akan memproses data API eksternal secara efisien menggunakan engine berkecepatan Rust (Polars) dan menyimpannya ke format kolom modern (Parquet).
*   **Aktivitas Utama:**
    *   Mengambil data produk menggunakan DummyJSON API.
    *   Eksplorasi data di Jupyter Notebook dengan Polars (Lazy evaluation, filtering, & nulls handling).
    *   Refactoring kode notebook ke script produksi `ingest.py` untuk menghasilkan file `.parquet`.

---

## 🛠️ Prasyarat (Requirements)

Pastikan instansi terminal dan python sudah terinstal:
*   Python 3.10+
*   Docker Desktop (untuk PostgreSQL di Sesi 1)
*   VS Code beserta extension **Python** & **Jupyter**
