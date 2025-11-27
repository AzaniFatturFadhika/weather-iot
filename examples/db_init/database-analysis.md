# Analisis Mendalam Database (`examples/db_init/weather_app_bd.sql`)

Dokumen ini berisi analisis teknis mendalam terhadap skema database yang ada (`weather_app_bd.sql`), diikuti dengan perbandingan komprehensif terhadap kebutuhan arsitektur sistem IoT Cuaca v2.0.0 yang direncanakan.

---

## BAGIAN 1: Analisis Skema Eksisting (`weather_app_bd.sql`)

### 1. Tinjauan Umum
File SQL ini adalah dump dari database MySQL bernama `ml`. Skema ini dirancang untuk dua tujuan yang sangat berbeda: penyimpanan dataset historis untuk pelatihan model Machine Learning dan backend operasional untuk aplikasi web cuaca sederhana.

### 2. Analisis Tabel

#### A. Tabel `historical_dataset`
*   **Tujuan**: Menyimpan data cuaca harian yang dikumpulkan (agregat). Kemungkinan besar dataset ini diimpor dari sumber eksternal (seperti Kaggle atau BMKG) untuk melatih model prediksi.
*   **Struktur Kolom**:
    *   `id` (int): Primary Key.
    *   `day`, `month`, `year` (int): Representasi tanggal terpisah.
    *   `tempmax`, `tempmin`, `temp` (float): Suhu maksimum, minimum, dan rata-rata harian.
    *   `humidity`, `windspeed`, `sealevelpressure` (float): Parameter cuaca standar.
    *   `conditions` (varchar): Deskripsi tekstual kondisi cuaca (misal: 'Partially cloudy', 'Rain').
*   **Volume Data**: Berisi sekitar 8.000+ baris data dari tahun 2021 hingga 2024.
*   **Kualitas Data**: Data tampak bersih dan terstruktur dengan baik untuk keperluan analisis deret waktu harian.

#### B. Tabel `weather_data`
*   **Tujuan**: Tabel operasional untuk menyimpan data yang masuk dari perangkat atau input manual.
*   **Struktur Kolom**:
    *   `id` (int): Primary Key.
    *   `temp`, `humidity` (float): Data sensor dasar.
    *   `isRaining` (tinyint/boolean): Indikator biner hujan (1=Hujan, 0=Tidak). Ini sangat terbatas dibandingkan sensor analog/digital modern.
    *   `lightIntensity` (float): Intensitas cahaya.
    *   `windSpeed`, `airPressure` (float): Kecepatan angin dan tekanan udara.
    *   `location` (varchar): **Kelemahan Utama**. Hanya menyimpan nama lokasi sebagai string (default 'Gazipur'). Tidak ada koordinat geografis.
    *   `createAt` (timestamp): Waktu data dimasukkan ke server.
*   **Analisis Kritis**: Tabel ini **tidak memadai** untuk sistem IoT modern karena:
    1.  Tidak ada `station_id` untuk membedakan banyak perangkat.
    2.  Tidak ada `observation_date` dari sisi sensor (hanya waktu server), menyebabkan ketidakakuratan jika ada latensi jaringan.
    3.  Tipe data `isRaining` terlalu sederhana.

#### C. Tabel `users` & `otp`
*   **Tujuan**: Manajemen identitas dan autentikasi pengguna.
*   **Struktur**:
    *   `users`: `username`, `password` (hashed), `email`, `role`.
    *   `otp`: `email`, `otp` (kode 6 digit), `createAt`.
*   **Relasi**: Tabel `users` memiliki foreign key ke `otp` pada kolom `email`. Ini desain yang tidak biasa (biasanya relasi ke `user_id`), namun fungsional untuk verifikasi email sederhana.

---

## BAGIAN 2: Perbandingan dengan Perencanaan Sistem v2.0.0

Bagian ini membandingkan skema saat ini dengan kebutuhan arsitektur baru (v2.0.0) yang berbasis MQTT dan Multi-Station.

### 1. Identifikasi & Metadata Stasiun
| Fitur | Skema Saat Ini (`weather_data`) | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Identitas Perangkat** | Tidak ada (hanya kolom `location` string) | **Station ID** (e.g., "TX001") | ❌ **Kritis** |
| **Metadata Gateway** | Tidak ada | **Gateway ID** (e.g., "GW_01") | ❌ Perlu Ditambah |
| **Geo-Lokasi** | Nama Kota (String) | **Latitude, Longitude, Elevasi** | ❌ Perlu Ditambah |
| **Status Perangkat** | Tidak ada | **Last Seen, Battery Level** | ❌ Perlu Ditambah |

### 2. Data Observasi & Sensor
| Fitur | Skema Saat Ini | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Presisi Waktu** | `createAt` (Waktu Server) | **Observation Date** (ISO 8601 dari Sensor) | ❌ Perlu Ditambah |
| **Curah Hujan** | `isRaining` (Boolean) | **Rain Level** (Analog 0-1023 / mm) | ⚠️ Perlu Upgrade |
| **Kualitas Sinyal** | Tidak ada | **RSSI & SNR** (Metrik LoRa) | ❌ Perlu Ditambah |
| **Unit Standar** | Implisit | **UN/CEFACT Codes** (Metadata) | ℹ️ Perlu Dokumentasi |

### 3. Integrasi Eksternal & Prediksi
| Fitur | Skema Saat Ini | Kebutuhan v2.0.0 | Status |
| :--- | :--- | :--- | :--- |
| **Data Pembanding** | Tidak ada | **External Forecasts** (API OpenSource) | ❌ Perlu Tabel Baru |
| **Hasil Prediksi** | Tidak ada (Hanya di memori Python) | **Weather Predictions** (Disimpan di DB) | ❌ Perlu Tabel Baru |

---

## BAGIAN 3: Rencana Migrasi & Aksi

Berdasarkan analisis di atas, skema database perlu direstrukturisasi secara signifikan. Kami tidak menyarankan memodifikasi file `weather_app_bd.sql` secara langsung karena berisi data historis yang berharga.

**Strategi Migrasi:**

1.  **Buat File Baru**: `weather_iot_v2.sql` (atau gunakan DBML yang telah didesain).
2.  **Migrasi Tabel Pendukung**: Salin struktur tabel `users` dan `otp` karena masih relevan untuk autentikasi dashboard.
3.  **Arsipkan Tabel Lama**: Biarkan `historical_dataset` sebagai tabel referensi untuk pelatihan model ML (jangan dihapus).
4.  **Implementasi Tabel Baru**:
    *   `stations`: Untuk mendaftarkan perangkat keras (Transmitter & Gateway).
    *   `weather_observations`: Tabel utama untuk data time-series dari MQTT, dengan kolom lengkap (`station_id`, `rssi`, `snr`, `rain_analog`, dll).
    *   `external_forecasts`: Untuk menyimpan data dari OpenWeatherMap/BMKG.
    *   `weather_predictions`: Untuk menyimpan hasil output model ML agar bisa ditampilkan di dashboard tanpa re-running model setiap saat.

Dokumen ini menjadi landasan teknis untuk implementasi database yang akan mendukung skalabilitas dan fitur real-time dari sistem Weather IoT v2.0.0.
