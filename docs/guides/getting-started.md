# Getting Started with Weather IoT Monitoring System

Complete guide untuk setup sistem weather station dari nol.

---

## 📋 Prerequisites

### Hardware yang Dibutuhkan

**Untuk 1 Transmitter Station:**
- 1x Arduino Nano / Pro Mini (ATmega328P)
- 1x LoRa SX1278 RA-02 Module (433MHz)
- 1x AHT20 Temperature & Humidity Sensor
- 1x BMP280 Pressure Sensor
- 1x Anemometer (wind speed sensor)
- 1x Raindrop sensor module
- 1x LDR (Light Dependent Resistor)
- 1x 10kΩ Resistor (untuk LDR)
- Jumper wires
- Power supply (5V untuk Arduino)

**Untuk Gateway:**
- 1x ESP32-S3 DevKit
- 1x LoRa SX1278 RA-02 Module (433MHz)
- USB cable untuk programming
- Power supply (5V)

**Budget:** ~$65 total untuk 1 complete station + gateway

---

## 🔧 Step 1: Hardware Assembly

### 1.1 Transmitter Wiring

Lihat [Pin Reference](../hardware/pin-reference.md) untuk detail lengkap.

**LoRa SX1278 ke Arduino Nano:**
```
LoRa Module    Arduino Nano
VCC       →    3.3V
GND       →    GND
MISO      →    D12
MOSI      →    D11
SCK       →    D13
NSS       →    D10
RESET     →    D9
DIO0      →    D2
```

**Sensors ke Arduino Nano:**
```
AHT20 (I2C):
VCC  → 3.3V
GND  → GND
SDA  → A4
SCL  → A5

BMP280 (I2C):
VCC  → 3.3V
GND  → GND
SDA  → A4
SCL  → A5

Anemometer:
Signal → D3

Raindrop:
AO → A0

LDR:
One end → 5V
Other end → A1 & 10kΩ resistor to GND
```

### 1.2 Gateway Wiring

**LoRa SX1278 ke ESP32-S3:**
```
LoRa Module    ESP32-S3
VCC       →    3.3V
GND       →    GND
MISO      →    GPIO13
MOSI      →    GPIO11
SCK       →    GPIO12
NSS       →    GPIO10
RESET     →    GPIO9
DIO0      →    GPIO8
```

**[📖 Detailed Assembly Guide →](../hardware/assembly-guide.md)**

---

## 💻 Step 2: Software Setup

### 2.1 Install Arduino IDE

1. Download Arduino IDE dari https://www.arduino.cc/en/software
2. Install Arduino IDE

### 2.2 Install Required Libraries

**Buka Arduino IDE → Tools → Manage Libraries**

Install libraries berikut:

**Untuk Transmitter:**
- LoRa by Sandeep Mistry
- Adafruit BMP280
- Adafruit AHTX0
- Adafruit Unified Sensor

**Untuk Gateway:**
- LoRa by Sandeep Mistry
- ESP32MQTTClient by cyijun
- ArduinoJson by Benoit Blanchon

### 2.3 Install ESP32 Board Support

**Untuk Gateway (ESP32-S3):**

1. File → Preferences
2. Additional Boards Manager URLs:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Tools → Board → Boards Manager
4. Search "esp32" → Install

---

## 📝 Step 3: Configure & Upload Firmware

### 3.1 Transmitter Configuration

1. Open `firmware/transmitter/transmitter.ino`

2. Set unique Device ID:
   ```cpp
   const String DEVICE_ID = "TX001";  // Change for each transmitter
   ```

3. Select Board:
   - Tools → Board → Arduino AVR Boards → Arduino Nano
   - Tools → Processor → ATmega328P (Old Bootloader)

4. Select Port: Tools → Port → (your Arduino port)

5. Upload: Click Upload button (→)

6. Open Serial Monitor (115200 baud) untuk verify:
   ```
   Weather Transmitter (Optimized) Starting...
   LoRa initialized!
   AHT20 initialized!
   BMP280 initialized!
   ```

### 3.2 Gateway Configuration

1. Open `firmware/gateway/gateway.ino`

2. Configure WiFi:
   ```cpp
   const char* WIFI_SSID = "YourWiFiName";
   const char* WIFI_PASSWORD = "YourWiFiPassword";
   ```

3. Configure MQTT (gunakan broker.emqx.io untuk testing):
   ```cpp
   const char* MQTT_HOST = "broker.emqx.io";
   const int MQTT_PORT = 1883;
   const char* MQTT_USER = "emqx";
   const char* MQTT_PASSWORD = "public";
   ```

4. Update Station Registry:
   ```cpp
   StationConfig stationRegistry[] = {
     {
       "TX001",                    // Match transmitter ID
       "My Weather Station",       // Your station name
       -6.9600, 110.4200, 10.0,   // Your GPS coordinates
       {"AHT20", "BMP280", "Anemometer", "Raindrop", "LDR"},
       5
     }
   };
   ```

5. Select Board:
   - Tools → Board → ESP32 Arduino → ESP32S3 Dev Module

6. Select Port: Tools → Port → (your ESP32 port)

7. Upload: Click Upload

8. Open Serial Monitor (115200 baud):
   ```
   ===== Weather Gateway (Optimized) Starting =====
   ✓ LoRa initialized!
   Connecting to WiFi: YourWiFiName
   ✓ WiFi connected!
   ✓ NTP time synchronized!
   ✓ MQTT client started!
   ✓ Gateway ready!
   ```

---

## 🔌 Step 4: Setup MQTT Broker (Optional)

**Untuk Testing:** Gunakan public broker `broker.emqx.io` (sudah configured di atas)

**Untuk Production:** Setup private Mosquitto broker

**[📖 Mosquitto Setup Guide →](mosquitto-setup.md)**

---

## 📡 Step 5: Verify Data Flow

### 5.1 Subscribe to MQTT Topic

```bash
# Install mosquitto clients (if not installed)
sudo apt install mosquitto-clients

# Subscribe to weather data
mosquitto_sub -h broker.emqx.io -p 1883 -u emqx -P public \
  -t "weather/station/data" -v
```

### 5.2 Expected Output

Setiap 10 detik, Anda akan melihat JSON message:

```json
{
  "@context": "https://schema.org",
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "name": "My Weather Station",
  "observationDate": "2025-11-23T12:00:00+07:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -6.9600,
    "longitude": 110.4200
  },
  "temperature": {
    "@type": "QuantitativeValue",
    "value": "28.50",
    "unitCode": "CEL",
    "sensor": "AHT20"
  },
  ...
}
```

---

## ✅ Verification Checklist

- [ ] Transmitter power on & LED blink
- [ ] Serial monitor shows sensor readings
- [ ] Gateway connected to WiFi
- [ ] Gateway connected to MQTT
- [ ] NTP time synchronized
- [ ] MQTT messages received every 10 seconds
- [ ] JSON data valid (no CRC errors)
- [ ] Temperature, humidity, pressure values reasonable

---

## 🎉 Success!

Sistem Anda sudah running! Sekarang Anda bisa:

1. **Add More Transmitters** - [Adding Transmitter Guide](adding-transmitter.md)
2. **Visualize Data** - Setup Grafana dashboard
3. **Store Data** - Setup InfluxDB
4. **Production Deploy** - [Production Guide](../architecture/production-deployment.md)

---

## 🐛 Troubleshooting

Mengalami masalah? Lihat [Troubleshooting Guide](troubleshooting.md)

---

## 📚 Next Steps

- [Quick Start Guide](quick-start.md) - TL;DR version
- [JSON Schema](../api/json-schema.md) - Data format reference
- [Hardware Parts List](../hardware/parts-list.md) - Complete BOM
- [Production Deployment](../architecture/production-deployment.md) - Scale up
