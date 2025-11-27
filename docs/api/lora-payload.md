# LoRa Payload Format

Technical specification for transmitter-to-gateway LoRa packet format.

---

## 📦 Payload Structure

### Format (v2.0-standard)

```
DEVICE_ID|temp|hum|press|wind|rain|light|CRC
```

**Example:**
```
TX001|28.50|65.20|1013.25|5.20|100|800|3F
```

---

## 📋 Field Specification

| Position | Field | Type | Unit | Range | Example |
|----------|-------|------|------|-------|---------|
| 0 | Device ID | String | - | 3-10 chars | `TX001` |
| 1 | Temperature | Float | °C | -40 to 80 | `28.50` |
| 2 | Humidity | Float | % | 0 to 100 | `65.20` |
| 3 | Pressure | Float | hPa | 300 to 1100 | `1013.25` |
| 4 | Wind Speed | Float | km/h | 0+ | `5.20` |
| 5 | Rain Level | Integer | ADC | 0 to 1023 | `100` |
| 6 | Light Level | Integer | ADC | 0 to 1023 | `800` |
| 7 | CRC Checksum | Hex | - | 00 to FF | `3F` |

---

## 🔢 Data Types

### Temperature & Humidity
- **Sensor:** AHT20
- **Precision:** 2 decimal places
- **Format:** `String(value, 2)`

### Pressure
- **Sensor:** BMP280
- **Precision:** 2 decimal places
- **Conversion:** Pascal / 100 = hPa

### Wind Speed
- **Sensor:** Anemometer
- **Calculation:** Pulse counter → rotation/sec → m/s → km/h
- **Precision:** 2 decimal places

### Rain & Light
- **Type:** Analog (ADC)
- **Range:** 0-1023 (10-bit Arduino ADC)
- **Rain:** 0=wet, 1023=dry
- **Light:** 0=dark, 1023=bright

---

## ✅ CRC8 Checksum

### Algorithm: Simple XOR

```cpp
uint8_t crc = 0;
for (int i = 0; i < payload.length(); i++) {
  crc ^= payload[i];
}
```

### Purpose
- Detect data corruption during LoRa transmission
- Gateway validates CRC before processing

### Format
- Hexadecimal string (e.g., `"3F"`)
- Appended to payload with `|` delimiter

---

## 📏 Payload Size

**Typical Size:** 40-45 bytes

**Example Breakdown:**
```
TX001|28.50|65.20|1013.25|5.20|100|800|3F
  5  + 5   + 5   +  7    + 4  + 3  + 3 + 2 = 34 chars
Plus 7 '|' delimiters = 41 bytes total
```

**LoRa Limit:** 256 bytes (plenty of headroom)

---

## 🔄 Version History

### v2.0 (Current)
```
TX001|28.50|65.20|1013.25|5.20|100|800|3F
```
- Added CRC checksum
- Removed redundant sensors (DHT22)
- Optimized to AHT20 + BMP280

### v1.0 (Legacy)
```
TX001|temp_dht|hum_dht|temp_aht|hum_aht|temp_bmp|press|wind|rain|light
```
- 10 fields (redundant)
- No CRC
- Larger payload

---

## 🧪 Payload Examples

### Normal Reading
```
TX001|28.50|65.20|1013.25|5.20|100|800|3F
```

### Hot Day
```
TX001|35.80|45.10|1010.50|12.30|900|950|A2
```

### Rainy Day
```
TX001|24.20|88.50|1005.75|8.10|50|300|1B
```

### Night (Low Light)
```
TX001|22.10|75.30|1012.00|3.50|600|20|C7
```

---

## 🔍 Parsing in Gateway

```cpp
// Split by '|'
String fields[8];
int fieldCount = 0;

for (int i = 0; i <= data.length(); i++) {
  if (data.charAt(i) == '|' || i == data.length()) {
    fields[fieldCount] = data.substring(lastIndex, i);
    fieldCount++;
  }
}

// Validate CRC
String receivedCRC = fields[7];
uint8_t expectedCRC = calculateCRC(payloadWithoutCRC);

if (receivedCRC != String(expectedCRC, HEX)) {
  Serial.println("CRC MISMATCH!");
  return;  // Reject packet
}

// Parse values
String stationID = fields[0];
float temp = fields[1].toFloat();
float hum = fields[2].toFloat();
// ...
```

---

## ⚡ Optimization Trade-offs

| Approach | Size | Pros | Cons |
|----------|------|------|------|
| **Text (Current)** | 41 bytes | Human-readable, easy debug | Larger than binary |
| **Binary** | ~18 bytes | Very compact | Hard to debug, complex parsing |
| **JSON** | ~150 bytes | Self-describing | Too large for LoRa |
| **Protobuf** | ~25 bytes | Compact, typed | Requires schema, complex |

**Decision:** Text format chosen for simplicity and debuggability. Size (41 bytes) is acceptable for LoRa.

---

## 🚀 Future Enhancements

**Possible Additions:**

1. **Sequence Number** (packet loss detection)
   ```
   TX001|12345|28.50|...|3F
          ↑ seq
   ```

2. **Battery Voltage** (power monitoring)
   ```
   TX001|28.50|...|800|3.7|3F
                       ↑ voltage
   ```

3. **Firmware Version**
   ```
   TX001|v2.0|28.50|...|3F
          ↑ version
   ```

**Note:** Each addition increases payload size. Current format optimized for essential data only.

---

## 📚 Related Documentation

- [JSON Schema](json-schema.md) - Gateway output format
- [Data Format Standard](../architecture/data-format.md) - Industry compliance
- [Gateway Code](../../firmware/gateway/) - Parsing implementation
