# Quick Start Guide

**TL;DR:** Get weather station running in 15 minutes.

---

## 🔀 Choose Gateway Version

| Version | Best For |
|---------|----------|
| **MQTT** ✅ | New projects, IoT platforms, multi-station |
| **HTTP** | Legacy backends with HTTP API |

---

## 🚀 For Experienced Users

### Hardware
- Arduino Nano + LoRa + AHT20 + BMP280 + sensors
- ESP32-S3 + LoRa

**[Pin Reference →](../hardware/pin-reference.md)**

### Software

**1. Install Libraries:**
```
Transmitter: LoRa, Adafruit_BMP280, Adafruit_AHTX0

Gateway MQTT: LoRa, ESP32MQTTClient, ArduinoJson
Gateway HTTP: LoRa, HTTPClient (built-in)
```

**2. Upload Firmware:**
```
Transmitter: firmware/transmitter/transmitter.ino

Gateway MQTT: firmware/gateway/gateway_mqtt/gateway_mqtt.ino
Gateway HTTP: firmware/gateway/gateway_http/gateway_http.ino
```

**3. Configure:**

**MQTT Gateway:**
```cpp
// Transmitter
const String DEVICE_ID = "TX001";

// Gateway MQTT
const char* WIFI_SSID = "YourWiFi";
const char* MQTT_HOST = "broker.emqx.io";

StationConfig stationRegistry[] = {
  {"TX001", "Station Name", lat, lon, elevation, {...}, 5}
};
```

**HTTP Gateway:**
```cpp
// Transmitter
const String DEVICE_ID = "TX001";

// Gateway HTTP
const char* WIFI_SSID = "YourWiFi";
const char* BACKEND_URL = "http://192.168.1.100:8000";
```

**4. Test:**

**MQTT:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 \
  -t "weather/station/data" -v
```

**HTTP:**
Check your backend logs for incoming GET requests to `/weather-data/create`

---

## 📖 Need Details?

**[Full Getting Started Guide →](getting-started.md)**

---

## Configuration Quick Reference

| Parameter | Transmitter | Gateway MQTT | Gateway HTTP |
|-----------|-------------|--------------|--------------|
| **Board** | Arduino Nano | ESP32S3 Dev | ESP32S3 Dev |
| **Baud** | 115200 | 115200 | 115200 |
| **LoRa Freq** | 433E6 | 433E6 | 433E6 |
| **Interval** | 10 sec | - | - |
| **Must Config** | DEVICE_ID | WiFi, MQTT, Registry | WiFi, Backend URL |

---

## Common Issues

| Problem | Solution |
|---------|----------|
| LoRa not init | Check wiring & 3.3V power |
| WiFi failed | Check SSID/password |
| MQTT not connected | Check broker address & port |
| HTTP not working | Check backend URL & endpoint |
| No data | Check transmitter ID in registry (MQTT) |
| CRC error | Check LoRa frequency match |

**[Full Troubleshooting →](troubleshooting.md)**
