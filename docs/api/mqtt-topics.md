# MQTT Topics Reference

Complete reference for MQTT topic structure and usage.

---

## 📡 Topic Structure

```
weather/
├── station/
│   ├── data          # Weather observations (published by gateway)
│   └── status        # Gateway health status
└── config/           # (Future) Configuration updates
    └── {stationID}
```

---

## 📊 Topics Detail

### `weather/station/data`

**Publisher:** Gateway  
**Frequency:** Every 10 seconds (per transmitter)  
**QoS:** 0 (At most once)  
**Retained:** No

**Payload:** [JSON WeatherObservation](json-schema.md)

**Example:**
```json
{
  "@context": "https://schema.org",
  "@type": "WeatherObservation",
  "stationID": "TX001",
  "observationDate": "2025-11-23T12:00:00+07:00",
  ...
}
```

**Subscribe:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 -u emqx -P public \
  -t "weather/station/data" -v
```

**Filter by Station:**
```javascript
// In code, filter by stationID field
if (data.stationID === "TX001") { ... }
```

---

### `weather/station/status`

**Publisher:** Gateway  
**Frequency:** Every 60 seconds  
**QoS:** 0  
**Retained:** Yes

**Payload:**
```json
{
  "gateway_id": "ESP32_Gateway_001",
  "uptime": 3600,
  "wifi_rssi": -45,
  "wifi_ip": "192.168.1.100",
  "mqtt_connected": true,
  "free_heap": 250000
}
```

**Subscribe:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 \
  -t "weather/station/status" -v
```

**Use Case:** Monitor gateway health

---

## 🎯 Usage Patterns

### Pattern 1: Real-time Dashboard

```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://broker.emqx.io');

client.subscribe('weather/station/data');

client.on('message', (topic, message) => {
  const data = JSON.parse(message);
  updateDashboard(data.stationID, data);
});
```

### Pattern 2: Regional Filtering

```python
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    # Filter by location
    lat = data['geo']['latitude']
    lon = data['geo']['longitude']
    
    if is_in_region(lat, lon, SEMARANG_REGION):
        process_data(data)
```

### Pattern 3: Multi-Topic Subscribe

```bash
# Subscribe to all weather topics
mosquitto_sub -h broker.emqx.io -p 1883 \
  -t "weather/#" -v
```

---

## 📝 Topic Naming Conventions

**Format:** `{domain}/{entity}/{action}`

- ✅ Good: `weather/station/data`
- ❌ Bad: `weatherData` or `data/weather`

**Best Practices:**
- Use lowercase
- Use `/` as separator
- Be hierarchical
- Be specific

---

## 🔐 Security Considerations

### Authentication

**Production:**
```cpp
const char* MQTT_USER = "weather_gateway";
const char* MQTT_PASSWORD = "SecurePassword123";
```

### Topic ACL (Mosquitto)

```
# /etc/mosquitto/acl
user weather_gateway
topic write weather/station/data
topic write weather/station/status

user dashboard_user
topic read weather/#
```

---

## 📈 Scalability

**Multiple Gateways:**
```
weather/
├── gateway1/
│   ├── station/data
│   └── station/status
└── gateway2/
    ├── station/data
    └── station/status
```

**Per-Station Topics (Alternative):**
```
weather/
├── TX001/
│   ├── data
│   └── status
├── TX002/
    ├── data
    └── status
```

**Current approach** (single `weather/station/data`) is recommended for simplicity. Filter by `stationID` field in payload.

---

## 🔍 Debugging

**View all messages:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 -t "#" -v
```

**Count messages:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 -t "weather/station/data" | wc -l
```

**Monitor rate:**
```bash
watch -n 1 'mosquitto_sub -h broker.emqx.io -p 1883 -t "weather/station/data" -C 10'
```
