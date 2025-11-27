# Weather Station Data Format - Industry Standard Implementation

## 📊 Perubahan Format Data

### **TRANSMITTER (Optimized + Validated)**
Tidak ada perubahan pada protokol LoRa. Data tetap menggunakan pipe-delimited format untuk efisiensi bandwidth:
```
TX001|28.5|65.2|1013.25|5.2|100|800
```

**Peningkatan:**
- ✅ Range validation untuk semua sensor
- ✅ Sensor identification dalam debug output

---

### **GATEWAY (Optimized + Normalized)**
Gateway kini melakukan normalisasi data lengkap sesuai standar industri.

#### **Format JSON Sebelum:**
```json
{
  "device_id": "TX001",
  "timestamp": 123456,
  "temperature": 28.5,
  "humidity": 65.2,
  "pressure": 1013.25,
  "wind_speed": 5.2,
  "rain_level": 100,
  "light_level": 800,
  "signal": {"rssi": -45, "snr": 9.5}
}
```

#### **Format JSON Sesudah (Industry Standard):**
```json
{
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "gatewayID": "ESP32_Gateway_001",
  "stationName": "Weather Station Surabaya",
  "observationTime": "2025-11-23T11:04:55+07:00",
  "location": {
    "latitude": -7.2575,
    "longitude": 112.7521,
    "elevation": 3.0
  },
  "temperature": {
    "value": "28.50",
    "unit": "celsius",
    "sensor": "AHT20"
  },
  "humidity": {
    "value": "65.20",
    "unit": "percent",
    "sensor": "AHT20"
  },
  "pressure": {
    "value": "1013.25",
    "unit": "hPa",
    "sensor": "BMP280"
  },
  "windSpeed": {
    "value": "5.20",
    "unit": "km/h",
    "sensor": "Anemometer"
  },
  "precipitation": {
    "rawLevel": 100,
    "unit": "ADC",
    "sensor": "Raindrop",
    "note": "0=wet, 1023=dry"
  },
  "illuminance": {
    "rawLevel": 800,
    "unit": "ADC",
    "sensor": "LDR",
    "note": "0=dark, 1023=bright"
  },
  "signal": {
    "rssi": -45,
    "snr": "9.5",
    "protocol": "LoRa 433MHz"
  }
}
```

---

## 🎯 Fitur Baru Gateway

### 1. **NTP Time Synchronization** ⏰
```cpp
// Di setup()
configTime(7 * 3600, 0, "pool.ntp.org");  // GMT+7 Indonesia
```

**Benefits:**
- Timestamp akurat dalam format ISO 8601
- Compatible dengan sistem time-series database
- Mudah di-parse oleh backend

### 2. **Data Validation** ✅
```cpp
// Range checking untuk setiap sensor
if (tempValue < -40 || tempValue > 80) {
  Serial.println("⚠ Temperature out of valid range");
  validData = false;
}
```

**Valid Ranges:**
- Temperature: -40°C to 80°C
- Humidity: 0% to 100%
- Pressure: 300 hPa to 1100 hPa

**Jika data invalid:** Gateway **TIDAK** akan publish ke MQTT (data protection)

### 3. **Unit Metadata** 📏
Setiap parameter sekarang punya metadata lengkap:
```json
{
  "value": "28.50",
  "unit": "celsius",
  "sensor": "AHT20"
}
```

### 4. **Location Information** 🌍
```cpp
// Konfigurasi di gateway_optimized.ino
const float STATION_LATITUDE = -7.2575;   // Surabaya
const float STATION_LONGITUDE = 112.7521;
const float STATION_ELEVATION = 3.0;      // meter
const char* STATION_NAME = "Weather Station Surabaya";
```

**PENTING:** Ganti dengan koordinat lokasi Anda!

### 5. **Sensor Identification** 🔍
Setiap data mencantumkan sensor yang digunakan:
- Temperature & Humidity: **AHT20**
- Pressure: **BMP280**
- Wind: **Anemometer**
- Rain: **Raindrop Sensor**
- Light: **LDR**

---

## 🔧 Konfigurasi yang Perlu Disesuaikan

### **Gateway Configuration:**

```cpp
// LOCATION - WAJIB DIGANTI!
const float STATION_LATITUDE = -7.2575;   // Latitude stasiun Anda
const float STATION_LONGITUDE = 112.7521; // Longitude stasiun Anda
const float STATION_ELEVATION = 3.0;      // Elevasi (meter)
const char* STATION_NAME = "Weather Station Surabaya";

// NTP SERVER
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 7 * 3600;     // GMT+7 untuk Indonesia
```

**Cara cari koordinat:**
1. Buka Google Maps
2. Klik kanan di lokasi stasiun Anda
3. Pilih koordinat yang muncul
4. Copy ke kode

---

## 📋 Comparison Table

| Feature | Original | Optimized | Normalized (Baru) |
|---------|----------|-----------|-------------------|
| **Sensor Count** | 3 temp, 2 hum | 1 temp, 1 hum | 1 temp, 1 hum |
| **LoRa Payload** | 10 fields | 7 fields | 7 fields |
| **JSON Size** | ~512 bytes | ~384 bytes | ~768 bytes |
| **Timestamp** | `millis()` ❌ | `millis()` ❌ | ISO 8601 ✅ |
| **Units** | Implicit ❌ | Implicit ❌ | Explicit ✅ |
| **Validation** | None ❌ | Basic ✅ | Range checking ✅ |
| **Location** | None ❌ | None ❌ | GPS coords ✅ |
| **Sensor ID** | None ❌ | None ❌ | Full metadata ✅ |
| **@type** | None ❌ | None ❌ | WeatherObservation ✅ |

---

## 🚀 Benefits Normalisasi Data

### **1. Interoperability**
- Compatible dengan weather API standar
- Bisa integrasi dengan Weather Underground, APRS, dll
- Easy to integrate dengan dashboard framework apapun

### **2. Time-Series Database Ready**
Format ini perfect untuk:
- ✅ InfluxDB
- ✅ TimescaleDB
- ✅ Prometheus
- ✅ Grafana

### **3. Data Quality**
- Range validation mencegah data error
- NTP timestamp yang akurat
- Metadata lengkap untuk traceability

### **4. Scalability**
- Multiple stations support (dengan lokasi berbeda)
- Query by location/sensor type
- Filtering berdasarkan unit

---

## 🧪 Testing Normalized Format

### **MQTT Subscribe:**
```bash
mosquitto_sub -h 192.168.110.131 -t "weather/station/data" -v | jq .
```

### **Expected Output:**
```json
{
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "gatewayID": "ESP32_Gateway_001",
  "stationName": "Weather Station Surabaya",
  "observationTime": "2025-11-23T11:04:55+07:00",
  "location": {
    "latitude": -7.2575,
    "longitude": 112.7521,
    "elevation": 3
  },
  "temperature": {
    "value": "28.50",
    "unit": "celsius",
    "sensor": "AHT20"
  },
  ...
}
```

---

## ⚠️ Important Notes

### **1. NTP Requires Internet**
Gateway membutuhkan koneksi internet untuk NTP sync:
- Jika NTP gagal, akan fallback ke `uptimeMs`
- Gateway akan retry NTP sync otomatis

### **2. JSON Size Lebih Besar**
- Original: ~384 bytes
- Normalized: ~768 bytes
- Trade-off: Size vs Metadata richness

### **3. MQTT Payload Size**
Pastikan MQTT broker support payload >1KB:
```bash
# Di mosquitto.conf
message_size_limit 10000
```

---

## 📊 Recommended Backend Stack

### **Option 1: InfluxDB + Grafana**
```bash
# Store normalized data ke InfluxDB
# Visualize dengan Grafana
```

### **Option 2: Node-RED Flow**
```javascript
// Parse normalized JSON
// Store to database
// Send alerts
```

### **Option 3: Custom Backend**
```python
# Python MQTT subscriber
# Parse ISO 8601 timestamp
# Store with location metadata
```

---

## ✅ Checklist Migration

- [ ] Upload `transmitter_optimized.ino` ke Arduino Nano
- [ ] Upload `gateway_optimized.ino` ke ESP32-S3
- [ ] Update `STATION_LATITUDE` dan `STATION_LONGITUDE`
- [ ] Update `STATION_NAME`
- [ ] Verify NTP sync berhasil (check serial monitor)
- [ ] Subscribe ke MQTT dan verify JSON format
- [ ] Update backend/dashboard untuk consume new format

---

**Selamat! Weather station Anda sekarang menggunakan format data standar industri!** 🎉
