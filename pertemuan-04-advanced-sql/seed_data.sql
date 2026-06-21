-- seed_data.sql
-- Script untuk membuat data transaksi penjualan historis (Sesi 4)
-- Jalankan ini di DBeaver sebelum memulai sesi analisis query!

-- 1. Membuat Tabel Transaksi Penjualan
CREATE TABLE IF NOT EXISTS raw_schema.sales (
    sale_id SERIAL PRIMARY KEY,
    id_produk INT,
    jumlah_terjual INT NOT NULL,
    total_bayar DECIMAL(12, 2) NOT NULL,
    tanggal_penjualan DATE NOT NULL
);

-- 2. Mengosongkan Tabel untuk Menghindari Duplikasi Latihan
TRUNCATE TABLE raw_schema.sales;

-- 3. Menyuntikkan Data Transaksi Historis (Menghubungkan ke produk ID 1, 3, 4, 5)
INSERT INTO raw_schema.sales (id_produk, jumlah_terjual, total_bayar, tanggal_penjualan)
VALUES
-- Hari ke-1 (2026-06-01)
(1, 2, 19.98, '2026-06-01'), -- Essence Mascara
(3, 1, 11.49, '2026-06-01'), -- Powder Canister
(4, 3, 38.97, '2026-06-01'), -- Red Lipstick
-- Hari ke-2 (2026-06-02)
(1, 4, 39.92, '2026-06-02'),
(4, 2, 25.98, '2026-06-02'),
(5, 5, 27.45, '2026-06-02'), -- Green Tea Soap
-- Hari ke-3 (2026-06-03)
(3, 2, 22.98, '2026-06-03'),
(5, 10, 54.90, '2026-06-03'),
-- Hari ke-4 (2026-06-04)
(1, 1, 9.99, '2026-06-04'),
(3, 5, 57.45, '2026-06-04'),
(4, 10, 129.90, '2026-06-04'),
-- Hari ke-5 (2026-06-05)
(1, 3, 29.97, '2026-06-05'),
(5, 2, 10.98, '2026-06-05');
