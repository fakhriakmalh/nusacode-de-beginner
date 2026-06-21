# app.py
# File latihan Sesi 1 - Python Core, Error Handling, & Logging
# Diketik bareng instruktur di kelas!

import logging
import sys

# =====================================================================
# 1. KONFIGURASI LOGGING (Menggantikan print biasa agar tercatat rapi)
# =====================================================================
logging.basicConfig(
    level=logging.INFO, # Menentukan level log minimum yang dicatat
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"), # Log ditulis ke file
        logging.StreamHandler(sys.stdout)                # Log juga muncul di terminal
    ]
)

# Dummy data transaksi inventaris toko (sengaja dibuat kotor untuk memicu error)
data_barang = [
    {"nama": "Laptop", "harga_total": 50000000, "jumlah": 5},
    {"nama": "Mouse", "harga_total": 300000, "jumlah": 0},      # Jumlah 0 -> Bisa memicu ZeroDivisionError!
    {"nama": "Keyboard", "harga_total": 1200000},               # Key 'jumlah' hilang -> Bisa memicu KeyError!
    {"nama": "Monitor", "harga_total": 15000000, "jumlah": 3}
]

# =====================================================================
# FASE 1: MENCOBA MENULIS SECARA INSTAN (Rentan Crash)
# =====================================================================
def hitung_harga_satuan_rusak():
    # KODE INI AKAN CRASH!
    # Jika dijalankan, ia akan berhenti di barang kedua (ZeroDivisionError) atau ketiga (KeyError)
    print("\n--- FASE 1: Menghitung Harga Satuan (Tanpa Proteksi) ---")
    for barang in data_barang:
        nama = barang["nama"]
        total = barang["harga_total"]
        jumlah = barang["jumlah"]
        
        harga_satuan = total / jumlah
        print(f"Barang: {nama} | Harga Satuan: Rp {harga_satuan:,}")


# =====================================================================
# FASE 2: MEMPERBAIKI DENGAN TRY-EXCEPT & LOGGING (Robust/Tangguh)
# =====================================================================
def hitung_harga_satuan_robust():
    logging.info("=== Memulai Pipeline Hitung Harga Satuan ===")
    
    for idx, barang in enumerate(data_barang):
        nama = barang.get("nama", f"Barang_Tanpa_Nama_{idx}")
        
        try:
            # Mengambil data dengan aman
            total = barang["harga_total"]
            
            # Sengaja kita ambil secara direct agar memicu exception jika key hilang
            jumlah = barang["jumlah"] 
            
            # Kalkulasi harga satuan
            harga_satuan = total / jumlah
            
            # Logging info jika sukses diproses
            logging.info(f"SUKSES: {nama} | Harga Satuan: Rp {harga_satuan:,.2f}")
            
        except KeyError as ke:
            # Menangkap error jika key 'jumlah' atau 'harga_total' tidak ditemukan
            logging.error(f"GAGAL PROSES: Data barang '{nama}' tidak memiliki kolom {ke}! Melewati baris...")
            
        except ZeroDivisionError:
            # Menangkap error pembagian dengan nol
            logging.error(f"GAGAL PROSES: Jumlah barang '{nama}' bernilai 0 (pembagian nol)! Melewati baris...")
            
        except Exception as e:
            # Menangkap error tidak terduga lainnya agar program tidak mati total
            logging.critical(f"FATAL ERROR pada '{nama}': {e}")
            
    logging.info("=== Pipeline Selesai Diproses ===\n")


# =====================================================================
# TOMBOL AKTIVASI PROGRAM
# =====================================================================
if __name__ == "__main__":
    # INSTRUKTUR: Di kelas, jalankan fungsi rusak dulu untuk demo error.
    # Setelah peserta paham error-nya, comment baris di bawah dan jalankan fungsi robust!
    
    # hitung_harga_satuan_rusak() # <-- Jalankan ini dulu di 30 menit awal
    hitung_harga_satuan_robust()  # <-- Aktifkan ini untuk perbaikan & logging
