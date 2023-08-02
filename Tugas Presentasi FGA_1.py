#!/usr/bin/env python
# coding: utf-8

# In[40]:


import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Siswa:
    def __init__(self, nama, nim, jenis_kelamin):
        self.nama = nama
        self.nim = nim
        self.jenis_kelamin = jenis_kelamin
        self.nilai_tugas = []
        self.nilai_uts = 0
        self.nilai_uas = 0

    def tambah_nilai_tugas(self, nilai_tugas):
        self.nilai_tugas.append(nilai_tugas)

    def set_nilai_uts(self, nilai_uts):
        self.nilai_uts = nilai_uts

    def set_nilai_uas(self, nilai_uas):
        self.nilai_uas = nilai_uas

    def nilai_rata_rata_tugas(self):
        if len(self.nilai_tugas) > 0:
            return sum(self.nilai_tugas) / len(self.nilai_tugas)
        else:
            return 0

    def nilai_akhir(self):
        return 0.3 * self.nilai_rata_rata_tugas() + 0.3 * self.nilai_uts + 0.4 * self.nilai_uas

    def lulus(self):
        return self.nilai_akhir() > 60


def create_table():
    connection = sqlite3.connect("rapot.db")
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS siswa (
                        nim TEXT PRIMARY KEY,
                        nama TEXT,
                        jenis_kelamin TEXT)""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS nilai (
                        nim TEXT PRIMARY KEY,
                        tugas1 REAL,
                        tugas2 REAL,
                        tugas3 REAL,
                        uts REAL,
                        uas REAL)""")

    connection.commit()
    connection.close()


def tambah_siswa():
    nama = entry_nama.get()
    nim = entry_nim.get()
    jenis_kelamin = entry_jenis_kelamin.get()

    if not nama or not nim or not jenis_kelamin:
        messagebox.showerror("Error", "Nama, NIM, dan Jenis Kelamin harus diisi.")
        return

    connection = sqlite3.connect("rapot.db")
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO siswa (nim, nama, jenis_kelamin) VALUES (?, ?, ?)",
                       (nim, nama, jenis_kelamin))
        connection.commit()
        connection.close()
        messagebox.showinfo("Informasi", "Data siswa berhasil ditambahkan!")
    except sqlite3.IntegrityError:
        connection.close()
        messagebox.showerror("Error", "NIM siswa sudah ada dalam database. Gunakan NIM yang berbeda.")


def tambah_nilai():
    nim = entry_nim_nilai.get()
    nilai_tugas1 = float(entry_tugas1.get())
    nilai_tugas2 = float(entry_tugas2.get())
    nilai_tugas3 = float(entry_tugas3.get())
    nilai_uts = float(entry_uts.get())
    nilai_uas = float(entry_uas.get())

    if not nim:
        messagebox.showerror("Error", "NIM harus diisi.")
        return

    connection = sqlite3.connect("rapot.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM siswa WHERE nim=?", (nim,))
    siswa_data = cursor.fetchone()

    if not siswa_data:
        connection.close()
        messagebox.showerror("Error", "NIM siswa tidak ditemukan. Silakan tambahkan data siswa terlebih dahulu.")
        return

    try:
        cursor.execute("INSERT INTO nilai (nim, tugas1, tugas2, tugas3, uts, uas) VALUES (?, ?, ?, ?, ?, ?)",
                       (nim, nilai_tugas1, nilai_tugas2, nilai_tugas3, nilai_uts, nilai_uas))
        connection.commit()
        connection.close()
        messagebox.showinfo("Informasi", "Nilai siswa berhasil ditambahkan!")
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE nilai SET tugas1=?, tugas2=?, tugas3=?, uts=?, uas=? WHERE nim=?",
                       (nilai_tugas1, nilai_tugas2, nilai_tugas3, nilai_uts, nilai_uas, nim))
        connection.commit()
        connection.close()
        messagebox.showinfo("Informasi", "Data nilai siswa berhasil diperbarui!")


def lihat_inputan():
    connection = sqlite3.connect("rapot.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM siswa")
    data_siswa = cursor.fetchall()

    cursor.execute("SELECT * FROM nilai")
    data_nilai = cursor.fetchall()

    connection.close()

    df_siswa = pd.DataFrame(data_siswa, columns=['NIM', 'Nama', 'Jenis Kelamin'])
    df_nilai = pd.DataFrame(data_nilai, columns=['NIM', 'Tugas 1', 'Tugas 2', 'Tugas 3', 'UTS', 'UAS'])

    # Menggabungkan data siswa dan data nilai
    df_gabungan = pd.merge(df_siswa, df_nilai, on='NIM', how='outer')

    # Menghitung nilai akhir sebagai rata-rata dari nilai tugas, UTS, dan UAS
    df_gabungan['Nilai Akhir'] = df_gabungan[['Tugas 1', 'Tugas 2', 'Tugas 3', 'UTS', 'UAS']].mean(axis=1)

    # Menandai siswa yang tidak lulus jika nilai akhirnya di bawah 60
    df_gabungan['Lulus/Tidak'] = df_gabungan['Nilai Akhir'].apply(lambda x: 'Lulus' if x >= 60 else 'Tidak')

    if df_gabungan.empty:
        messagebox.showerror("Error", "Data siswa kosong. Silakan masukkan data siswa terlebih dahulu.")
    else:
        # Tampilkan data dalam bentuk tabel
        plt.close()
        fig, ax = plt.subplots(figsize=(12, 7))  # Sesuaikan ukuran tabel di sini
        ax.axis('off')
        colors = []
        for status in df_gabungan['Lulus/Tidak']:
            if status == 'Lulus':
                colors.append(['#dce6f1'] * len(df_gabungan.columns))  # Warna latar belakang baris untuk siswa yang lulus
            else:
                colors.append(['#ff6961'] * len(df_gabungan.columns))  # Warna latar belakang baris untuk siswa yang tidak lulus

        table = ax.table(cellText=df_gabungan.values, colLabels=df_gabungan.columns, cellLoc='center', loc='center', cellColours=colors)
        table.auto_set_font_size(False)
        table.set_fontsize(12)  # Sesuaikan ukuran tulisan di sini
        table.auto_set_column_width(col=list(range(len(df_gabungan.columns))))  # Agar lebar kolom otomatis disesuaikan

        # Tampilkan tabel pada aplikasi desktop menggunakan tk.Toplevel()
        table_frame = tk.Toplevel(app)
        table_frame.title("Data Siswa dan Nilai")
        table_canvas = FigureCanvasTkAgg(fig, master=table_frame)
        table_canvas.draw()
        table_canvas.get_tk_widget().pack()
        plt.show()


def edit_data():
    nim_to_edit = simpledialog.askstring("Edit Data", "Masukkan NIM siswa yang akan diubah:")
    if nim_to_edit is None:
        return

    connection = sqlite3.connect("rapot.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM siswa WHERE nim=?", (nim_to_edit,))
    data_siswa = cursor.fetchone()

    if not data_siswa:
        connection.close()
        messagebox.showerror("Error", "NIM siswa tidak ditemukan.")
        return

    dialog_result = simpledialog.askinteger("Edit Data", "Pilih opsi yang akan diubah:\n1. Nama\n2. Jenis Kelamin")
    if dialog_result not in [1, 2]:
        connection.close()
        return

    if dialog_result == 1:
        new_nama = simpledialog.askstring("Edit Data", "Masukkan nama baru:")
        if new_nama is None:
            connection.close()
            return

        cursor.execute("UPDATE siswa SET nama=? WHERE nim=?", (new_nama, nim_to_edit))
        connection.commit()
        connection.close()
        messagebox.showinfo("Informasi", "Data siswa berhasil diubah.")
    elif dialog_result == 2:
        new_jenis_kelamin = simpledialog.askstring("Edit Data", "Masukkan jenis kelamin baru (L/P):")
        if new_jenis_kelamin is None:
            connection.close()
            return

        cursor.execute("UPDATE siswa SET jenis_kelamin=? WHERE nim=?", (new_jenis_kelamin, nim_to_edit))
        connection.commit()
        connection.close()
        messagebox.showinfo("Informasi", "Data siswa berhasil diubah.")

# Membuat tabel jika belum ada
create_table()

# Setup GUI
app = tk.Tk()
app.title("Sistem Informasi Rapot")
app.geometry("800x600")  # Sesuaikan ukuran jendela aplikasi di sini

frame_input_siswa = tk.Frame(app)
frame_input_siswa.pack(pady=10)

label_nama = tk.Label(frame_input_siswa, text="Nama:")
label_nama.grid(row=0, column=0, padx=5)
entry_nama = tk.Entry(frame_input_siswa)
entry_nama.grid(row=0, column=1, padx=5)

label_nim = tk.Label(frame_input_siswa, text="NIM:")
label_nim.grid(row=1, column=0, padx=5)
entry_nim = tk.Entry(frame_input_siswa)
entry_nim.grid(row=1, column=1, padx=5)

label_jenis_kelamin = tk.Label(frame_input_siswa, text="Jenis Kelamin (L/P):")
label_jenis_kelamin.grid(row=2, column=0, padx=0)
entry_jenis_kelamin = tk.Entry(frame_input_siswa)
entry_jenis_kelamin.grid(row=2, column=1, padx=5)

button_tambah_siswa = tk.Button(frame_input_siswa, text="Tambah Data Siswa", command=tambah_siswa)
button_tambah_siswa.grid(row=3, column=0, columnspan=2, pady=5)

frame_input_nilai = tk.Frame(app)
frame_input_nilai.pack(pady=10)

label_nim_nilai = tk.Label(frame_input_nilai, text="NIM Siswa:")
label_nim_nilai.grid(row=0, column=0, padx=5)
entry_nim_nilai = tk.Entry(frame_input_nilai)
entry_nim_nilai.grid(row=0, column=1, padx=5)

label_tugas1 = tk.Label(frame_input_nilai, text="Nilai Tugas 1:")
label_tugas1.grid(row=1, column=0, padx=5)
entry_tugas1 = tk.Entry(frame_input_nilai)
entry_tugas1.grid(row=1, column=1, padx=5)

label_tugas2 = tk.Label(frame_input_nilai, text="Nilai Tugas 2:")
label_tugas2.grid(row=2, column=0, padx=5)
entry_tugas2 = tk.Entry(frame_input_nilai)
entry_tugas2.grid(row=2, column=1, padx=5)

label_tugas3 = tk.Label(frame_input_nilai, text="Nilai Tugas 3:")
label_tugas3.grid(row=3, column=0, padx=5)
entry_tugas3 = tk.Entry(frame_input_nilai)
entry_tugas3.grid(row=3, column=1, padx=5)

label_uts = tk.Label(frame_input_nilai, text="Nilai UTS:")
label_uts.grid(row=4, column=0, padx=5)
entry_uts = tk.Entry(frame_input_nilai)
entry_uts.grid(row=4, column=1, padx=5)

label_uas = tk.Label(frame_input_nilai, text="Nilai UAS:")
label_uas.grid(row=5, column=0, padx=5)
entry_uas = tk.Entry(frame_input_nilai)
entry_uas.grid(row=5, column=1, padx=5)

button_tambah_nilai = tk.Button(frame_input_nilai, text="Tambah Nilai", command=tambah_nilai)
button_tambah_nilai.grid(row=6, column=0, columnspan=2, pady=5)

frame_tampil_hasil = tk.Frame(app)
frame_tampil_hasil.pack(pady=10)

button_lihat_hasil = tk.Button(frame_tampil_hasil, text="Lihat Data Siswa dan Nilai", command=lihat_inputan)
button_lihat_hasil.pack()

button_edit_data = tk.Button(frame_tampil_hasil, text="Edit Data Siswa", command=edit_data)
button_edit_data.pack()

app.mainloop()


# In[ ]:





# In[ ]:




