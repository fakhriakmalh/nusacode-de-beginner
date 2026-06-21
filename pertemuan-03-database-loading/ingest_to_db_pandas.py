# ingest_to_db_pandas.py
# Script Hands-on Sesi 3 - Ingesti data Parquet lokal ke PostgreSQL
# Menggunakan Pandas (sebagai alternatif dari versi Polars)
#
# Package tambahan yang disarankan:
#   1. pandas       -> untuk membaca Parquet & transformasi data
#   2. sqlalchemy   -> sebagai engine koneksi database (ORM-style)
#   3. psycopg2-binary -> driver PostgreSQL untuk SQLAlchemy
#
# Alternatif package lain (all-in-one):
#   - `pandas` + `pyarrow` (engine read_parquet)
#     cukup dengan:  pip install pandas pyarrow psycopg2-binary sqlalchemy

import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine, text

# =====================================================================
# 1. KONFIGURASI LOGGING
# =====================================================================
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest_to_db_pandas.log", encoding="utf-8"),
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
# 3. FUNGSI BANTU DROP TABLE
# =====================================================================
def drop_table_if_exists(engine, table_name: str):
    """
    Menghapus tabel jika sudah ada.
    Fungsi ini digunakan untuk mensimulasikan if_table_exists='replace'
    karena pd.to_sql() membutuhkan parameter 'replace' di tingkat SQLAlchemy.
    """
    with engine.connect() as conn:
        # Eksekusi DROP TABLE IF EXISTS
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()
        logging.info(f"Tabel {table_name} berhasil dihapus (jika ada).")

# =====================================================================
# 4. PIPELINE EKSEKUSI
# =====================================================================
def load_parquet_to_postgres():
    # File Parquet keluaran dari Sesi 2
    parquet_path = "products_cleaned.parquet"

    # Path adjustment jika script dijalankan dari folder sesi 3 atau root
    if not os.path.exists(parquet_path) and os.path.exists(f"../pertemuan-02-api-polars/{parquet_path}"):
        parquet_path = f"../pertemuan-02-api-polars/{parquet_path}"
    elif not os.path.exists(parquet_path) and os.path.exists(f"../{parquet_path}"):
        parquet_path = f"../{parquet_path}"

    logging.info("=== MEMULAI INGESTI DATA PARQUET KE POSTGRESQL (PANDAS) ===")
    logging.info(f"Membaca file Parquet: {parquet_path}")

    # Validasi file Parquet
    if not os.path.exists(parquet_path):
        logging.error(f"Fungsi Batal: File '{parquet_path}' tidak ditemukan! Jalankan Sesi 2 terlebih dahulu.")
        return False

    try:
        # ------------------------------------------------------------------
        # Pendekatan 1: Pandas + SQLAlchemy (engine database)
        # ------------------------------------------------------------------
        logging.info("Membuat engine koneksi ke PostgreSQL via SQLAlchemy...")
        engine = create_engine(DB_URI)
        logging.info("Engine berhasil dibuat.")

        # 1. Read Parquet menggunakan Pandas
        df_parquet = pd.read_parquet(parquet_path)
        logging.info(f"Sukses membaca Parquet. Ditemukan {len(df_parquet)} baris data.")
        logging.info(f"Kolom yang terdeteksi: {list(df_parquet.columns)}")
        logging.info(f"Tipe data tiap kolom:\n{df_parquet.dtypes}")

        # 2. Drop tabel lama + buat ulang (simulasi if_table_exists='replace')
        drop_table_if_exists(engine, TARGET_TABLE)

        # 3. Write ke database PostgreSQL
        #    Parameter if_exists='replace' di pd.to_sql hanya bekerja dalam satu sesi,
        #    tapi untuk safety kita drop manual dulu.
        logging.info(f"Menulis data ke database PostgreSQL -> Tabel: {TARGET_TABLE}...")
        df_parquet.to_sql(
            name=TARGET_TABLE.split(".")[-1],      # nama tabel saja (tanpa skema)
            con=engine,
            schema=TARGET_TABLE.split(".")[0],      # skema dipisahkan
            if_exists="replace",
            index=False,
            method="multi"                          # insert multi-baris untuk kecepatan
        )
        logging.info("✅ SUKSES: Data berhasil masuk ke PostgreSQL menggunakan Pandas!")
        return True

    except ImportError as ie:
        logging.error("Gagal melakukan load database! Dependency belum terinstal.")
        logging.error("Instruksi: Jalankan 'pip install pandas pyarrow psycopg2-binary sqlalchemy'")
        logging.error(f"Detail error: {ie}")

    except Exception as e:
        logging.error(f"Terjadi kegagalan saat menulis ke PostgreSQL: {e}")
        logging.warning("Saran: Pastikan Docker Desktop aktif dan container 'postgres_dw_sesi3' sudah running.")

    finally:
        # Tutup engine jika berhasil dibuat
        if 'engine' in locals():
            engine.dispose()
            logging.info("Engine database ditutup.")

    logging.info("=== PROSES SELESAI DENGAN ANOMALI ===\n")
    return False


# =====================================================================
# 5. EKSEKUSI UTAMA
# =====================================================================
if __name__ == "__main__":
    load_parquet_to_postgres()