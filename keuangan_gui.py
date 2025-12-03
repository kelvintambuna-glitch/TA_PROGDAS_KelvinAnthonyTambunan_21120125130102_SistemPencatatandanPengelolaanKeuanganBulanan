import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

# ---------- NAMA FILE PENYIMPANAN ----------
NAMA_FILE = "data_keuangan.json"

# ---------- DATA ----------
transaksi = []  # list of dict: {id, tanggal, tipe, kategori, jumlah, catatan}

def format_rupiah(n):
    return f"Rp {n:,.0f}".replace(",", ".")

# ---------- FUNGSI SIMPAN & LOAD ----------
def simpan_ke_file():
    try:
        with open(NAMA_FILE, "w", encoding="utf-8") as f:
            json.dump(transaksi, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan data ke file.\n{e}")

def muat_dari_file():
    global transaksi
    if not os.path.exists(NAMA_FILE):
        transaksi = []
        return

    try:
        with open(NAMA_FILE, "r", encoding="utf-8") as f:
            transaksi = json.load(f)
    except Exception:
        transaksi = []

# ---------- LOGIC ----------
def tambah_transaksi():
    tipe = combo_tipe.get()
    tanggal = entry_tanggal.get().strip()
    kategori = entry_kategori.get().strip()
    jumlah_str = entry_jumlah.get().strip()
    catatan = entry_catatan.get().strip()

    if not tanggal or not kategori or not jumlah_str:
        messagebox.showwarning("Input kurang", "Tanggal, kategori, dan jumlah wajib diisi.")
        return

    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Tanggal salah", "Format tanggal harus YYYY-MM-DD (contoh: 2025-11-22).")
        return

    try:
        jumlah = float(jumlah_str)
        if jumlah <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Jumlah salah", "Jumlah harus angka lebih dari 0.")
        return

    data = {
        "id": datetime.now().timestamp(),
        "tanggal": tanggal,
        "tipe": tipe,
        "kategori": kategori,
        "jumlah": jumlah,
        "catatan": catatan
    }
    transaksi.append(data)

    simpan_ke_file()       # <-- simpan setiap ada perubahan
    refresh_tabel()
    refresh_ringkasan()

    entry_jumlah.delete(0, tk.END)
    entry_catatan.delete(0, tk.END)
    entry_jumlah.focus()

def hapus_transaksi_terpilih():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Hapus", "Pilih dulu transaksi yang mau dihapus.")
        return

    konfirm = messagebox.askyesno("Konfirmasi", "Yakin hapus transaksi terpilih?")
    if not konfirm:
        return

    item_id = selected[0]
    trans_id = tree.item(item_id, "values")[0]

    global transaksi
    transaksi = [t for t in transaksi if str(t["id"]) != str(trans_id)]

    simpan_ke_file()       # <-- simpan setelah hapus
    refresh_tabel()
    refresh_ringkasan()

def hapus_semua_transaksi():
    global transaksi
    if not transaksi:
        messagebox.showinfo("Hapus Semua", "Tidak ada transaksi untuk dihapus.")
        return

    konfirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus semua transaksi?")
    if not konfirm:
        return

    transaksi = []  # kosongkan semua transaksi

    simpan_ke_file()
    refresh_tabel()
    refresh_ringkasan()

    messagebox.showinfo("Hapus Semua", "Semua transaksi berhasil dihapus.")



def refresh_tabel():
    for row in tree.get_children():
        tree.delete(row)

    for t in transaksi:
        tree.insert(
            "",
            tk.END,
            values=(
                t["id"],
                t["tanggal"],
                "Pemasukan" if t["tipe"] == "masuk" else "Pengeluaran",
                t["kategori"],
                format_rupiah(t["jumlah"]),
                t["catatan"]
            )
        )

def refresh_ringkasan():
    total_masuk = sum(t["jumlah"] for t in transaksi if t["tipe"] == "masuk")
    total_keluar = sum(t["jumlah"] for t in transaksi if t["tipe"] == "keluar")
    saldo = total_masuk - total_keluar

    label_total_masuk_val.config(text=format_rupiah(total_masuk))
    label_total_keluar_val.config(text=format_rupiah(total_keluar))
    label_saldo_val.config(text=format_rupiah(saldo))

# ---------- GUI ----------
root = tk.Tk()
root.title("Sistem Pencatatan dan Pengelolaan Keuangan Bulanan")

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
ACCENT  = "#38bdf8"
TEXT    = "#e5e7eb"

root.configure(bg=BG_MAIN)
root.geometry("950x520")

style = ttk.Style()
style.theme_use("clam")

style.configure("Card.TFrame", background=BG_CARD)
style.configure("Main.TFrame", background=BG_MAIN)
style.configure("TLabel", background=BG_CARD, foreground=TEXT, font=("Segoe UI", 9))
style.configure("Title.TLabel", background=BG_MAIN, foreground=TEXT, font=("Segoe UI", 13, "bold"))
style.configure("Small.TLabel", background=BG_CARD, foreground=TEXT, font=("Segoe UI", 9, "bold"))
style.configure("Accent.TButton", font=("Segoe UI", 9, "bold"))
style.map(
    "Accent.TButton",
    background=[("!disabled", ACCENT), ("pressed", "#0ea5e9"), ("active", "#0ea5e9")]
)

frame_utama = ttk.Frame(root, style="Main.TFrame", padding=14)
frame_utama.pack(fill="both", expand=True)

judul = ttk.Label(
    frame_utama,
    text="Sistem Pencatatan dan Pengelolaan Keuangan Bulanan",
    style="Title.TLabel"
)
judul.pack(anchor="w", pady=(0, 10))

frame_isi = ttk.Frame(frame_utama, style="Main.TFrame")
frame_isi.pack(fill="both", expand=True)

# kiri
frame_kiri = ttk.Frame(frame_isi, style="Card.TFrame", padding=12)
frame_kiri.pack(side="left", fill="y", padx=(0, 10))

label_judul = ttk.Label(frame_kiri, text="Tambah Transaksi", style="Small.TLabel")
label_judul.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

ttk.Label(frame_kiri, text="Tipe").grid(row=1, column=0, sticky="w", pady=2)
combo_tipe = ttk.Combobox(frame_kiri, values=["masuk", "keluar"], state="readonly")
combo_tipe.current(1)
combo_tipe.grid(row=1, column=1, sticky="ew", pady=2)

ttk.Label(frame_kiri, text="Tanggal (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=2)
entry_tanggal = ttk.Entry(frame_kiri)
entry_tanggal.grid(row=2, column=1, sticky="ew", pady=2)
entry_tanggal.insert(0, datetime.now().strftime("%Y-%m-%d"))

ttk.Label(frame_kiri, text="Kategori").grid(row=3, column=0, sticky="w", pady=2)
entry_kategori = ttk.Entry(frame_kiri)
entry_kategori.grid(row=3, column=1, sticky="ew", pady=2)

ttk.Label(frame_kiri, text="Jumlah (Rp)").grid(row=4, column=0, sticky="w", pady=2)
entry_jumlah = ttk.Entry(frame_kiri)
entry_jumlah.grid(row=4, column=1, sticky="ew", pady=2)

ttk.Label(frame_kiri, text="Catatan").grid(row=5, column=0, sticky="w", pady=2)
entry_catatan = ttk.Entry(frame_kiri)
entry_catatan.grid(row=5, column=1, sticky="ew", pady=2)

btn_tambah = ttk.Button(frame_kiri, text="Tambah", style="Accent.TButton", command=tambah_transaksi)
btn_tambah.grid(row=6, column=0, columnspan=2, pady=(10, 4), sticky="ew")

btn_hapus = ttk.Button(frame_kiri, text="Hapus Transaksi Terpilih", command=hapus_transaksi_terpilih)
btn_hapus.grid(row=7, column=0, columnspan=2, sticky="ew")

btn_hapus_semua = ttk.Button(frame_kiri, text="Hapus Semua Transaksi", command=hapus_semua_transaksi)
btn_hapus_semua.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 0))

frame_kiri.columnconfigure(1, weight=1)

# kanan
frame_kanan_card = ttk.Frame(frame_isi, style="Card.TFrame", padding=10)
frame_kanan_card.pack(side="right", fill="both", expand=True)

kolom = ("id", "tanggal", "tipe", "kategori", "jumlah", "catatan")
tree = ttk.Treeview(frame_kanan_card, columns=kolom, show="headings", height=10)

tree.heading("tanggal", text="Tanggal")
tree.heading("tipe", text="Tipe")
tree.heading("kategori", text="Kategori")
tree.heading("jumlah", text="Jumlah")
tree.heading("catatan", text="Catatan")
tree.heading("id", text="ID")

tree.column("id", width=0, stretch=False)
tree.column("tanggal", width=90)
tree.column("tipe", width=90)
tree.column("kategori", width=120)
tree.column("jumlah", width=110)
tree.column("catatan", width=220)

scrollbar = ttk.Scrollbar(frame_kanan_card, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
scrollbar.grid(row=0, column=1, sticky="ns", pady=(0, 8))

frame_kanan_card.rowconfigure(0, weight=1)
frame_kanan_card.columnconfigure(0, weight=1)

frame_ringkasan = ttk.Frame(frame_kanan_card, style="Card.TFrame")
frame_ringkasan.grid(row=1, column=0, columnspan=2, sticky="ew")

ttk.Label(frame_ringkasan, text="Total Pemasukan:").grid(row=0, column=0, sticky="w")
label_total_masuk_val = ttk.Label(frame_ringkasan, text="Rp 0")
label_total_masuk_val.grid(row=0, column=1, sticky="w", padx=(5, 20))

ttk.Label(frame_ringkasan, text="Total Pengeluaran:").grid(row=1, column=0, sticky="w")
label_total_keluar_val = ttk.Label(frame_ringkasan, text="Rp 0")
label_total_keluar_val.grid(row=1, column=1, sticky="w", padx=(5, 20))

ttk.Label(frame_ringkasan, text="Saldo:").grid(row=2, column=0, sticky="w")
label_saldo_val = ttk.Label(frame_ringkasan, text="Rp 0")
label_saldo_val.grid(row=2, column=1, sticky="w", padx=(5, 20))

frame_ringkasan.columnconfigure(1, weight=1)

# --- load data saat aplikasi dibuka ---
muat_dari_file()
refresh_tabel()
refresh_ringkasan()

root.mainloop()
