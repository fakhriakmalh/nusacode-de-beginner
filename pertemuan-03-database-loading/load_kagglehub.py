"""
load_kagglehub.py
==================
Script untuk mendownload dataset Olist Brazilian E-Commerce dari Kaggle.

Dataset: Olist Brazilian E-Commerce
Link:    https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Jika script gagal (misal kagglehub belum terinstal), cukup download manual dari link di atas
dan extract file CSV ke folder 'archive/'.

Cara install kagglehub:
    pip install kagglehub

Cara jalankan:
    python pertemuan-03-database-loading/load_kagglehub.py
"""

import kagglehub
import os
import shutil

# Path ke folder archive lokal
ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), "archive")

def main():
    print("📥 Mendownload dataset Olist Brazilian E-Commerce dari Kaggle...")
    try:
        # Download latest version
        path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
        print(f"✅ Dataset berhasil didownload ke: {path}")
        print(f"📂 File CSV sudah tersedia di folder: {ARCHIVE_DIR}")
        print("\n🔗 Link Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
    except Exception as e:
        print(f"❌ Gagal mendownload: {e}")
        print("\n🔗 Download manual: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        print("📂 Extract file CSV ke folder: archive/")

if __name__ == "__main__":
    main()