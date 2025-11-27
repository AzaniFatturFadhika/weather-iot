# Firmware Source Code

This directory contains the Arduino sketches for the Weather IoT Monitoring System.

---

## 📁 Structure

```
firmware/
├── transmitter/    # ✅ Current - Industry compliant
└── gateway/        # ✅ Current - Industry compliant
```

---

## 🚀 Current Version:

### **Transmitter** (`transmitter/`)

- Arduino Nano + LoRa SX1278
- Sensors: AHT20, BMP280, Anemometer, Raindrop, LDR
- Features: CRC checksum, data validation, optimized sensors
- Transmission: Every 10 seconds

### **Gateway** (`gateway/`)

- ESP32-S3 + LoRa SX1278
- Features:
  - CRC validation
  - Schema.org compliant JSON
  - UN/CEFACT unit codes
  - NTP time sync
  - Multi-station registry
  - MQTT publishing

---

## 📥 Upload Instructions

### Transmitter

1. Open `firmware/transmitter/transmitter.ino` in Arduino IDE
2. Select Board: **Arduino Nano**
3. Set unique `DEVICE_ID` (e.g., "TX001", "TX002")
4. Upload

### Gateway

1. Open `firmware/gateway/gateway.ino` in Arduino IDE
2. Select Board: **ESP32S3 Dev Module**
3. Configure:
   - WiFi SSID & Password
   - MQTT broker details
   - Station registry (if multiple transmitters)
4. Upload

---

## 🔧 Dependencies

### Transmitter Libraries

```
- SPI (built-in)
- LoRa by Sandeep Mistry
- Wire (built-in)
- Adafruit BMP280
- Adafruit AHTX0
```

### Gateway Libraries

```
- SPI (built-in)
- LoRa by Sandeep Mistry
- WiFi (built-in ESP32)
- time.h (built-in)
- ESP32MQTTClient by cyijun
- ArduinoJson by Benoit Blanchon
```

Install via Arduino Library Manager.

---

## 📊 Version Comparison

| Feature         | v1.0-basic                | v2.0-standard             |
| --------------- | ------------------------- | ------------------------- |
| Sensors         | DHT22, BMP280 (redundant) | AHT20, BMP280 (optimized) |
| Data Integrity  | ❌ None                   | ✅ CRC8 checksum          |
| JSON Format     | Custom                    | ✅ Schema.org compliant   |
| Unit Codes      | Custom strings            | ✅ UN/CEFACT standard     |
| Multi-Station   | ❌ No                     | ✅ Station registry       |
| Time Sync       | ❌ No                     | ✅ NTP                    |
| Data Validation | ⚠️ Basic                | ✅ Comprehensive          |

---

## 📖 Documentation

- [Getting Started Guide](../docs/guides/getting-started.md)
- [Pin Reference](../docs/hardware/pin-reference.md)
- [API Documentation](../docs/api/json-schema.md)
- [Multi-Transmitter Setup](../docs/guides/adding-transmitter.md)

---

## 🔄 Upgrading from v1.0 to v2.0

**Transmitter:**

- Replace `.ino` file
- No hardware changes needed
- Change `DEVICE_ID` if needed

**Gateway:**

- Replace `.ino` file
- Update station registry for multi-station
- Configure WiFi & MQTT
- No hardware changes needed

**Backend:**

- Update JSON parsers to handle new format
- See [Migration Guide](../docs/changelog/v2.0.0.md#migration-guide)

---

**For support, see [Troubleshooting](../docs/guides/troubleshooting.md)**
