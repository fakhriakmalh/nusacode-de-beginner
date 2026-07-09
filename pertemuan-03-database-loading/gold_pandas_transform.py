# gold_pandas_transform.py
# Hands-on - Gold Layer transformasi dengan Pandas
# Membaca data dari raw_schema lalu melakukan agregasi
# dan menulis hasilnya ke schema gold
#
# 2 Query:
#   1. daily_sales_summary  -> agregasi penjualan harian
#   2. payment_analysis     -> agregasi pembayaran per tipe
#
# Jalankan SETELAH ingest_to_db.py sukses
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
        logging.FileHandler("logs/gold_pandas_transform.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# =====================================================================
# 2. KONFIGURASI DATABASE (sama dengan ingest_to_db.py)
# =====================================================================
DB_USER = "postgres"
DB_PASS = "admindwpass"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dw_nusacode"

DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# =====================================================================
# 3. FUNGSI BANTU DATABASE
# =====================================================================
def drop_table(engine, table_name: str):
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()
        logging.info(f"   Tabel {table_name} dihapus (jika ada).")

def read_table(engine, table_name: str) -> pd.DataFrame:
    logging.info(f"   Membaca {table_name}...")
    df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
    logging.info(f"   ✅ {len(df)} baris, {len(df.columns)} kolom")
    return df

def write_table(engine, df: pd.DataFrame, table_name: str):
    schema, tbl = table_name.split(".")
    df.to_sql(
        name=tbl,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi"
    )
    logging.info(f"   💾 {len(df)} baris → {table_name}")

# =====================================================================
# 4. TRANSFORM 1: Daily Sales Summary
#    SQL: seed_data.sql baris 20-35
# =====================================================================
def build_daily_sales_summary(engine) -> pd.DataFrame:
    logging.info("\n" + "─" * 50)
    logging.info("TRANSFORM: gold.daily_sales_summary")

    orders = read_table(engine, "raw_schema.fact_order")
    items = read_table(engine, "raw_schema.fact_order_item")

    cancel = ["canceled", "unavailable"]
    orders_valid = orders[~orders["order_status"].isin(cancel)].copy()
    orders_valid["order_date"] = pd.to_datetime(
        orders_valid["order_purchase_timestamp"]
    ).dt.date

    merged = orders_valid.merge(items, on="order_id", how="left")

    grouped = merged.groupby("order_date").agg(
        total_orders       =("order_id", "nunique"),
        total_customers   =("customer_id", "nunique"),
        total_items_sold  =("order_item_id", "count"),
        total_revenue     =("price", "sum"),
        total_freight     =("freight_value", "sum"),
        avg_item_price    =("price", "mean"),
        avg_freight       =("freight_value", "mean"),
    ).reset_index()

    grouped["total_gross"] = grouped["total_revenue"] + grouped["total_freight"]

    num_cols = ["total_revenue", "total_freight", "total_gross",
                "avg_item_price", "avg_freight"]
    for col in num_cols:
        grouped[col] = grouped[col].round(2)

    int_cols = ["total_orders", "total_customers", "total_items_sold"]
    for col in int_cols:
        grouped[col] = grouped[col].astype(int)

    grouped = grouped.sort_values("order_date").reset_index(drop=True)
    logging.info(f"   ✅ Hasil: {len(grouped)} hari")
    return grouped

# =====================================================================
# 5. TRANSFORM 2: Payment Analysis
#    SQL: seed_data.sql baris 119-133
# =====================================================================
def build_payment_analysis(engine) -> pd.DataFrame:
    logging.info("\n" + "─" * 50)
    logging.info("TRANSFORM: gold.payment_analysis")

    payments = read_table(engine, "raw_schema.fact_order_payment")
    orders = read_table(engine, "raw_schema.fact_order")

    cancel = ["canceled", "unavailable"]
    valid_order_ids = orders[~orders["order_status"].isin(cancel)][["order_id"]]

    # Inner join: hanya payment dari order yang valid
    merged = payments.merge(valid_order_ids, on="order_id", how="inner")

    grouped = merged.groupby("payment_type").agg(
        total_orders        =("order_id", "nunique"),
        total_transactions  =("order_id", "count"),
        total_payment_volume=("payment_value", "sum"),
        avg_payment_value   =("payment_value", "mean"),
        avg_installments   =("payment_installments", "mean"),
        min_payment        =("payment_value", "min"),
        max_payment        =("payment_value", "max"),
    ).reset_index()

    grouped["total_payment_volume"] = grouped["total_payment_volume"].round(2)
    grouped["avg_payment_value"]    = grouped["avg_payment_value"].round(2)
    grouped["avg_installments"]     = grouped["avg_installments"].round(2)
    grouped["total_orders"]         = grouped["total_orders"].astype(int)
    grouped["total_transactions"]   = grouped["total_transactions"].astype(int)

    grouped = grouped.sort_values("total_payment_volume", ascending=False).reset_index(drop=True)
    logging.info(f"   ✅ Hasil: {len(grouped)} tipe payment")
    return grouped

# =====================================================================
# 6. PIPELINE UTAMA
# =====================================================================
def run_gold_transform():
    logging.info("=" * 60)
    logging.info("MEMULAI GOLD LAYER TRANSFORM DENGAN PANDAS")
    logging.info("=" * 60)

    engine = create_engine(DB_URI)
    logging.info("✅ Koneksi database berhasil.")

    total_start = time.perf_counter()

    try:
        # Buat schema gold
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold"))
            conn.commit()

        # Transform 1
        df_sales = build_daily_sales_summary(engine)
        drop_table(engine, "gold.daily_sales_summary")
        write_table(engine, df_sales, "gold.daily_sales_summary")

        # Transform 2
        df_payment = build_payment_analysis(engine)
        drop_table(engine, "gold.payment_analysis")
        write_table(engine, df_payment, "gold.payment_analysis")

    except Exception as e:
        logging.error(f"❌ Gagal: {e}")
        engine.dispose()
        return False

    total_elapsed = time.perf_counter() - total_start
    engine.dispose()

    logging.info(f"\n{'=' * 60}")
    logging.info(f"SELESAI! Total waktu: {total_elapsed:.2f} detik")
    logging.info(f"{'=' * 60}")
    return True

if __name__ == "__main__":
    start = time.perf_counter()
    ok = run_gold_transform()
    elapsed = time.perf_counter() - start
    logging.info(f"Total script: {elapsed:.2f} detik")
    sys.exit(0 if ok else 1)