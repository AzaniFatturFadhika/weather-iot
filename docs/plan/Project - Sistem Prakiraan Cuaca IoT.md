---
title: "Ringkasan artikel cuaca"
source: "https://chatgpt.com/c/6901c1ec-c8f4-8320-bf51-ea47d38f8178"
author:
  - "[[ChatGPT]]"
published:
created: 2025-10-29
description: "ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster."
tags:
  - "clippings"
---
---
# Artikel

Link: [IoT-driven real-time weather measurement and forecasting mobile application with machine learning integration](https://1drv.ms/b/c/d6e5b2511990e088/ERuTKaPTL6pAsIkzySPnFzkBPD5N59BMpAyMX-guLt9llw?e=0FMG3L)

<iframe src="https://1drv.ms/b/c/d6e5b2511990e088/IQQbkymj0y-qQLCJM8kj5xc5Af5b2QoyoNyABRk1gkKs7bQ?em=2" width="476px" height="288px" frameborder="0">Ini adalah PDF <a target="_blank" href="https://office.com">Microsoft Office</a> yang disematkan, didukung oleh <a target="_blank" href="https://office.com/webapps">Office</a>.</iframe>

---
# Ringkasan Artikel

---
Berikut ringkasan singkat artikel:

**Topik & Latar Belakang**  
Aplikasi prakiraan cuaca umum sering kurang akurat di level lokal karena bergantung pada stasiun cuaca yang jauh dan parameter lingkungan yang terbatas. Artikel ini menawarkan solusi terintegrasi IoT + machine learning (ML) untuk pengukuran dan peramalan cuaca secara _real-time_ dan sangat lokal.

**Kontribusi Utama**

- Membangun stasiun cuaca IoT berbiaya rendah (± 8.865 BDT ≈ USD 73,88) dengan sensor suhu–kelembapan (DHT21), tekanan (BMP180), kecepatan angin (anemometer), intensitas cahaya (LDR), dan hujan.
    
- Komunikasi data jarak jauh hemat daya menggunakan **LoRa** (RA-02) dari node sensor (Arduino Uno) ke penerima (ESP32).
    
- Aplikasi **mobile Flutter** menampilkan data _real-time_, grafik, mode gelap, notifikasi ambang batas, serta peramalan berbasis ML.
    
- Backend **FastAPI** + **MySQL** dengan 9 endpoint (registrasi/OTP, login, reset sandi, input/pengambilan data sensor, data grafik, hingga prediksi).
    
- Pendekatan **Incremental Learning** agar model terus beradaptasi dengan data baru dan meningkatkan akurasi seiring waktu.
    
- Perbandingan prakiraan lokal vs prakiraan Google untuk menunjukkan keunggulan pemasangan sensor setempat.
    

**Data & Pra-proses**  
Data historis harian (2000–Apr 2024) diambil dari Visual Crossing dan digabung data sensor lokal; dilakukan pembersihan kolom, penanganan nilai hilang (termasuk _imputation_ median untuk tekanan), standarisasi format tanggal, serta **label encoding** untuk deskripsi kondisi cuaca.

**Pemodelan & Evaluasi**

- Model regresi yang diuji: Linear Regression, Decision Tree, KNN, dan **Random Forest** (terbaik).
    
- Metrik: MSE, MAE, RMSE, dan R². Random Forest mencapai R² ≈ **0,91** untuk suhu; performa baik juga pada kelembapan (R² ≈ 0,88), kecepatan angin (≈ 0,87), dan tekanan (≈ 0,89).
    
- Uji harian (24 jam) dan 7-hari menunjukkan jejak prediksi model yang dekat dengan data sensor lokal dan lebih representatif dibanding prakiraan umum Google untuk lokasi yang sama.
    

**Implementasi Sistem**

- Arsitektur dua unit: pemancar (Arduino + sensor + LoRa) dan penerima (ESP32 + LoRa) lalu diteruskan ke server lokal; tidak bergantung Internet, cocok untuk daerah minim infrastruktur.
    
- Aplikasi Flutter menyediakan pencarian stasiun, ringkasan kondisi (mis. logika sederhana “sunny/rainy”), tabel/diagram, dan notifikasi _real-time_.
    

**Dampak & Manfaat**  
Solusi ini meningkatkan ketepatan cuaca lokal untuk pengambilan keputusan di sektor seperti pertanian, logistik, energi terbarukan, dan kesiapsiagaan bencana — sekaligus skalabel dan ekonomis.

**Keterbatasan & Rencana Lanjut**  
Saat ini implementasi berfokus di Gazipur (Bangladesh) sehingga generalisasi lintas iklim masih terbatas. Ke depan: memperluas jaringan stasiun di berbagai wilayah, memperkaya data, mengeksplor model ML yang lebih kuat dalam kerangka _incremental learning_, dan menambah fitur aplikasi berdasarkan umpan balik pengguna.

---
# Arsitektur Sistem

---
Berikut rancangan arsitektur sistem lengkap—disesuaikan dengan implementasi v2.0.0 yang menggunakan standar industri (Schema.org), komunikasi MQTT, dan sensor presisi tinggi.

## 1) Ringkasan Arsitektur v2.0.0

- **Node Sensor (Transmitter)**: Arduino Nano + modul LoRa (SX1278/RA-02) membaca **AHT20 (suhu-kelembapan), BMP280 (tekanan), Anemometer (kecepatan angin), Rain sensor, LDR**. Data dikirim via LoRa dengan validasi CRC8.
    
- **Gateway**: **ESP32-S3** menerima paket LoRa, melakukan validasi, sinkronisasi waktu (NTP), dan mempublikasikan data via **MQTT** ke broker.
    
- **Broker**: **EMQX** (atau broker MQTT publik/lokal lainnya) sebagai perantara pesan.
    
- **Backend/Subscriber**: Layanan yang subscribe ke topik MQTT untuk menyimpan data ke database (MySQL/PostgreSQL) dan melayani API.
    
- **Aplikasi**: **Flutter** (Android) atau Dashboard Web yang mengambil data real-time via MQTT atau API.
    
- **Standar Data**: Menggunakan format JSON-LD **Schema.org/WeatherObservation** dengan kode unit UN/CEFACT.

## 2) Diagram Arsitektur (Logis)

```
[Node Sensor (Arduino Nano)]
  ├─ AHT20 (I2C) ──┐
  ├─ BMP280 (I2C) ─┤
  ├─ Anemometer (Analog)
  ├─ Rain sensor (Digital)
  └─ LDR (Analog)  └─> [Modul LoRa (SX1278)]
                         ↓ LoRa 433MHz (CRC8 Checked)
                   [Gateway ESP32-S3 + LoRa]
                         ↓ WiFi
                   [MQTT Broker (EMQX)]
                         ↓
            ┌────────────┴─────────────┐
            ↓                          ↓
    [Backend Service]            [Mobile App]
    (Storage & API)            (Realtime Monitor)
```

## 3) Diagram Deployment (Fisik)

```
[Lapangan - Station 1..N]
  ├─ Transmitter Unit (IP65 Box)
  │   └─ Arduino Nano + Sensors + LoRa
  └─ Power: Solar Panel + Battery 18650

[Base Station / Indoor]
  └─ Gateway Unit
      └─ ESP32-S3 + LoRa + WiFi

[Cloud / Server]
  └─ MQTT Broker
  └─ Database & API Server
```

## 4) Desain Tiap Lapisan & Keputusan Teknis

**Perangkat Lapangan (Transmitter)**

- **MCU**: Arduino Nano (ATmega328P). Dipilih karena hemat daya, murah, dan cukup untuk akuisisi data sensor dasar.
- **Sensor Utama**: 
    - **AHT20**: Akurasi tinggi untuk suhu & kelembapan (pengganti DHT).
    - **BMP280**: Tekanan udara presisi.
- **Komunikasi**: LoRa Point-to-Point dengan protokol kustom (Struct data + CRC8 checksum) untuk efisiensi dan integritas data.

**Gateway**

- **MCU**: ESP32-S3. Dual core, WiFi+Bluetooth, performa tinggi untuk handle LoRa packet processing dan koneksi MQTT stabil.
- **Fungsi**: 
    - Menerima raw packet LoRa.
    - Validasi checksum.
    - Menambahkan timestamp (NTP) dan geolokasi stasiun.
    - Konversi ke format JSON Schema.org.
    - Publish ke topik MQTT `weather/station/data`.

**Protokol Data**

- **Format**: JSON-LD (Lightweight Linked Data).
- **Standar**: Schema.org `WeatherObservation`.
- **Unit**: UN/CEFACT (e.g., `CEL` untuk Celsius, `P1` untuk Persen).

## 5) Estimasi Biaya (IDR, Estimasi 2025)

### 5.1 Bill of Materials – **Transmitter (1 unit)**

| Komponen | Estimasi Harga (IDR) | Catatan |
| :--- | :--- | :--- |
| Arduino Nano V3 (Type-C/Mini USB) | 45.000 - 60.000 | Clone CH340 umum digunakan |
| LoRa SX1278 RA-02 (433MHz) | 65.000 - 80.000 | Jangkauan jauh |
| AHT20 + BMP280 Module | 35.000 - 50.000 | Sering dijual dalam satu modul combo |
| Anemometer (Analog Voltage) | 150.000 - 450.000 | Varian budget (plastik) |
| Rain Sensor (FC-37) | 10.000 | Deteksi hujan simpel |
| LDR Module | 5.000 | Intensitas cahaya |
| Baterai 18650 x2 + Holder | 50.000 | Power supply |
| Box X6 / IP65 Enclosure | 25.000 - 50.000 | Pelindung cuaca |
| **Total Estimasi** | **~Rp 400.000 - 700.000** | Tergantung kualitas enclosure & sensor angin |

### 5.2 **Gateway** (1 unit)

| Komponen | Estimasi Harga (IDR) | Catatan |
| :--- | :--- | :--- |
| ESP32-S3 DevKit | 90.000 - 120.000 | Performa tinggi |
| LoRa SX1278 RA-02 | 65.000 - 80.000 | |
| PCB / Breadboard & Kabel | 20.000 | |
| Adaptor 5V | 25.000 | Power supply |
| **Total Estimasi** | **~Rp 200.000 - 250.000** | |

## 6) Alur Data (Flow)

1.  **Transmitter** membaca sensor setiap 10 detik (atau interval yang diatur).
2.  Data dikemas dalam `struct` C++ dan dihitung CRC8-nya.
3.  Paket dikirim via LoRa (433MHz).
4.  **Gateway** menerima paket, hitung ulang CRC8. Jika cocok:
    *   Ambil konfigurasi stasiun (Nama, Lokasi) dari Registry internal.
    *   Ambil waktu sekarang dari NTP Server.
    *   Format JSON sesuai standar.
5.  Gateway publish JSON ke MQTT Broker (Topik: `weather/station/data`).
6.  **Subscriber** (App/DB) menerima data real-time.

## 7) Praktik Terbaik yang Diterapkan

-   **Data Integrity**: Penggunaan CRC8 mencegah data korup (noise) terproses.
-   **Interoperabilitas**: Format JSON Schema.org memungkinkan data mudah dikonsumsi sistem lain.
-   **Skalabilitas**: Arsitektur MQTT memungkinkan banyak subscriber tanpa membebani gateway.
-   **Reliabilitas**: Gateway otomatis reconnect WiFi/MQTT jika putus.