# Arsitektur Multi-Transmitter Weather Station System

## 📋 Studi Kasus: Sistem Kabupaten-Kecamatan

### **Skenario:**
- **Gateway:** Kantor Kabupaten (Central Hub)
- **Transmitter 1:** Kecamatan A (Sensor: AHT20, BMP280, Anemometer)
- **Transmitter 2:** Kecamatan B (Sensor: DHT22, BMP280, Rain gauge)
- **Transmitter 3:** Kecamatan C (Sensor: AHT20, UV sensor, Light sensor)

---

## 🤔 **Pertanyaan Kritis & Jawaban**

### **Q1: Apakah perlu menyertakan informasi sensor dari transmitter?**

**Jawaban: TIDAK perlu di payload LoRa, TAPI perlu di Gateway mapping!**

#### **Opsi A: Kirim Metadata Sensor di LoRa** ❌ (Tidak Disarankan)
```
TX001|AHT20|BMP280|Anemometer|28.5|65.2|1013.25|5.2
                               ↑
                    Metadata sensor (waste bandwidth)
```

**Masalah:**
- ❌ Bandwidth LoRa terbuang (sensor type tidak berubah setiap transmisi)
- ❌ Payload lebih besar
- ❌ Parsing lebih kompleks
- ❌ Transmitter code lebih rumit

#### **Opsi B: Mapping di Gateway** ✅ (RECOMMENDED)
```
TX001 → {sensors: ["AHT20", "BMP280", "Anemometer"], location: {lat, lon}}
TX002 → {sensors: ["DHT22", "BMP280", "Rain gauge"], location: {lat, lon}}
TX003 → {sensors: ["AHT20", "UV", "LDR"], location: {lat, lon}}
```

**Keuntungan:**
- ✅ Payload LoRa tetap kecil dan efisien
- ✅ Metadata sensor di-manage terpusat di gateway
- ✅ Mudah update konfigurasi tanpa re-flash transmitter
- ✅ Gateway inject metadata saat publish ke MQTT

---

### **Q2: Apa yang harus dilakukan Gateway?**

Gateway bertanggung jawab untuk:

#### **1. Station Registry (Database Mini)**
```cpp
struct StationConfig {
  String stationID;
  String name;
  float latitude;
  float longitude;
  float elevation;
  String sensors[6];  // Daftar sensor yang digunakan
  int sensorCount;
};

StationConfig stations[] = {
  {"TX001", "Kec. Semarang Utara", -6.9600, 110.4200, 10.0, 
   {"AHT20", "BMP280", "Anemometer", "LDR", "Raindrop"}, 5},
   
  {"TX002", "Kec. Semarang Barat", -6.9850, 110.3950, 15.0,
   {"DHT22", "BMP280", "Rain gauge", "LDR"}, 4},
   
  {"TX003", "Kec. Genuk", -6.9450, 110.4500, 5.0,
   {"AHT20", "UV sensor", "LDR", "Raindrop"}, 4}
};
```

#### **2. Dynamic Metadata Injection**
```cpp
// Get station config berdasarkan ID
StationConfig getStationConfig(String stationID) {
  for (int i = 0; i < sizeof(stations)/sizeof(stations[0]); i++) {
    if (stations[i].stationID == stationID) {
      return stations[i];
    }
  }
  // Return default jika tidak ditemukan
  return {"UNKNOWN", "Unknown Station", -6.9859, 110.4093, 15.0, {}, 0};
}
```

#### **3. Data Enrichment di MQTT**
```json
{
  "stationID": "TX001",
  "stationName": "Kec. Semarang Utara",
  "location": {
    "latitude": -6.9600,
    "longitude": 110.4200,
    "elevation": 10.0
  },
  "sensors": ["AHT20", "BMP280", "Anemometer", "LDR", "Raindrop"],
  "temperature": {
    "value": "28.50",
    "unit": "celsius",
    "sensor": "AHT20"  // ← Injected by gateway
  },
  ...
}
```

---

### **Q3: Apakah perlu penyesuaian kode jika tambah transmitter ke-3?**

**Jawaban: YA, tapi MINIMAL (hanya update registry)!**

#### **Sebelum (Tanpa Registry):**
```cpp
// Hardcoded untuk 1 lokasi
const float STATION_LATITUDE = -6.9859;
const float STATION_LONGITUDE = 110.4093;
```
❌ **Masalah:** Semua transmitter dapat lokasi sama!

#### **Sesudah (Dengan Registry):**
```cpp
// Cukup tambah 1 entry di array
StationConfig stations[] = {
  {"TX001", "Kec. Semarang Utara", ...},
  {"TX002", "Kec. Semarang Barat", ...},
  {"TX003", "Kec. Genuk", ...},           // ← TAMBAH BARIS INI SAJA!
};
```
✅ **Tidak perlu ubah logika code!**

---

### **Q4: Apakah transmitter otomatis terdeteksi gateway?**

**Jawaban: YA dan TIDAK (tergantung definisi "terdeteksi")**

#### **Auto-Detection LoRa:** ✅ YA
```
TX001 → LoRa broadcast → Gateway receives ✅
TX002 → LoRa broadcast → Gateway receives ✅
TX003 → LoRa broadcast → Gateway receives ✅ (NEW!)
```
- Gateway **OTOMATIS menerima** semua packet LoRa di frequency 433MHz
- Tidak perlu pairing/registration
- Transmitter baru langsung bisa kirim data

#### **Auto-Configuration:** ❌ TIDAK (Perlu Registry)
```
TX003 (new) → Gateway receives → Cek registry → TIDAK ADA!
                                                      ↓
                                          Use default location/metadata
```

**Solusi:**
1. **Manual Registry Update** (Recommended untuk production)
   ```cpp
   // Admin tambah config di gateway code
   {"TX003", "Kec. Genuk", -6.9450, 110.4500, 5.0, ...}
   ```

2. **Auto-Registration dengan Default** (Good for testing)
   ```cpp
   if (stationNotFound) {
     registerNewStation(stationID);  // Use default values
     sendAlertToAdmin("New station detected: " + stationID);
   }
   ```

3. **Remote Configuration via MQTT** (Advanced)
   ```
   Admin → MQTT topic: "weather/config/TX003" → Gateway updates registry
   ```

---

## 🏗️ **Arsitektur yang Direkomendasikan**

### **Desain Sistem:**

```
┌─────────────────────────────────────────────────┐
│         KANTOR KABUPATEN (Gateway)              │
│  ┌───────────────────────────────────────────┐  │
│  │  ESP32-S3 Gateway                         │  │
│  │  - Station Registry (Metadata Database)  │  │
│  │  - Location Mapping                       │  │
│  │  - Sensor Type Mapping                    │  │
│  │  - NTP Time Sync                          │  │
│  │  - Data Validation                        │  │
│  │  - MQTT Publisher                         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
            │
            │ LoRa 433MHz
            │ (Broadcast)
            │
    ┌───────┴──────┬──────────────┬──────────────┐
    │              │              │              │
    v              v              v              v
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ TX001   │   │ TX002   │   │ TX003   │   │ TX00N   │
│ Kec. A  │   │ Kec. B  │   │ Kec. C  │   │ Kec. N  │
│ Sensors:│   │ Sensors:│   │ Sensors:│   │ Sensors:│
│ • AHT20 │   │ • DHT22 │   │ • AHT20 │   │ • ...   │
│ • BMP280│   │ • BMP280│   │ • UV    │   │         │
│ • Anemo │   │ • Rain  │   │ • LDR   │   │         │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

### **Data Flow:**

```
1. Transmitter (TX001):
   Payload: "TX001|28.5|65.2|1013.25|5.2|100|800"
              ↓
2. Gateway LoRa Receiver:
   Parse → stationID = "TX001"
              ↓
3. Gateway Registry Lookup:
   TX001 → {name: "Kec. A", lat: -6.96, sensors: ["AHT20", "BMP280",...]}
              ↓
4. Gateway Data Enrichment:
   {
     "stationID": "TX001",
     "stationName": "Kec. Semarang Utara",
     "location": {...},
     "sensors": ["AHT20", "BMP280", "Anemometer"],
     "temperature": {"value": 28.5, "unit": "celsius", "sensor": "AHT20"},
     ...
   }
              ↓
5. MQTT Publish:
   Topic: weather/station/data
   Payload: {enriched JSON}
              ↓
6. Backend/Dashboard:
   Filter by stationID, location, sensor type, etc.
```

---

## 📊 **Perbandingan Pendekatan**

| Aspek | Sensor Metadata di Transmitter | Sensor Metadata di Gateway |
|-------|-------------------------------|---------------------------|
| **Bandwidth LoRa** | ❌ Boros (kirim setiap kali) | ✅ Efisien |
| **Transmitter Code** | ❌ Kompleks | ✅ Simple |
| **Flexibility** | ❌ Perlu re-flash untuk update | ✅ Update registry saja |
| **Scalability** | ❌ Sulit untuk banyak station | ✅ Easy to manage |
| **Maintenance** | ❌ Distributed config | ✅ Centralized config |
| **Auto-detection** | ⚠️ Self-describing | ⚠️ Perlu registry |

---

## ✅ **Best Practices untuk Multi-Station System**

### **1. Naming Convention untuk Station ID**
```cpp
// Format: {AREA}{TYPE}{NUMBER}
"SU01"  // Semarang Utara 01
"SB01"  // Semarang Barat 01
"GN01"  // Genuk 01
"TM01"  // Tembalang 01
```

### **2. MQTT Topic Organization**
```
weather/
  ├── station/
  │   ├── data           # Semua station publish di sini
  │   ├── status         # Gateway status
  │   └── config         # Configuration updates
  ├── region/
  │   ├── semarang-utara # Filter by region
  │   ├── semarang-barat
  │   └── genuk
  └── sensor/
      ├── temperature    # Filter by sensor type
      ├── pressure
      └── wind
```

### **3. Versioning untuk Transmitter**
```cpp
const String FIRMWARE_VERSION = "v1.0.0";
const String SENSOR_CONFIG = "AHT20-BMP280-ANEM";

// Kirim di payload sesekali (misal setiap 1 jam)
String payload = DEVICE_ID + "|" + FIRMWARE_VERSION + "|" + 
                 SENSOR_CONFIG + "|" + sensorData;
```

### **4. Heartbeat & Health Monitoring**
```cpp
// Gateway track last seen time per station
unsigned long lastSeen[MAX_STATIONS];

if (millis() - lastSeen[stationIndex] > 300000) {  // 5 menit
  sendAlert("Station " + stationID + " offline!");
}
```

### **5. Data Aggregation**
```cpp
// Gateway bisa aggregate data dari multiple station
{
  "region": "Semarang",
  "averageTemperature": 28.3,  // Average dari TX001, TX002, TX003
  "stations": [
    {"id": "TX001", "temp": 28.5, "location": {...}},
    {"id": "TX002", "temp": 28.0, "location": {...}},
    {"id": "TX003", "temp": 28.4, "location": {...}}
  ]
}
```

---

## 🔧 **Implementasi di Code**

### **Gateway dengan Station Registry:**

```cpp
// Definisi struktur
struct StationConfig {
  String id;
  String name;
  float lat;
  float lon;
  float elevation;
  String sensors[6];
  int sensorCount;
};

// Database station (hardcoded, bisa dari SD card / SPIFFS)
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
  }
};

const int STATION_COUNT = 3;

// Lookup function
StationConfig* getStationConfig(String stationID) {
  for (int i = 0; i < STATION_COUNT; i++) {
    if (stationRegistry[i].id == stationID) {
      return &stationRegistry[i];
    }
  }
  return nullptr;  // Not found
}

// Di parseAndPublish()
StationConfig* station = getStationConfig(fields[0]);

if (station != nullptr) {
  // Use station-specific config
  doc["stationName"] = station->name;
  location["latitude"] = station->lat;
  location["longitude"] = station->lon;
  location["elevation"] = station->elevation;
  
  // Add sensor list
  JsonArray sensors = doc.createNestedArray("sensors");
  for (int i = 0; i < station->sensorCount; i++) {
    sensors.add(station->sensors[i]);
  }
} else {
  // Unknown station - use defaults or skip
  Serial.println("⚠️ Unknown station: " + fields[0]);
  doc["stationName"] = "Unknown Station";
  // Use default location or skip publishing
}
```

---

## 🎯 **Workflow Menambah Transmitter Baru**

### **Langkah 1: Setup Hardware Transmitter**
```arduino
// transmitter_optimized.ino
const String DEVICE_ID = "TX004";  // ← Ganti ID baru

// Upload ke Arduino Nano
```

### **Langkah 2: Update Gateway Registry**
```cpp
// gateway_optimized.ino
StationConfig stationRegistry[] = {
  {"TX001", "Kec. Semarang Utara", ...},
  {"TX002", "Kec. Semarang Barat", ...},
  {"TX003", "Kec. Genuk", ...},
  {"TX004", "Kec. Mijen", -6.9750, 110.3550, 20.0,  // ← TAMBAH BARIS INI
   {"AHT20", "BMP280", "Anemometer", "LDR"}, 4}
};

const int STATION_COUNT = 4;  // ← Update count

// Upload ke ESP32-S3
```

### **Langkah 3: Deploy & Monitor**
```bash
# Subscribe MQTT
mosquitto_sub -h broker.emqx.io -t "weather/station/data" -v | grep TX004

# Verify data dari TX004 muncul dengan lokasi yang benar
```

**Total Time:** < 10 menit! ✅

---

## 📈 **Scalability Limits**

| Parameter | Limit | Reason |
|-----------|-------|--------|
| **Max Transmitters** | ~50 stations | LoRa collision probability |
| **Transmission Interval** | 10-60 seconds | Balance antara freshness vs bandwidth |
| **Gateway Memory** | ~20-30 stations | ESP32 SRAM untuk registry |
| **MQTT Payload** | < 2KB | Broker limits |
| **LoRa Range** | 2-15 km | Depends on terrain/obstacles |

**Catatan:** Untuk >50 stations, gunakan multiple gateways atau LoRaWAN network.

---

## ✅ **Kesimpulan**

### **Design Decisions:**

1. ✅ **Sensor metadata di Gateway (bukan transmitter)**
   - Efisien, fleksibel, mudah maintenance

2. ✅ **Station registry di Gateway**
   - Centralized configuration
   - Easy to update

3. ✅ **Auto-detection LoRa + Manual configuration**
   - Gateway otomatis receive packet
   - Admin manual register station di registry

4. ✅ **Minimal code change untuk scaling**
   - Tambah station = tambah 1 entry di array
   - No logic change needed

### **Implementation Checklist:**

- [ ] Update gateway dengan station registry
- [ ] Define StationConfig struct
- [ ] Implement getStationConfig() function
- [ ] Update parseAndPublish() untuk inject metadata
- [ ] Add sensor list to JSON output
- [ ] Document station naming convention
- [ ] Create monitoring dashboard dengan filtering by station

---

**Sistem siap untuk scale ke ratusan transmitter dengan minimal effort!** 🚀
