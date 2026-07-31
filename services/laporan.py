def mahasiswa_lulus(daftar_mahasiswa: list) -> list:
    """
    Mengembalikan daftar mahasiswa yang lulus (nilai >= 60),
    diurutkan dari peringkat kelas (tertinggi ke terendah).
    """
    # 1. Filter nilai akhir >= 60
    mahasiswa_terfilter = filter(lambda m: m.nilai_akhir() >= 60, daftar_mahasiswa)
    
    # 2. Urutkan dari nilai terbesar (reverse=True)
    return sorted(mahasiswa_terfilter, key=lambda m: m.nilai_akhir(), reverse=True)


def rata_rata_per_komponen(daftar_mahasiswa: list) -> dict:
    """
    Menghitung nilai rata-rata kelas per komponen ujian/tugas.
    """
    # Mengumpulkan semua objek nilai ke dalam satu list pipih (flatten list) 
    # tanpa for-loop menggunakan trik sum(list_of_lists, [])
    semua_nilai = sum(map(lambda m: m._nilai_list, daftar_mahasiswa), [])

    def filter_dan_rata_rata(jenis_target: str) -> float:
        # Mencocokkan berdasarkan atribut 'komponen', 'jenis', atau nama Class-nya (misal: NilaiTugas -> Tugas)
        nilai_spesifik = list(filter(
            lambda n: getattr(n, 'komponen', getattr(n, 'jenis', type(n).__name__.replace('Nilai', ''))) == jenis_target, 
            semua_nilai
        ))
        
        # Mencegah pembagian dengan nol jika datanya kosong
        if not nilai_spesifik:
            return 0.0
            
        total_nilai = sum(map(lambda n: getattr(n, 'nilai', 0), nilai_spesifik))
        return total_nilai / len(nilai_spesifik)

    return {
        "Tugas": filter_dan_rata_rata("Tugas"),
        "UTS": filter_dan_rata_rata("UTS"),
        "UAS": filter_dan_rata_rata("UAS")
    }


def mahasiswa_kehadiran_rendah(daftar_mahasiswa: list) -> list:
    """
    Mengembalikan daftar mahasiswa dengan kehadiran < 75%,
    diurutkan dari persentase paling rendah (paling kritis).
    """
    # 1. Filter kehadiran < 75%
    mahasiswa_terfilter = filter(lambda m: m.absensi.persentase_hadir() < 75, daftar_mahasiswa)
    
    # 2. Urutkan persentase terendah ke tertinggi (ascending)
    return sorted(mahasiswa_terfilter, key=lambda m: m.absensi.persentase_hadir())


def ringkasan_kelas(daftar_mahasiswa: list) -> list:
    """
    Memetakan setiap objek mahasiswa menjadi teks string ringkasan data.
    """
    # Gunakan getattr untuk mengamankan pengambilan data jika atribut menggunakan 'id_pengguna' atau 'nim'
    return list(map(
        lambda m: f"{m.nama} — NIM {getattr(m, 'id_pengguna', getattr(m, 'nim', ''))} — Nilai Akhir: {m.nilai_akhir():.1f} — Kehadiran: {m.absensi.persentase_hadir():.0f}%",
        daftar_mahasiswa
    ))