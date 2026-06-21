# ingest_to_db.py
# Script Hands-on Sesi 3 - Ingesti data Parquet lokal ke PostgreSQL
# Diketik bareng instruktur di kelas!

import os
import sys
import logging
import polars as pl

# =====================================================================
# 1. KONFIGURASI LOGGING
# =====================================================================
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest_to_db.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# =====================================================================
# 2. KONFIGURASI DATABASE
# =====================================================================
# Menghubungkan ke PostgreSQL kontainer Docker yang sudah kita jalankan
DB_USER = "postgres"
DB_PASS = "admindwpass"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_nusacode"

# Target skema dan nama tabel
TARGET_TABLE = "raw_schema.products"

# Connection URI (standar SQLAlchemy & Polars)
DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =====================================================================
# 3. PIPELINE EKSEKUSI
# =====================================================================
def load_parquet_to_postgres():
    # File Parquet keluaran dari Sesi 2
    parquet_path = "products_cleaned.parquet"
    
    # Path adjustment jika script dijalankan dari folder sesi 3 atau root
    if not os.path.exists(parquet_path) and os.path.exists(f"../pertemuan-02-api-polars/{parquet_path}"):
        parquet_path = f"../pertemuan-02-api-polars/{parquet_path}"
    elif not os.path.exists(parquet_path) and os.path.exists(f"../{parquet_path}"):
        parquet_path = f"../{parquet_path}"
        
    logging.info("=== MEMULAI INGESTI DATA PARQUET KE POSTGRESQL ===")
    logging.info(f"Membaca file Parquet: {parquet_path}")
    
    # Validasi file Parquet
    if not os.path.exists(parquet_path):
        logging.error(f"Fungsi Batal: File '{parquet_path}' tidak ditemukan! Jalankan Sesi 2 terlebih dahulu.")
        return False
        
    try:
        # 1. Read Parquet (Sangat cepat & hemat memori)
        df_parquet = pl.read_parquet(parquet_path)
        logging.info(f"Sukses membaca Parquet. Ditemukan {len(df_parquet)} baris data.")
        
        # 2. Write Database
        logging.info(f"Menulis data ke database PostgreSQL -> Tabel: {TARGET_TABLE}...")
        
        # Polars write_database akan otomatis memetakan skema tipe data Polars ke kolom SQL.
        # if_table_exists='replace' akan menghapus tabel lama jika ada, lalu membuat baru.
        df_parquet.write_database(
            table_name=TARGET_TABLE,
            connection=DB_URI,
            if_table_exists="replace"
        )
        
        logging.info("✅ SUKSES: Data berhasil masuk ke PostgreSQL!")
        return True
        
    except ImportError as ie:
        logging.error("Gagal melakukan load database! Dependency konektor database belum terinstal.")
        logging.error("Instruksi: Jalankan 'pip install psycopg2-binary sqlalchemy'")
        
    except Exception as e:
        logging.error(f"Terjadi kegagalan saat menulis ke PostgreSQL: {e}")
        # Strategi recovery: infokan untuk cek apakah Docker container sudah menyala
        logging.warning("Saran: Pastikan Docker Desktop aktif dan container 'postgres_dw_sesi3' sudah running.")
        
    logging.info("=== PROSES SELESAI DENGAN ANOMALI ===\n")
    return False

if __name__ == "__main__":
    load_parquet_to_postgres()
