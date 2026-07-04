import pandas as pd
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
df = pd.DataFrame(products_list)
print(df.info())

print("Daftar kolom:", df.columns.tolist())
print("jumlah row nya sekarang ", len(df))

# 1. Filter rating >= 4.0
df_filtered = df[df['rating'] >= 4.0].copy()
print("jumlah row nya sekarang ", len(df_filtered))

# 2. Mengisi null & casting
df['price'] = df['price'].fillna(df['price'].median())
df['stock'] = df['stock'].fillna(0).astype('int64')
df['category'] = df['category'].fillna('other')
df['rating'] = df['rating'].fillna(0.0)


#  3. Rename & Format Text
df_filtered = df_filtered.rename(columns={
    'id': 'id_produk',
    'title': 'nama_produk',
    'price': 'harga',
    'stock': 'stok',
    'category': 'kategori',
    'rating': 'skor_rating'
})

df_filtered['nama_produk'] = df_filtered['nama_produk'].str.upper()

# 4. Memilih kolom akhir
final_df = df_filtered[['id_produk', 'nama_produk', 'harga', 'stok', 'kategori', 'skor_rating']]
print(final_df)

print("Pembersihan data versi Pandas selesai.")



