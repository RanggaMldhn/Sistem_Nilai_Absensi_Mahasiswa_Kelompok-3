from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey

# 1. Base class SQLAlchemy
class Base(DeclarativeBase):
    pass

# 2. Definisi Tabel Mahasiswa
class MahasiswaDB(Base):
    __tablename__ = 'mahasiswa'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nim = Column(String(20), unique=True, nullable=False)
    nama = Column(String(100))
    semester = Column(Integer)
    persentase_kehadiran = Column(Float, default=0.0)

    # Relasi one-to-many ke NilaiDB
    # back_populates menghubungkan variabel ini dengan variabel 'mahasiswa' di NilaiDB
    nilai_list = relationship("NilaiDB", back_populates="mahasiswa", cascade="all, delete-orphan")

# 3. Definisi Tabel Nilai
class NilaiDB(Base):
    __tablename__ = 'nilai'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mahasiswa_id = Column(Integer, ForeignKey('mahasiswa.id'))
    komponen = Column(String(20)) # Isi: "Tugas", "UTS", "UAS"
    nilai = Column(Float)
    waktu_input = Column(String(20))

    # Relasi balik ke MahasiswaDB
    mahasiswa = relationship("MahasiswaDB", back_populates="nilai_list")