# hasil rapot

import math
import os
import sqlite3

clear_console = lambda: os.system("cls" if os.name in ("nt", "dos") else "clear")
warning = ""

conn = None
db = None


def input_user():
    global warning
    # Nama Umur JenisKelamin
    if not warning == "":
        print(warning)
        print("*Kosongkan untuk kembali")
        warning = ""
    else:
        print(
            "Masukan data siswa/i (NIM_Nama_Umur_JenisKelamin):\n*Kosongkan untuk kembali"
        )
    user_input = input("> ")

    if not user_input:
        return True

    data_input = user_input.split("_")
    data_input = [
        x for x in data_input if x
    ]  # jika data kosong, ex ["","a","b"] => ["a","b"]
    if len(data_input) > 4:
        warning = "Data kelebihan, dibutuhkan 4 data (Ex: NIM_Nama_Umur_JenisKelamin)"
        return False
    if len(data_input) < 4:
        warning = "Data kekurangan, dibutuhkan 4 data (Ex: NIM_Nama_Umur_JenisKelamin)"
        return False

    db.execute(f"SELECT nim FROM siswa WHERE nim={data_input[0]}")
    result = db.fetchone()
    if result:
        warning = "Data siswa/i sudah ada di dalam database"
        return False
    else:
        db.execute(f"INSERT INTO siswa VALUES (?, ?, ?, ?)", data_input)
        conn.commit()
        warning = "siswa/i sudah dimasukan kedalam database"
    return True


def input_data_to_user():
    global warning
    if not warning == "":
        print(warning)
        print("*Kosongkan untuk kembali")
        warning = ""
    else:
        print("Masukan NIM siswa untuk dimasukan nilainya:\n*Kosongkan untuk kembali")

    user_input = input("> ")

    if not user_input:
        return True

    user_input = "".join([x for x in user_input if x])

    db.execute(f"SELECT nim FROM siswa WHERE nim={user_input}")
    result = db.fetchone()

    if result:
        print(
            "Nilai yang dibutuhkan : Nilai tugas, Nilai kehadiran, Nilai uts, Nilai uas"
        )
        nilai_input = input("> ")
        while (
            not nilai_input
            or len(nilai_input.split(",")) < 4
            or len(nilai_input.split(",")) > 4
        ):
            print(
                "Masukan NIM siswa untuk dimasukan nilainya:\n*Kosongkan untuk kembali"
            )
            print(user_input)
            print(
                "Nilai yang dibutuhkan : Nilai tugas,Nilai kehadiran,Nilai uts,Nilai uas"
            )
            nilai_input = input("> ")

        nilai_input = nilai_input.split(",")
        print(nilai_input)
        input()
        data_nilai = [
            20 / 100 * float(nilai_input[0]),
            10 / 100 * float(nilai_input[1]),
            30 / 100 * float(nilai_input[2]),
            40 / 100 * float(nilai_input[3]),
        ]
        nilai_total = sum(data_nilai)

        db.execute(
            "INSERT INTO nilai Values (?, ?, ?, ?, ?, ?)",
            (
                user_input,
                nilai_input[0],
                nilai_input[1],
                nilai_input[2],
                nilai_input[3],
                nilai_total,
            ),
        )
        conn.commit()
        warning = "Nilai sudah dimasukan"
        return True
    else:
        warning = "siswa/i dengan nim itu tidak ada di database"
        return False


def passing_data():
    pass


menu_list = [
    {"text": "Masukan siswa/i", "run": input_user},
    {"text": "Masukan nilai", "run": input_data_to_user},
    {"text": "Hasil data", "run": passing_data},
]


def main():
    global warning

    print("Sistem rapot siswa/i".center(40))
    print(("-" * 40).center(40))
    for index, value in enumerate(menu_list, 1):
        print(str(index) + ". " + value["text"])
    print((str(len(menu_list) + 1) + ". keluar"))
    print(("-" * 40))
    if not warning == "":
        print(warning)
        warning = ""
    user_input = input("> ")

    if not user_input:
        return False

    if user_input.isnumeric():
        if int(user_input) == len(menu_list) + 1:
            return True
        elif int(user_input) <= len(menu_list):
            enable = True
            while enable:
                clear_console()
                enable = not menu_list[int(user_input) - 1]["run"]()

    else:
        return False


if __name__ == "__main__":
    conn = sqlite3.connect("siswa.db")
    db = conn.cursor()

    db.execute(
        "CREATE TABLE IF NOT EXISTS siswa(nim text primary key, nama text, umur integer, jenisKelamin varchar)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS nilai(nim_siswa text REFERENCES siswa(nim),tugas integer, kehadiran integer, uts integer, uas integer, total real)"
    )

    conn.commit()

    try:
        enable = True
        while enable:
            clear_console()
            enable = not main()
        clear_console()
    except KeyboardInterrupt:
        clear_console()
    conn.close()
    print("Terima kasih sudah menggunakan program kami")
