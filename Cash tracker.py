import tkinter as tk
from tkinter import ttk, messagebox
import json, os, threading, time
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from matplotlib.figure import Figure
from collections import defaultdict


FILE_JSON = "data_cash.json"
refresh_lock = False


# -------------------------------------------------------------
#   JSON MANAGEMENT
# -------------------------------------------------------------
def init_json():
    if not os.path.exists(FILE_JSON):
        data = {
            "transaksi": [],
            "kategori": []
        }
        with open(FILE_JSON, "w") as f:
            json.dump(data, f, indent=4)


def load_json():
    with open(FILE_JSON, "r") as f:
        return json.load(f)


def save_json(data):
    global refresh_lock
    refresh_lock = True
        
    with open(FILE_JSON, "w") as f:
        json.dump(data, f, indent=4)

    refresh_lock = False


# -------------------------------------------------------------
#   GUI UPDATE FUNCTIONS
# -------------------------------------------------------------
def refresh_all():
    data = load_json()
    refresh_table(data)
    refresh_summary(data)
    refresh_category_list(data)
    update_charts(data)


def refresh_table(data):
    tabel.delete(*tabel.get_children())
    tanggal_filter = cmb_filter_tanggal.get()

    transaksi = data["transaksi"]

    if tanggal_filter != "Semua":
        transaksi = [t for t in transaksi if
                     datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d") == tanggal_filter]

    for i, t in enumerate(transaksi, start=1):
        waktu = datetime.fromtimestamp(t["timestamp"]).strftime("%H:%M:%S")
        tabel.insert("", "end", values=(
            i,
            t["tipe"],
            t["jumlah"],
            t["kategori"],
            t["keterangan"],
            waktu
        ))


def refresh_summary(data):
    pemasukan = sum(t["jumlah"] for t in data["transaksi"] if t["tipe"] == "pemasukan")
    pengeluaran = sum(t["jumlah"] for t in data["transaksi"] if t["tipe"] == "pengeluaran")

    lbl_saldo.config(text=f"Saldo : Rp {pemasukan - pengeluaran:,.0f}")

    now = datetime.now()
    this_month = [t for t in data["transaksi"]
                  if datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m") == now.strftime("%Y-%m")]

    pengeluaran_bulan = sum(t["jumlah"] for t in this_month if t["tipe"] == "pengeluaran")
    lbl_pengeluaran_bulan.config(text=f"Pengeluaran bulan ini : Rp {pengeluaran_bulan:,.0f}")

    today = datetime.now().strftime("%Y-%m-%d")
    today_data = [t for t in data["transaksi"]
                  if datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d") == today
                  and t["tipe"] == "pengeluaran"]

    total_today = sum(t["jumlah"] for t in today_data)
    lbl_pengeluaran_hari.config(text=f"Pengeluaran hari ini : Rp {total_today:,.0f}")


def refresh_category_list(data):
    kategori = list(set(t["kategori"] for t in data["transaksi"]))
    kategori.sort()

    cmb_kategori["values"] = kategori


# -------------------------------------------------------------
#   CHARTS
# -------------------------------------------------------------
def update_charts(data):
    update_weekly_chart(data)
    update_pie_chart(data)


def update_weekly_chart(data):
    figure_weekly.clear()
    ax = figure_weekly.add_subplot(111)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',').replace(',', '.')))

    mode = view_mode.get()
    now = datetime.now()

    if mode == "mingguan":
        # find Sunday (start)
        start = now - timedelta(days=now.weekday() + 1)
        days = [start + timedelta(days=i) for i in range(7)]

        pemasukan = []
        pengeluaran = []

        for d in days:
            list_p = [t["jumlah"] for t in data["transaksi"]
                      if t["tipe"] == "pemasukan" and
                      datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d") == d.strftime("%Y-%m-%d")]
            list_q = [t["jumlah"] for t in data["transaksi"]
                      if t["tipe"] == "pengeluaran" and
                      datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d") == d.strftime("%Y-%m-%d")]

            pemasukan.append(sum(list_p))
            pengeluaran.append(sum(list_q))

        x = range(7)
        ax.bar(x, pemasukan, color="#4CAF50", label="Pemasukan")
        ax.bar(x, pengeluaran, bottom=0, color="#F44336", alpha=0.7, label="Pengeluaran")

        ax.set_xticks(x)
        ax.set_xticklabels(["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"])
        ax.set_title("Grafik Mingguan")

    else:  # bulanan
        this_month = now.strftime("%Y-%m")
        trans_month = [t for t in data["transaksi"]
                       if datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m") == this_month]

        # week of month
        weekly_pemasukan = defaultdict(int)
        weekly_pengeluaran = defaultdict(int)

        for t in trans_month:
            dt = datetime.fromtimestamp(t["timestamp"])
            week_index = (dt.day - 1) // 7 + 1

            if t["tipe"] == "pemasukan":
                weekly_pemasukan[week_index] += t["jumlah"]
            else:
                weekly_pengeluaran[week_index] += t["jumlah"]

                # selalu tampilkan minggu 1–5
                x = [1, 2, 3, 4, 5]

                pemasukan = [weekly_pemasukan[i] if i in weekly_pemasukan else 0 for i in x]
                pengeluaran = [weekly_pengeluaran[i] if i in weekly_pengeluaran else 0 for i in x]

                ax.set_xticks(x)            
                ax.set_xticklabels([f"Minggu {i}" for i in x])

        ax.set_title("Grafik Bulanan")

    ax.legend()
    canvas_weekly.draw()


def update_pie_chart(data):
    figure_pie.clear()
    ax = figure_pie.add_subplot(111)

    mode = view_mode.get()
    now = datetime.now()

    if mode == "mingguan":
        start = now - timedelta(days=now.weekday() + 1)
        end = start + timedelta(days=6)

        pengeluaran = [t for t in data["transaksi"]
                       if t["tipe"] == "pengeluaran" and
                       start.date() <= datetime.fromtimestamp(t["timestamp"]).date() <= end.date()]
    else:
        pengeluaran = [t for t in data["transaksi"]
                       if t["tipe"] == "pengeluaran" and
                       datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m") == now.strftime("%Y-%m")]

    if not pengeluaran:
        ax.text(0.5, 0.5, "Tidak ada data", ha="center", va="center")
    else:
        kategori_sum = defaultdict(int)
        for t in pengeluaran:
            kategori_sum[t["kategori"]] += t["jumlah"]

        labels = kategori_sum.keys()
        sizes = kategori_sum.values()

        ax.pie(sizes, labels=labels, autopct="%1.1f%%")

    ax.set_title("Kategori Pengeluaran")
    canvas_pie.draw()


# -------------------------------------------------------------
#   ADD / EDIT / DELETE
# -------------------------------------------------------------
def tambah_data():
    data = load_json()

    tipe = cmb_tipe.get()
    jumlah = entry_jumlah.get()
    kategori = cmb_kategori.get()
    ket = entry_keterangan.get()

    if tipe not in ["pemasukan", "pengeluaran"]:
        messagebox.showwarning("Error", "Pilih tipe yang benar")
        return

    try:
        jumlah = float(jumlah)
    except:
        messagebox.showwarning("Error", "Jumlah harus angka")
        return

    ts = time.time()

    new_trans = {
        "tipe": tipe,
        "jumlah": jumlah,
        "kategori": kategori,
        "keterangan": ket,
        "waktu": datetime.fromtimestamp(ts).strftime("%H:%M:%S"),
        "timestamp": ts
    }

    data["transaksi"].append(new_trans)

    if kategori not in data["kategori"]:
        data["kategori"].append(kategori)

    save_json(data)
    refresh_all()

    entry_jumlah.delete(0, tk.END)
    entry_keterangan.delete(0, tk.END)


def edit_data():
    selected = tabel.selection()
    if not selected:
        messagebox.showwarning("Error", "Pilih data")
        return

    idx = tabel.index(selected[0])
    data = load_json()

    # Create popup
    win = tk.Toplevel(root)
    win.title("Edit Data")
    win.geometry("300x300")

    tk.Label(win, text="Tipe").pack()
    tipe_e = ttk.Combobox(win, values=["pemasukan", "pengeluaran"])
    tipe_e.pack()

    tk.Label(win, text="Jumlah").pack()
    jumlah_e = tk.Entry(win)
    jumlah_e.pack()

    tk.Label(win, text="Kategori").pack()
    kategori_e = tk.Entry(win)
    kategori_e.pack()

    tk.Label(win, text="Keterangan").pack()
    ket_e = tk.Entry(win)
    ket_e.pack()

    old = data["transaksi"][idx]

    tipe_e.set(old["tipe"])
    jumlah_e.insert(0, old["jumlah"])
    kategori_e.insert(0, old["kategori"])
    ket_e.insert(0, old["keterangan"])

    def save_edit():
        try:
            jumlah = float(jumlah_e.get())
        except:
            messagebox.showerror("Jumlah salah")
            return

        data["transaksi"][idx]["tipe"] = tipe_e.get()
        data["transaksi"][idx]["jumlah"] = jumlah
        data["transaksi"][idx]["kategori"] = kategori_e.get()
        data["transaksi"][idx]["keterangan"] = ket_e.get()

        save_json(data)
        refresh_all()
        win.destroy()

    tk.Button(win, text="Simpan", command=save_edit).pack()


def hapus_data():
    selected = tabel.selection()
    if not selected:
        messagebox.showwarning("Error", "Pilih data")
        return

    idx = tabel.index(selected[0])
    data = load_json()

    del data["transaksi"][idx]

    save_json(data)
    refresh_all()


# -------------------------------------------------------------
#   WATCHDOG (REALTIME JSON)
# -------------------------------------------------------------
class JSONEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global refresh_lock
        if refresh_lock:
            return
        if FILE_JSON in event.src_path:
            refresh_all()


def start_watchdog():
    handler = JSONEventHandler()
    observer = Observer()
    observer.schedule(handler, ".", recursive=False)
    observer.start()


# -------------------------------------------------------------
#   GUI TKINTER
# -------------------------------------------------------------
root = tk.Tk()
root.title("Cash Tracker")
root.geometry("1300x900")
root.configure(bg="#f5f5f5")


# -------------------------------------------------------------
#   LEFT PANEL
# -------------------------------------------------------------
left = tk.Frame(root, bg="#f5f5f5")
left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

title = tk.Label(left, text="Cash Tracker",
                 font=("Segoe UI", 22, "bold"), bg="#f5f5f5", fg="#2E7D32")
title.pack(anchor="w")

subtitle = tk.Label(left, text="Sistem Manajemen Keuangan",
                    font=("Segoe UI", 11), bg="#f5f5f5", fg="#555")
subtitle.pack(anchor="w")


# SUMMARY BOXES
summary_frame = tk.Frame(left, bg="#f5f5f5")
summary_frame.pack(pady=10, anchor="w")

lbl_saldo = tk.Label(summary_frame, text="Saldo : Rp 0",
                     font=("Segoe UI", 13, "bold"), bg="#A5D6A7", fg="#1B5E20", width=30, pady=10)
lbl_saldo.grid(row=0, column=0, padx=5)

lbl_pengeluaran_bulan = tk.Label(summary_frame, text="Pengeluaran bulan ini : Rp 0",
                                 font=("Segoe UI", 13, "bold"), bg="#C8E6C9", fg="#1B5E20", width=30, pady=10)
lbl_pengeluaran_bulan.grid(row=0, column=1, padx=5)


# DAILY SPEND HEADER
daily_header = tk.Label(left, text="Daily Spend",
                        font=("Segoe UI", 14, "bold"), bg="#f5f5f5", fg="#2E7D32")
daily_header.pack(anchor="w", pady=(20, 0))
# Tanggal hari ini
today_str = datetime.now().strftime("%A, %d %B %Y")
lbl_tanggal_hari_ini = tk.Label(left, text=today_str, font=("Segoe UI", 11),
                                bg="#f5f5f5", fg="#444")
lbl_tanggal_hari_ini.pack(anchor="w")

lbl_pengeluaran_hari = tk.Label(left, text="Pengeluaran hari ini : Rp 0",
                                font=("Segoe UI", 12), bg="#f5f5f5")
lbl_pengeluaran_hari.pack(anchor="w")


# tambah data form
form = tk.Frame(left, bg="#e8f5e9", padx=10, pady=10, bd=1, relief="solid")
form.pack(pady=10, fill="x")

tk.Label(form, text="Tipe").pack(anchor="w")
cmb_tipe = ttk.Combobox(form, values=["pemasukan", "pengeluaran"], state="readonly")
cmb_tipe.pack(fill="x")

tk.Label(form, text="Jumlah").pack(anchor="w")
entry_jumlah = tk.Entry(form)
entry_jumlah.pack(fill="x")

tk.Label(form, text="Kategori").pack(anchor="w")
cmb_kategori = ttk.Combobox(form)
cmb_kategori.pack(fill="x")

tk.Label(form, text="Keterangan").pack(anchor="w")
entry_keterangan = tk.Entry(form)
entry_keterangan.pack(fill="x")

btn_add = tk.Button(form, text="Tambah", bg="#66BB6A", fg="white", command=tambah_data)
btn_add.pack(side="left", padx=5, pady=10)

btn_cancel = tk.Button(form, text="Batal", bg="white", command=lambda: [entry_jumlah.delete(0, tk.END),
                                                                        entry_keterangan.delete(0, tk.END)])
btn_cancel.pack(side="right", padx=5, pady=10)


# -------------------------------------------------------------
# TABEL RIWAYAT
# -------------------------------------------------------------
history_frame = tk.Frame(left, bg="#f5f5f5")
history_frame.pack(fill="both", expand=True)

tk.Label(history_frame, text="Riwayat Transaksi", bg="#f5f5f5",
         font=("Segoe UI", 14, "bold")).pack(anchor="w")

# filter tanggal
filter_frame = tk.Frame(history_frame, bg="#f5f5f5")
filter_frame.pack(anchor="w")

tk.Label(filter_frame, text="Tanggal: ", bg="#f5f5f5").pack(side="left")

cmb_filter_tanggal = ttk.Combobox(filter_frame, values=["Semua"])
cmb_filter_tanggal.set("Semua")
cmb_filter_tanggal.pack(side="left")

def update_filter_options():
    data = load_json()
    dates = sorted(list(set(datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d")
                            for t in data["transaksi"])))
    cmb_filter_tanggal["values"] = ["Semua"] + dates

cmb_filter_tanggal.bind("<<ComboboxSelected>>", lambda e: refresh_all())

# table
columns = ("No", "Tipe", "Jumlah", "Kategori", "Keterangan", "Waktu")
tabel = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

for col in columns:
    tabel.heading(col, text=col)
    tabel.column(col, width=120)

tabel.pack(fill="both", expand=True)

# edit + delete
btn_edit = tk.Button(history_frame, text="Edit", bg="#81C784", command=edit_data)
btn_edit.pack(side="left", padx=10, pady=5)

btn_delete = tk.Button(history_frame, text="Hapus", bg="#FFCDD2", command=hapus_data)
btn_delete.pack(side="left", padx=10, pady=5)


# -------------------------------------------------------------
#   RIGHT PANEL
# -------------------------------------------------------------
right = tk.Frame(root, bg="#f5f5f5")
right.pack(side="right", fill="both", padx=10, pady=10)

# switch grafik
view_mode = tk.StringVar(value="mingguan")

# Frame khusus untuk menjejerkan radio button
mode_frame = tk.Frame(right, bg="#f5f5f5")
mode_frame.pack(anchor="n", pady=5)

btn_week = tk.Radiobutton(mode_frame, text="Mingguan", variable=view_mode, value="mingguan",
                          bg="#f5f5f5", command=lambda: refresh_all())
btn_week.pack(side="left", padx=10)

btn_month = tk.Radiobutton(mode_frame, text="Bulanan", variable=view_mode, value="bulanan",
                           bg="#f5f5f5", command=lambda: refresh_all())
btn_month.pack(side="left", padx=10)


# weekly chart
figure_weekly = Figure(figsize=(4, 3), dpi=100)
canvas_weekly = FigureCanvasTkAgg(figure_weekly, right)
canvas_weekly.get_tk_widget().pack(fill="both", expand=True)

# pie chart
figure_pie = Figure(figsize=(4, 3), dpi=100)
canvas_pie = FigureCanvasTkAgg(figure_pie, right)
canvas_pie.get_tk_widget().pack(fill="both", expand=True)


# -------------------------------------------------------------
# START
# -------------------------------------------------------------
init_json()
refresh_all()

threading.Thread(target=start_watchdog, daemon=True).start()

update_filter_options()

root.mainloop()
