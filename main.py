from models.pengguna import Mahasiswa, Dosen
from services.akademik import SistemAkademik
from exceptions.custom_exceptions import (
    NIMDuplikatError,
    MahasiswaTidakDitemukanError,
    NilaiTidakValidError,
    AbsensiDuplikatError
)
from datetime import datetime

# ① Import fungsionalitas Layer 1 (Database)
from database.db_handler import (
    init_db, simpan_mahasiswa, ambil_semua_mahasiswa,
    update_persentase_kehadiran, simpan_nilai, ambil_nilai_mahasiswa
)

# ⑤ Import fungsionalitas Layer 2 (API)
from services.api_client import harga_dalam_mata_uang

# ⑧ Import fungsionalitas Layer 2 (Functional Programming)
from services.laporan import (
    mahasiswa_lulus, 
    rata_rata_per_komponen, 
    mahasiswa_kehadiran_rendah, 
    ringkasan_kelas
)

# Konstanta Biaya Remedial
BIAYA_REMEDIAL_PER_SKS = 100_000
SKS_MATA_KULIAH = 4

def menu_utama(sistem: SistemAkademik):
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
        print("9. Cek Estimasi Biaya Remedial")
        print("10. Menu Laporan (Functional Programming)") # ⑧ Menu Baru untuk Layer 2 (FP)
        print("0. Keluar")
        print("-" * 40)
        
        pilihan = input("Pilih menu (0-10): ")
        
        try:
            if pilihan == '1':
                print("\n-- TAMBAH MAHASISWA --")
                nama = input("Masukkan Nama: ")
                nim = input("Masukkan NIM: ")
                email = input("Masukkan Email: ")
                semester = int(input("Masukkan Semester (Angka): "))
                
                mhs = Mahasiswa(nama, nim, email, semester)
                pesan = sistem.tambah_mahasiswa(mhs)
                
                simpan_mahasiswa(nim, nama, semester)
                print(f"✅ [SUKSES] {pesan}")
                
            elif pilihan == '2':
                # (Sama seperti sebelumnya)
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
                
                mhs = sistem.cari_mahasiswa(nim)
                update_persentase_kehadiran(nim, mhs.absensi.persentase_hadir())
                print(f"✅ [SUKSES] {pesan}")
                
            elif pilihan == '5':
                print("\n-- INPUT NILAI --")
                nim = input("Masukkan NIM Mahasiswa: ")
                jenis = input("Jenis Komponen (Tugas/UTS/UAS): ")
                nilai = float(input("Nilai (0 - 100): "))
                
                pesan = sistem.input_nilai(nim, jenis, nilai)
                
                daftar_mhs_db = ambil_semua_mahasiswa()
                mhs_db = next((m for m in daftar_mhs_db if m.nim == nim), None)
                if mhs_db:
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    simpan_nilai(mhs_db.id, jenis, nilai, waktu)
                
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
                print("\n-- CEK ESTIMASI BIAYA REMEDIAL --")
                nim = input("Masukkan NIM Mahasiswa: ")
                mhs = sistem.cari_mahasiswa(nim)
                nilai = mhs.nilai_akhir()
                
                if nilai < 60:
                    biaya_idr = BIAYA_REMEDIAL_PER_SKS * SKS_MATA_KULIAH
                    mata_uang = input("Tampilkan dalam mata uang asing? (kosongkan untuk skip): ").strip()
                    if mata_uang:
                        try:
                            hasil = harga_dalam_mata_uang(biaya_idr, mata_uang)
                            print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,} (≈ {hasil})")
                        except (ConnectionError, ValueError) as e:
                            print(f"⚠️ [API ERROR] {e}")
                            print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,}")
                    else:
                        print(f"Mahasiswa perlu remedial. Estimasi biaya: Rp{biaya_idr:,}")
                else:
                    print("✅ Mahasiswa sudah lulus, tidak perlu remedial.")

            elif pilihan == '10':
                print("\n-- MENU LAPORAN (FUNCTIONAL PROGRAMMING) --")
                print("1. Peringkat Kelulusan (Nilai >= 60)")
                print("2. Rata-rata per Komponen (Tugas/UTS/UAS)")
                print("3. Mahasiswa Kehadiran Rendah (< 75%)")
                print("4. Ringkasan Keseluruhan Kelas")
                
                sub_pilihan = input("Pilih laporan (1-4): ")
                
                # Mengambil data list mahasiswa langsung dari atribut sistem
                data_mhs = getattr(sistem, '_daftar_mahasiswa', getattr(sistem, 'daftar_mahasiswa', []))
                
                if not data_mhs:
                    print("⚠️ Data mahasiswa masih kosong. Silakan tambah mahasiswa terlebih dahulu.")
                else:
                    if sub_pilihan == '1':
                        print("\n📊 PERINGKAT KELULUSAN:")
                        lulus = mahasiswa_lulus(data_mhs)
                        if not lulus: print("- Belum ada mahasiswa yang lulus.")
                        for i, m in enumerate(lulus, 1):
                            print(f"{i}. {m.nama} (NIM: {getattr(m, 'id_pengguna', getattr(m, 'nim', ''))}) - Nilai: {m.nilai_akhir():.1f}")
                            
                    elif sub_pilihan == '2':
                        print("\n📊 RATA-RATA KOMPONEN KELAS:")
                        rata_rata = rata_rata_per_komponen(data_mhs)
                        for komponen, nilai in rata_rata.items():
                            print(f"- {komponen}: {nilai:.1f}")
                            
                    elif sub_pilihan == '3':
                        print("\n⚠️ KEHADIRAN RENDAH (< 75%):")
                        kritis = mahasiswa_kehadiran_rendah(data_mhs)
                        if not kritis: print("- Semua mahasiswa memiliki kehadiran aman.")
                        for m in kritis:
                            print(f"- {m.nama} (Kehadiran: {m.absensi.persentase_hadir():.0f}%)")
                            
                    elif sub_pilihan == '4':
                        print("\n📝 RINGKASAN KELAS:")
                        ringkasan = ringkasan_kelas(data_mhs)
                        for baris in ringkasan:
                            print(baris)
                    else:
                        print("❌ Pilihan sub-menu tidak valid.")
                    
            elif pilihan == '0':
                print("👋 Keluar dari program. Terima kasih!")
                break
                
            else:
                print("⚠️ [PERINGATAN] Pilihan tidak valid.")
                
        except ValueError:
            print("❌ [ERROR INPUT] Masukan tidak valid! Pastikan pengisian angka sudah benar.")
        except (NIMDuplikatError, MahasiswaTidakDitemukanError, NilaiTidakValidError, AbsensiDuplikatError) as e:
            print(f"❌ [ERROR SISTEM] {e}")
        except Exception as e:
            print(f"❌ [FATAL ERROR] Terjadi kesalahan sistem: {e}")

if __name__ == '__main__':
    init_db()
    sistem_akademik = SistemAkademik()
    menu_utama(sistem_akademik)