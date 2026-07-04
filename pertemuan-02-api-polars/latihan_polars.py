import polars as pl
import requests
import json

api_url = "https://dummyjson.com/products"

try:
    print(f"Mencoba mengambil data dari: {api_url}...")
    response = requests.get(api_url, timeout=5)
    response.raise_for_status()
    raw_data = response.json()
    print(f"Sukses! Ditemukan {len(raw_data['products'])} data dari API.")
except Exception as e:
    print(f" Gagal mengakses API: {e}")
    print("Menggunakan file fallback lokal 'data_dummy.json'...")
    with open("../data_dummy.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    print(f"Sukses memuat {len(raw_data['products'])} data dari file fallback.")

products_list = raw_data["products"]

# 1. Data masuk pertama kali sebagai Eager DataFrame
df_eager = pl.DataFrame(products_list)
print("Jumlah row awal:", df_eager.height)

# =====================================================================
# MASUK KE MODE LAZY SEBELUM TRANSFORMATION
# =====================================================================
# Mengubah DataFrame menjadi LazyFrame menggunakan .lazy()
lf = df_eager.lazy()

# 2. Mengisi null & casting pada data utama (Masih berupa Rencana/Lazy)
lf_cleaned = lf.with_columns([
    pl.col('price').fill_null(pl.col('price').median()),
    pl.col('stock').fill_null(0).cast(pl.Int64),
    pl.col('category').fill_null('other'),
    pl.col('rating').fill_null(0.0)
])

# 3. Filter, Rename, Format Text, dan Pilih Kolom Akhir (Masih berupa Rencana/Lazy)
lf_final_plan = (
    lf_cleaned
    .filter(pl.col('rating') >= 4.0)
    .select([
        pl.col('id').alias('id_produk'),
        pl.col('title').str.to_uppercase().alias('nama_produk'),
        pl.col('price').alias('harga'),
        pl.col('stock').alias('stok'),
        pl.col('category').alias('kategori'),
        pl.col('rating').alias('skor_rating')
    ])
)

# Jika kita print lf_final_plan di sini, dia TIDAK AKAN menampilkan data,
# melainkan hanya menampilkan Query Plan (Rencana Eksekusi).
print("\n--- Rencana Eksekusi Polars (Optimized Query Plan) ---")
print(lf_final_plan.explain()) 

# =====================================================================
# EKSEKUSI NYATA DENGAN .collect()
# =====================================================================
print("\nMengeksekusi semua transformasi secara paralel...")
final_df = lf_final_plan.collect()

print("\n--- Hasil Akhir (Kembali ke Eager DataFrame) ---")
print(final_df)
print("Jumlah row setelah filter:", final_df.height)
print("Pembersihan data versi Polars Lazy selesai.")