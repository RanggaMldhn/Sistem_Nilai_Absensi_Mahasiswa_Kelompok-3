from models.pengguna import Mahasiswa, Dosen
from services.akademik import SistemAkademik
from exceptions.custom_exceptions import (
    NIMDuplikatError,
    MahasiswaTidakDitemukanError,
    NilaiTidakValidError,
    AbsensiDuplikatError
)
from datetime import datetime

# ① Tambahan Layer 1: Import fungsi CRUD dari database
from database.db_handler import (
    init_db, simpan_mahasiswa, ambil_semua_mahasiswa,
    update_persentase_kehadiran, simpan_nilai, ambil_nilai_mahasiswa
)

# ⑤ Tambahan Layer 2: Import API Client
from services.api_client import harga_dalam_mata_uang

# Konstanta Biaya Remedial
BIAYA_REMEDIAL_PER_SKS = 100_000   # Rp100.000 per SKS
SKS_MATA_KULIAH = 4                # sesuai RPS Pemrograman Lanjut

def menu_utama(sistem: SistemAkademik):
    """
    Fungsi menu utama untuk mengendalikan antarmuka CLI.
    Menerima parameter objek dari kelas SistemAkademik sebagai controller.
    """
    while True:
        print("\n" + "="*40)
        print("🎓 SISTEM INFORMASI AKADEMIK CLI 🎓")
        print("="*40)
        print("1. Tambah Mahasiswa")
        print("2. Tambah Dosen")
        print("3. Tampilkan Daftar Mahasiswa")
        print("4. Catat Absensi Mahasiswa")
        print("5. Input Nilai Mahasiswa")
        print("6. Rekap Peringkat & Nilai Kelas")
        print("7. Laporan Mahasiswa (Kehadiran < 75%)")
        print("8. Tampilkan dari Database (SQLite)")
        print("9. Cek Estimasi Biaya Remedial") # ⑤ Menu Baru Layer 2
        print("0. Keluar")
        print("-" * 40)
        
        pilihan = input("Pilih menu (0-9): ")
        
        try:
            if pilihan == '1':
                print("\n-- TAMBAH MAHASISWA --")
                nama = input("Masukkan Nama: ")
                nim = input("Masukkan NIM: ")
                email = input("Masukkan Email: ")
                semester = int(input("Masukkan Semester (Angka): "))
                
                mhs = Mahasiswa(nama, nim, email, semester)
                pesan = sistem.tambah_mahasiswa(mhs)
                
                # ③ Tambahan Layer 1: Simpan ke Database
                simpan_mahasiswa(nim, nama, semester)
                
                print(f"✅ [SUKSES] {pesan}")
                
            elif pilihan == '2':
                print("\n-- TAMBAH DOSEN --")
                nama = input("Masukkan Nama: ")
                nidn = input("Masukkan NIDN: ")
                email = input("Masukkan Email: ")
                mk = input("Masukkan Mata Kuliah: ")
                
                dsn = Dosen(nama, nidn, email, mk)
                pesan = sistem.tambah_dosen(dsn)
                print(f"✅ [SUKSES] {pesan}")

            elif pilihan == '3':
                sistem.tampilkan_daftar_mahasiswa()
                
            elif pilihan == '4':
                print("\n-- CATAT ABSENSI --")
                nim = input("Masukkan NIM Mahasiswa: ")
                pertemuan = int(input("Pertemuan ke- (Angka): "))
                status = input("Status (Hadir/Izin/Alpa): ")
                
                pesan = sistem.catat_absensi(nim, pertemuan, status)
                
                # ③ Tambahan Layer 1: Update Persentase Kehadiran di Database
                mhs = sistem.cari_mahasiswa(nim)
                persentase_baru = mhs.absensi.persentase_hadir()
                update_persentase_kehadiran(nim, persentase_baru)
                
                print(f"✅ [SUKSES] {pesan}")
                
            elif pilihan == '5':
                print("\n-- INPUT NILAI --")
                nim = input("Masukkan NIM Mahasiswa: ")
                jenis = input("Jenis Komponen (Tugas/UTS/UAS): ")
                nilai = float(input("Nilai (0 - 100): "))
                
                pesan = sistem.input_nilai(nim, jenis, nilai)
                
                # ③ Tambahan Layer 1: Simpan Nilai ke Database
                daftar_mhs_db = ambil_semua_mahasiswa()
                mhs_db = next((m for m in daftar_mhs_db if m.nim == nim), None)
                
                if mhs_db:
                    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    simpan_nilai(mhs_db.id, jenis, nilai, waktu_sekarang)
                
                print(f"✅ [SUKSES] {pesan}")
                
            elif pilihan == '6':
                sistem.rekap_nilai_kelas()
                sistem.peringkat_kelas()
                
            elif pilihan == '7':
                sistem.laporan_kehadiran_kurang()
                
            elif pilihan == '8':
                print("\n-- DATA MAHASISWA DARI DATABASE SQLITE --")
                daftar_mhs_db = ambil_semua_mahasiswa()
                
                if not daftar_mhs_db:
                    print("Belum ada data di database.")
                else:
                    for m in daftar_mhs_db:
                        print(f"[{m.nim}] {m.nama} (Semester {m.semester}) - Kehadiran: {m.persentase_kehadiran}%")
            
            elif pilihan == '9':
                # ⑤ Tambahan Layer 2: Fitur API Estimasi Biaya
                print("\n-- CEK ESTIMASI BIAYA REMEDIAL --")
                nim = input("Masukkan NIM Mahasiswa: ")
                
                # Cari mahasiswa; jika tidak ada, otomatis memicu MahasiswaTidakDitemukanError
                mhs = sistem.cari_mahasiswa(nim)
                nilai = mhs.nilai_akhir()
                
                if nilai < 60:
                    biaya_idr = BIAYA_REMEDIAL_PER_SKS * SKS_MATA_KULIAH
                    mata_uang = input("Tampilkan dalam mata uang asing? (kosongkan untuk skip): ").strip()
                    
                    if mata_uang:
                        try:
                            # Memanggil fungsi API dari api_client.py
                            hasil_konversi = harga_dalam_mata_uang(biaya_idr, mata_uang)
                            print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,} (≈ {hasil_konversi})")
                        except (ConnectionError, ValueError) as e:
                            # Menangkap error jaringan atau mata uang ngawur, jadi program nggak crash
                            print(f"⚠️ [API ERROR] {e}")
                            print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,}")
                    else:
                        print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,}")
                else:
                    print("✅ Mahasiswa sudah lulus, tidak perlu remedial.")
                    
            elif pilihan == '0':
                print("👋 Keluar dari program. Terima kasih!")
                break
                
            else:
                print("⚠️ [PERINGATAN] Pilihan tidak valid, silakan pilih angka 0-9.")
                
        except ValueError:
            print("❌ [ERROR INPUT] Masukan tidak valid! Pastikan kolom Semester, Pertemuan, atau Nilai diisi dengan angka.")
        except (NIMDuplikatError, MahasiswaTidakDitemukanError, NilaiTidakValidError, AbsensiDuplikatError) as e:
            print(f"❌ [ERROR SISTEM] {e}")
        except Exception as e:
            print(f"❌ [FATAL ERROR] Terjadi kesalahan sistem: {e}")

if __name__ == '__main__':
    init_db()
    sistem_akademik = SistemAkademik()
    menu_utama(sistem_akademik)