# Panduan Cepat: Menambah Transmitter Baru

## 📍 Skenario
Anda ingin menambah transmitter keempat (TX004) di Kec. Mijen.

## ⚡ Langkah Singkat

### 1. Update Gateway Registry
Buka `gateway_optimized/gateway_optimized.ino`, cari bagian `stationRegistry[]` (sekitar baris 60):

```cpp
StationConfig stationRegistry[] = {
  {
    "TX001",
    "Kec. Semarang Utara",
    -6.9600, 110.4200, 10.0,
    {"AHT20", "BMP280", "Anemometer", "Raindrop", "LDR"},
    5
  },
  {
    "TX002",
    "Kec. Semarang Barat",
    -6.9850, 110.3950, 15.0,
    {"DHT22", "BMP280", "Rain gauge", "LDR"},
    4
  },
  {
    "TX003",
    "Kec. Genuk",
    -6.9450, 110.4500, 5.0,
    {"AHT20", "UV", "LDR", "Raindrop"},
    4
  },
  // ← TAMBAHKAN ENTRY BARU DI SINI
  {
    "TX004",                         // ← ID baru
    "Kec. Mijen",                    // ← Nama lokasi
    -6.9750, 110.3550, 20.0,         // ← Lat, Lon, Elevasi
    {"AHT20", "BMP280", "Anemometer", "LDR"},  // ← Daftar sensor
    4                                // ← Jumlah sensor
  }
};

const int STATION_COUNT = 4;  // ← UPDATE dari 3 ke 4
```

### 2. Upload Gateway
- Compile & Upload `gateway_optimized.ino` ke ESP32-S3
- Tunggu sampai selesai

### 3. Setup Transmitter
Buka `transmitter_optimized/transmitter_optimized.ino`, ubah ID:

```cpp
const String DEVICE_ID = "TX004";  // ← Ubah dari TX001
```

Upload ke Arduino Nano baru.

### 4. Test
```bash
# Subscribe MQTT
mosquitto_sub -h broker.emqx.io -p 1883 -u emqx -P public \
  -t "weather/station/data" -v | jq 'select(.stationID == "TX004")'
```

Dalam 10 detik, data TX004 akan muncul dengan lokasi Kec. Mijen! ✅

---

## 🗺️ Cara Mendapatkan Koordinat GPS

### Google Maps
1. Buka https://maps.google.com
2. Klik kanan di lokasi transmitter
3. Pilih koordinat yang muncul
4. Copy latitude dan longitude

### Format
```
Contoh: -6.9750, 110.3550
         ↑        ↑
      Latitude  Longitude
```

---

## ⚠️ Checklist

- [ ] Entry baru ditambahkan di `stationRegistry[]`
- [ ] `STATION_COUNT` di-update (tambah 1)
- [ ] Latitude, Longitude, Elevation benar
- [ ] Daftar sensor sesuai hardware transmitter
- [ ] `sensorCount` sama dengan jumlah nama sensor
- [ ] Gateway di-upload ke ESP32
- [ ] Transmitter DEVICE_ID diubah
- [ ] Transmitter di-upload ke Arduino Nano
- [ ] Test dengan MQTT subscribe

---

**Total waktu: ~5 menit** ⏱️
