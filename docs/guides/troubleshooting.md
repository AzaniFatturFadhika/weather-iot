# Troubleshooting Guide

Common problems and solutions for Weather IoT system.

---

## 🔧 Transmitter Issues

### ❌ LoRa init failed!

**Symptoms:**
```
LoRa init failed!
```

**Causes & Solutions:**

1. **Wiring Issue**
   - Check all LoRa connections
   - Verify SPI pins (MISO, MOSI, SCK, NSS)
   - Ensure DIO0 connected to D2

2. **Power Issue**
   - LoRa module needs 3.3V (not 5V!)
   - Check power supply current (>100mA)

3. **Bad Module**
   - Try different LoRa module
   - Check with multimeter: VCC should be 3.3V

---

### ⚠️ Sensor readings = 0.0

**Symptoms:**
```
[AHT20] Temperature: 0.00 °C
[AHT20] Humidity: 0.00 %
```

**Solutions:**

1. **AHT20/BMP280 not detected**
   ```
   - Check I2C wiring (SDA=A4, SCL=A5)
   - Try I2C scanner sketch
   - Verify sensor address (AHT20=0x38, BMP280=0x76 or 0x77)
   ```

2. **Sensor out of range**
   - Values >80°C or <-40°C are invalid
   - Check sensor not overheating

---

### 📡 Data not transmitting

**Check Serial Monitor:**
```
Data transmitted: TX001|28.5|65.2|1013.25|...
CRC: 0x3F
```

If NOT showing:
- Loop not running → Check `delay()` in code
- LoRa.beginPacket() failing → Reinit LoRa

---

## 🌐 Gateway Issues

### ❌ WiFi connection failed!

**Symptoms:**
```
Connecting to WiFi: YourWiFi
....................
✗ WiFi connection failed!
```

**Solutions:**

1. **Wrong Credentials**
   ```cpp
   const char* WIFI_SSID = "YourActualWiFiName";  // Case sensitive!
   const char* WIFI_PASSWORD = "YourActualPassword";
   ```

2. **WiFi Out of Range**
   - Move gateway closer to router
   - Check WiFi signal strength

3. **2.4GHz Only**
   - ESP32 only supports 2.4GHz WiFi
   - Switch router to 2.4GHz or mixed mode

---

### ❌ MQTT client failed to start!

**Symptoms:**
```
✗ MQTT client failed to start!
```

**Solutions:**

1. **Wrong Broker Address**
   ```cpp
   const char* MQTT_HOST = "broker.emqx.io";  // No 'http://'!
   const int MQTT_PORT = 1883;  // Not 8083 or 8883
   ```

2. **Broker Offline**
   - Test broker: `ping broker.emqx.io`
   - Try alternative: `test.mosquitto.org`

3. **Network Firewall**
   - Check firewall allows outbound port 1883
   - Try different network

---

### ⏰ NTP sync timeout

**Symptoms:**
```
⚠ NTP sync timeout - using millis() for timestamp
```

**Impact:** Timestamps will be uptime instead of real time

**Solutions:**

1. **No Internet**
   - Check internet connectivity
   - Try: `ping pool.ntp.org`

2. **NTP Server Blocked**
   - Firewall blocking UDP port 123
   - Try different NTP server:
     ```cpp
     const char* NTP_SERVER = "time.google.com";
     ```

3. **Not Critical**
   - System still works with `uptimeMs`
   - Fix network and restart gateway

---

### ✗ CRC MISMATCH! Data corrupted

**Symptoms:**
```
✗ CRC MISMATCH! Data corrupted.
  Expected: 0x3F
  Received: 0x2A
```

**Causes:**

1. **LoRa Frequency Mismatch**
   - Transmitter & Gateway must both use 433E6
   - Check: `LoRa.begin(433E6)`

2. **Interference**
   - Other 433MHz devices nearby
   - Move devices apart
   - Try different location

3. **Weak Signal**
   - RSSI < -100 dBm is too weak
   - Move transmitter closer
   - Check antennas connected

4. **Rare Corruption**
   - CRC is working! (rejected bad data)
   - Occasional mismatch is normal
   - Concern if >10% packets fail

---

### ⚠️ Stasiun tidak dikenal: TX002

**Symptoms:**
```
⚠️ Stasiun tidak dikenal: TX002
```

**Cause:** Transmitter ID not in gateway registry

**Solution:**

Add to `stationRegistry[]`:
```cpp
StationConfig stationRegistry[] = {
  {"TX001", "Station 1", ...},
  {"TX002", "Station 2", ...},  // ← Add this
};

const int STATION_COUNT = 2;  // ← Update this
```

**[📖 Adding Transmitter Guide →](adding-transmitter.md)**

---

## 📊 Data Issues

### JSON parsing errors in MQTT subscriber

**Symptoms:** Backend can't parse JSON

**Solutions:**

1. **Check JSON Format**
   - View raw MQTT message
   - Validate at jsonlint.com

2. **Field Name Changes**
   - v2.0 uses `observationDate` not `observationTime`
   - v2.0 uses `geo` not `location`
   - Update backend parsers

3. **Character Encoding**
   - Ensure UTF-8
   - Check special characters in station names

---

### Values seem wrong

**Temperature too high/low:**
- Check sensor placement (not in direct sun)
- Verify sensor calibration
- AHT20 range: -40 to 80°C

**Pressure unrealistic:**
- BMP280 range: 300-1100 hPa
- Check elevation setting
- Sea level pressure ≈ 1013 hPa

**Wind speed always 0:**
- Check anemometer wiring
- Verify interrupt on D3
- Test with manual rotation

---

## 🔍 Debugging Tips

### Enable Verbose Logging

**ESP32 (Gateway):**
```cpp
mqttClient.enableDebuggingMessages(true);  // Already enabled
```

**Check Serial Monitor:**
- 115200 baud
- Both NL & CR line ending

### MQTT Debugging

**Subscribe to all topics:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 -t "#" -v
```

**Check connection:**
```bash
mosquitto_sub -h broker.emqx.io -p 1883 -t "weather/station/status" -v
```

### Test Components Separately

**LoRa Test:**
- Upload LoRa ping/pong example
- Verify communication works

**Sensor Test:**
- Comment out LoRa code
- Print sensors to Serial only

**MQTT Test:**
- Use MQTT.fx or MQTT Explorer
- Publish test message manually

---

## 📞 Getting Help

If problem persists:

1. **Check Documentation**
   - [Getting Started](getting-started.md)
   - [Pin Reference](../hardware/pin-reference.md)
   - [API Schema](../api/json-schema.md)

2. **Common Patterns**
   - 90% issues are wiring or configuration
   - Check power supply first
   - Verify WiFi/MQTT credentials

3. **File Issue**
   - GitHub Issues (if open source)
   - Include: Serial monitor output, code snippet, hardware setup

---

## ✅ Health Check Checklist

Run this checklist when things aren't working:

**Transmitter:**
- [ ] Power LED on
- [ ] Serial monitor shows sensor readings
- [ ] LoRa initialized successfully
- [ ] Data transmitted message appears
- [ ] CRC value shown

**Gateway:**
- [ ] Power LED on
- [ ] WiFi connected (IP shown)
- [ ] NTP sync successful (time shown)
- [ ] MQTT client started
- [ ] LoRa packets received
- [ ] CRC validation passed
- [ ] Published to MQTT

**System:**
- [ ] MQTT messages received by subscriber
- [ ] JSON valid
- [ ] Values realistic
- [ ] Timestamps correct (if NTP synced)
