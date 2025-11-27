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
Berikut rancangan arsitektur sistem lengkap—disusun setia pada isi artikel (node sensor ber-LoRa, gateway ESP32, backend FastAPI+MySQL, app Flutter, prediksi cuaca Random Forest)—ditambah rincian estimasi biaya berbasis harga pasar Indonesia (Okt 2025).

## 1) Ringkasan arsitektur dari artikel

- **Node sensor**: Arduino UNO + modul LoRa (Ai-Thinker RA-02) membaca **anemometer (kecepatan angin), sensor hujan, DHT21/AM2301 (suhu-kelembapan), BMP180 (tekanan), LDR (cahaya)**. Data dikirim via LoRa.
    
- **Gateway**: **ESP32** menerima LoRa dari node dan meneruskan ke server melalui Wi-Fi.
    
- **Backend**: **FastAPI** (REST) + **MySQL** untuk koleksi & penyajian data; mengekspose endpoint ke aplikasi.
    
- **Aplikasi**: **Flutter** (Android) menampilkan realtime, histori & prediksi.
    
- **Prediksi**: **Random Forest** dipakai untuk peramalan cuaca; sistem dirancang agar **pembelajaran bertahap (incremental)** ketika data baru masuk.
    
- **Motivasi LoRa**: jangkauan jauh, biaya rendah, konsumsi daya kecil.
    

## 2) Diagram arsitektur (logis)

```
[Node Sensor (Arduino UNO)]
  ├─ DHT21  ──┐
  ├─ BMP180 ──┤
  ├─ Anemometer
  ├─ Rain sensor
  └─ LDR     └─> [Modul LoRa (RA-02)]
                     ↓ LoRa (sub-GHz)
               [Gateway ESP32 + LoRa]
                     ↓ Wi-Fi (HTTP)
             [FastAPI REST API Server]
                     ↓
         [MySQL] <-> [Servis Prediksi RF]
                     ↓
               [Aplikasi Flutter]
         (Realtime, histori, prediksi)
```

## 3) Diagram deployment (fisik)

```
[Lapangan]
  ├─ 1..N Node Sensor + RA-02  ── LoRa ──┐
  └─ Tiang/Enclosure IP65              [Gateway ESP32 + LoRa + Antena]
                                        │ Wi-Fi/ETH
                                        ▼
[Infrastruktur]
  [VPS Indonesia] ─ Docker:
    - FastAPI (API & Auth)
    - Servis Prediksi (Random Forest)
    - MySQL (data meteorologi)
    - Reverse proxy + TLS
```

## 4) Desain tiap lapisan & keputusan teknis

**Perangkat lapangan (node)**

- **MCU**: Arduino UNO (sesuai artikel). **Catatan regulasi**: di Indonesia LoRaWAN menggunakan **AS923-2 (±920–923 MHz)**; RA-02 umumnya varian **433 MHz**. Untuk kepatuhan, disarankan mengganti ke modul LoRa **AS923-2/915 MHz (mis. RFM95/SX1276, REYAX RYLR8xx)** pada node & gateway. ([read.uberflip.com](https://read.uberflip.com/i/1540208/81?utm_source=chatgpt.com "Document - RP002-1.0.5 LoRaWAN Regional Parameters"))
    
- **Sensor**: anemometer (kecepatan angin), rain sensor, DHT21, BMP180, LDR; dirangkai pada shield/PCB dan dimasukkan ke **enclosure IP65**.
    

**Komunikasi**

- **LoRa point-to-point** dari node ke gateway (bukan LoRaWAN publik), laju data rendah, periodik. (Alternatif: LoRaWAN AS923-2 bila ingin pakai jaringan Telkom/Antares). ([docs.antares.id](https://docs.antares.id/en/contoh-kode-dan-library/register-perangkat-lorawan?utm_source=chatgpt.com "LoRaWAN Device Register | Antares"))
    

**Gateway**

- **ESP32 + modul LoRa**; firmware meneruskan payload via **HTTP** ke FastAPI (bisa ditambah **MQTT** opsional untuk skalabilitas).
    

**Backend**

- **FastAPI**: endpoint ingest (POST), query (GET), auth (JWT). **MySQL** menyimpan metrik waktu-nyata & histori; indeks per waktu & lokasi.
    
- **Servis Prediksi**: model **Random Forest** dilatih awal dari histori; **refit periodik** (harian/mingguan) memakai data terbaru (sesuai semangat incremental di artikel). Expose `/predict` untuk app.
    

**Aplikasi Flutter**

- Tiga layar inti: **Realtime** (terima data terkini), **Historis** (grafik), **Prediksi** (hasil RF).
    

**Keamanan & operasi**

- **TLS** end-to-end (gateway→server), **JWT** untuk app, **rotasi API key** perangkat.
    
- **Kalibrasi sensor** (angin/hujan), **backup DB** harian, **monitoring** (health, latensi, loss paket).
    
- **OTA** ke gateway ESP32 via Wi-Fi.
    

## 5) Estimasi biaya (IDR, harga Indonesia per Okt 2025)

> Harga bervariasi antar toko & kota; saya berikan **rentang & contoh tautan produk** sebagai rujukan.

### 5.1 Bill of Materials – **Node Sensor (1 unit)**

| Komponen                                           | Perkiraan Harga (IDR) | Sumber                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------------------- | --------------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Arduino UNO R3 kompatibel (CH340)                  |    **57.500–120.000** | Blibli Rp120.000 (Ori/CH340) ([Blibli](https://www.blibli.com/jual/ch7340?utm_source=chatgpt.com "Daftar Harga Ch7340 🔥 Original & Spesifikasi Lengkap Oktober 2025")); Sabira Rp57.500 (clone) ([Sabira Ads](https://sabira.id/ad/arduino-uno-r3-ch340-clone-kabel/?utm_source=chatgpt.com "Arduino Uno R3 CH340 Clone + Kabel - Sabira"))                                                                                                                     |
| **Modul LoRa** (pilihan):                          |                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| — Ai-Thinker **RA-02** (433 MHz)                   |           **±72.571** | Lazada ([Lazada Indonesia](https://www.lazada.co.id/products/lora-sx1278-ra02-433mhz-long-range-10km-transciever-module-i5724880238.html?utm_source=chatgpt.com "Lora SX1278 RA-02 433Mhz Long Range 10km Transciever Module \| Lazada Indonesia"))                                                                                                                                                                                                              |
| — **RFM95 / SX1276** (AS923-2/915 MHz, disarankan) |     **94.500–95.000** | Blibli ([Blibli](https://www.blibli.com/jual/lora-modul?utm_source=chatgpt.com "Daftar Harga Lora Modul 🔥 Original & Spesifikasi Lengkap Oktober 2025"))                                                                                                                                                                                                                                                                                                        |
| DHT21 / AM2301                                     |           **±50.000** | Blibli (SmartCase) ([monotaro.id](https://www.monotaro.id/k/store/Sensor%20Anemometer?utm_source=chatgpt.com "Beli Sensor Anemometer 100% Original \| monotaro.id"))                                                                                                                                                                                                                                                                                             |
| BMP180                                             |           **±89.000** | Blibli ([Ufuon](https://store.ufuon.com/product/dht21-am2301-temperature-and-humidity-sensor/65a642d800b6e7ecf1e79b6c?utm_source=chatgpt.com "DHT21 AM2301 Temperature and Humidity Sensor"))                                                                                                                                                                                                                                                                    |
| Sensor hujan **FC-37** (deteksi hujan)             |      **8.500–13.000** | Blibli/Tokopedia ([griyatekno.com](https://www.griyatekno.com/automation-sensor-c-65_133/rain-sensor-p-371.html?utm_source=chatgpt.com "Rain Sensor Module, Home Automation System, Smart Home, Building, Indonesia, Distributor - Rp720.000,00"))                                                                                                                                                                                                               |
| **Anemometer** (angin) – opsi:                     |                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| — Budget (sensor cup sederhana)                    |          **±165.000** | depoinovasi (Tokopedia) ([depoinovasi.co.id](https://depoinovasi.co.id/sensor-anemometer/?utm_source=chatgpt.com "Sensor Anemometer - Depoinovasi Electronics"))                                                                                                                                                                                                                                                                                                 |
| — Menengah (0–5 V analog)                          |          **±466.000** | Blibli Achernar ([monotaro.id](https://www.monotaro.id/k/store/Cup%20Anemometer?utm_source=chatgpt.com "Beli Cup Anemometer 100% Original \| monotaro.id"))                                                                                                                                                                                                                                                                                                      |
| — Pro (DC 5–24 V)                                  |        **±1.221.000** | Blibli Ajs&co ([FlipHTML5](https://fliphtml5.com/wtrlx/xpgu/EL.200_2425.01.033/?utm_source=chatgpt.com "EL.200_2425.01.033 - Carly Nainggolan \| PDF Online \| FlipHTML5"))                                                                                                                                                                                                                                                                                      |
| LDR / modul LDR                                    |       **1.500–8.000** | Blibli ([Blibli](https://www.blibli.com/jual/ldr-sensor-cahaya?utm_source=chatgpt.com "Jual Ldr Sensor Cahaya 💯 Harga Murah & Kualitas Terbaik Oktober 2025"))                                                                                                                                                                                                                                                                                                  |
| Buck converter **LM2596**                          |     **10.000–35.000** | Blibli/Ichibot ([Blibli](https://www.blibli.com/jual/stepdown-module-lm2596?utm_source=chatgpt.com "Jual Stepdown Module Lm2596 💯 Harga Murah & Kualitas Terbaik Oktober 2025"))                                                                                                                                                                                                                                                                                |
| **Enclosure IP65** (ABS/metal)                     |   **59.000–329.900+** | Lazada ABS IP65 Rp59k ([Lazada](https://h5.lazada.co.id/products/box-panel-listrik-ip65-waterproof-outdoor-abs-kotak-panel-listrik-box-terminal-i7905294824.html?utm_source=chatgpt.com "Box Panel Listrik IP65 Waterproof Outdoor ABS Kotak Panel Listrik Box Terminal \| Lazada Indonesia")); Monotaro IP65 metal Rp329.900+ ([monotaro.id](https://www.monotaro.id/k/store/panel%20box?utm_source=chatgpt.com "Beli panel box 100% Original \| monotaro.id")) |
| Baterai **18650 3000 mAh** (per sel)               |    **35.000–100.000** | Blibli (VTC6 & lain-lain) ([Blibli](https://www.blibli.com/jual/18650-3000-mah?utm_source=chatgpt.com "18650 3000 Mah Gratis Ongkir 🏷️ Harga Murah Oktober 2025"))                                                                                                                                                                                                                                                                                              |
| Antena LoRa **915 MHz** 3–5 dBi (untuk AS923)      |    **91.800–121.900** | Digiwarestore ([digiwarestore.com](https://digiwarestore.com/id/lora-lorawan/lora-antenna/?utm_source=chatgpt.com "LoRa Antenna - Digiware Store"))                                                                                                                                                                                                                                                                                                              |
| Kabel, PCB, konektor, ring logam                   |    **~35.000–50.000** | (estimasi pasar lokal)                                                                                                                                                                                                                                                                                                                                                                                                                                           |

**Contoh total per node**

- **Konfigurasi hemat (AS923 disarankan)**: UNO (80k) + RFM95 (95k) + DHT21 (50k) + BMP180 (89k) + FC-37 (8.5k) + Anemo budget (165k) + LDR (1.5k) + LM2596 (12k) + Enclosure ABS (59k) + kecil2 (35k) + 1×18650 (50k) + antena 915 MHz 3 dBi (91.8k) ≈ **Rp714.000**.
    
- **Konfigurasi tangguh outdoor**: enclosure IP65 metal, anemo menengah, 2×18650, antena fiberglass 7 dBi (opsi). Dengan pilihan mid di atas + enclosure IP65 (329.9k) + anemo 466k + baterai ekstra + antena 7 dBi (jika dipasang di gateway saja) total **≈ Rp1,40–1,60 juta** per node. (Perhitungan berbasis penjumlahan item ber-sumber di tabel di atas.)
    

### 5.2 **Gateway** (1 unit)

|Komponen|Estimasi|Sumber|
|---|--:|---|
|ESP32 DevKit|**74.000–133.200**|Blibli/Lazada/mbizmarket ([Blibli](https://www.blibli.com/jual/arduino-dip?utm_source=chatgpt.com "Arduino Dip Garansi Resmi Indonesia 🏷️ Harga Murah Oktober 2025"))|
|Modul LoRa (AS923, disarankan)|**94.500–95.000**|Blibli (RFM95) ([Blibli](https://www.blibli.com/jual/lora-modul?utm_source=chatgpt.com "Daftar Harga Lora Modul 🔥 Original & Spesifikasi Lengkap Oktober 2025"))|
|Antena LoRa outdoor **7 dBi fiberglass** (opsional, jangkauan)|**±1.403.000**|Digiwarestore ([digiwarestore.com](https://digiwarestore.com/id/lora-lorawan/lora-antenna/?utm_source=chatgpt.com "LoRa Antenna - Digiware Store"))|
|Enclosure IP65 (panel box)|**329.900–675.000**|Monotaro/Durabox ([monotaro.id](https://www.monotaro.id/k/store/panel%20box?utm_source=chatgpt.com "Beli panel box 100% Original \| monotaro.id"))|
|Adaptor 5 V/2 A + kabel|**~50.000**|(estimasi pasar lokal)|

**Contoh total**

- **Gateway hemat** (antena kecil 3–5 dBi, enclosure ABS): **≈ Rp350–450 ribu**.
    
- **Gateway outdoor** (antena fiberglass 7 dBi, panel box IP65): **≈ Rp1,9–2,1 juta**.
    

### 5.3 **Tenaga surya (opsional, per titik)**

|Item|Estimasi|Sumber|
|---|--:|---|
|**Panel surya 20 Wp**|**Rp275.000–370.000**|Blibli / PanelSuryaJakarta (harga 20 Wp) ([Blibli](https://www.blibli.com/jual/surya-20-wp?utm_source=chatgpt.com "Jual Surya 20 Wp 💯 Harga Murah & Kualitas Terbaik Oktober 2025"))|
|**Solar charge controller PWM 10 A**|**Rp65.000–138.000**|Lazada/Dinomarket ([Lazada Indonesia](https://www.lazada.co.id/products/solar-charge-controller-pwm-10a--20a--30a-lithium-12v--24v-i7216040421.html?utm_source=chatgpt.com "Solar Charge Controller PWM 10A / 20A / 30A Lithium 12V / 24V \| Lazada Indonesia"))|
|Aki 12 V 7 Ah (opsional, paket)|(paket 20 Wp+SCC+aki ± **Rp790.000**)|Lazada paket 20 Wp ([Lazada Indonesia](https://www.lazada.co.id/products/paket-solar-panel-surya-20wp-solar-controller-10a-aki-12v-7ah--sollare-i8675084974.html?utm_source=chatgpt.com "PAKET SOLAR PANEL SURYA 20WP, SOLAR CONTROLLER 10A, AKI 12V 7AH - sollare \| Lazada Indonesia"))|

### 5.4 **Server & Domain (bulanan)**

|Komponen|Estimasi|Sumber|
|---|--:|---|
|**VPS Indonesia ~2 vCPU/2 GB**|**Rp149.000–180.000 / bulan**|IDCloudHost, Cloudmatika ([IDCloudHost](https://idcloudhost.com/en/cloud-vps/?utm_source=chatgpt.com "Cloud VPS Indonesia - Auto Scale Up & Murah \| IDCloudhost"))|
|**Domain .my.id**|**Rp30.000–50.000 / tahun** (promo sering ada)|BuyCloud, info PANDI 2024/25 ([BuyCloud](https://www.buycloud.id/domain/name/my.id?utm_source=chatgpt.com "Murah! Promo Domain MY.ID Oktober 2025 Rp 30,000"))|

**Contoh TCO awal** (tanpa tenaga surya):

- **5 node (hemat) + 1 gateway hemat + 1 bulan VPS + domain** ≈ **Rp4,1 juta**.
    
- **5 node (outdoor) + 1 gateway outdoor + 1 bulan VPS + domain** ≈ **Rp9,1 juta**.  
    (Angka dibulatkan dari penjumlahan item-item pada tabel sumber di atas.)
    

## 6) Alur data & API (tanpa kode)

1. **Node** sampling (mis. tiap 1–5 menit) → paket **LoRa** (timestamp, id, nilai sensor).
    
2. **Gateway ESP32** decode & kirim **HTTP POST** ke **FastAPI** (payload JSON + API-key perangkat).
    
3. **FastAPI** validasi → tulis ke **MySQL** (tabel readings, stations, sensors).
    
4. **Servis Prediksi** tarik data histori → **Random Forest** → simpan output (tabel forecasts).
    
5. **Flutter app** memanggil endpoint `/realtime`, `/history`, `/predict`.
    

## 7) Non-fungsional & praktik terbaik

- **Kepatuhan frekuensi**: gunakan **AS923-2 (921.4–922.0 MHz, dsb.)** sesuai praktik Indonesia; rujukan LoRa Alliance & Helium/Antares. ([read.uberflip.com](https://read.uberflip.com/i/1540208/81?utm_source=chatgpt.com "Document - RP002-1.0.5 LoRaWAN Regional Parameters"))
    
- **Keandalan**: retry di gateway, queue ringan (mis. buffer RAM/flash), **watchdog**.
    
- **Monitoring**: metrik ingest (RPS, latency), packet loss LoRa, status node.
    
- **Skala**: multi-gateway (overlap coverage), **sharding** DB per lokasi, cache baca (Redis).
    
- **Keamanan**: TLS, JWT, rotasi key, rate-limit, firewall VPS.
    
- **Kalibrasi**: anemometer & hujan → tabel faktor kalibrasi; verifikasi lapangan berkala.
    
- **Backup**: dump MySQL harian; retensi 30–90 hari.
    

---

**Catatan akhir**

- Arsitektur di atas **mengikuti struktur artikel (LoRa→ESP32→FastAPI/MySQL→Flutter→RF)** dan disesuaikan untuk pasar Indonesia (band **AS923-2** & harga komponen lokal).
    
- Jika Anda ingin, saya bisa turunkan ke **arsitektur fisik rinci** (layout PCB, wiring pin, daftar endpoint REST, skema tabel MySQL) **tanpa kode** dalam iterasi berikut.