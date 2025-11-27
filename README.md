# Weather IoT Monitoring System

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](docs/changelog/v2.0.0.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Industry Standard](https://img.shields.io/badge/Schema.org-compliant-brightgreen.svg)](https://schema.org/WeatherObservation)

> **Sistem monitoring cuaca berbasis IoT dengan LoRa + MQTT yang memenuhi standar industri internasional**

## 🌟 Features

- ✅ **Industry Standard Compliant** - Schema.org WeatherObservation + UN/CEFACT unit codes
- ✅ **Multi-Transmitter Support** - Station registry untuk puluhan stasiun
- ✅ **Data Integrity** - CRC8 checksum untuk validasi packet
- ✅ **Real-time Monitoring** -Data setiap 10 detik via LoRa + MQTT
- ✅ **Production Ready** - NTP sync, data validation, error handling

---

## 📚 Quick Links

| For...                    | Start Here                                                  |
| ------------------------- | ----------------------------------------------------------- |
| **New Users**       | [📖 Getting Started](docs/guides/getting-started.md)           |
| **Quick Setup**     | [⚡ Quick Start Guide](docs/guides/quick-start.md)             |
| **API Reference**   | [📡 JSON Schema](docs/api/json-schema.md)                      |
| **Troubleshooting** | [🔧 Common Issues](docs/guides/troubleshooting.md)             |
| **Architecture**    | [🏗️ System Overview](docs/architecture/multi-transmitter.md) |
| **Hardware**        | [🔌 Pin Reference](docs/hardware/pin-reference.md)             |

---

## 🚀 Quick Start

### 1. Hardware Setup

```
Transmitter: Arduino Nano + LoRa SX1278 + AHT20 + BMP280 + Anemometer
Gateway: ESP32-S3 + LoRa SX1278
```

### 2. Upload Firmware

```bash
# Transmitter (Arduino IDE)
firmware/transmitter/transmitter.ino

# Gateway (Arduino IDE)
firmware/gateway/gateway.ino
```

### 3. Configure

```cpp
// Transmitter: Set unique ID
const String DEVICE_ID = "TX001";

// Gateway: Set WiFi & MQTT
const char* WIFI_SSID = "your-wifi";
const char* MQTT_HOST = "broker.emqx.io";
```

### 4. Monitor Data

```bash
mosquitto_sub -h broker.emqx.io -p 1883 -u emqx -P public \
  -t "weather/station/data" -v
```

**[📖 Full Setup Guide →](docs/guides/getting-started.md)**

---

## 📁 Project Structure

```
weather-iot/
├── firmware/             # Source code (Arduino sketches)
│   ├── transmitter/       # ✅ Current (industry compliant)
│   └── gateway/           # ✅ Current (industry compliant)
├── docs/                 # Documentation
│   ├── guides/            # User guides & tutorials
│   ├── architecture/      # System design & architecture
│   ├── api/               # API reference & schemas
│   ├── hardware/          # Hardware specs & assembly
│   ├── development/       # Developer docs
│   └── changelog/         # Version history
├── examples/             # Example configs & code
│   ├── mosquitto/         # MQTT broker configs
│   └── python/            # Python MQTT clients
├── schemas/              # JSON schemas
└── tools/                # Utility scripts
```

---

## 📊 System Overview

```
┌─────────────┐  LoRa 433MHz    ┌──────────┐    MQTT/WiFi    ┌────────────┐
│ Transmitter │ ──────────────> │ Gateway  │ ──────────────> │   Broker   │
│  (Arduino)  │   CRC checked   │ (ESP32)  │  JSON enriched  │  (EMQX)    │
└─────────────┘                 └──────────┘                 └────────────┘
     |                               |                              |
  Sensors:                      Functions:                     Subscribers:
  • AHT20                       • NTP sync                     • Dashboard
  • BMP280                      • Data validation              • Database
  • Anemometer                  • Location mapping             • Mobile app
  • Raindrop                    • Format normalization         • Analytics
  • LDR                         • Station registry
```

**[🏗️ Detailed Architecture →](docs/architecture/multi-transmitter.md)**

---

## 🔧 Hardware Requirements

### Transmitter (per station)

- Arduino Nano / Pro Mini
- LoRa SX1278 RA-02 (433MHz)
- AHT20 (Temperature & Humidity)
- BMP280 (Pressure)
- Anemometer (Wind speed)
- Raindrop sensor
- LDR (Light)

**Budget:** ~$50 per station

### Gateway (central hub)

- ESP32-S3 DevKit
- LoRa SX1278 RA-02 (433MHz)

**Budget:** ~$15

**[📋 Complete Parts List →](docs/hardware/pin-reference.md)**

---

## 📡 Data Format (Industry Standard)

```json
{
  "@context": "https://schema.org",
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "observationDate": "2025-11-23T12:00:00+07:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -6.9600,
    "longitude": 110.4200,
    "elevation": 10.0
  },
  "temperature": {
    "@type": "QuantitativeValue",
    "value": "28.50",
    "unitCode": "CEL",
    "sensor": "AHT20"
  }
}
```

**[📖 Complete JSON Schema →](docs/api/json-schema.md)**

---

## 🌐 Multi-Transmitter Support

Sistem mendukung puluhan transmitter di lokasi berbeda:

```cpp
// Gateway - Station Registry
StationConfig stationRegistry[] = {
  {"TX001", "Kec. Semarang Utara", -6.9600, 110.4200, ...},
  {"TX002", "Kec. Semarang Barat", -6.9850, 110.3950, ...},
  {"TX003", "Kec. Genuk", -6.9450, 110.4500, ...}
};
```

**[📖 Adding New Transmitter Guide →](docs/guides/adding-transmitter.md)**

---

## 📈 Changelog

### v2.0.0 (2025-11-23) - Industry Standard Compliant

- ✅ CRC8 checksum untuk data integrity
- ✅ Schema.org full compliance (@context, QuantitativeValue)
- ✅ UN/CEFACT unit codes (CEL, P1, HPA, KMH)
- ✅ Multi-station registry system
- ✅ NTP time synchronization

### v1.0.0 (2025-11-22) - Initial Release

- Basic LoRa → MQTT gateway
- Single transmitter support

**[📝 Full Changelog →](docs/changelog/v2.0.0.md)**

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/development/contributing.md) first.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Schema.org](https://schema.org/) - WeatherObservation standard
- [UN/CEFACT](https://www.unece.org/cefact/) - Unit codes
- [LoRa by Sandeep Mistry](https://github.com/sandeepmistry/arduino-LoRa)
- [ESP32MQTTClient](https://github.com/cyijun/ESP32MQTTClient)

---

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/your-username/weather-iot/issues)
- 💬 [Discussions](https://github.com/your-username/weather-iot/discussions)

---

**Made with ❤️ for IoT Community**
