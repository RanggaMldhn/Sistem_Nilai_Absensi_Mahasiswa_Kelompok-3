# Sistem Nilai dan Absensi Mahasiswa (Project UTS)

Ini adalah project program CLI berbasis Python (dengan konsep OOP) yang kita buat untuk mengelola data mahasiswa, mulai dari input nilai sampai pencatatan absen. 

## 👥 Anggota Kelompok
* **Moh. Rozan Istazada Firdausy** - 25083000060 (Tugas: Menambahkan file dan branch Absensi dan Memperbaiki Error error yang terjadi pada vscode ini, dan juga membuat unit test)
* **Rangga Maulidhani** - 25083000064 (Tugas: Menambahkan file file pertama serta branch dikarenakan ketua dan juga memperbaiki error error pada vscode serta membuat main.py)
* **Arbi Maulana** - 25083000070 (Tugas: Menambahkan file akademik, memperbaiki bug)

---

## 🚀 Cara Menjalankan Program
Untuk mencoba programnya, buka terminal/command prompt di dalam folder project ini atau bisa di atas kanan langsung play dan juga bisa ditekan f5 shortcut agar menjalankan program tersebut
jika buka terminalnya bisa menulis ini dan menjalankannya:

```bash
python main.py

```

---

## 🧪 Cara Menjalankan Unit Test

Kita juga nyiapin *unit testing* buat mastiin fitur-fiturnya berjalan normal dan bebas *bug*. Cara test-nya tinggal ketik ini di terminal:

```bash
python -m pytest tests/test_akademik.py

```

---

## ✨ Fitur Utama

* **Kelola Mahasiswa:** Bisa nambahin dan nyimpen data mahasiswa.
* **Hitung Nilai Otomatis:** Tinggal masukin nilai Tugas (30%), UTS (35%), dan UAS (35%), nanti program yang hitung nilai akhirnya.
* **Sistem Absensi:** Bisa nyatet kehadiran per pertemuan dan nampilin persentase kehadiran.
* **Lihat Rekap:** Nampilin ringkasan data mahasiswa lengkap sama nilai akhir dan status absennya.
* **Aman dari Error:** Kita udah tambahin validasi, jadi program nggak akan *crash* kalau user masukin NIM yang sama (duplikat), absen dua kali, atau masukin nilai lebih dari 100.

---

## 🏗️ Struktur Class (Class Diagram)

Konsep OOP di program ini dibagi jadi beberapa *class*:

* **Pengguna**: Ini *Base class*-nya (nyimpen nama, id, email).
* **Mahasiswa**: Turunan dari `Pengguna` (ketambahan fungsi simpan nilai & absensi).
* **Dosen**: Turunan dari `Pengguna` (punya atribut mata kuliah).


* **KomponenNilai**: Ini *Abstract class* buat nentuin standar bobot nilai.
* Turunannya ada **NilaiTugas**, **NilaiUTS**, dan **NilaiUAS**.


* **Absensi & CatatanAbsensi**: Class khusus buat ngurusin data kehadiran tiap pertemuan.
* **SistemAkademik**: Bertindak sebagai *Controller* yang nyambungin semua class di atas biar aplikasinya jalan.

---

## 💡 Kenapa Desain Kodenya Begini? (Design Decisions)

1. **Foldernya Dipisah (Modular):** Kodenya sengaja kita pecah ke folder `models`, `services`, dan `exceptions`. Tujuannya biar rapi aja, jadi gampang kalau mau nyari file pas lagi *debugging*.
2. **Pakai Inheritance:** `Mahasiswa` sama `Dosen` diturunkan dari class `Pengguna`. Biar kita nggak capek nulis ulang variabel dasar kayak nama dan ID di masing-masing class.
3. **Pakai Polymorphism:** Kita bikin *abstract class* di `KomponenNilai` biar cara hitung nilai akhirnya lebih rapi dan gampang kalau nanti mau nambah komponen nilai baru.
4. **Bikin Custom Exceptions:** Daripada pakai *error* bawaan Python yang bahasanya susah dimengerti, kita bikin class *error* sendiri (contohnya `NIMDuplikatError`). Jadi kalau user salah input, pesan *error*-nya lebih jelas.

```

```