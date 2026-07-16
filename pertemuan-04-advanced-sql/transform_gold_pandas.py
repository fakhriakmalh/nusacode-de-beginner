# transform_gold_pandas.py
# Hands-on Sesi 4 - Transformasi Gold Layer dengan Pandas
# Mengambil data dari raw_schema (fact/dim), melakukan agregasi,
# lalu menulis hasilnya ke schema gold.
#
# 2 query yang dipilih:
#   1. gold.daily_sales_summary  -> agregasi harian (total orders, revenue, items)
#   2. gold.payment_analysis     -> agregasi pembayaran per tipe
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
        logging.FileHandler("logs/transform_gold_pandas.log", encoding="utf-8"),
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
# 3. FUNGSI BANTU
# =====================================================================
def drop_table(engine, table_name: str):
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        conn.commit()
        logging.info(f"   Tabel {table_name} dihapus (jika ada).")

def write_to_db(engine, df: pd.DataFrame, table_name: str, schema: str):
    df.to_sql(
        name=table_name.split(".")[-1],
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi"
    )
    logging.info(f"   ✅ {len(df)} baris → {schema}.{table_name}")

def read_table(engine, table_name: str) -> pd.DataFrame:
    return pd.read_sql(f"SELECT * FROM {table_name}", con=engine)

# =====================================================================
# 4. TRANSFORM: daily_sales_summary
# =====================================================================
def transform_daily_sales(engine) -> pd.DataFrame:
    logging.info("\n" + "─" * 50)
    logging.info("[GOLD] daily_sales_summary")

    fact_order = read_table(engine, "raw_schema.fact_order")
    fact_order_item = read_table(engine, "raw_schema.fact_order_item")

    cancel_status = ["canceled", "unavailable"]
    orders_filtered = fact_order[~fact_order["order_status"].isin(cancel_status)].copy()

    orders_filtered["order_date"] = pd.to_datetime(orders_filtered["order_purchase_timestamp"]).dt.date

    merged = orders_filtered.merge(fact_order_item, on="order_id", how="left")

    grouped = merged.groupby("order_date").agg(
        total_orders=("order_id", "nunique"),
        total_customers=("customer_id", "nunique"),
        total_items_sold=("order_item_id", "count"),
        total_revenue=("price", "sum"),
        total_freight=("freight_value", "sum"),
        avg_item_price=("price", "mean"),
        avg_freight=("freight_value", "mean"),
    ).reset_index()

    grouped["total_gross"] = grouped["total_revenue"] + grouped["total_freight"]
    grouped["total_revenue"] = grouped["total_revenue"].round(2)
    grouped["total_freight"] = grouped["total_freight"].round(2)
    grouped["total_gross"] = grouped["total_gross"].round(2)
    grouped["avg_item_price"] = grouped["avg_item_price"].round(2)
    grouped["avg_freight"] = grouped["avg_freight"].round(2)
    grouped["total_items_sold"] = grouped["total_items_sold"].astype(int)
    grouped["total_orders"] = grouped["total_orders"].astype(int)
    grouped["total_customers"] = grouped["total_customers"].astype(int)

    grouped = grouped.sort_values("order_date").reset_index(drop=True)

    logging.info(f"   Hasil: {len(grouped)} hari, kolom: {list(grouped.columns)}")
    return grouped

# =====================================================================
# 5. TRANSFORM: payment_analysis
# =====================================================================
def transform_payment_analysis(engine) -> pd.DataFrame:
    logging.info("\n" + "─" * 50)
    logging.info("[GOLD] payment_analysis")

    fact_payment = read_table(engine, "raw_schema.fact_order_payment")
    fact_order = read_table(engine, "raw_schema.fact_order")

    cancel_status = ["canceled", "unavailable"]
    valid_orders = fact_order[~fact_order["order_status"].isin(cancel_status)][["order_id"]]

    payments_valid = fact_payment.merge(valid_orders, on="order_id", how="inner")

    grouped = payments_valid.groupby("payment_type").agg(
        total_orders=("order_id", "nunique"),
        total_transactions=("order_id", "count"),
        total_payment_volume=("payment_value", "sum"),
        avg_payment_value=("payment_value", "mean"),
        avg_installments=("payment_installments", "mean"),
        min_payment=("payment_value", "min"),
        max_payment=("payment_value", "max"),
    ).reset_index()

    grouped["total_payment_volume"] = grouped["total_payment_volume"].round(2)
    grouped["avg_payment_value"] = grouped["avg_payment_value"].round(2)
    grouped["avg_installments"] = grouped["avg_installments"].round(2)
    grouped["total_orders"] = grouped["total_orders"].astype(int)
    grouped["total_transactions"] = grouped["total_transactions"].astype(int)

    grouped = grouped.sort_values("total_payment_volume", ascending=False).reset_index(drop=True)

    logging.info(f"   Hasil: {len(grouped)} tipe payment, kolom: {list(grouped.columns)}")
    return grouped

# =====================================================================
# 6. PIPELINE UTAMA
# =====================================================================
def run_gold_transform():
    logging.info("=" * 60)
    logging.info("MEMULAI GOLD LAYER TRANSFORM (PANDAS)")
    logging.info("=" * 60)

    try:
        engine = create_engine(DB_URI)
        logging.info("✅ Engine database berhasil dibuat.")
    except Exception as e:
        logging.error(f"❌ Gagal buat engine: {e}")
        return False

    total_start = time.perf_counter()

    try:
        # --- Transform 1: daily_sales_summary ---
        df_sales = transform_daily_sales(engine)
        drop_table(engine, "gold.daily_sales_summary")
        write_to_db(engine, df_sales, "daily_sales_summary", "gold")

        # --- Transform 2: payment_analysis ---
        df_payment = transform_payment_analysis(engine)
        drop_table(engine, "gold.payment_analysis")
        write_to_db(engine, df_payment, "payment_analysis", "gold")

    except Exception as e:
        logging.error(f"❌ Gagal transformasi: {e}")
        engine.dispose()
        return False

    total_elapsed = time.perf_counter() - total_start
    engine.dispose()

    logging.info(f"\n{'=' * 60}")
    logging.info(f"GOLD TRANSFORM SELESAI dalam {total_elapsed:.2f} detik")
    logging.info(f"{'=' * 60}")
    return True

if __name__ == "__main__":
    script_start = time.perf_counter()
    success = run_gold_transform()
    script_elapsed = time.perf_counter() - script_start
    logging.info(f"TOTAL WAKTU SCRIPT: {script_elapsed:.2f} detik")
    sys.exit(0 if success else 1)