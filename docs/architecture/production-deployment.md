# Implementasi Real-World Weather Station: Standar Industri

## 📊 Arsitektur End-to-End Production-Ready

### **Gambaran Sistem Lengkap**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 1: FIELD DEVICES                       │
│  (Transmitter di berbagai lokasi kecamatan)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                    LoRa 433MHz (2-15km)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 2: GATEWAY HUB                         │
│  ESP32-S3 Gateway di Kantor Kabupaten                          │
│  - Terima data LoRa                                             │
│  - Data normalization                                           │
│  - Station registry lookup                                      │
│  - NTP time sync                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                      MQTT (TLS/SSL)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LAYER 3: MESSAGE BROKER                        │
│  MQTT Broker (Mosquitto / EMQX / HiveMQ)                       │
│  - Topic routing                                                │
│  - QoS guarantee                                                │
│  - Authentication & authorization                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Layer 4A   │  │   Layer 4B   │  │   Layer 4C   │
    │  Data Store  │  │  Processing  │  │ Realtime App │
    └──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🏢 Real-Case: Monitoring Cuaca Kabupaten Semarang

### **Requirement**
- **Cakupan:** 16 kecamatan di Kabupaten Semarang
- **Update Rate:** Data setiap 10 detik dari setiap stasiun
- **Stakeholder:** 
  - Pemerintah daerah (monitoring cuaca real-time)
  - BMKG lokal (data historis)
  - Masyarakat (public dashboard)
  - Petani (alert curah hujan)

### **Deployment Topology**

```
Kantor Kabupaten (Gateway Hub)
├── Server Room
│   ├── ESP32-S3 Gateway (primary)
│   ├── ESP32-S3 Gateway (backup - redundancy)
│   ├── Mini PC / Raspberry Pi 4 (local processing)
│   └── UPS (uninterruptible power supply)
│
Field Stations (16 kecamatan):
├── TX001 - Kec. Semarang Utara (Coastal)
├── TX002 - Kec. Semarang Barat (Urban)
├── TX003 - Kec. Genuk (Industrial)
├── TX004 - Kec. Mijen (Agriculture)
├── TX005 - Kec. Gunungpati (Highland)
├── ... (11 more stations)
└── TX016 - Kec. Bancak (Rural)
```

---

## 🔧 Layer 4A: Data Storage & Time-Series Database

### **Opsi 1: InfluxDB (Recommended untuk Weather Data)**

**Kenapa InfluxDB?**
- ✅ Optimized untuk time-series data
- ✅ Efficient storage dengan compression
- ✅ Built-in downsampling & retention policies
- ✅ Native Grafana integration
- ✅ Continuous queries untuk aggregations

**Setup di WSL/Linux:**

```bash
# Install InfluxDB 2.x
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
sudo apt install influxdb2 influxdb2-cli

# Start service
sudo service influxdb start

# Setup initial config
influx setup \
  --username admin \
  --password SecurePassword123 \
  --org SemarangWeather \
  --bucket weather_data \
  --retention 365d
```

**MQTT to InfluxDB Bridge (Telegraf):**

```toml
# /etc/telegraf/telegraf.conf

# Input from MQTT
[[inputs.mqtt_consumer]]
  servers = ["tcp://broker.emqx.io:1883"]
  topics = ["weather/station/data"]
  username = "emqx"
  password = "public"
  data_format = "json"
  
  # Parse JSON fields
  json_time_key = "observationTime"
  json_time_format = "2006-01-02T15:04:05-07:00"
  
  # Tag keys (for filtering)
  tag_keys = [
    "stationID",
    "stationName"
  ]

# Output to InfluxDB
[[outputs.influxdb_v2]]
  urls = ["http://localhost:8086"]
  token = "$INFLUX_TOKEN"
  organization = "SemarangWeather"
  bucket = "weather_data"
```

**Query Example:**

```flux
// Get average temperature per hour for last 7 days
from(bucket: "weather_data")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "temperature_value")
  |> aggregateWindow(every: 1h, fn: mean)
  |> yield(name: "hourly_avg_temp")
```

---

### **Opsi 2: PostgreSQL + TimescaleDB**

**Untuk Analytical Queries & Relational Data:**

```sql
-- Table schema
CREATE TABLE weather_observations (
  time TIMESTAMPTZ NOT NULL,
  station_id TEXT NOT NULL,
  station_name TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  temperature DOUBLE PRECISION,
  humidity DOUBLE PRECISION,
  pressure DOUBLE PRECISION,
  wind_speed DOUBLE PRECISION,
  rain_level INTEGER,
  light_level INTEGER,
  rssi INTEGER,
  snr DOUBLE PRECISION
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('weather_observations', 'time');

-- Create indexes
CREATE INDEX idx_station_time ON weather_observations (station_id, time DESC);
CREATE INDEX idx_location ON weather_observations USING GIST (
  point(longitude, latitude)
);

-- Continuous aggregate (pre-computed hourly averages)
CREATE MATERIALIZED VIEW weather_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', time) AS hour,
  station_id,
  AVG(temperature) as avg_temp,
  AVG(humidity) as avg_humidity,
  MIN(temperature) as min_temp,
  MAX(temperature) as max_temp
FROM weather_observations
GROUP BY hour, station_id;
```

**MQTT to PostgreSQL (Node.js Script):**

```javascript
const mqtt = require('mqtt');
const { Client } = require('pg');

const pgClient = new Client({
  host: 'localhost',
  database: 'weather_db',
  user: 'weather_user',
  password: 'secure_password'
});

const mqttClient = mqtt.connect('mqtt://broker.emqx.io', {
  username: 'emqx',
  password: 'public'
});

mqttClient.on('message', async (topic, message) => {
  const data = JSON.parse(message.toString());
  
  await pgClient.query(`
    INSERT INTO weather_observations (
      time, station_id, station_name, latitude, longitude,
      temperature, humidity, pressure, wind_speed,
      rain_level, light_level, rssi, snr
    ) VALUES (
      $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
    )
  `, [
    data.observationTime,
    data.stationID,
    data.stationName,
    data.location.latitude,
    data.location.longitude,
    parseFloat(data.temperature.value),
    parseFloat(data.humidity.value),
    parseFloat(data.pressure.value),
    parseFloat(data.windSpeed.value),
    data.precipitation.rawLevel,
    data.illuminance.rawLevel,
    data.signal.rssi,
    parseFloat(data.signal.snr)
  ]);
});

mqttClient.subscribe('weather/station/data');
```

---

## 📊 Layer 4B: Data Processing & Analytics (Node-RED)

### **Node-RED: Visual Programming untuk IoT**

**Install:**
```bash
npm install -g --unsafe-perm node-red
npm install -g node-red-dashboard
npm install -g node-red-contrib-influxdb
```

**Flow Example:**

```json
[
  {
    "id": "mqtt_in",
    "type": "mqtt in",
    "topic": "weather/station/data",
    "broker": "broker.emqx.io"
  },
  {
    "id": "parse_json",
    "type": "json"
  },
  {
    "id": "validate",
    "type": "function",
    "func": "if (msg.payload.temperature.value < -40 || msg.payload.temperature.value > 60) {\n  return null;\n}\nreturn msg;"
  },
  {
    "id": "alert_high_temp",
    "type": "switch",
    "property": "payload.temperature.value",
    "rules": [
      {"t": "gt", "v": "35"}
    ]
  },
  {
    "id": "send_telegram",
    "type": "telegram sender",
    "chatId": "YOUR_CHAT_ID",
    "message": "⚠️ Suhu tinggi di {{payload.stationName}}: {{payload.temperature.value}}°C"
  },
  {
    "id": "store_influx",
    "type": "influxdb out",
    "database": "weather_data"
  }
]
```

**Use Cases:**
1. **Alerting:** Kirim notifikasi Telegram/WhatsApp saat suhu >35°C
2. **Data Enrichment:** Tambah weather forecast dari API eksternal
3. **Aggregation:** Hitung rata-rata regional per jam
4. **Integration:** Forward ke API pemerintah daerah

---

## 📈 Layer 4C: Visualization & Dashboard (Grafana)

### **Grafana Dashboard Setup**

**Install:**
```bash
sudo apt-get install -y grafana
sudo service grafana-server start
```

**Dashboard Panels:**

1. **Map View (Worldmap Panel)**
   ```json
   {
     "type": "grafana-worldmap-panel",
     "query": "SELECT latitude, longitude, temperature FROM weather_observations WHERE time > now() - 1h",
     "locationData": "json endpoint"
   }
   ```

2. **Time Series (Temperature Trends)**
   ```flux
   from(bucket: "weather_data")
     |> range(start: -24h)
     |> filter(fn: (r) => r["_field"] == "temperature_value")
     |> aggregateWindow(every: 10m, fn: mean)
   ```

3. **Stat Panel (Current Values)**
   - Temperature saat ini per stasiun
   - Humidity rata-rata regional
   - Wind speed maximum

4. **Heatmap (Temperature by Hour & Location)**

5. **Table (Latest 10 Observations)**

**Public Dashboard Configuration:**
```ini
# /etc/grafana/grafana.ini

[auth.anonymous]
enabled = true
org_name = SemarangWeather
org_role = Viewer

[security]
allow_embedding = true
```

**Embed di Website Pemerintah:**
```html
<iframe 
  src="http://grafana.semarang.go.id/d/weather-dashboard?orgId=1&refresh=30s&kiosk" 
  width="100%" 
  height="800px"
  frameborder="0">
</iframe>
```

---

## 🔐 Security Best Practices

### **1. MQTT Security**

**TLS/SSL Encryption:**
```bash
# Generate certificates
openssl req -new -x509 -days 365 -extensions v3_ca \
  -keyout ca.key -out ca.crt

# Mosquitto config
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate false
```

**Authentication:**
```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd gateway_user
sudo mosquitto_passwd /etc/mosquitto/passwd dashboard_user

# Enable in config
allow_anonymous false
password_file /etc/mosquitto/passwd
```

**Gateway Code Update:**
```cpp
const char* MQTT_HOST = "mqtt.semarang.go.id";
const int MQTT_PORT = 8883;  // TLS port
const char* MQTT_USER = "gateway_user";
const char* MQTT_PASSWORD = "SecurePassword123";

// Set CA certificate
const char* ca_cert = \
"-----BEGIN CERTIFICATE-----\n" \
"MIIDXTCCAkW...YOUR_CA_CERT...\n" \
"-----END CERTIFICATE-----\n";

mqttClient.setCaCert(ca_cert);
```

### **2. Network Security**

**VPN untuk Gateway:**
```bash
# WireGuard VPN setup
sudo apt install wireguard

# Gateway config
[Interface]
PrivateKey = GATEWAY_PRIVATE_KEY
Address = 10.0.0.2/24

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = server.semarang.go.id:51820
AllowedIPs = 10.0.0.0/24
```

### **3. Data Validation & Sanitization**

```cpp
// Di gateway - tambahkan rate limiting
unsigned long lastPublishTime[16] = {0};  // Max 16 stations

// Dalam parseAndPublish()
int stationIndex = getStationIndex(stationID);
if (millis() - lastPublishTime[stationIndex] < 5000) {
  Serial.println("⚠️ Rate limit: terlalu cepat dari " + stationID);
  return;  // Block spam/DoS
}
lastPublishTime[stationIndex] = millis();
```

---

## 📱 Layer 5: End-User Applications

### **Public Web Dashboard**

**Technology Stack:**
- Frontend: Next.js + React + Leaflet (maps)
- Backend API: Node.js + Express
- Database: PostgreSQL (read replica)

**Features:**
```javascript
// Real-time updates dengan WebSocket
const socket = io('ws://api.semarang.go.id');

socket.on('weather_update', (data) => {
  updateStationMarker(data.stationID, {
    temperature: data.temperature.value,
    humidity: data.humidity.value
  });
});

// Historical data query
fetch('/api/weather/history?station=TX001&range=7d')
  .then(res => res.json())
  .then(data => renderChart(data));
```

### **Mobile App (Flutter)**

```dart
// MQTT subscriber di Flutter
final client = MqttServerClient('mqtt.semarang.go.id', '');

client.subscribe('weather/station/+/data', MqttQos.atMostOnce);

client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> messages) {
  final recMessage = messages[0].payload as MqttPublishMessage;
  final payload = MqttPublishPayload.bytesToStringAsString(
    recMessage.payload.message
  );
  
  final data = jsonDecode(payload);
  updateUI(data);
});
```

### **WhatsApp Bot (Twilio API)**

```javascript
const twilio = require('twilio');

// User subscribe: "CUACA TX001"
// Bot reply dengan data terkini

app.post('/webhook/whatsapp', async (req, res) => {
  const userMessage = req.body.Body;
  const match = userMessage.match(/CUACA (TX\d{3})/);
  
  if (match) {
    const stationID = match[1];
    const weather = await getLatestWeather(stationID);
    
    const reply = `
🌡️ *${weather.stationName}*
Suhu: ${weather.temperature}°C
Kelembaban: ${weather.humidity}%
Tekanan: ${weather.pressure} hPa
Angin: ${weather.windSpeed} km/h
    `;
    
    twilioClient.messages.create({
      from: 'whatsapp:+14155238886',
      to: req.body.From,
      body: reply
    });
  }
});
```

---

## 🚨 Monitoring & Alerting System

### **System Health Monitoring**

**Prometheus + Grafana Stack:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mqtt_broker'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'gateway_health'
    static_configs:
      - targets: ['gateway.local:8080']
```

**Alert Rules:**
```yaml
groups:
  - name: weather_station_alerts
    rules:
      - alert: StationOffline
        expr: time() - station_last_seen > 300
        labels:
          severity: warning
        annotations:
          summary: "Stasiun {{ $labels.station_id }} offline"
      
      - alert: HighTemperature
        expr: temperature_celsius > 35
        labels:
          severity: critical
        annotations:
          summary: "Suhu tinggi di {{ $labels.station_name }}"
      
      - alert: LowBattery
        expr: battery_voltage < 3.3
        labels:
          severity: warning
```

### **Log Aggregation (ELK Stack)**

```bash
# Filebeat (collect logs)
filebeat.inputs:
  - type: log
    paths:
      - /var/log/mosquitto/*.log
      - /var/log/gateway/*.log

# Logstash (parse & filter)
filter {
  if [type] == "mqtt" {
    json {
      source => "message"
    }
    date {
      match => ["observationTime", "ISO8601"]
    }
  }
}

# Elasticsearch (store)
# Kibana (visualize)
```

---

## 📐 Scalability Considerations

### **Horizontal Scaling**

```
Load Balancer (NGINX)
├── Gateway Cluster 1 (Active)
├── Gateway Cluster 2 (Standby)
└── Gateway Cluster 3 (Future expansion)

MQTT Broker Cluster
├── Node 1 (Primary)
├── Node 2 (Secondary)
└── Node 3 (Tertiary)

Database Cluster
├── InfluxDB Primary (Write)
├── InfluxDB Replica 1 (Read)
└── InfluxDB Replica 2 (Read)
```

### **Data Retention Policy**

```sql
-- Raw data: 90 days
CREATE RETENTION POLICY "raw_data" ON "weather_db" 
  DURATION 90d REPLICATION 1 DEFAULT;

-- 10-minute averages: 1 year
CREATE RETENTION POLICY "downsampled_10m" ON "weather_db" 
  DURATION 365d REPLICATION 1;

-- Hourly averages: 5 years
CREATE RETENTION POLICY "downsampled_1h" ON "weather_db" 
  DURATION 1825d REPLICATION 1;

-- Continuous query untuk downsampling
CREATE CONTINUOUS QUERY "cq_10m_avg" ON "weather_db"
BEGIN
  SELECT mean("temperature") AS "temperature"
  INTO "downsampled_10m"."weather"
  FROM "raw_data"."weather"
  GROUP BY time(10m), "station_id"
END;
```

---

## 💰 Cost Estimation (Budget Tahunan)

### **Hardware (One-time)**
- 16x Arduino Nano + sensors: $50 × 16 = **$800**
- 1x ESP32-S3 Gateway: **$15**
- 1x Mini PC (Intel NUC): **$300**
- 16x Solar panel + battery (optional): $100 × 16 = **$1,600**
- **Total Hardware: ~$2,715**

### **Infrastructure (Annual)**
- Cloud VPS (4GB RAM, 2 vCPU): $10/mo × 12 = **$120/year**
- Domain & SSL: **$15/year**
- MQTT broker (managed EMQX Cloud): $0 (free tier) - $300/year
- Backup storage (1TB): **$60/year**
- **Total Infrastructure: ~$195-495/year**

### **Maintenance**
- 1 technician (part-time): **$3,000/year**
- Internet (dedicated line): $50/mo × 12 = **$600/year**
- **Total Maintenance: ~$3,600/year**

**Grand Total Year 1: ~$6,500-7,000**  
**Recurring (Year 2+): ~$4,000/year**

---

## ✅ Deployment Checklist

### **Phase 1: Proof of Concept (2 weeks)**
- [ ] Deploy 1 transmitter + 1 gateway
- [ ] Setup local MQTT broker
- [ ] Verify data flow
- [ ] Create basic Grafana dashboard

### **Phase 2: Pilot (1 month)**
- [ ] Deploy 3 transmitters (different locations)
- [ ] Setup InfluxDB + Telegraf
- [ ] Configure Node-RED flows
- [ ] Implement alerting (email/SMS)
- [ ] Public dashboard beta

### **Phase 3: Production (3 months)**
- [ ] Deploy all 16 transmitters
- [ ] Migrate to production MQTT broker (TLS)
- [ ] Setup PostgreSQL replication
- [ ] Launch public website
- [ ] Mobile app (Android/iOS)
- [ ] WhatsApp bot integration
- [ ] SLA monitoring (99.5% uptime target)

### **Phase 4: Operations (Ongoing)**
- [ ] Weekly maintenance checks
- [ ] Monthly data quality reports
- [ ] Quarterly hardware inspection
- [ ] Annual calibration of sensors

---

## 📚 Standards & Compliance

### **Data Format:**
- ✅ ISO 8601 timestamps
- ✅ WGS84 coordinate system
- ✅ SI units (Celsius, hPa, km/h)
- ✅ JSON-LD schema.org/WeatherObservation

### **API Standards:**
- ✅ RESTful API design
- ✅ OpenAPI 3.0 documentation
- ✅ Rate limiting (100 req/min)
- ✅ CORS enabled for public dashboard

### **Security:**
- ✅ MQTT over TLS
- ✅ OAuth 2.0 for API access
- ✅ GDPR compliance (data privacy)
- ✅ Regular security audits

---

**Sistem weather station Anda siap untuk deployment production-level!** 🚀
