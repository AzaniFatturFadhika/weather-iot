# Quick Start Guide

**TL;DR:** Get weather station running in 15 minutes.

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
Gateway: LoRa, ESP32MQTTClient, ArduinoJson
```

**2. Upload Firmware:**
```
Transmitter: firmware/transmitter/transmitter.ino
Gateway: firmware/gateway/gateway.ino
```

**3. Configure:**
```cpp
// Transmitter
const String DEVICE_ID = "TX001";

// Gateway
const char* WIFI_SSID = "YourWiFi";
const char* MQTT_HOST = "broker.emqx.io";

StationConfig stationRegistry[] = {
  {"TX001", "Station Name", lat, lon, elevation, {...}, 5}
};
```

**4. Test:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 \
  -t "weather/station/data" -v
```

---

## 📖 Need Details?

**[Full Getting Started Guide →](getting-started.md)**

---

## Configuration Quick Reference

| Parameter | Transmitter | Gateway |
|-----------|-------------|---------|
| **Board** | Arduino Nano | ESP32S3 Dev |
| **Baud** | 115200 | 115200 |
| **LoRa Freq** | 433E6 | 433E6 |
| **Interval** | 10 sec | - |
| **Must Config** | DEVICE_ID | WiFi, MQTT, Registry |

---

## Common Issues

| Problem | Solution |
|---------|----------|
| LoRa not init | Check wiring & 3.3V power |
| WiFi failed | Check SSID/password |
| MQTT not connected | Check broker address & port |
| No data | Check transmitter ID in registry |
| CRC error | Check LoRa frequency match |

**[Full Troubleshooting →](troubleshooting.md)**
