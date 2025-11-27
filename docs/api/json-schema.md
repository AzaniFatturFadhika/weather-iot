# JSON Schema Reference

Complete reference for Weather IoT MQTT JSON messages.

---

## 📡 Message Format (Schema.org Compliant)

### Full Example

```json
{
  "@context": "https://schema.org",
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "gatewayID": "ESP32_Gateway_001",
  "name": "Kec. Semarang Utara",
  "observationDate": "2025-11-23T12:00:00+07:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -6.9600,
    "longitude": 110.4200,
    "elevation": 10.0
  },
  "sensors": ["AHT20", "BMP280", "Anemometer", "Raindrop", "LDR"],
  "temperature": {
    "@type": "QuantitativeValue",
    "value": "28.50",
    "unitCode": "CEL",
    "unitText": "°C",
    "sensor": "AHT20"
  },
  "humidity": {
    "@type": "QuantitativeValue",
    "value": "65.20",
    "unitCode": "P1",
    "unitText": "%",
    "sensor": "AHT20"
  },
  "atmosphericPressure": {
    "@type": "QuantitativeValue",
    "value": "1013.25",
    "unitCode": "HPA",
    "unitText": "hPa",
    "sensor": "BMP280"
  },
  "windSpeed": {
    "@type": "QuantitativeValue",
    "value": "5.20",
    "unitCode": "KMH",
    "unitText": "km/h",
    "sensor": "Anemometer"
  },
  "precipitation": {
    "@type": "QuantitativeValue",
    "rawLevel": 100,
    "unitCode": "ADC",
    "unitText": "ADC (0-1023)",
    "sensor": "Raindrop",
    "note": "0=basah, 1023=kering"
  },
  "illuminance": {
    "@type": "QuantitativeValue",
    "rawLevel": 800,
    "unitCode": "ADC",
    "unitText": "ADC (0-1023)",
    "sensor": "LDR",
    "note": "0=gelap, 1023=terang"
  },
  "signal": {
    "rssi": -45,
    "snr": "9.5",
    "protocol": "LoRa 433MHz"
  }
}
```

---

## 📋 Field Reference

### Root Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `@context` | string | ✅ Yes | Always "https://schema.org" |
| `@type` | string | ✅ Yes | Always "WeatherObservation" |
| `stationID` | string | ✅ Yes | Transmitter ID (e.g., "TX001") |
| `gatewayID` | string | ✅ Yes | Gateway ID |
| `name` | string | ✅ Yes | Station name (human-readable) |
| `observationDate` | string | ✅ Yes | ISO 8601 timestamp |
| `geo` | object | ✅ Yes | GeoCoordinates object |
| `sensors` | array | ✅ Yes | List of sensors used |
| `temperature` | object | ✅ Yes | QuantitativeValue |
| `humidity` | object | ✅ Yes | QuantitativeValue |
| `atmosphericPressure` | object | ✅ Yes | QuantitativeValue |
| `windSpeed` | object | ✅ Yes | QuantitativeValue |
| `precipitation` | object | ✅ Yes | QuantitativeValue |
| `illuminance` | object | ✅ Yes | QuantitativeValue |
| `signal` | object | ✅ Yes | LoRa signal quality |

### GeoCoordinates Object

| Field | Type | Description |
|-------|------|-------------|
| `@type` | string | Always "GeoCoordinates" |
| `latitude` | float | WGS84 latitude |
| `longitude` | float | WGS84 longitude |
| `elevation` | float | Meters above sea level |

### QuantitativeValue Object

| Field | Type | Description |
|-------|------|-------------|
| `@type` | string | Always "QuantitativeValue" |
| `value` | string | Numeric value as string |
| `unitCode` | string | UN/CEFACT unit code |
| `unitText` | string | Human-readable unit |
| `sensor` | string | Sensor name |

### Signal Object

| Field | Type | Description |
|-------|------|-------------|
| `rssi` | integer | Received Signal Strength (dBm) |
| `snr` | string | Signal-to-Noise Ratio (dB) |
| `protocol` | string | "LoRa 433MHz" |

---

## 🔢 Unit Codes (UN/CEFACT)

| Parameter | Code | Text | Range |
|-----------|------|------|-------|
| Temperature | `CEL` | °C | -40 to 80 |
| Humidity | `P1` | % | 0 to 100 |
| Pressure | `HPA` | hPa | 300 to 1100 |
| Wind Speed | `KMH` | km/h | 0+ |
| Rain/Light | `ADC` | ADC | 0 to 1023 |

---

## 📖 Standards Compliance

- ✅ [Schema.org WeatherObservation](https://schema.org/WeatherObservation)
- ✅ [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)
- ✅ [UN/CEFACT Common Codes](https://www.unece.org/cefact/codesfortrade/codes_index.html)
- ✅ [ISO 8601 Date/Time](https://www.iso.org/iso-8601-date-and-time-format.html)
- ✅ [WGS84 Coordinates](https://epsg.io/4326)

---

## 💻 Usage Examples

### Python (MQTT Subscribe)

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    station = data['name']
    temp = float(data['temperature']['value'])
    unit = data['temperature']['unitText']
    
    print(f"{station}: {temp}{unit}")

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.emqx.io", 1883)
client.subscribe("weather/station/data")
client.loop_forever()
```

### Node.js

```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://broker.emqx.io');

client.on('message', (topic, message) => {
  const data = JSON.parse(message.toString());
  
  console.log(`Station: ${data.name}`);
  console.log(`Temp: ${data.temperature.value}${data.temperature.unitText}`);
  console.log(`Location: ${data.geo.latitude}, ${data.geo.longitude}`);
});

client.subscribe('weather/station/data');
```

---

**[📡 MQTT Topics Reference →](mqtt-topics.md)**
