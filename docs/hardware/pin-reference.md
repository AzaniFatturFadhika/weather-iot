# Pin Reference Guide

## Arduino Nano Pin Configuration

### Digital Pins
| Pin | Function | Component |
|-----|----------|-----------|
| D2  | Interrupt | LoRa DIO0 |
| D3  | Interrupt | Anemometer Pulse Input |
| D4  | Digital I/O | DHT22 Data |
| D9  | Digital I/O | LoRa RESET |
| D10 | SPI CS | LoRa NSS/CS |
| D11 | SPI MOSI | LoRa MOSI |
| D12 | SPI MISO | LoRa MISO |
| D13 | SPI SCK | LoRa SCK |

### Analog Pins
| Pin | Function | Component |
|-----|----------|-----------|
| A0  | Analog Input | Raindrop Sensor |
| A1  | Analog Input | LDR |
| A4  | I2C SDA | BMP280 + AHT20 (shared) |
| A5  | I2C SCL | BMP280 + AHT20 (shared) |

### Power Pins
- **5V**: DHT22, Anemometer, Raindrop Sensor, LDR circuit
- **3.3V**: LoRa Module, BMP280, AHT20
- **GND**: Common ground untuk semua komponen

---

## ESP32-S3 Pin Configuration

### SPI Pins (LoRa) - ⚠️ UPDATED
| Pin | Function | Component | Notes |
|-----|----------|-----------|-------|
| GPIO 8  | Interrupt | LoRa DIO0 | Interrupt-capable, safe pin |
| GPIO 9  | Digital I/O | LoRa RESET | Safe GPIO |
| GPIO 10 | SPI CS | LoRa NSS/CS | Safe GPIO |
| GPIO 11 | SPI MOSI | LoRa MOSI | Safe GPIO |
| GPIO 12 | SPI SCK | LoRa SCK | Safe GPIO |
| GPIO 13 | SPI MISO | LoRa MISO | Safe GPIO |

### Built-in
| Pin | Function | Component |
|-----|----------|-----------|
| GPIO 48 | RGB LED | Built-in WS2812 LED indicator |

### Power Pins
- **3.3V**: LoRa Module
- **GND**: Common ground

### ⚠️ GPIO to AVOID on ESP32-S3
| GPIO Range | Reason | Impact |
|------------|--------|--------|
| **19-20** | USB D-/D+ | Will conflict with USB programming/Serial |
| **0** | Strapping pin | Boot mode selection |
| **45, 46** | Strapping pins | Flash voltage, ROM messages |
| **26-32** | Not available | These GPIOs don't exist on ESP32-S3 |
| **33-37** | PSRAM/Flash | Usually occupied if module has PSRAM |

**Note**: Pin configuration telah diupdate untuk menghindari konflik dengan USB native ESP32-S3 dan strapping pins. Lihat [esp32s3-pinout-notes.md](./esp32s3-pinout-notes.md) untuk detail lengkap.

---

## I2C Address Reference

| Sensor | Default Address | Alternative Address |
|--------|----------------|---------------------|
| BMP280 | 0x76 | 0x77 |
| AHT20  | 0x38 | - |

**Note**: Jika dua sensor I2C memiliki address yang sama, Anda perlu menggunakan I2C multiplexer atau mengubah address (jika didukung oleh sensor).

---

## Voltage Requirements

| Component | Operating Voltage | Notes |
|-----------|------------------|-------|
| Arduino Nano | 5V (via USB/VIN) | Regulated to 3.3V & 5V |
| ESP32-S3 | 3.3V (via USB/5V) | Built-in regulator |
| LoRa SX1278 | 3.3V | **IMPORTANT**: NOT 5V tolerant! |
| DHT22 | 3.3V - 5.5V | Works on both |
| BMP280 | 1.8V - 3.6V | Use 3.3V |
| AHT20 | 2.0V - 5.5V | Use 3.3V or 5V |
| Anemometer | 5V - 12V | Depends on model |
| Raindrop Sensor | 3.3V - 5V | Usually 5V |
| LDR | 3.3V - 5V | Voltage divider |

---

## Current Consumption (Typical)

| Device/Component | Current Draw | Notes |
|------------------|--------------|-------|
| Arduino Nano | ~19 mA | Idle |
| ESP32-S3 | ~40 mA | WiFi off |
| ESP32-S3 | ~160 mA | WiFi active |
| LoRa SX1278 (RX) | ~10 mA | Receiving |
| LoRa SX1278 (TX) | ~120 mA | Transmitting at 20dBm |
| DHT22 | ~2.5 mA | Measuring |
| BMP280 | ~0.7 mA | Measuring |
| AHT20 | ~0.3 mA | Measuring |

**Total Transmitter**: ~200 mA (saat transmit)  
**Total Gateway**: ~300 mA (saat WiFi + LoRa active)

---

## Recommended Power Supply

### Transmitter (Arduino Nano)
- **USB Power**: 5V via USB (easiest untuk testing)
- **Battery**: 7-12V via VIN pin + voltage regulator
- **Recommended**: 9V battery atau 3x 18650 Li-ion (11.1V)

### Gateway (ESP32-S3)
- **USB Power**: 5V via USB
- **Battery**: 5V via 5V pin atau 3.7V Li-ion dengan boost converter
- **Recommended**: Power bank atau 5V/2A adapter
