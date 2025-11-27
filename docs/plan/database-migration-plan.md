# Analisis Skema Database & Rencana Migrasi

## 1. Analisis `examples/db_init/weather_app_bd.sql`

File SQL yang disediakan tampaknya merupakan dump dari database MySQL bernama `ml`. File ini memiliki dua tujuan utama: menyimpan dataset historis untuk machine learning dan menyediakan backend untuk aplikasi web cuaca sederhana.

### Tabel yang Ada

#### 1. `historical_dataset`

* **Tujuan**: Menyimpan data cuaca harian yang dikumpulkan (agregat), kemungkinan digunakan untuk melatih model Random Forest yang disebutkan dalam rencana proyek.
* **Struktur**: `id`, `day`, `month`, `year`, `tempmax`, `tempmin`, `temp`, `humidity`, `windspeed`, `sealevelpressure`, `conditions` (teks).
* **Data**: Berisi ~8.000 rekaman data cuaca harian historis (2021-2024).
* **Penilaian**: Tabel ini **berharga untuk pelatihan ML** tetapi **tidak cocok untuk pemantauan IoT real-time**. Tabel ini kurang presisi waktu (hanya harian), tidak ada identifikasi stasiun, dan tidak menyimpan nilai sensor mentah.

#### 2. `weather_data`

* **Tujuan**: Menyimpan observasi cuaca langsung (live) untuk dashboard web.
* **Struktur**: `id`, `temp`, `humidity`, `isRaining` (boolean), `lightIntensity`, `windSpeed`, `airPressure`, `location` (varchar), `createAt` (timestamp).
* **Penilaian**: Tabel ini lebih mendekati kebutuhan tetapi **tidak memadai untuk v2.0.0**.
  * **Kurang `stationID`**: Tidak dapat membedakan antara beberapa stasiun pemancar.
  * **Kurang koordinat `location`**: Menggunakan string nama kota sederhana ('Gazipur') alih-alih Latitude/Longitude.
  * **Fidelitas Data**: `isRaining` hanya boolean, sedangkan sistem baru dapat memberikan tingkat hujan analog.
  * **Waktu**: Mengandalkan `createAt` (waktu penyisipan server) daripada `observationDate` aktual dari sensor.

#### 3. `users` & `otp`

* **Tujuan**: Sistem autentikasi dasar (Username/Password + OTP).
* **Struktur**: Kredensial pengguna standar dan penyimpanan OTP.
* **Penilaian**: Dapat digunakan kembali untuk autentikasi dashboard web.

---

## 2. Analisis Kesenjangan (Kebutuhan v2.0.0 vs Skema Saat Ini)

| Kebutuhan                        | `weather_data` Saat Ini   | Kebutuhan v2.0.0                                 | Tindakan                    |
| :------------------------------- | :-------------------------- | :----------------------------------------------- | :-------------------------- |
| **Dukungan Multi-Stasiun** | Tidak (hanya `id`)        | `stationID` (misal: "TX001")                   | **Tambah Kolom**      |
| **Geo-Lokasi**             | `location` (String)       | `latitude`, `longitude`, `elevation`       | **Tambah Kolom**      |
| **Waktu Presisi**          | `createAt` (Waktu Server) | `observationDate` (Waktu Sensor)               | **Tambah Kolom**      |
| **Spesifikasi Sensor**     | Kolom generik               | Metadata (Model Sensor, Kode Unit)               | **Tambah JSON/Kolom** |
| **Integritas Data**        | Tidak ada                   | `checksum`, `rssi`, `snr` (Statistik LoRa) | **Tambah Kolom**      |

---

## 3. Rencana Migrasi

Kami merekomendasikan pembuatan skrip SQL baru `weather_iot_v2.sql` yang mempertahankan kemampuan ML sambil mengaktifkan pemantauan IoT yang kuat.

### Langkah 1: Pertahankan `historical_dataset`

Biarkan tabel ini apa adanya untuk komponen Machine Learning.

### Langkah 2: Buat Tabel `stations` (Baru)

Untuk mengelola konsep "Station Registry" yang dijelaskan dalam arsitektur.

```sql
CREATE TABLE `stations` (
    `station_id` VARCHAR(50) PRIMARY KEY, -- misal: 'TX001'
    `name` VARCHAR(100),
    `latitude` DECIMAL(10, 8),
    `longitude` DECIMAL(11, 8),
    `elevation` FLOAT,
    `is_active` BOOLEAN DEFAULT TRUE,
    `last_seen` TIMESTAMP
);
```

### Langkah 3: Upgrade `weather_data` (atau Buat `weather_observations`)

Kami mengusulkan pembuatan tabel baru `weather_observations` untuk menghindari kerusakan kompatibilitas aplikasi lama, atau mengubah `weather_data` jika dukungan lama tidak diperlukan.

**Usulan Tabel `weather_observations`:**

```sql
CREATE TABLE `weather_observations` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `station_id` VARCHAR(50),
    `observation_date` DATETIME NOT NULL, -- Dari payload MQTT
    `temperature` FLOAT, -- Celsius
    `humidity` FLOAT, -- %
    `pressure` FLOAT, -- hPa
    `wind_speed` FLOAT, -- m/s
    `rain_level` FLOAT, -- Nilai analog atau mm
    `light_lux` FLOAT, -- Lux
    `uv_index` FLOAT,
    `rssi` INT, -- Kekuatan Sinyal LoRa
    `snr` FLOAT, -- Signal to Noise LoRa
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`station_id`) REFERENCES `stations`(`station_id`)
);
```

### Langkah 4: Update `users` (Opsional)

Pastikan tabel `users` memiliki peran yang sesuai untuk `admin` (dapat mengelola stasiun) dan `viewer` (hanya baca).

## 4. Langkah Selanjutnya

1. **Persetujuan**: Konfirmasi apakah kita harus memodifikasi file yang ada atau membuat file `v2` baru.
2. **Implementasi**: Hasilkan file skema SQL baru.
