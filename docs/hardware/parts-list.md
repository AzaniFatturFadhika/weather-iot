# Hardware Parts List (BOM)

Complete Bill of Materials untuk 1 weather station + gateway.

---

## 🛒 Shopping List

### Transmitter Station (1x)

| Item | Qty | Est. Price | Link |
|------|-----|-----------|------|
| Arduino Nano (ATmega328P) | 1 | $3-5 | AliExpress/Amazon |
| LoRa SX1278 RA-02 433MHz | 1 | $3-4 | AliExpress |
| AHT20 Temperature & Humidity Sensor | 1 | $1-2 | AliExpress |
| BMP280 Pressure Sensor (GY-BMP280) | 1 | $1-2 | AliExpress |
| Anemometer (wind speed sensor) | 1 | $5-15 | Amazon/AliExpress |
| Raindrop Sensor Module | 1 | $1-2 | AliExpress |
| LDR 5mm (Light Sensor) | 1 | $0.10 | Local electronics |
| 10kΩ Resistor | 1 | $0.05 | Local electronics |
| Breadboard (400 points) or PCB | 1 | $2-3 | Local/Online |
| Jumper Wires (M-M, M-F) | 20+ | $2 | Local/Online |
| USB Cable (Mini-B) | 1 | $1 | Local/Online |
| 5V Power Supply / Solar Panel | 1 | $3-10 | Depends on choice |
| Weatherproof Enclosure | 1 | $5-10 | Local hardware store |

**Subtotal: $28-58** (depending on antenna, solar, enclosure quality)

---

### Gateway (1x)

| Item | Qty | Est. Price | Link |
|------|-----|-----------|------|
| ESP32-S3 DevKit (N16R8) | 1 | $8-12 | AliExpress/Amazon |
| LoRa SX1278 RA-02 433MHz | 1 | $3-4 | AliExpress |
| Breadboard or PCB | 1 | $2-3 | Local/Online |
| Jumper Wires (M-M, M-F) | 10+ | $1 | Local/Online |
| USB-C Cable | 1 | $2 | Local/Online |
| 5V Power Supply | 1 | $3-5 | Local/Online |
| Enclosure (Optional) | 1 | $3-5 | Local hardware store |

**Subtotal: $22-35**

---

## 💰 Total Budget

| Configuration | Price Range |
|---------------|-------------|
| **Minimal (1 Station + Gateway)** | $50-90 |
| **Standard (1 Station + Gateway)** | $70-110 |
| **With Solar Power** | Add $20-40 |
| **Each Additional Transmitter** | Add $30-60 |

---

## 📦 Recommended Bundles

### Budget Kit ($60)
- Basic components
- No solar
- Simple weatherproof box
- Good for indoor/protected testing

### Standard Kit ($90)
- Quality sensors
- Weatherproof enclosure
- Spare components
- Production-ready

### Solar Kit ($120)
- Standard kit + solar panel
- Battery bank
- Charge controller
- Off-grid capable

---

## 🔧 Tools Required

**Minimum:**
- [ ] Soldering iron (if using permanent PCB)
- [ ] Wire stripper
- [ ] Small screwdriver set
- [ ] Multimeter (for debugging)
- [ ] Hot glue gun (weatherproofing)

**Optional:**
- [ ] Helping hands
- [ ] Heat shrink tubing
- [ ] Cable ties
- [ ] Drill (for enclosure mounting)

---

## 🛡️ Optional Upgrades

### Weather Protection
- **Stevenson Screen**: $20-50 (professional weather station housing)
- **UV-resistant cable glands**: $5-10
- **Silicone sealant**: $3-5

### Power Options
- **Solar Panel (5V 2W)**: $10-20
- **18650 Battery Holder**: $2-5
- **TP4056 Charge Controller**: $1-2
- **Step-up Converter (if needed)**: $2-3

### Sensors Upgrades
- **BME280** (temp+hum+press in one): $3-5 (replaces AHT20+BMP280)
- **UV Sensor (ML8511)**: $3-5
- **Soil Moisture Sensor**: $2-3

### Connectivity
- **LoRa Antenna (external)**: $5-15 (improves range)
- **U.FL to SMA pigtail**: $2-3

---

## 📍 Where to Buy

### International (Cheapest)
- **AliExpress** - Best prices, 2-4 weeks shipping
- **Banggood** - Similar to AliExpress
- **DHgate** - Bulk orders

### Fast Shipping
- **Amazon** - 1-2 days, higher prices
- **eBay** - Varies by seller
- **DigiKey** / **Mouser** - Professional, expensive

### Local (Indonesia)
- **Tokopedia** / **Bukalapak** - Local sellers
- **Electronic stores** - Immediate availability

---

## ⚠️ Important Notes

### Quality Considerations

**LoRa Modules:**
- Ensure 433MHz (not 868MHz or 915MHz)
- Check antenna included or buy separately
- RA-02 recommended (better than RFM95W for beginners)

**Arduino Nano:**
- Clone boards OK for prototyping
- Check bootloader (Old Bootloader common)
- USB chip: CH340 is fine

**Sensors:**
- AHT20/AHT21/AHT25 are similar
- BMP280 (not BMP180) for better accuracy
- Check I2C address (some need solder jumper)

**Power Supply:**
- Arduino Nano: 5V, 500mA min
- ESP32-S3: 5V, 1A recommended
- Consider surge protection for outdoor

---

## 📝 Alternatives

### Transmitter Board
| Option | Pros | Cons | Price |
|--------|------|------|-------|
| **Arduino Nano** | Cheap, easy | Limited memory | $3-5 |
| Arduino Pro Mini | Very small | Needs FTDI adapter | $2-3 |
| ESP8266 | WiFi capable | Higher power | $3-4 |

### Gateway Board
| Option | Pros | Cons | Price |
|--------|------|------|-------|
| **ESP32-S3** | Modern, plenty RAM | Newest | $8-12 |
| ESP32 (original) | Cheaper | Less RAM | $5-8 |
| ESP8266 | Very cheap | Limited RAM | $2-3 |

---

## ✅ Checklist Before Ordering

- [ ] Check LoRa frequency (433MHz for this project)
- [ ] Verify shipping time acceptable
- [ ] Compare prices across platforms
- [ ] Order spare components (10% extra)
- [ ] Check return policy
- [ ] Verify voltage compatibility (5V/3.3V)

---

**[🔌 Next: Assembly Guide →](assembly-guide.md)**
