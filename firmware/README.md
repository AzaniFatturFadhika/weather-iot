# Firmware Source Code

This directory contains the Arduino sketches for the Weather IoT Monitoring System.

---

## 📁 Structure

```
firmware/
├── transmitter/           # Weather station transmitter
└── gateway/               # Gateway implementations
    ├── gateway_mqtt/      # ✅ Recommended - MQTT version
    └── gateway_http/      # Legacy - HTTP version
```

---

## 🔀 Gateway Version Selection

**Choose the gateway version that fits your needs:**

### **MQTT Gateway** ✅ Recommended

**Location:** `gateway/gateway_mqtt/gateway_mqtt.ino`

**Best for:**
- ✅ New projects
- ✅ IoT platforms (AWS IoT, Azure IoT, ThingsBoard)
- ✅ Industry-standard compliance required
- ✅ Multiple transmitter stations

**Features:**
- Schema.org-compliant JSON format
- UN/CEFACT unit codes  
- Multi-station registry system
- NTP time synchronization
- Full CRC8 validation
- MQTT pub/sub protocol

---

### **HTTP Gateway** (Legacy)

**Location:** `gateway/gateway_http/gateway_http.ino`

**Best for:**
- ⚙️ Existing HTTP-based backends
- 🔧 Legacy systems with `/weather-data/create` endpoint
- 📦 Simple deployments without MQTT broker

**Features:**
- HTTP GET requests to backend
- Simple query parameter format
- Minimal dependencies
- Basic CRC validation

---

## 📊 Gateway Comparison

| Feature | MQTT Gateway | HTTP Gateway |
|---------|--------------|-------------|
| **Protocol** | MQTT pub/sub | HTTP GET |
| **Data Format** | Schema.org JSON | Query parameters |
| **Multi-Station** | ✅ Yes (registry) | ❌ No |
| **Time Sync** | ✅ NTP | ❌ No |
| **CRC Validation** | ✅ Full | ⚠️ Minimal |
| **Standards Compliance** | ✅ Schema.org + UN/CEFACT | ❌ Custom |
| **Dependencies** | ESP32MQTTClient, ArduinoJson | HTTPClient |
| **Setup Complexity** | Medium (MQTT broker) | Low (direct HTTP) |
| **Scalability** | ✅ High | ⚠️ Limited |
| **Recommended For** | **New projects** | Legacy systems |

---

## 🚀 Components Overview

### **Transmitter** (`transmitter/transmitter.ino`)

**Hardware:** Arduino Nano + LoRa SX1278

**Sensors:**
- AHT20 (Temperature & Humidity)
- BMP280 (Atmospheric Pressure)
- Anemometer (Wind Speed)
- Raindrop Sensor
- LDR (Light Intensity)

**Features:**
- CRC8 checksum for data integrity
- Optimized sensor reading
- 10-second transmission interval
- Compatible with both gateway versions

---

## 📥 Upload Instructions

### Transmitter

1. Open `firmware/transmitter/transmitter.ino` in Arduino IDE
2. Select Board: **Arduino Nano**
3. Set unique `DEVICE_ID` (e.g., "TX001", "TX002")
4. Upload

### Gateway - MQTT Version (Recommended)

1. Open `firmware/gateway/gateway_mqtt/gateway_mqtt.ino` in Arduino IDE
2. Select Board: **ESP32S3 Dev Module**
3. Configure:
   ```cpp
   const char* WIFI_SSID = "your-wifi";
   const char* WIFI_PASSWORD = "your-password";
   const char* MQTT_HOST = "broker.emqx.io";  // or your broker
   const char* MQTT_USER = "emqx";
   const char* MQTT_PASSWORD = "public";
   ```
4. Update station registry if using multiple transmitters
5. Upload

### Gateway - HTTP Version (Legacy)

1. Open `firmware/gateway/gateway_http/gateway_http.ino` in Arduino IDE
2. Select Board: **ESP32S3 Dev Module**
3. Configure:
   ```cpp
   const char* WIFI_SSID = "your-wifi";
   const char* WIFI_PASSWORD = "your-password";
   const char* BACKEND_URL = "http://192.168.1.100:8000";
   ```
4. Upload

---

## 🔧 Dependencies

### Transmitter Libraries

Install via Arduino Library Manager:

```
- SPI (built-in)
- LoRa by Sandeep Mistry
- Wire (built-in)
- Adafruit BMP280
- Adafruit AHTX0
```

### Gateway MQTT Libraries

Install via Arduino Library Manager:

```
- SPI (built-in)
- LoRa by Sandeep Mistry
- WiFi (built-in ESP32)
- time.h (built-in)
- ESP32MQTTClient by cyijun
- ArduinoJson by Benoit Blanchon
```

### Gateway HTTP Libraries

Install via Arduino Library Manager:

```
- SPI (built-in)
- LoRa by Sandeep Mistry
- WiFi (built-in ESP32)
- HTTPClient (built-in ESP32)
```

---

## 📖 Documentation

- [Getting Started Guide](../docs/guides/getting-started.md)
- [Quick Start Guide](../docs/guides/quick-start.md)
- [Pin Reference](../docs/hardware/pin-reference.md)
- [API Documentation](../docs/api/json-schema.md)
- [Multi-Transmitter Setup](../docs/guides/adding-transmitter.md)
- [Troubleshooting](../docs/guides/troubleshooting.md)

---

**For support, see [Troubleshooting](../docs/guides/troubleshooting.md)**
