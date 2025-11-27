# Analisis Backend (`examples/weatherapp_backend/main.py`)

## 1. Tinjauan Umum
File `main.py` adalah aplikasi backend berbasis **FastAPI** yang berfungsi sebagai API server untuk aplikasi cuaca. Aplikasi ini menangani autentikasi pengguna, penyimpanan data cuaca, dan prediksi cuaca menggunakan model Machine Learning.

## 2. Temuan Utama

### A. Protokol Komunikasi (Discrepancy Kritis)
*   **Saat Ini**: Menggunakan endpoint HTTP GET `@app.get("/weather-data/create")` untuk menerima data sensor.
*   **Kebutuhan v2.0.0**: Arsitektur baru mewajibkan penggunaan protokol **MQTT** (Publish/Subscribe) untuk efisiensi energi dan skalabilitas IoT. Gateway harus mempublikasikan data ke broker MQTT, bukan memanggil API HTTP.

### B. Struktur Database
*   **Koneksi**: Terhubung ke database MySQL bernama `ums`.
*   **Tabel**: Menggunakan tabel `weather_data` yang strukturnya sesuai dengan analisis database sebelumnya (kurang `stationID`, `observationDate`, dll).
*   **Isu**: Data dimasukkan tanpa validasi stasiun atau penanda waktu yang presisi dari sensor.

### C. Keamanan
*   **Hardcoded Credentials**: Baris 63-64 berisi username dan password email (`1901029@iot.bdu.ac.bd`) secara hardcoded. Ini adalah risiko keamanan serius.
*   **OTP**: Logika OTP dan pengiriman email tercampur dalam kode utama.

### D. Fitur Machine Learning
*   **Model**: Memuat model `rf_model_pkl` (Random Forest) untuk memprediksi cuaca 3 hari ke depan.
*   **Input**: Tanggal (hari, bulan, tahun).
*   **Output**: Prediksi suhu, kelembaban, angin, tekanan, dan kondisi.
*   **Status**: Fitur ini tampaknya independen dari aliran data sensor real-time dan dapat dipertahankan.

## 3. Rekomendasi Perbaikan (Roadmap v2.0.0)

1.  **Integrasi MQTT**:
    *   Buat layanan terpisah (atau background task di FastAPI) yang berlangganan (subscribe) ke topik MQTT `weather/station/data`.
    *   Saat pesan diterima, simpan ke database baru (`weather_observations`).

2.  **Refactoring Database**:
    *   Perbarui kode untuk menggunakan tabel baru `stations` dan `weather_observations` sesuai rencana migrasi DB.
    *   Hapus hardcoded credentials dan gunakan Environment Variables (`.env`).

3.  **Pembersihan Kode**:
    *   Hapus endpoint `/weather-data/create` (HTTP) setelah transisi ke MQTT selesai.
    *   Pisahkan logika koneksi database dan email ke modul terpisah.

## 4. Kesimpulan
Backend saat ini **belum siap** untuk v2.0.0. Diperlukan modifikasi signifikan untuk beralih dari pola "HTTP Request" ke "MQTT Consumer" dan untuk mendukung skema database yang baru.
