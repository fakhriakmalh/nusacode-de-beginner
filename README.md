# 📑 Silabus Kurikulum Data Engineering (Beginner)
**Durasi:** 8 Pertemuan  
**Fokus Utama:** Kombinasi Fondasi Data Pipeline Tradisional & Modern Data Stack (Python, Polars, PostgreSQL, dbt)  
**Metodologi:** *Minimal Theory, Maximum Hands-on, Fast Onboarding*

---

## 📦 SESI 1 & 2: Environment Setup & Local Data Processing
**Fokus:** Menyiapkan *tools* kerja dan belajar memanipulasi data mentah secara lokal dengan performa tinggi.

### 📌 Pertemuan 1: The DE Environment & Python Core
* **Format Penyajian:** 100% Terminal/CLI & Script Python (`.py`) via VS Code.
* **Materi & Checklist:**
    * [ ] **Git & GitHub:** Workflow dasar (`clone`, `status`, `add`, `commit`, `push`, `branching`).
    * [ ] **CLI & Bash Dasar:** Navigasi terminal untuk eksekusi script dan pengelolaan file (`cd`, `ls`, `mkdir`, `pwd`).
    * [ ] **Docker for Beginners:** Menjalankan database PostgreSQL lokal menggunakan `docker-compose` tanpa instalasi manual yang rumit.
    * [ ] **Python Core for DE:** Pembuatan fungsi (*functions*), penanganan error (*error handling* dengan `try-except`), dan implementasi *logging* (menggantikan fungsi `print()` untuk standar produksi).

### 📌 Pertemuan 2: Modern Local Ingestion (API & Polars)
* **Format Penyajian:** 60% Jupyter Notebook (Eksplorasi visual) $\rightarrow$ 40% Refactor ke Script `.py`.
* **Materi & Checklist:**
    * [ ] **API Data Extraction:** Mengambil data dari REST API menggunakan library `requests` dan membaca format JSON.
    * [ ] **File Formats:** Memahami karakteristik data berbasis baris (CSV) vs kolumnar (**Parquet**).
    * [ ] **Polars Dataframe:** Eksplorasi manipulasi data dasar menggunakan Polars (*filtering*, *grouping*, penanganan *missing values/null*).
    * [ ] **Lazy Evaluation:** Memahami konsep *Lazy Evaluation* (`.lazy()` dan `.collect()`) pada Polars untuk efisiensi memori.

> ### 📝 TUGAS 1: "The Local Ingestor"
> * **Instruksi:** Buat sebuah script Python (`ingest.py`) yang mengambil data mentah dari *public* API (misal: Open-Meteo API, DummyJSON, atau API finansial), bersihkan kolom yang rusak/kosong menggunakan **Polars**, lalu simpan hasil akhirnya ke folder lokal dalam format **Parquet**.
> * **Goal:** Melatih kemampuan interaksi API, *error handling*, dan manipulasi dataframe dengan Polars.

---

## 🗄️ SESI 3 & 4: Database Storage & Analytics Querying
**Fokus:** Memindahkan data dari tingkat lokal ke database relational dan menguasai query analitik tingkat lanjut.

### 📌 Pertemuan 3: Database & Data Loading
* **Format Penyajian:** Live Coding (Python + SQL Editor/DBeaver).
* **Materi & Checklist:**
    * [ ] **PostgreSQL Architecture:** Memahami cara kerja database relational di dalam ekosistem Docker.
    * [ ] **Data Ingestion to DB:** Menghubungkan Python (Polars) ke PostgreSQL untuk memasukkan (*load*) data Parquet dari Sesi 2.
    * [ ] **SQL DDL & DML:** Dasar pembuatan tabel (*Data Definition Language*) dan manipulasi data (*Data Manipulation Language*).

### 📌 Pertemuan 4: Advanced SQL for Analytics
* **Format Penyajian:** Praktik interaktif menulis Query Analitik.
* **Materi & Checklist:**
    * [ ] **OLTP vs OLAP:** Perbedaan mendasar antara database operasional (aplikasi) dan database analitik (Data Warehouse).
    * [ ] **Advanced Joins & Aggregations:** Menguasai variasi `JOIN` dan fungsi `GROUP BY` untuk kebutuhan bisnis.
    * [ ] **CTE (Common Table Expressions):** Menulis query yang bersih dan mudah dibaca menggunakan klausa `WITH`.
    * [ ] **Window Functions:** Menggunakan fungsi `ROW_NUMBER()`, `RANK()`, dan fungsi agregasi berbasis window untuk analisis data kronologis.

> ### 📝 TUGAS 2: "The Warehouse Ingestion & SQL Mastery"
> * **Instruksi:** Lanjutkan kode dari Tugas 1. Modifikasi script Python Anda agar data dari Polars langsung dimasukkan (*load*) ke dalam tabel PostgreSQL di dalam skema mentah (`raw_schema`). Setelah data berhasil masuk, tulis 3 query SQL analitik menggunakan CTE dan Window Functions untuk menjawab pertanyaan bisnis tertentu.
> * **Goal:** Melatih koneksi program ke database (*database ingestion*) dan penulisan SQL analitik tingkat lanjut.

---

## 🏗️ SESI 5 & 6: Modern Analytics Engineering (dbt Layer)
**Fokus:** Mengubah paradigma dari ETL ke ELT. Melakukan transformasi data langsung di dalam database menggunakan dbt Core.

### 📌 Pertemuan 5: Introduction to dbt (Data Build Tool)
* **Format Penyajian:** CLI + VS Code dbt Project Setup.
* **Materi & Checklist:**
    * [ ] **ELT Paradigm:** Memahami pergeseran tren dari ETL tradisional ke *Modern Data Stack* (ELT).
    * [ ] **dbt Core Setup:** Instalasi dbt Core dan konfigurasi file `profiles.yml` untuk menghubungkannya ke PostgreSQL lokal.
    * [ ] **dbt Architecture & Staging:** Membuat arsitektur proyek dbt pertama dan membangun *Staging Models* (`stg_`) berbasis SQL murni.

### 📌 Pertemuan 6: Data Modeling & Star Schema with dbt
* **Format Penyajian:** Refactoring query SQL analitik menjadi Data Model yang terstruktur.
* **Materi & Checklist:**
    * [ ] **Dimensional Modeling:** Konsep perancangan skema data analitik menggunakan skema bintang (**Star Schema**).
    * [ ] **Fact & Dimension Tables:** Membedakan peran *Fact Table* (metrik/transaksi) dan *Dimension Table* (konteks/atribut).
    * [ ] **dbt Lineage & Marts:** Membuat model lanjutan (*Intermediate* dan *Marts* / `fct_` & `dim_`).
    * [ ] **dbt Testing & Docs:** Menerapkan pengujian kualitas data otomatis (`unique`, `not_null`) serta melakukan *generate* dokumentasi bawaan dbt.

> ### 📝 TUGAS 3: "The Transformation Layer"
> * **Instruksi:** Inisialisasi proyek dbt di atas database PostgreSQL Anda. Ubah data mentah pada `raw_schema` (dari Tugas 2) menjadi skema siap pakai (*Star Schema*) dengan struktur jalur dbt yang benar (`stg_models` $\rightarrow$ `intermediate` $\rightarrow$ `dim_` atau `fct_` models). Tambahkan minimal 2 *data quality test* pada file `.yml` Anda.
> * **Goal:** Memahami alur kerja *Analytics Engineering* dan otomatisasi transformasi data terstruktur di dalam warehouse.

---

## 🚀 SESI 7 & 8: Orchestration & Capstone Showcase
**Fokus:** Mengotomatiskan seluruh alur kerja pipeline data dan membangun portofolio profesional.

### 📌 Pertemuan 7: Automation & Pipeline Orchestration
* **Format Penyajian:** Demo Arsitektur + Workshop GitHub.
* **Materi & Checklist:**
    * [ ] **Pipeline Automation:** Strategi menjalankan script Python (Sesi 1-4) dan transformasi dbt (Sesi 5-6) secara berurutan dan otomatis.
    * [ ] **Orchestration Concept:** Pengenalan dasar konsep *scheduler* (dari yang sederhana seperti Linux Cron Job hingga pengenalan fungsional *tools* modern seperti Prefect atau Apache Airflow).
    * [ ] **DE Portfolio Building:** Tips menyusun dokumentasi proyek di GitHub (*README.md*) yang dilirik oleh HRD/Recruiter.

### 📌 Pertemuan 8: Final Project Showcase & Graduation
* **Format Penyajian:** Presentasi & Demo Live Proyek Akhir.
* **Materi & Checklist:**
    * [ ] **Capstone Presentation:** Setiap peserta mendemonstrasikan secara *live* seluruh alur pipeline data yang telah mereka bangun secara end-to-end dari pertemuan 1 hingga 7.
    * [ ] **Alur Pipeline Akhir:** $$\text{API Source} \xrightarrow{\text{Python/Polars}} \text{PostgreSQL (Raw)} \xrightarrow{\text{dbt Core}} \text{PostgreSQL (Clean Analytics/Star Schema)}$$
    * [ ] **Evaluation & Feedback:** Sesi tanya jawab teknis, evaluasi kode (*code review*) oleh mentor, dan penyerahan sertifikat/kelulusan.