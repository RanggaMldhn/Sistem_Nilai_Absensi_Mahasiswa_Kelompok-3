from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import Base, MahasiswaDB, NilaiDB

# 1. Koneksi ke file database di root folder proyek (akademik.db)
engine = create_engine("sqlite:///akademik.db")

def init_db() -> None:
    """Buat semua tabel jika belum ada. Dipanggil saat program mulai."""
    Base.metadata.create_all(engine)

def simpan_mahasiswa(nim: str, nama: str, semester: int) -> MahasiswaDB:
    """Tambah baris baru ke tabel mahasiswa. Return objek MahasiswaDB."""
    with Session(engine) as session:
        mhs_baru = MahasiswaDB(nim=nim, nama=nama, semester=semester)
        session.add(mhs_baru)
        session.commit()
        session.refresh(mhs_baru)
        
        # Expunge agar data bisa dibaca di luar blok 'with' (mencegah error DetachedInstance)
        session.expunge(mhs_baru)
        return mhs_baru

def ambil_semua_mahasiswa() -> list[MahasiswaDB]:
    """Return list semua MahasiswaDB dari database."""
    with Session(engine) as session:
        daftar_mahasiswa = session.query(MahasiswaDB).all()
        session.expunge_all()
        return daftar_mahasiswa

def update_persentase_kehadiran(nim: str, persentase_baru: float) -> None:
    """Update kolom persentase_kehadiran pada mahasiswa dengan nim tertentu."""
    with Session(engine) as session:
        # Cari mahasiswa berdasarkan NIM
        mhs = session.query(MahasiswaDB).filter(MahasiswaDB.nim == nim).first()
        if mhs:
            mhs.persentase_kehadiran = persentase_baru
            session.commit()

def simpan_nilai(mahasiswa_id: int, komponen: str, nilai: float, waktu_input: str) -> NilaiDB:
    """Tambah baris baru ke tabel nilai. Return objek NilaiDB."""
    with Session(engine) as session:
        nilai_baru = NilaiDB(
            mahasiswa_id=mahasiswa_id,
            komponen=komponen,
            nilai=nilai,
            waktu_input=waktu_input
        )
        session.add(nilai_baru)
        session.commit()
        session.refresh(nilai_baru)
        session.expunge(nilai_baru)
        return nilai_baru

def ambil_nilai_mahasiswa(mahasiswa_id: int) -> list[NilaiDB]:
    """Return list semua NilaiDB milik satu mahasiswa tertentu."""
    with Session(engine) as session:
        # Filter nilai berdasarkan id mahasiswa
        daftar_nilai = session.query(NilaiDB).filter(NilaiDB.mahasiswa_id == mahasiswa_id).all()
        session.expunge_all()
        return daftar_nilai