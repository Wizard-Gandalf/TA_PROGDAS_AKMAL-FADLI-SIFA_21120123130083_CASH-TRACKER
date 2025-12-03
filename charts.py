# charts.py
from datetime import datetime, timedelta
from collections import defaultdict
from matplotlib.ticker import FuncFormatter


def _format_y_axis(ax):
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, p: format(int(x), ',').replace(',', '.'))
    )


def update_charts(
    data,
    selected_date,
    mode,
    figure_weekly,
    canvas_weekly,
    lbl_bulan,
    figure_pie,
    canvas_pie,
):
    """Update label bulan + grafik bar dan pie."""
    bulan_str = selected_date.strftime("%B %Y")
    lbl_bulan.config(text=bulan_str)

    update_weekly_chart(data, selected_date, mode, figure_weekly, canvas_weekly)
    update_pie_chart(data, selected_date, mode, figure_pie, canvas_pie)


def update_weekly_chart(data, ref_date, mode, figure_weekly, canvas_weekly):
    figure_weekly.clear()
    ax = figure_weekly.add_subplot(111)

    # margin supaya label & angka sumbu tidak kepotong
    figure_weekly.subplots_adjust(left=0.18, bottom=0.30, top=0.88, right=0.96)

    _format_y_axis(ax)

    # styling umum
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    # lebar satu batang
    width = 0.4

    if mode == "mingguan":
        # ===================== MODE MINGGUAN =====================
        # minggu referensi: mulai dari Minggu (Min)
        start = ref_date - timedelta(days=ref_date.weekday() + 1)
        days = [start + timedelta(days=i) for i in range(7)]

        pemasukan = []
        pengeluaran = []

        for d in days:
            list_p = [
                t["jumlah"]
                for t in data["transaksi"]
                if t["tipe"] == "pemasukan"
                and datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d")
                == d.strftime("%Y-%m-%d")
            ]
            list_q = [
                t["jumlah"]
                for t in data["transaksi"]
                if t["tipe"] == "pengeluaran"
                and datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m-%d")
                == d.strftime("%Y-%m-%d")
            ]

            pemasukan.append(sum(list_p))
            pengeluaran.append(sum(list_q))

        x = list(range(7))  # 0..6
        # posisi batang: pemasukan sedikit ke kiri, pengeluaran sedikit ke kanan
        x_pemasukan = [i - width / 2 for i in x]
        x_pengeluaran = [i + width / 2 for i in x]

        bars_p = ax.bar(x_pemasukan, pemasukan, width=width,
                        label="Pemasukan", color="#4CAF50")
        bars_q = ax.bar(x_pengeluaran, pengeluaran, width=width,
                        label="Pengeluaran", color="#F44336", alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels(["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"])

        for label in ax.get_xticklabels():
            label.set_rotation(90)
            label.set_ha("center")

        ax.set_title("Grafik Mingguan", fontsize=12, fontweight="bold", pad=10)

    else:
        # ===================== MODE BULANAN =====================
        this_month = ref_date.strftime("%Y-%m")
        trans_month = [
            t for t in data["transaksi"]
            if datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m") == this_month
        ]

        weekly_pemasukan = defaultdict(int)
        weekly_pengeluaran = defaultdict(int)

        for t in trans_month:
            dt = datetime.fromtimestamp(t["timestamp"])
            week_index = (dt.day - 1) // 7 + 1  # 1..5

            if t["tipe"] == "pemasukan":
                weekly_pemasukan[week_index] += t["jumlah"]
            elif t["tipe"] == "pengeluaran":
                weekly_pengeluaran[week_index] += t["jumlah"]

        x = [1, 2, 3, 4, 5]
        pemasukan = [weekly_pemasukan[i] for i in x]
        pengeluaran = [weekly_pengeluaran[i] for i in x]

        x_pemasukan = [i - width / 2 for i in x]
        x_pengeluaran = [i + width / 2 for i in x]

        bars_p = ax.bar(x_pemasukan, pemasukan, width=width,
                        label="Pemasukan", color="#4CAF50")
        bars_q = ax.bar(x_pengeluaran, pengeluaran, width=width,
                        label="Pengeluaran", color="#F44336", alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels([f"Minggu {i}" for i in x])

        for label in ax.get_xticklabels():
            label.set_rotation(90)
            label.set_ha("center")

        ax.set_title("Grafik Bulanan", fontsize=12, fontweight="bold", pad=10)

    ax.legend(fontsize=9, loc="upper right")
    canvas_weekly.draw()


def update_pie_chart(data, ref_date, mode, figure_pie, canvas_pie):
    figure_pie.clear()
    ax = figure_pie.add_subplot(111)

    if mode == "mingguan":
        start = ref_date - timedelta(days=ref_date.weekday() + 1)
        end = start + timedelta(days=6)

        pengeluaran = [
            t for t in data["transaksi"]
            if t["tipe"] == "pengeluaran"
            and start.date()
            <= datetime.fromtimestamp(t["timestamp"]).date()
            <= end.date()
        ]
    else:
        month_str = ref_date.strftime("%Y-%m")
        pengeluaran = [
            t for t in data["transaksi"]
            if t["tipe"] == "pengeluaran"
            and datetime.fromtimestamp(t["timestamp"]).strftime("%Y-%m")
            == month_str
        ]

    if not pengeluaran:
        ax.text(0.5, 0.5, "Tidak ada data", ha="center", va="center", fontsize=10)
    else:
        kategori_sum = defaultdict(int)
        for t in pengeluaran:
            kategori_sum[t["kategori"]] += t["jumlah"]

        labels = list(kategori_sum.keys())
        sizes = list(kategori_sum.values())

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            textprops={"fontsize": 9},
            startangle=90,
        )

        # supaya benar-benar bentuk lingkaran
        ax.axis("equal")

    ax.set_title("Kategori Pengeluaran", fontsize=12, fontweight="bold", pad=10)
    canvas_pie.draw()
