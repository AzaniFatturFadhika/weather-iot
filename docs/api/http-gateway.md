# HTTP Gateway Documentation

## Overview

HTTP Gateway adalah versi legacy dari gateway Weather IoT Monitoring System yang mengirimkan data sensor ke backend melalui HTTP GET requests. Versi ini didesain untuk kompatibilitas dengan sistem backend yang sudah ada.

> [!WARNING]
> HTTP Gateway adalah **legacy version**. Untuk project baru, gunakan [MQTT Gateway](json-schema.md) yang lebih modern dan feature-rich.

---

## When to Use HTTP Gateway

### ✅ Use HTTP Gateway if:

- ✅ Anda memiliki backend HTTP yang sudah berjalan
- ✅ Backend memiliki endpoint `/weather-data/create` untuk menerima data
- ✅ Anda hanya memiliki **satu transmitter station**
- ✅ Tidak memerlukan metadata kompleks (GPS, timestamps, dll)
- ✅ Preferensi setup yang sederhana tanpa MQTT broker

### ❌ Don't Use HTTP Gateway if:

- ❌ Project baru yang butuh scalability
- ❌ Memerlukan multi-transmitter support
- ❌ Butuh industry-standard compliance (Schema.org)
- ❌ Memerlukan metadata lengkap (GPS coordinates, sensor info)
- ❌ Integrasi dengan IoT platforms (AWS IoT, ThingsBoard, dll)

> [!TIP]
> Untuk use case di atas, gunakan [MQTT Gateway](json-schema.md) sebagai gantinya.

---

## Architecture

```
┌─────────────┐  LoRa 433MHz    ┌──────────────┐  HTTP GET      ┌──────────┐
│ Transmitter │ ──────────────> │ HTTP Gateway │ ─────────────> │ Backend  │
│  (Arduino)  │   CRC checked   │   (ESP32)    │  Query Params  │  Server  │
└─────────────┘                 └──────────────┘                └──────────┘
     |                                |                               |
  Sensors:                      Functions:                      Functions:
  • AHT20                       • LoRa receive                  • Store data
  • BMP280                      • WiFi connect                  • Process
  • Anemometer                  • Parse data                    • Visualize
  • Raindrop                    • HTTP request
  • LDR
```

---

## Data Format

### HTTP Method

```
GET
```

### Endpoint

```
/weather-data/create
```

### Parameters (Query String)

| Parameter          | Type    | Range           | Unit    | Description                                |
| ------------------ | ------- | --------------- | ------- | ------------------------------------------ |
| `temp`           | Float   | -40.0 to 80.0   | °C     | Temperature from AHT20                     |
| `humidity`       | Float   | 0.0 to 100.0    | %       | Relative humidity from AHT20               |
| `pressure`       | Float   | 300.0 to 1100.0 | hPa     | Atmospheric pressure from BMP280           |
| `windSpeed`      | Float   | 0.0+            | km/h    | Wind speed from anemometer                 |
| `isRaining`      | Integer | 0 or 1          | boolean | Rain detection (0=dry, 1=raining)          |
| `lightIntensity` | Integer | 0 to 1023       | ADC     | Light level from LDR (0=dark, 1023=bright) |

### Example Request

**Full URL:**

```
http://192.168.1.100:8000/weather-data/create?temp=28.50&humidity=65.20&pressure=1013.25&windSpeed=5.30&isRaining=0&lightIntensity=512
```

**Decoded Parameters:**

```
temp=28.50
humidity=65.20
pressure=1013.25
windSpeed=5.30
isRaining=0
lightIntensity=512
```

---

## Sample Data

### Clear Weather (Day)

```
GET /weather-data/create?temp=32.15&humidity=58.40&pressure=1012.80&windSpeed=3.20&isRaining=0&lightIntensity=920
```

### Cloudy Weather

```
GET /weather-data/create?temp=28.90&humidity=72.30&pressure=1011.50&windSpeed=8.50&isRaining=0&lightIntensity=450
```

### Rainy Weather

```
GET /weather-data/create?temp=25.40&humidity=88.60&pressure=1009.20&windSpeed=12.70&isRaining=1&lightIntensity=180
```

### Night Time

```
GET /weather-data/create?temp=24.30&humidity=75.50&pressure=1013.10&windSpeed=2.10&isRaining=0&lightIntensity=15
```

---

## Data Conversion Logic

### Rain Detection

The gateway converts analog rain sensor reading to boolean:

```cpp
// Raindrop sensor: 0 (wet) to 1023 (dry)
int isRaining = (rain < 500) ? 1 : 0;
```

**Logic:**

- Raw value < 500 → **Wet** → `isRaining = 1`
- Raw value ≥ 500 → **Dry** → `isRaining = 0`

### Number Formatting

```cpp
temp          // 2 decimal places: 28.50
humidity      // 2 decimal places: 65.20
pressure      // 2 decimal places: 1013.25
windSpeed     // 2 decimal places: 5.30
isRaining     // Integer: 0 or 1
lightIntensity // Integer: 0-1023
```

---

## Backend Implementation

### Requirements

Your backend server must:

1. ✅ Accept HTTP GET requests
2. ✅ Parse query parameters from URL
3. ✅ Handle endpoint `/weather-data/create`
4. ✅ Return HTTP 200 response on success
5. ✅ Add timestamp (gateway doesn't send it)

### Example Implementations

#### Node.js (Express)

```javascript
const express = require('express');
const app = express();

app.get('/weather-data/create', (req, res) => {
  const {
    temp,
    humidity,
    pressure,
    windSpeed,
    isRaining,
    lightIntensity
  } = req.query;
  
  const weatherData = {
    temperature: parseFloat(temp),
    humidity: parseFloat(humidity),
    pressure: parseFloat(pressure),
    windSpeed: parseFloat(windSpeed),
    isRaining: parseInt(isRaining) === 1,
    lightIntensity: parseInt(lightIntensity),
    timestamp: new Date()
  };
  
  // Save to database
  console.log('Weather data received:', weatherData);
  
  res.json({ 
    status: 'success', 
    message: 'Data received',
    data: weatherData 
  });
});

app.listen(8000, () => {
  console.log('Backend listening on port 8000');
});
```

#### Python (FastAPI)

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/weather-data/create")
async def create_weather_data(
    temp: float,
    humidity: float,
    pressure: float,
    windSpeed: float,
    isRaining: int,
    lightIntensity: int
):
    weather_data = {
        "temperature": temp,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": windSpeed,
        "is_raining": bool(isRaining),
        "light_intensity": lightIntensity,
        "timestamp": datetime.now()
    }
  
    # Save to database
    print(f"Weather data received: {weather_data}")
  
    return {
        "status": "success",
        "message": "Data received",
        "data": weather_data
    }
```

#### PHP (Laravel)

```php
Route::get('/weather-data/create', function (Request $request) {
    $data = [
        'temperature' => (float) $request->temp,
        'humidity' => (float) $request->humidity,
        'pressure' => (float) $request->pressure,
        'wind_speed' => (float) $request->windSpeed,
        'is_raining' => (int) $request->isRaining === 1,
        'light_intensity' => (int) $request->lightIntensity,
        'timestamp' => now()
    ];
  
    // Save to database
    WeatherData::create($data);
  
    return response()->json([
        'status' => 'success',
        'message' => 'Data received',
        'data' => $data
    ]);
});
```

---

## Gateway Configuration

### Hardware

- ESP32-S3 DevKit
- LoRa SX1278 RA-02 Module (433MHz)

### Pin Configuration

```cpp
#define LORA_SCK   12
#define LORA_MISO  13
#define LORA_MOSI  11
#define LORA_SS    10
#define LORA_RST   9
#define LORA_DIO0  8
#define LED_BUILTIN 48
```

### WiFi Configuration

```cpp
const char* WIFI_SSID = "YourWiFiName";
const char* WIFI_PASSWORD = "YourWiFiPassword";
```

### Backend Configuration

```cpp
// Change to your backend IP or domain
const char* BACKEND_URL = "http://192.168.1.100:8000";
```

> [!IMPORTANT]
> Ensure your backend server is accessible from the ESP32's network.

---

## Setup Instructions

### 1. Prerequisites

**Hardware:**

- ESP32-S3 DevKit
- LoRa SX1278 RA-02 Module
- USB cable for programming

**Software:**

- Arduino IDE
- Required libraries:
  - `SPI` (built-in)
  - `LoRa` by Sandeep Mistry
  - `WiFi` (built-in ESP32)
  - `HTTPClient` (built-in ESP32)

### 2. Install Libraries

1. Open Arduino IDE
2. Go to **Tools → Manage Libraries**
3. Search and install: `LoRa by Sandeep Mistry`

### 3. Configure Firmware

Open `firmware/gateway/gateway_http/gateway_http.ino` and modify:

```cpp
// WiFi credentials
const char* WIFI_SSID = "YourWiFiName";
const char* WIFI_PASSWORD = "YourWiFiPassword";

// Backend URL (IP or domain)
const char* BACKEND_URL = "http://192.168.1.100:8000";
```

### 4. Upload Firmware

1. Select Board: **Tools → Board → ESP32 Arduino → ESP32S3 Dev Module**
2. Select Port: **Tools → Port → (your ESP32 port)**
3. Click **Upload** button (→)

### 5. Verify Operation

Open Serial Monitor (115200 baud). You should see:

```
===== Weather Gateway (HTTP Legacy) Starting =====
✓ LoRa initialized!
Connecting to WiFi: YourWiFiName
✓ WiFi connected!
  IP address: 192.168.1.50
✓ Gateway ready! Waiting for LoRa packets...
```

When data is received from transmitter:

```
===== LoRa Packet Received =====
Data: TX001|28.50|65.20|1013.25|5.30|512|820|A3
RSSI: -65 dBm

Sending HTTP GET: http://192.168.1.100:8000/weather-data/create?temp=28.50&humidity=65.20&pressure=1013.25&windSpeed=5.30&isRaining=0&lightIntensity=820
HTTP Response code: 200
Response: {"status":"success","message":"Data received"}
```

---

## Transmission Details

### Frequency

- Data sent every **~10 seconds** (based on transmitter interval)

### Protocol

- **HTTP GET** request
- No authentication (add if needed in backend)
- Synchronous request-response

### Error Handling

- WiFi disconnection: Auto-reconnect
- HTTP error: Logged to serial, request dropped
- Network timeout: Request fails, retried on next cycle

---

## Limitations

> [!WARNING]
> HTTP Gateway has several limitations compared to MQTT Gateway:

| Feature                             | HTTP Gateway             | MQTT Gateway        |
| ----------------------------------- | ------------------------ | ------------------- |
| **Multi-Transmitter**         | ❌ No                    | ✅ Yes              |
| **Station Registry**          | ❌ No                    | ✅ Yes              |
| **GPS Coordinates**           | ❌ No                    | ✅ Yes              |
| **Timestamps**                | ❌ No (backend must add) | ✅ Yes (NTP synced) |
| **Schema.org Compliance**     | ❌ No                    | ✅ Yes              |
| **Sensor Metadata**           | ❌ No                    | ✅ Yes              |
| **Signal Quality (RSSI/SNR)** | ❌ No                    | ✅ Yes              |
| **Device ID**                 | ❌ No                    | ✅ Yes              |
| **CRC Validation**            | ⚠️ Minimal             | ✅ Full             |
| **Data Format**               | Query params             | JSON                |
| **Scalability**               | ⚠️ Limited             | ✅ High             |

---

## Migration to MQTT Gateway

If you need more features, consider migrating to MQTT Gateway:

### Migration Steps

1. **Setup MQTT Broker**

   - Use public broker (broker.emqx.io)
   - Or setup private Mosquitto broker
2. **Update Gateway Firmware**

   - Replace `gateway_http.ino` with `gateway_mqtt.ino`
   - Configure WiFi, MQTT, and station registry
3. **Update Backend**

   - Subscribe to MQTT topics instead of HTTP endpoint
   - Parse JSON instead of query parameters
   - Handle Schema.org format

**[📖 MQTT Gateway Documentation →](json-schema.md)**

---

## Troubleshooting

### WiFi Connection Failed

**Symptoms:** Gateway can't connect to WiFi

**Solutions:**

- Verify SSID and password
- Check WiFi signal strength
- Ensure ESP32 is within range
- Try 2.4GHz WiFi only (ESP32 doesn't support 5GHz)

### HTTP Request Failed

**Symptoms:** `HTTP Response code: -1` or error codes

**Solutions:**

- Verify backend URL is correct
- Check backend server is running
- Ensure ESP32 can reach backend (same network or port forwarding)
- Check firewall settings
- Test backend endpoint manually using browser or Postman

### No Data Received

**Symptoms:** No HTTP requests being sent

**Solutions:**

- Check transmitter is powered and transmitting
- Verify LoRa frequency match (433MHz)
- Check LoRa wiring and antenna
- Monitor serial output for packet reception

### Data Values Wrong

**Symptoms:** Incorrect sensor readings

**Solutions:**

- Verify sensor connections on transmitter
- Check sensor calibration
- Monitor raw LoRa packet data
- Validate data parsing logic

---

## API Reference Summary

### Endpoint

```
GET /weather-data/create
```

### Parameters

```typescript
interface WeatherData {
  temp: number;           // Float, 2 decimals, °C
  humidity: number;        // Float, 2 decimals, %
  pressure: number;        // Float, 2 decimals, hPa
  windSpeed: number;       // Float, 2 decimals, km/h
  isRaining: 0 | 1;       // Integer, boolean
  lightIntensity: number;  // Integer, 0-1023
}
```

### Expected Response

**Success (200):**

```json
{
  "status": "success",
  "message": "Data received"
}
```

**Error (4xx/5xx):**

```json
{
  "status": "error",
  "message": "Error description"
}
```

---

## Related Documentation

- [MQTT Gateway (Recommended)](json-schema.md) - Modern, feature-rich alternative
- [Getting Started Guide](../guides/getting-started.md) - Complete setup guide
- [Pin Reference](../hardware/pin-reference.md) - Hardware wiring
- [Troubleshooting](../guides/troubleshooting.md) - Common issues

---

**Last Updated:** 2025-12-03
