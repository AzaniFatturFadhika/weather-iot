# Analisis Mendalam Backend (`examples/weatherapp_backend/main.py`)

Dokumen ini berisi analisis teknis mendalam terhadap kode sumber backend yang ada (`main.py`), diikuti dengan perbandingan komprehensif terhadap kebutuhan arsitektur sistem IoT Cuaca v2.0.0 yang direncanakan.

---

## BAGIAN 1: Analisis Kode Eksisting (`main.py`)

### 1. Tinjauan Arsitektur & Teknologi
*   **Framework**: FastAPI (Python).
*   **Server**: Uvicorn (dijalankan pada host `0.0.0.0`, port `8000`).
*   **Database Driver**: `MySQLdb` (mysqlclient) - Driver sinkron (blocking).
*   **Machine Learning**: `scikit-learn` (LinearRegression), `numpy`, `pickle` untuk memuat model.
*   **Autentikasi**: Kustom menggunakan `bcrypt` untuk hashing password dan mekanisme OTP via Email.
*   **Konkurensi**: Menggunakan `asyncio` untuk tugas latar belakang (penghapusan OTP), namun operasi database bersifat blocking yang dapat menghambat performa pada beban tinggi.

### 2. Analisis Komponen Fungsional

#### A. Konfigurasi Database
*   **Koneksi**: Menggunakan dictionary `db_config` hardcoded.
*   **Kredensial**: User `root` dengan password kosong (`''`). Database target bernama `ums`.
*   **Manajemen Koneksi**: Koneksi dibuat secara global (`conn`) di awal aplikasi, namun juga dibuat ulang secara lokal di dalam endpoint `/login/`. Ini menunjukkan ketidakkonsistenan pola manajemen koneksi (tidak menggunakan Connection Pool).

#### B. Manajemen Pengguna & Autentikasi
*   **Model Data**: Menggunakan Pydantic `User` dan `Login`.
*   **Endpoint `/generate_otp/`**:
    *   Menghasilkan OTP 6 digit.
    *   Menyimpan OTP di memori (`otp_map`) dan database.
    *   **Isu Keamanan**: Kredensial email pengirim (`1901029@iot.bdu.ac.bd`) dan password **tertanam langsung (hardcoded)** di dalam fungsi `send_email`.
    *   **Logika**: OTP kedaluwarsa dalam 5 menit (diatur via `asyncio.sleep`).
*   **Endpoint `/users/` (Register)**:
    *   Memverifikasi OTP sebelum membuat user.
    *   Password di-hash menggunakan `bcrypt`.
*   **Endpoint `/login/`**:
    *   Memverifikasi username dan password hash.
    *   Membuka koneksi DB baru setiap request (tidak efisien).
*   **Endpoint `/forgot-password`**:
    *   Memungkinkan reset password dengan verifikasi OTP.

#### C. Ingesti Data Cuaca (Input)
*   **Endpoint**: `@app.get("/weather-data/create")`
*   **Metode**: **HTTP GET**. Ini adalah pelanggaran standar RESTful API yang seharusnya menggunakan **POST** untuk pembuatan data.
*   **Parameter**: Menerima `temp`, `humidity`, `isRaining`, `lightIntensity`, `windSpeed`, `pressure` sebagai query parameters.
*   **Validasi**: Nilai default `0` jika parameter tidak ada. Tidak ada validasi range nilai atau tipe data yang ketat selain casting float.
*   **Kelemahan Fatal**: Tidak ada mekanisme autentikasi atau identifikasi perangkat (Station ID) pada endpoint ini. Siapapun dapat menyuntikkan data palsu.

#### D. Pengambilan Data (Output)
*   **Endpoint `/weather-data/get/last`**: Mengambil 1 data terakhir berdasarkan lokasi (nama kota).
*   **Endpoint `/weather-data/line-chart`**: Mengambil 10 data `windSpeed` terakhir (hardcoded lokasi "Gazipur"). Sangat spesifik dan tidak fleksibel.

#### E. Machine Learning & Prediksi
#### E. Machine Learning & Prediksi
*   **Endpoint**: `/weather-data/get-predicted-data`
*   **Model**: Memuat file `rf_model_pkl` (kemungkinan Random Forest) menggunakan `pickle`.
*   **Logika Prediksi**:
    1.  **Input**: Menerima parameter `day`, `month`, `year`.
    2.  **Looping**: Melakukan iterasi 3 kali untuk memprediksi cuaca tanggal tersebut dan 2 hari berikutnya.
    3.  **Load Model**: Membuka dan memuat model `rf_model_pkl` di setiap iterasi (tidak efisien).
    4.  **Eksekusi**: Memanggil `rf_model.predict(features)` dengan fitur `[day, month, year]`.
    5.  **Output**: Mengembalikan 7 nilai prediksi (suhu, kelembaban, dll) dan mapping kondisi cuaca (0-5) ke teks.
*   **Analisis Incremental Learning**:
    *   **Status**: ❌ **BELUM DIIMPLEMENTASIKAN**.
    *   **Temuan**: Kode hanya memiliki fitur **Data Collection** via endpoint `/weather-data/create` (INSERT ke DB).
    *   **Kekurangan**: Tidak ada logika untuk melatih ulang model (`fit` / `partial_fit`) secara otomatis saat data baru masuk. Model `rf_model_pkl` bersifat statis.
    *   **Rekomendasi**: Perlu background worker (misal Celery/APScheduler) untuk mengambil data baru dari DB secara berkala, melatih ulang model, dan memperbarui file `.pkl`.

### 3. Audit Keamanan & Kualitas Kode
1.  **Hardcoded Secrets**: Password email dan konfigurasi DB terekspos dalam kode sumber.
2.  **SQL Injection**: Sebagian besar query menggunakan parameter binding (`%s`), yang aman. Namun, praktik membuka/tutup kursor manual rentan terhadap kebocoran resource jika terjadi error sebelum `cursor.close()`.
3.  **Blocking I/O**: Penggunaan `MySQLdb` (sinkron) dalam fungsi `async` FastAPI dapat memblokir event loop, menurunkan throughput server secara drastis.
4.  **Error Handling**: Minim. Banyak blok kode tanpa `try-except` yang memadai, berpotensi menyebabkan "Internal Server Error" (500) pada klien.
5.  **Struktur**: Kode monolitik dalam satu file `main.py` menyulitkan pemeliharaan.

---

## BAGIAN 2: Perbandingan dengan Perencanaan Sistem v2.0.0

Bagian ini membandingkan implementasi saat ini dengan kebutuhan arsitektur baru (v2.0.0).

### 1. Protokol Komunikasi
| Fitur | Implementasi Saat Ini (`main.py`) | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Protokol Data** | HTTP GET Request | **MQTT (Pub/Sub)** | ❌ **Tidak Kompatibel** |
| **Arah Data** | Gateway -> API Server (Direct) | Gateway -> MQTT Broker -> Backend | ❌ Perlu Arsitektur Baru |
| **Efisiensi** | Rendah (Overhead HTTP Header) | Tinggi (Header biner ringan) | ❌ Perlu Upgrade |

### 2. Struktur Data & Database
| Fitur | Implementasi Saat Ini | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Identitas Stasiun** | Tidak ada (Hanya nama lokasi string) | **Station ID** (e.g., "TX001") | ❌ Kritis |
| **Identitas Gateway** | Tidak ada | **Gateway ID** | ❌ Perlu Ditambah |
| **Waktu Observasi** | Waktu server (`createAt`) | **Waktu Sensor** (`observationDate`) | ❌ Perlu Ditambah |
| **Data Hujan** | Boolean (`isRaining`) | **Analog/Curah Hujan** (mm/ADC) | ⚠️ Perlu Penyesuaian |
| **Metadata Sinyal** | Tidak ada | **RSSI & SNR** (LoRa) | ❌ Perlu Ditambah |

### 3. Fungsionalitas
| Fitur | Implementasi Saat Ini | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Prediksi Cuaca** | Ada (Random Forest, 3 hari) | Ada (Perlu integrasi data real-time) | ✅ Dapat Digunakan Kembali |
| **Autentikasi User** | Ada (OTP Email) | Ada (Role-based Access) | ✅ Dapat Digunakan Kembali |
| **Integrasi API Luar**| Tidak ada | **OpenWeatherMap/BMKG** (Pembanding) | ❌ Perlu Fitur Baru |

### 4. Kesimpulan & Rekomendasi Migrasi

Backend yang ada **tidak dapat digunakan secara langsung** untuk sistem v2.0.0 karena perbedaan fundamental dalam protokol komunikasi (HTTP vs MQTT) dan struktur data.

**Langkah Migrasi yang Disarankan:**

1.  **Pertahankan Logika Bisnis**: Gunakan kembali logika prediksi ML (`rf_model_pkl`) dan sistem autentikasi user (dengan perbaikan keamanan).
2.  **Buat Service Baru (MQTT Consumer)**:
    *   Alih-alih endpoint HTTP `/weather-data/create`, buat skrip Python terpisah (atau background service) yang berlangganan ke topik `weather/station/data`.
    *   Service ini akan mem-parsing JSON payload (sesuai Schema.org) dan menyimpannya ke tabel database baru.
3.  **Refactoring Database**:
    *   Migrasi dari tabel `weather_data` lama ke `weather_observations` yang mendukung Station ID dan data LoRa.
    *   Gunakan ORM (seperti SQLAlchemy atau Prisma) atau driver async (`aiomysql`) untuk performa lebih baik.
4.  **Security Hardening**:
    *   Pindahkan semua kredensial (DB, Email) ke environment variables (`.env`).
    *   Hapus endpoint HTTP GET untuk input data.

Dokumen ini menjadi dasar untuk pengembangan backend v2.0.0 yang lebih robust, aman, dan skalabel.
