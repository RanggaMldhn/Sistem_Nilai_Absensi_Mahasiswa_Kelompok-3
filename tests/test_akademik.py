import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from exceptions.custom_exceptions import (
    NilaiTidakValidError,
    AbsensiDuplikatError,
    NIMDuplikatError
)
from models.pengguna import Pengguna, Mahasiswa
from models.nilai import NilaiTugas, NilaiUTS, NilaiUAS
from services.akademik import SistemAkademik

# Tambahan import untuk testing Layer 1 (Database)
from database.models import Base, MahasiswaDB, NilaiDB


def test_nilai_di_luar_range():
    with pytest.raises(NilaiTidakValidError):
        nilai_invalid_atas = NilaiTugas(105)
        
    with pytest.raises(NilaiTidakValidError):
        nilai_invalid_bawah = NilaiTugas(-10)

def test_nilai_akhir_benar():
    mhs = Mahasiswa("Andi", "2024001", "andi@kampus.ac.id", semester=3)
    
    # 100 * 0.30 = 30
    mhs.tambah_nilai(NilaiTugas(100))
    # 80 * 0.35 = 28
    mhs.tambah_nilai(NilaiUTS(80))
    # 80 * 0.35 = 28
    mhs.tambah_nilai(NilaiUAS(80))
    
    hasil = mhs.nilai_akhir()
    assert hasil == 86.0

def test_mahasiswa_adalah_pengguna():
    mhs = Mahasiswa("Budi", "2024002", "budi@kampus.ac.id", semester=3)
    
    # Act & Assert
    assert isinstance(mhs, Pengguna)
    assert isinstance(mhs, Mahasiswa)

def test_absensi_duplikat():
    sistem = SistemAkademik()
    mhs = Mahasiswa("Cici", "2024003", "cici@kampus.ac.id", semester=3)
    sistem.tambah_mahasiswa(mhs)
    
    sistem.catat_absensi("2024003", pertemuan=1, status="Hadir")
    
    # Assert: Absen kedua (harus gagal)
    with pytest.raises(AbsensiDuplikatError):
        sistem.catat_absensi("2024003", pertemuan=1, status="Hadir")

def test_nim_duplikat():
    sistem = SistemAkademik()
    mhs1 = Mahasiswa("Dedi", "2024004", "dedi@kampus.ac.id", semester=3)
    mhs2 = Mahasiswa("Dewa", "2024004", "dewa@kampus.ac.id", semester=5) # NIM sama
    
    sistem.tambah_mahasiswa(mhs1)
    
    with pytest.raises(NIMDuplikatError):
        sistem.tambah_mahasiswa(mhs2)

# --- TEST BARU UNTUK LAYER 1 (DATABASE) ---

@pytest.fixture
def db():
    """
    Fixture: buat database SQLite in-memory untuk satu test.
    Database ini hanya hidup selama 1 test, lalu hilang otomatis.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_simpan_mahasiswa_ke_db(db):
    mhs = MahasiswaDB(nim="2026001", nama="Tester", semester=2)
    db.add(mhs)
    db.commit()
    
    hasil = db.query(MahasiswaDB).filter_by(nim="2026001").first()
    assert hasil is not None
    assert hasil.nama == "Tester"
    assert hasil.persentase_kehadiran == 0.0

def test_update_persentase_kehadiran(db):
    mhs = MahasiswaDB(nim="2026002", nama="Tester 2", semester=2)
    db.add(mhs)
    db.commit()
    
    mhs_update = db.query(MahasiswaDB).filter_by(nim="2026002").first()
    mhs_update.persentase_kehadiran = 85.5
    db.commit()
    
    hasil = db.query(MahasiswaDB).filter_by(nim="2026002").first()
    assert hasil.persentase_kehadiran == 85.5

def test_relasi_mahasiswa_nilai(db):
    mhs = MahasiswaDB(nim="2026003", nama="Tester 3", semester=2)
    db.add(mhs)
    db.commit()
    
    nilai = NilaiDB(mahasiswa_id=mhs.id, komponen="UTS", nilai=88.0, waktu_input="2026-07-17")
    db.add(nilai)
    db.commit()
    
    db.refresh(mhs)
    assert len(mhs.nilai_list) == 1
    assert mhs.nilai_list[0].komponen == "UTS"


# --- TAMBAHAN LAYER 2: TEST REST API & FUNCTIONAL PROGRAMMING ---
from unittest.mock import patch, MagicMock
from services.api_client import get_kurs
import requests
from services.laporan import mahasiswa_lulus

def test_get_kurs_berhasil():
    # Membuat 'aktor pengganti' untuk response API
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rates": {"USD": 0.000064}}
    mock_resp.raise_for_status.return_value = None
    
    # Mengganti fungsi requests.get asli dengan yang palsu selama blok 'with' berjalan
    with patch("services.api_client.requests.get", return_value=mock_resp):
        hasil = get_kurs("USD")
        assert hasil == 0.000064

def test_get_kurs_timeout():
    # Menguji apakah error Timeout dari library requests diubah menjadi ConnectionError kita
    with patch("services.api_client.requests.get", side_effect=requests.exceptions.Timeout):
        import pytest
        with pytest.raises(ConnectionError):
            get_kurs("USD")

def test_mahasiswa_lulus_hanya_yang_lulus():
    # Buat 3 mahasiswa dummy
    m1 = Mahasiswa("Andi", "101", "andi@mail.com", 1)
    m2 = Mahasiswa("Budi", "102", "budi@mail.com", 1)
    m3 = Mahasiswa("Cita", "103", "cita@mail.com", 1)
    
    # Kita akali nilai akhirnya menggunakan MagicMock agar tidak perlu input nilai manual
    m1.nilai_akhir = MagicMock(return_value=80.0)  # Lulus
    m2.nilai_akhir = MagicMock(return_value=50.0)  # Tidak lulus
    m3.nilai_akhir = MagicMock(return_value=75.0)  # Lulus
    
    hasil = mahasiswa_lulus([m1, m2, m3])
    
    # Pastikan yang return cuma 2 orang (Andi dan Cita)
    assert len(hasil) == 2
    assert m1 in hasil
    assert m3 in hasil
    assert m2 not in hasil

def test_mahasiswa_lulus_diurutkan_nilai():
    m1 = Mahasiswa("Andi", "101", "andi@mail.com", 1)
    m2 = Mahasiswa("Budi", "102", "budi@mail.com", 1)
    
    # Andi dapat 70, Budi dapat 90
    m1.nilai_akhir = MagicMock(return_value=70.0)
    m2.nilai_akhir = MagicMock(return_value=90.0)
    
    hasil = mahasiswa_lulus([m1, m2])
    
    # Budi harusnya ada di urutan pertama (index 0) karena nilainya lebih tinggi
    assert len(hasil) == 2
    assert hasil[0] == m2
    assert hasil[1] == m1
