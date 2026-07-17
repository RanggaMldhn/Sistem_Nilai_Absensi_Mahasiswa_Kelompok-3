import requests

BASE_URL = "https://api.frankfurter.app"

def get_kurs(mata_uang_tujuan: str) -> float:
    url = f"{BASE_URL}/latest"
    params = {'from': 'IDR', 'to': mata_uang_tujuan.upper()}
    
    try:
        # Request ke API dengan batas waktu 5 detik
        response = requests.get(url, params=params, timeout=5)
        
        # Memicu HTTPError jika status response adalah 4xx atau 5xx
        response.raise_for_status() 
        
        data = response.json()
        return float(data['rates'][mata_uang_tujuan.upper()])
        
    except requests.exceptions.Timeout:
        raise ConnectionError("Server tidak merespons. Periksa koneksi internet Anda.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Mata uang '{mata_uang_tujuan}' tidak valid. Status: {e.response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Koneksi gagal. Pastikan komputer terhubung ke internet.")

def harga_dalam_mata_uang(harga_idr: float, mata_uang_tujuan: str) -> str:
    kurs = get_kurs(mata_uang_tujuan)
    biaya_estimasi = harga_idr * kurs
    return f"{mata_uang_tujuan.upper()} {biaya_estimasi:.2f}"