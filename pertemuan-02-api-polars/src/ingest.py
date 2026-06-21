# ingest.py
# Script Produksi ETL - Refactor dari Jupyter Notebook Sesi 2
# Digunakan untuk mengotomatiskan penarikan data dari API ke format penyimpanan Parquet

import os
import sys
import json
import logging
import requests
import polars as pl

# ==========================================
# 1. KONFIGURASI LOGGING
# ==========================================
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("Ingestion_Pipeline")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

# Handler File
file_handler = logging.FileHandler("logs/ingest.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Handler Console (Terminal)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ==========================================
# 2. PROSES ETL MODULAR
# ==========================================

def extract(api_url: str, fallback_path: str) -> list:
    """Mengambil data mentah JSON dari API dengan fallback file lokal."""
    logger.info(f"[EXTRACT] Menghubungi API Endpoint: {api_url}")
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        logger.info(f"[EXTRACT] Penarikan data dari API sukses. Jumlah data: {len(raw_data.get('products', []))}")
        return raw_data.get("products", [])
    except Exception as e:
        logger.warning(f"[EXTRACT] API Gagal diakses ({e}). Membuka file fallback: {fallback_path}")
        
        if not os.path.exists(fallback_path):
            logger.error(f"[EXTRACT] File backup '{fallback_path}' tidak ditemukan!")
            raise FileNotFoundError(f"File backup {fallback_path} tidak ditemukan!")
            
        with open(fallback_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        logger.info(f"[EXTRACT] Sukses memuat data dari fallback lokal. Jumlah data: {len(raw_data.get('products', []))}")
        return raw_data.get("products", [])


def transform(products_list: list) -> pl.DataFrame:
    """Melakukan pembersihan data secara cepat menggunakan Polars Lazy Evaluation."""
    logger.info("[TRANSFORM] Memuat data produk ke Polars DataFrame")
    
    # 1. Membuat DataFrame biasa
    df = pl.DataFrame(products_list)
    
    # 2. Mengaktifkan mode Lazy (Robot Pekerja)
    lazy_df = df.lazy()
    
    # 3. Merancang urutan pembersihan (Lazy Expressions)
    processed_lazy = (
        lazy_df
        # Mengisi kolom kosong
        .with_columns([
            pl.col("price").fill_null(pl.col("price").median()),
            pl.col("stock").fill_null(0).cast(pl.Int64),
            pl.col("category").fill_null("other"),
            pl.col("rating").fill_null(0.0)
        ])
        # Filter rating >= 4.0
        .filter(
            pl.col("rating") >= 4.0
        )
        # Memilih & memformat nama kolom
        .select([
            pl.col("id").alias("id_produk"),
            pl.col("title").str.to_uppercase().alias("nama_produk"),
            pl.col("price").alias("harga"),
            pl.col("stock").alias("stok"),
            pl.col("category").alias("kategori"),
            pl.col("rating").alias("skor_rating")
        ])
    )
    
    # 4. Eksekusi optimasi rencana query (collect)
    logger.info("[TRANSFORM] Menjalankan kompilasi optimasi query Polars (collect)")
    final_df = processed_lazy.collect()
    logger.info(f"[TRANSFORM] Transformasi sukses. Dari {len(df)} baris tereduksi menjadi {len(final_df)} baris.")
    
    return final_df


def load(df: pl.DataFrame, output_path: str):
    """Menyimpan DataFrame hasil olahan ke format Columnar Parquet."""
    logger.info(f"[LOAD] Menyimpan data bersih ke format Parquet di: {output_path}")
    try:
        # Menulis langsung ke file Parquet (sangat hemat disk & memori)
        df.write_parquet(output_path)
        logger.info("[LOAD] Sukses! File Parquet berhasil ditulis.")
    except Exception as e:
        logger.error(f"[LOAD] Gagal menyimpan file Parquet! Error: {e}")
        raise e


# ==========================================
# 3. RUN PIPELINE
# ==========================================
if __name__ == "__main__":
    logger.info("=== START PIPELINE PRODUCTS INGESTION ===")
    
    API_URL = "https://dummyjson.com/products"
    FALLBACK_FILE = "data_dummy.json"
    OUTPUT_FILE = "products_cleaned.parquet"
    
    # Menyesuaikan path fallback berdasarkan direktori kerja terminal saat ini
    if not os.path.exists(FALLBACK_FILE) and os.path.exists(f"../{FALLBACK_FILE}"):
        FALLBACK_FILE = f"../{FALLBACK_FILE}"
        
    try:
        # Step 1: Extract
        raw_products = extract(API_URL, FALLBACK_FILE)
        
        # Step 2: Transform
        cleaned_data = transform(raw_products)
        
        # Step 3: Load
        load(cleaned_data, OUTPUT_FILE)
        
        logger.info("=== PIPELINE PRODUCTS INGESTION SUCCESSFUL ===")
        
    except Exception as fatal_err:
        logger.critical(f"=== PIPELINE PRODUCTS INGESTION CRASHED: {fatal_err} ===", exc_info=True)
        sys.exit(1)
