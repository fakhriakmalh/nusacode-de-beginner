# ingest_to_db_pandas.py
# Script Hands-on Sesi 3 - Ingesti data CSV Olist ke PostgreSQL
# Menggunakan Pandas (sebagai alternatif dari versi Polars)
#
# Dataset: Olist Brazilian E-Commerce (Kaggle)
# Link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
#
# Klasifikasi Tabel:
#   Fact Tables  : fact_order, fact_order_item, fact_order_payment, fact_order_review
#   Dim Tables   : dim_customer, dim_geolocation, dim_product, dim_product_category, dim_seller
#
# Package tambahan:
#   1. pandas       -> untuk membaca CSV & transformasi data
#   2. sqlalchemy   -> sebagai engine koneksi database (ORM-style)
#   3. psycopg2-binary -> driver PostgreSQL untuk SQLAlchemy
#
# Install:
#   pip install pandas pyarrow psycopg2-binary sqlalchemy

import os
import sys
import time
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
DB_USER = "postgres"
DB_PASS = "admindwpass"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_nusacode"

DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =====================================================================
# 3. DEFINISI TABEL: Mapping CSV -> Table Name (dengan klasifikasi Fact/Dim)
# =====================================================================
# Struktur: (label_tabel, nama_file_csv, nama_tabel_db, kategori)
DATASET_MAP = [
    # --- DIMENSION TABLES ---
    ("dim_customer",        "olist_customers_dataset.csv",              "public.dim_customer",        "DIM"),
    ("dim_geolocation",     "olist_geolocation_dataset.csv",           "public.dim_geolocation",     "DIM"),
    ("dim_product",         "olist_products_dataset.csv",              "public.dim_product",         "DIM"),
    ("dim_product_category","product_category_name_translation.csv",   "public.dim_product_category","DIM"),
    ("dim_seller",          "olist_sellers_dataset.csv",               "public.dim_seller",          "DIM"),
    # --- FACT TABLES ---
    ("fact_order",          "olist_orders_dataset.csv",                "public.fact_order",          "FACT"),
    ("fact_order_item",     "olist_order_items_dataset.csv",           "public.fact_order_item",     "FACT"),
    ("fact_order_payment",  "olist_order_payments_dataset.csv",        "public.fact_order_payment",  "FACT"),
    ("fact_order_review",   "olist_order_reviews_dataset.csv",         "public.fact_order_review",   "FACT"),
]

ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), "archive")

# =====================================================================
# 4. FUNGSI BANTU DROP TABLE
# =====================================================================
def drop_table_if_exists(engine, table_name: str):
    """
    Menghapus tabel jika sudah ada.
    Digunakan untuk simulasi if_table_exists='replace'
    """
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()
        logging.info(f"   Tabel {table_name} berhasil dihapus (jika ada).")

# =====================================================================
# 5. PIPELINE EKSEKUSI
# =====================================================================
def ingest_csv_to_postgres():
    logging.info("=" * 60)
    logging.info("MEMULAI INGESTI DATA OLIST CSV KE POSTGRESQL (PANDAS)")
    logging.info("=" * 60)

    # Buat engine koneksi
    try:
        engine = create_engine(DB_URI)
        logging.info("✅ Engine database berhasil dibuat.")
    except Exception as e:
        logging.error(f"❌ Gagal membuat engine database: {e}")
        return False

    total_start = time.perf_counter()

    total_success = 0
    total_fail = 0

    for label, csv_filename, table_name, category in DATASET_MAP:
        csv_path = os.path.join(ARCHIVE_DIR, csv_filename)

        logging.info(f"\n{'─' * 50}")
        logging.info(f"[{category}] {label}")
        logging.info(f"   CSV  : {csv_path}")
        logging.info(f"   Table: {table_name}")

        if not os.path.exists(csv_path):
            logging.warning(f"   ⚠ File CSV tidak ditemukan: {csv_path}, dilewati.")
            total_fail += 1
            continue

        try:
            # 1. Baca CSV dengan Pandas
            logging.info(f"   📖 Membaca CSV...")
            df = pd.read_csv(csv_path)
            row_count = len(df)
            logging.info(f"   ✅ Membaca {row_count} baris, {len(df.columns)} kolom: {list(df.columns)}")
            logging.info(f"   Tipe data:\n{df.dtypes}")

            # 2. Drop tabel lama + buat ulang
            drop_table_if_exists(engine, table_name)

            # 3. Tulis ke PostgreSQL
            logging.info(f"   💾 Menulis ke {table_name}...")
            write_start = time.perf_counter()
            df.to_sql(
                name=table_name.split(".")[-1],
                con=engine,
                schema=table_name.split(".")[0],
                if_exists="replace",
                index=False,
                chunksize=500,
                method="multi"
            )
            write_elapsed = time.perf_counter() - write_start
            logging.info(f"   ✅ SUKSES: {row_count} baris → {table_name} ({write_elapsed:.2f}s)")
            total_success += 1

        except Exception as e:
            logging.error(f"   ❌ Gagal ingest {label}: {e}")
            total_fail += 1

    total_elapsed = time.perf_counter() - total_start

    # Tutup engine
    engine.dispose()
    logging.info("Engine database ditutup.")

    logging.info(f"\n{'=' * 60}")
    logging.info(f"RINGKASAN INGESTI: {total_success} sukses, {total_fail} gagal dari {len(DATASET_MAP)} tabel")
    logging.info(f"TOTAL WAKTU EKSEKUSI: {total_elapsed:.2f} detik")
    logging.info(f"{'=' * 60}")

    return total_fail == 0


# =====================================================================
# 6. EKSEKUSI UTAMA
# =====================================================================
if __name__ == "__main__":
    script_start = time.perf_counter()
    success = ingest_csv_to_postgres()
    script_elapsed = time.perf_counter() - script_start
    logging.info(f"TOTAL WAKTU SCRIPT: {script_elapsed:.2f} detik")
    sys.exit(0 if success else 1)