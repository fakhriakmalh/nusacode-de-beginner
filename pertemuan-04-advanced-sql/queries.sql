-- queries.sql
-- Kumpulan query analitik lanjutan (Sesi 4)
-- Diketik bersama instruktur di DBeaver!

-- =====================================================================
-- 1. ADVANCED JOIN & AGGREGATIONS
-- Menggabungkan tabel sales dengan products untuk melihat performa per barang
-- =====================================================================
SELECT 
    p.nama_produk,
    p.kategori,
    SUM(s.jumlah_terjual) AS total_item_terjual,
    SUM(s.total_bayar) AS total_pendapatan
FROM raw_schema.sales s
INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
GROUP BY p.nama_produk, p.kategori
ORDER BY total_pendapatan DESC;


-- =====================================================================
-- 2. COMMON TABLE EXPRESSIONS (CTE)
-- Mempermudah pembacaan query dengan membungkus subquery ke block WITH.
-- Studi kasus: Cari kategori barang yang pendapatannya di atas 50 USD.
-- =====================================================================
WITH pendapatan_kategori_cte AS (
    SELECT 
        p.kategori,
        SUM(s.total_bayar) AS total_pendapatan
    FROM raw_schema.sales s
    INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
    GROUP BY p.kategori
)
SELECT 
    kategori,
    total_pendapatan
FROM pendapatan_kategori_cte
WHERE total_pendapatan > 50.00
ORDER BY total_pendapatan DESC;


-- =====================================================================
-- 3. WINDOW FUNCTIONS (ANALISIS DETAIL BARIS)
-- Analisis dengan "kaca pembesar bergerak" per kelompok data (Partition)
-- =====================================================================

-- A. Perankingan Produk Terlaris per Hari (RANK & DENSE_RANK)
WITH rangking_harian_cte AS (
    SELECT 
        s.tanggal_penjualan,
        p.nama_produk,
        SUM(s.jumlah_terjual) AS qty_harian,
        DENSE_RANK() OVER (
            PARTITION BY s.tanggal_penjualan 
            ORDER BY SUM(s.jumlah_terjual) DESC
        ) AS rangking_penjualan
    FROM raw_schema.sales s
    INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
    GROUP BY s.tanggal_penjualan, p.nama_produk
)
SELECT * 
FROM rangking_harian_cte
WHERE rangking_penjualan = 1; -- Hanya ambil produk terlaris nomor 1 tiap harinya


-- B. Running Total Pendapatan per Produk (SUM OVER)
-- Untuk melihat akumulasi pendapatan produk dari hari ke hari
SELECT 
    s.tanggal_penjualan,
    p.nama_produk,
    s.total_bayar AS pendapatan_hari_ini,
    SUM(s.total_bayar) OVER (
        PARTITION BY s.id_produk 
        ORDER BY s.tanggal_penjualan
    ) AS akumulasi_pendapatan
FROM raw_schema.sales s
INNER JOIN raw_schema.products p ON s.id_produk = p.id_produk
ORDER BY p.nama_produk, s.tanggal_penjualan;
