# ingest_to_clickhouse.py
# Script Hands-on Sesi 3 - Ingesti data CSV Olist ke ClickHouse
# Menggunakan Pandas dan clickhouse-connect
#
# Dataset: Olist Brazilian E-Commerce (Kaggle)
# Link: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
#
# Klasifikasi Tabel:
#   Fact Tables  : fact_order, fact_order_item, fact_order_payment, fact_order_review
#   Dim Tables   : dim_customer, dim_geolocation, dim_product, dim_product_category, dim_seller
#
# Package tambahan:
#   1. pandas             -> untuk membaca CSV & transformasi data
#   2. clickhouse-connect -> driver ClickHouse resmi berbasis HTTP
#
# Install:
#   pip install pandas clickhouse-connect

import os
import sys
import time
import logging
import pandas as pd
import clickhouse_connect

# =====================================================================
# 1. KONFIGURASI LOGGING
# =====================================================================
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler("logs/ingest_to_clickhouse.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# =====================================================================
# 2. KONFIGURASI CLICKHOUSE
# =====================================================================
# Menyesuaikan dengan credential di Sesi 1 docker-compose.yml
CH_USER = "clickhousedev"
CH_PASS = "adminpass123"
CH_HOST = "localhost"
CH_PORT = 8123  # HTTP Interface
CH_DB = "nusacode_db"

# Konfigurasi chunksize untuk batch processing
# Set None untuk disable chunking (load semua data sekaligus)
# Set angka (misal 10000) untuk memproses data per batch
CHUNK_SIZE = 10000  # Jumlah baris per batch

# =====================================================================
# 3. DEFINISI TABEL: Mapping CSV -> Table Name (dengan klasifikasi Fact/Dim)
# =====================================================================
# Struktur: (label_tabel, nama_file_csv, nama_tabel_db, kategori)
# Kita pertahankan struktur yang sama dengan postgres script agar mudah dipahami
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
# 4. FUNGSI TYPE MAPPING PANDAS -> CLICKHOUSE
# =====================================================================
def map_pandas_dtype_to_clickhouse(col_name: str, dtype) -> str:
    """
    Memetakan tipe data Pandas ke tipe data ClickHouse yang sesuai,
    dan membungkusnya dalam Nullable untuk menangani nilai kosong (NaN/None).
    """
    dtype_str = str(dtype)
    if "int" in dtype_str:
        base_type = "Int64"
    elif "float" in dtype_str:
        base_type = "Float64"
    elif "bool" in dtype_str:
        base_type = "Bool"
    else:
        # Default ke String untuk objek/string/tipe data lain
        base_type = "String"
    
    return f"Nullable({base_type})"

# =====================================================================
# 5. PIPELINE EKSEKUSI
# =====================================================================
def ingest_csv_to_clickhouse():
    logging.info("=" * 60)
    logging.info("MEMULAI INGESTI DATA OLIST CSV KE CLICKHOUSE")
    logging.info("=" * 60)

    # Buat client ClickHouse
    try:
        # Menghubungkan client clickhouse-connect
        client = clickhouse_connect.get_client(
            host=CH_HOST,
            port=CH_PORT,
            username=CH_USER,
            password=CH_PASS
        )
        # Buat database jika belum ada
        client.command(f"CREATE DATABASE IF NOT EXISTS {CH_DB}")
        logging.info(f"✅ Berhasil terhubung ke ClickHouse dan memastikan database '{CH_DB}' tersedia.")
    except Exception as e:
        logging.error(f"❌ Gagal menghubungkan client ClickHouse: {e}")
        return False

    total_start = time.perf_counter()
    total_success = 0
    total_fail = 0

    for label, csv_filename, table_name_raw, category in DATASET_MAP:
        csv_path = os.path.join(ARCHIVE_DIR, csv_filename)
        # Ekstrak nama tabel murni (tanpa schema 'public.')
        table_name = table_name_raw.split(".")[-1]

        logging.info(f"\n{'─' * 50}")
        logging.info(f"[{category}] {label}")
        logging.info(f"   CSV  : {csv_path}")
        logging.info(f"   Table: {CH_DB}.{table_name}")

        if not os.path.exists(csv_path):
            logging.warning(f"   ⚠ File CSV tidak ditemukan: {csv_path}, dilewati.")
            total_fail += 1
            continue

        try:
            # 1. Hapus tabel lama jika ada
            logging.info(f"   🗑 Menghapus tabel lama {CH_DB}.{table_name} jika ada...")
            client.command(f"DROP TABLE IF EXISTS {CH_DB}.{table_name}")

            # 2. Baca CSV dengan/tanpa chunking
            if CHUNK_SIZE is not None:
                logging.info(f"   📖 Membaca CSV dengan chunksize={CHUNK_SIZE}...")
                chunk_iter = pd.read_csv(csv_path, chunksize=CHUNK_SIZE)
                
                total_rows = 0
                chunk_num = 0
                write_start = time.perf_counter()
                
                for chunk_df in chunk_iter:
                    chunk_num += 1
                    chunk_rows = len(chunk_df)
                    
                    # Pada chunk pertama, buat tabel berdasarkan struktur kolom
                    if chunk_num == 1:
                        logging.info(f"   ✅ Chunk pertama: {chunk_rows} baris, {len(chunk_df.columns)} kolom: {list(chunk_df.columns)}")
                        logging.info(f"   Tipe data awal:\n{chunk_df.dtypes}")
                        
                        # Tangani kolom string/object
                        for col in chunk_df.columns:
                            if chunk_df[col].dtype == 'object':
                                chunk_df[col] = chunk_df[col].apply(lambda x: str(x) if pd.notna(x) else None)
                        
                        # Buat tabel baru dengan kolom dinamis
                        columns_defs = []
                        for col, dtype in chunk_df.dtypes.items():
                            ch_type = map_pandas_dtype_to_clickhouse(col, dtype)
                            columns_defs.append(f"`{col}` {ch_type}")
                        
                        columns_sql = ",\n    ".join(columns_defs)
                        create_sql = f"""
                        CREATE TABLE IF NOT EXISTS {CH_DB}.{table_name} (
                            {columns_sql}
                        ) ENGINE = MergeTree()
                        ORDER BY tuple()
                        """
                        
                        logging.info(f"   🔨 Membuat tabel baru {CH_DB}.{table_name}...")
                        client.command(create_sql)
                    else:
                        # Tangani kolom string/object untuk chunk selanjutnya
                        for col in chunk_df.columns:
                            if chunk_df[col].dtype == 'object':
                                chunk_df[col] = chunk_df[col].apply(lambda x: str(x) if pd.notna(x) else None)
                    
                    # Insert chunk ke ClickHouse
                    logging.info(f"   💾 Menulis chunk #{chunk_num} ({chunk_rows} baris)...")
                    client.insert_df(
                        table=table_name,
                        df=chunk_df,
                        database=CH_DB
                    )
                    total_rows += chunk_rows
                
                write_elapsed = time.perf_counter() - write_start
                logging.info(f"   ✅ SUKSES: {total_rows} baris total dalam {chunk_num} chunks → {CH_DB}.{table_name} ({write_elapsed:.2f}s)")
                
            else:
                # Mode tanpa chunking (load semua sekaligus)
                logging.info(f"   📖 Membaca CSV (mode full load)...")
                df = pd.read_csv(csv_path)
                row_count = len(df)
                logging.info(f"   ✅ Membaca {row_count} baris, {len(df.columns)} kolom: {list(df.columns)}")
                logging.info(f"   Tipe data awal:\n{df.dtypes}")

                # Tangani kolom string/object agar aman dimasukkan ke ClickHouse
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)

                # Buat tabel baru dengan kolom dinamis berdasarkan DataFrame
                columns_defs = []
                for col, dtype in df.dtypes.items():
                    ch_type = map_pandas_dtype_to_clickhouse(col, dtype)
                    columns_defs.append(f"`{col}` {ch_type}")
                
                columns_sql = ",\n    ".join(columns_defs)

                create_sql = f"""
                CREATE TABLE IF NOT EXISTS {CH_DB}.{table_name} (
                    {columns_sql}
                ) ENGINE = MergeTree()
                ORDER BY tuple()
                """
                
                logging.info(f"   🔨 Membuat tabel baru {CH_DB}.{table_name}...")
                client.command(create_sql)

                # Tulis ke ClickHouse
                logging.info(f"   💾 Menulis ke ClickHouse...")
                write_start = time.perf_counter()
                client.insert_df(
                    table=table_name,
                    df=df,
                    database=CH_DB
                )
                write_elapsed = time.perf_counter() - write_start
                logging.info(f"   ✅ SUKSES: {row_count} baris → {CH_DB}.{table_name} ({write_elapsed:.2f}s)")
            
            total_success += 1

        except Exception as e:
            logging.error(f"   ❌ Gagal ingest {label}: {e}")
            total_fail += 1

    total_elapsed = time.perf_counter() - total_start

    # Tutup client
    client.close()
    logging.info("Client ClickHouse ditutup.")

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
    success = ingest_csv_to_clickhouse()
    script_elapsed = time.perf_counter() - script_start
    logging.info(f"TOTAL WAKTU SCRIPT: {script_elapsed:.2f} detik")
    sys.exit(0 if success else 1)