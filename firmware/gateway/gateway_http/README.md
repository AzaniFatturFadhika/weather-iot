# Gateway Firmware - Penjelasan Program

## 📋 Deskripsi Umum

Program ini adalah **Gateway** untuk sistem monitoring cuaca berbasis IoT. Gateway berfungsi sebagai **penerima data** dari transmitter via LoRa dan **pengirim data** ke backend server melalui protokol HTTP.

## 🔧 Hardware yang Digunakan

- **Mikrokontroler**: ESP32-S3
- **Modul Komunikasi**: LoRa SX1278 RA-02 (433MHz)
- **LED Indikator**:
  - LED Built-in (Pin 48): Status WiFi
  - LED LoRa (Pin 4): Indikator penerimaan data LoRa

## 📡 Pin Configuration (ESP32-S3)

```cpp
LORA_SCK   = 12  // SPI Clock
LORA_MISO  = 13  // SPI MISO
LORA_MOSI  = 11  // SPI MOSI
LORA_SS    = 10  // SPI Chip Select
LORA_RST   = 8   // Reset
LORA_DIO0  = 9   // DIO0 (untuk interrupt)
```

## 🌐 Konfigurasi WiFi & Backend

```cpp
WiFi SSID: "KelompokCuaca"
Password: "esTeHangetSegar"

Backend Primary: https://api.azanifattur.biz.id
Backend Secondary: https://api.wrseno.my.id
```

**Dual Endpoint**: Gateway mengirim data ke **2 endpoint sekaligus** untuk redundansi dan backup.

---

## 🔄 Alur Kerja Program

### 1. **Setup (Inisialisasi)**

```cpp
void setup()
```

- Inisialisasi Serial Monitor (115200 baud)
- Setup LED indikator
- **Inisialisasi LoRa** dengan konfigurasi Long Range:
  - Spreading Factor: 12 (jarak maksimal)
  - Bandwidth: 125kHz
  - Coding Rate: 4/8 (koreksi error maksimal)
  - Tx Power: 20 dBm
  - Sync Word: 0x12
- **Koneksi WiFi** ke access point
- **Sinkronisasi waktu** dengan NTP server (UTC+7/WIB)

### 2. **Loop Utama**

```cpp
void loop()
```

1. **Monitor koneksi WiFi** - reconnect jika terputus
2. **Cek paket LoRa** masuk dengan `LoRa.parsePacket()`
3. **Retry pengiriman** data yang gagal setiap 10 detik

### 3. **Penerimaan Data LoRa**

```cpp
void handleLoRaPacket(int packetSize)
```

**Format Data yang Diterima:**

```
DEVICE_ID|temp|hum|press|wind|rain|light|CRC
Contoh: TX001|28.50|75.30|1010.25|5.20|0|512|A3
```

**Proses:**

1. **Baca paket** dari buffer LoRa
2. **Cek RSSI & SNR** untuk kualitas sinyal
3. **Validasi CRC** (XOR checksum):
   - Hitung checksum dari payload
   - Bandingkan dengan CRC yang diterima
   - Tolak paket jika tidak cocok
4. **Parse data** dengan delimiter `|`:
   - [0] Device ID
   - [1] Temperature (°C)
   - [2] Humidity (%)
   - [3] Pressure (hPa)
   - [4] Wind Speed (km/h)
   - [5] Rain Level (0=Dry, 1=Wet)
   - [6] Light Level (0-1023)
5. **Simpan ke buffer** dan kirim ke backend
6. **Nyalakan LED** saat proses (indikator visual)

### 4. **Pengiriman Data ke Backend**

```cpp
int sendToAllEndpoints(...)
bool sendToEndpoint(const char* backendUrl, ...)
```

**Proses Multi-Endpoint:**

1. **Loop untuk setiap endpoint** (2 endpoint)
2. **Construct URL** dengan query parameters:
   ```
   /weather-data/create?temp=28.5&humidity=75&pressure=1010&windSpeed=5.2&isRaining=0&lightIntensity=512
   ```
3. **HTTP GET Request** dengan timeout 10 detik
4. **Tracking keberhasilan**:
   - Count jumlah endpoint yang berhasil
   - Return total sukses (0-2)
5. **Retry jika gagal total** (buffer data untuk retry 10s kemudian)

**Serial Output:**

```
--- Sending to Multiple Endpoints ---
[Endpoint 1/2] https://api.azanifattur.biz.id
  URL: https://api.azanifattur.biz.id/weather-data/create?...
  Response: 200 - {"status":"success"}
  ✓ Success
[Endpoint 2/2] https://api.wrseno.my.id
  URL: https://api.wrseno.my.id/weather-data/create?...
  Response: 200 - {"status":"success"}
  ✓ Success
--- Total: 2/2 endpoints succeeded ---
```

---

## 🔒 Keamanan Data

### CRC Checksum Validation

- Menggunakan **XOR checksum** untuk deteksi corrupt data
- Formula: `CRC = byte1 XOR byte2 XOR ... XOR byteN`
- Paket ditolak jika CRC tidak cocok

### Retry Mechanism

- Data disimpan dalam buffer jika pengiriman gagal
- Retry otomatis setiap 10 detik
- Buffer cleared setelah minimal 1 endpoint berhasil

---

## 📊 Monitoring & Debugging

### Serial Output

Program menampilkan informasi detail:

- Status koneksi WiFi & IP address
- Data LoRa yang diterima (raw + parsed)
- RSSI & SNR setiap paket
- Status CRC validation
- URL dan response dari setiap endpoint
- Success/failure rate

### LED Indicators

- **LED Built-in (Pin 48)**: ON = WiFi Connected
- **LED LoRa (Pin 4)**: Blink saat menerima & memproses paket

---

## ⚙️ Konfigurasi Lanjutan

### Menambah Endpoint Ketiga

```cpp
const char* BACKEND_URL_3 = "https://your-third-server.com";
const char* BACKEND_URLS[] = {BACKEND_URL_1, BACKEND_URL_2, BACKEND_URL_3};
const int NUM_ENDPOINTS = 3;
```

### Mengubah Interval Retry

```cpp
const unsigned long SEND_RETRY_INTERVAL_MS = 10000; // dalam miliseconds
```

### Mengubah Timeout HTTP

```cpp
http.setTimeout(10000); // 10 detik (di dalam sendToEndpoint)
```

---

## 📝 Catatan Penting

1. **Sinkronisasi dengan Transmitter**: Interval retry (10s) harus sama dengan interval transmit di transmitter
2. **Memory Management**: Buffer hanya menyimpan 1 set data terbaru
3. **Network Resilience**: Sistem akan retry sampai minimal 1 endpoint berhasil
4. **LoRa Configuration**: Harus **SAMA PERSIS** dengan transmitter (SF, BW, CR, SyncWord)

---

## 🐛 Troubleshooting

| Problem               | Solution                                          |
| --------------------- | ------------------------------------------------- |
| WiFi tidak terkoneksi | Cek SSID & password, pastikan dalam jangkauan     |
| Data tidak diterima   | Cek konfigurasi LoRa (harus sama dengan TX)       |
| CRC Mismatch          | Noise/interference tinggi, perbaiki antena/posisi |
| HTTP timeout          | Cek koneksi internet, ping backend server         |
| Endpoint failed       | Cek server status, log backend untuk detail error |

---

**Developer**: IoT Weather Monitoring Team  
**Last Updated**: December 2025  
**Version**: 2.0 (Dual Endpoint Support)
