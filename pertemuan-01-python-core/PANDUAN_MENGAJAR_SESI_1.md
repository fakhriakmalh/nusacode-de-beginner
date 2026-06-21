# Panduan Mengajar Sesi 1: The DE Environment & Python Core
**Materi:** CLI, Docker PostgreSQL, Exception Handling, & Logging di VS Code (120 Menit)

---

## 🍳 1. Analogi Dunia Nyata (2 Menit)

Gunakan analogi **"Dapur Restoran Modern"** untuk menjelaskan tools dasar Data Engineering kepada pemula:

*   **Script Python (`.py`)** = **SOP & Resep Masakan**. Dia adalah kertas berisi instruksi detail tentang langkah apa yang harus dilakukan koki (misalnya: kupas bawang, tumis, sajikan).
*   **Docker** = **Kontainer Dapur Portable (Food Truck)**. Jika kita ingin buka cabang, kita tidak perlu membangun gedung dapur baru dari nol (install database manual yang sering ribet dan beda-beda di Windows/Mac). Kita tinggal sewa *Food Truck* instan yang sudah otomatis lengkap dengan kompor, kulkas, dan oven yang siap pakai (PostgreSQL, Python, dll) hanya dalam 1 klik.
*   **Git** = **Buku Catatan Sejarah Resep**. Jika asisten koki mengubah takaran garam di resep lalu masakan jadi terlalu asin, kita bisa melihat siapa yang mengubahnya, kapan diubah, dan bisa mengembalikan resep tersebut ke versi kemarin yang rasanya pas secara instan.

---

## ⏰ 2. Rencana Alokasi Waktu (120 Menit)

*   **10 Menit — Pembuka & Analogi Dapur**
    *   Mencairkan suasana, analogi Dapur Restoran, dan memperkenalkan mindset operasional di Data Engineering.
*   **20 Menit — Fast Onboarding Environment (Docker & CLI)**
    *   Mengajari perintah dasar navigasi CLI (`pwd`, `ls`, `mkdir`, `cd`).
    *   Menyalakan PostgreSQL menggunakan Docker Compose di terminal VS Code.
*   **45 Menit — Live Code-Along Bagian 1: Menulis & Menganalisis Error**
    *   Peserta mengetik bersama instruktur file `app.py` Fase 1 (tanpa try-except).
    *   Menjalankan script, memicu error `ZeroDivisionError` & `KeyError`, dan membaca *Traceback* terminal.
*   **30 Menit — Live Code-Along Bagian 2: Try-Except & Logging**
    *   Merefaktor `app.py` menjadi tangguh (Robust).
    *   Mengganti `print()` dengan library `logging` bawaan dan membaca file output `app.log`.
*   **15 Menit — Penutup, Q&A, & Distribusi Cheat Sheet**
    *   Review singkat mengapa pipeline tidak boleh crash karena satu data kotor.
    *   Membagikan Cheat Sheet ke grup chat kelas.

---

## 🛠️ 3. Panduan Setup & Jalur Live Coding

### A. Docker PostgreSQL Super Simpel (20 Menit)
1.  Bimbing peserta membuat folder `pertemuan-01-python-core`.
2.  Minta peserta membuat file [docker-compose.yml](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-01-python-core/docker-compose.yml).
3.  Jelaskan kodenya:
    *   `image: postgres:15-alpine` -> Mengunduh sistem database PostgreSQL versi ringan.
    *   `POSTGRES_PASSWORD=admindwpass` -> Set password masuk database.
    *   `ports: - "5432:5432"` -> Membuka pintu gerbang database agar aplikasi luar bisa masuk.
4.  Minta peserta mengetik perintah ini di terminal untuk menyalakan database:
    ```bash
    docker-compose up -d
    ```
    *(Jelaskan bendera `-d` berarti container berjalan di belakang layar secara diam-diam).*

---

### B. Menulis Script `app.py` & Menjinakkan Error (75 Menit)

**Narasi Instruktur:**
> *"Oke guys, sekarang database kita sudah menyala. Mari kita mulai coding script Python pertama kita di VS Code. Bayangkan kita adalah Data Engineer di sebuah marketplace yang sedang membuat penarik data inventaris barang. Kita buat file bernama `app.py`!"*

1.  Minta peserta mengetik bagian awal data dan fungsi rusak di [app.py](file:///Users/fakhriakmalh/Documents/nusacode/pertemuan-01-python-core/app.py):
    ```python
    data_barang = [
        {"nama": "Laptop", "harga_total": 50000000, "jumlah": 5},
        {"nama": "Mouse", "harga_total": 300000, "jumlah": 0},      # Jumlah 0!
        {"nama": "Keyboard", "harga_total": 1200000},               # Kolom jumlah hilang!
        {"nama": "Monitor", "harga_total": 15000000, "jumlah": 3}
    ]
    ```
2.  Ketik fungsi rusak `hitung_harga_satuan_rusak()` dan jalankan:
    ```bash
    python pertemuan-01-python-core/app.py
    ```
3.  **Melihat Crash:** Program terhenti secara kasar dan memunculkan error:
    ```text
    ZeroDivisionError: division by zero
    ```
4.  **Analisis Bersama:** 
    *   Tunjukkan baris penyebab error di terminal.
    *   Jelaskan: *"Di dunia DE, jika server sedang mengolah 1 juta transaksi, lalu ada 1 data yang pembaginya 0, script kita mati di tengah jalan. Data sisa yang masih bagus di bawahnya (seperti Monitor) tidak akan pernah terproses. Ini kerugian bisnis!"*

5.  **Refactoring ke Try-Except:**
    Minta peserta menyalakan fungsi `hitung_harga_satuan_robust()` dan menjelaskan cara membungkus kode rentan dengan blok penyelamat:
    ```python
    try:
        harga_satuan = total / jumlah
    except ZeroDivisionError:
        print("Ada barang yang jumlahnya 0! Dilewati saja.")
    except KeyError:
        print("Kolom jumlah tidak ditemukan! Dilewati saja.")
    ```

6.  **Transisi dari `print()` ke `logging`:**
    Jelaskan: *"Kalau program jalan di server cloud, output `print()` akan hilang tertimbun atau tidak tersimpan permanen. Kita wajib menggunakan logging!"*
    *   Tulis setup `logging.basicConfig()` di bagian atas script.
    *   Ganti semua kata `print()` menjadi `logging.info()` atau `logging.error()`.
    *   Jalankan script robust, lalu minta peserta membuka file baru bernama `app.log` yang terbentuk di folder proyek.
    *   Tunjukkan timestamp log sebagai bukti riwayat audit.

---

## 📝 4. Lembar Contekkan (Cheat Sheet) CLI & Git

Bagikan bagian ini ke grup kelas sebagai pegangan pasca-sesi:

### 1. Perintah CLI Dasar (Navigasi Terminal)
| Perintah | Arti | Kegunaan | Contoh |
| :--- | :--- | :--- | :--- |
| `pwd` | Print Working Directory | Cek "Saya ada di folder mana sekarang?" | `pwd` |
| `ls` | List | Tampilkan isi file di folder aktif | `ls` atau `ls -la` |
| `mkdir <nama>` | Make Directory | Membuat folder baru | `mkdir dataset` |
| `cd <nama>` | Change Directory | Masuk ke dalam folder tertentu | `cd pertemuan-01-python-core` |
| `cd ..` | Change Directory Up | Keluar folder (naik 1 tingkat ke atas) | `cd ..` |
| `clear` | Clear | Bersihkan layar terminal yang penuh | `clear` |

### 2. Alur Kerja Git (Git Workflow)
Gunakan urutan ini jika ingin menyimpan kode Anda ke GitHub:
1.  **Inisialisasi Git** (Hanya 1 kali di awal proyek):
    ```bash
    git init
    ```
2.  **Hubungkan ke Cloud GitHub** (Ganti link dengan repositori milik Anda):
    ```bash
    git remote add origin https://github.com/username/repositori-anda.git
    ```
3.  **Bungkus Perubahan Data**:
    ```bash
    git add .
    # (Tanda titik berarti membungkus semua file baru / perubahan)
    ```
4.  **Tulis Catatan Perubahan**:
    ```bash
    git commit -m "fitur: membuat script app.py dengan logging"
    ```
5.  **Kirim ke GitHub**:
    ```bash
    git push -u origin main
    ```
