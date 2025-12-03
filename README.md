# Cash Tracker (Python + Tkinter)

Aplikasi **Cash Tracker** adalah program desktop sederhana berbasis Python dan Tkinter untuk memonitor **pemasukan** dan **pengeluaran** harian. Data disimpan dalam file JSON lokal, sehingga program bisa dijalankan tanpa database eksternal.

---

## 🧾 Fitur Utama

- Input **pemasukan** dan **pengeluaran**
  - Tipe transaksi (pemasukan / pengeluaran)
  - Jumlah
  - Kategori
  - Keterangan
- Ringkasan keuangan:
  - Saldo saat ini
  - Total pengeluaran bulan berjalan
  - Pengeluaran hari ini
- **Riwayat transaksi**
  - Tabel transaksi dengan filter berdasarkan tanggal
  - Edit dan hapus transaksi
- **Visualisasi**
  - Grafik batang:
    - Mode mingguan (pemasukan vs pengeluaran per hari)
    - Mode bulanan (pemasukan vs pengeluaran per minggu, Minggu 1–5)
  - Diagram pie kategori pengeluaran (mingguan / bulanan)
- Penyimpanan data ke file `data_cash.json` secara otomatis
- Watchdog: ketika file JSON berubah, tampilan akan ikut ter-refresh

---

## 🧱 Struktur Proyek

```text
.
├─ main.py         # entry point aplikasi, mengatur GUI Tkinter dan event
├─ charts.py       # logika pembuatan grafik (bar & pie) dengan matplotlib
├─ data_store.py   # manajemen file JSON (init, load, save, lock)
├─ data_cash.json  # file data transaksi (otomatis dibuat saat pertama jalan)

🔧 Prasyarat

Python 3.8 atau lebih baru

Pustaka Python:

tkinter (biasanya sudah include di instalasi Python)

matplotlib

watchdog

Jika ingin menggunakan virtual environment, disarankan membuat venv terlebih dahulu.

📦 Instalasi Dependensi

Dari folder proyek:

pip install matplotlib watchdog


Jika kamu membuat requirements.txt, isinya bisa seperti:

matplotlib
watchdog


Lalu jalankan:

pip install -r requirements.txt

▶️ Cara Menjalankan Program

Clone atau download repositori ini:

git clone https://github.com/USERNAME/NAMA_REPO.git
cd NAMA_REPO


(Opsional) Buat dan aktifkan virtual environment:

Windows:

python -m venv venv
venv\Scripts\activate


Linux / macOS:

python -m venv venv
source venv/bin/activate


Install dependensi (jika belum):

pip install matplotlib watchdog


Jalankan aplikasi:

python main.py


Pada run pertama, file data_cash.json akan dibuat otomatis di folder yang sama.

📝 Cara Menggunakan Singkat

Pilih Tipe transaksi (pemasukan / pengeluaran).

Isi Jumlah, Kategori, dan Keterangan.

Klik tombol Tambah untuk menyimpan transaksi.

Riwayat transaksi akan muncul pada tabel di bawah, dan ringkasan + grafik akan ter-update.

Gunakan combobox Tanggal di atas tabel untuk memfilter transaksi per hari tertentu.

Gunakan tombol Edit untuk memperbarui data transaksi dan Hapus untuk menghapus.

⚠️ Catatan

Aplikasi ini menyimpan semua data ke satu file lokal data_cash.json.
Jika ingin backup, cukup salin file tersebut.

Jika file JSON diubah secara manual, watcher akan mencoba me-refresh tampilan.
Pastikan format JSON tidak rusak agar aplikasi tetap bisa membaca data.
