from exceptions.custom_exceptions import AbsensiDuplikatError

class CatatanAbsensi:
    def __init__(self, pertemuan_ke: int, status: str):
        self.pertemuan_ke = pertemuan_ke
        self.status = status

    def __str__(self) -> str:
        return f"Pertemuan ke-{self.pertemuan_ke}: {self.status}"


class Absensi:
    def __init__(self):
        self._catatan: list[CatatanAbsensi] = []

    def catat_kehadiran(self, pertemuan_ke: int, status: str) -> None:
        # Optimasi pencarian menggunakan generator expression (Lebih cepat untuk data besar)
        if any(c.pertemuan_ke == pertemuan_ke for c in self._catatan):
            raise AbsensiDuplikatError(f"Absensi pertemuan ke-{pertemuan_ke} sudah dicatat!")
        
        self._catatan.append(CatatanAbsensi(pertemuan_ke, status))

    def hitung_persentase(self) -> float:
        if not self._catatan:
            return 0.0
        
        # Menggunakan filter generator hemat memori
        total_hadir = sum(1 for c in self._catatan if c.status.strip().lower() == 'hadir')
        return (total_hadir / len(self._catatan)) * 100

    # 🟢 DITAMBAHKAN: Alias agar bisa dipanggil oleh main.py dan laporan.py
    def persentase_hadir(self) -> float:
        return self.hitung_persentase()

    def tampilkan(self) -> None:
        for c in self._catatan:
            print(c)