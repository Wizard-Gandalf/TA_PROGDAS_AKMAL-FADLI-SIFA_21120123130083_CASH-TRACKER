# data_store.py
import json
import os

FILE_JSON = "data_cash.json"
refresh_lock = False


def init_json():
    """Buat file JSON awal jika belum ada."""
    if not os.path.exists(FILE_JSON):
        data = {
            "transaksi": [],
            "kategori": []
        }
        with open(FILE_JSON, "w") as f:
            json.dump(data, f, indent=4)


def load_json():
    """Membaca seluruh data dari JSON."""
    with open(FILE_JSON, "r") as f:
        return json.load(f)


def save_json(data):
    """Menyimpan data ke JSON dengan lock agar watchdog tidak double-refresh."""
    global refresh_lock
    refresh_lock = True

    with open(FILE_JSON, "w") as f:
        json.dump(data, f, indent=4)

    refresh_lock = False
