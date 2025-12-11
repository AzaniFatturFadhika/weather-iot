# Transmitter Firmware - Penjelasan Program

## 📋 Deskripsi Umum

Program ini adalah **Transmitter** untuk sistem monitoring cuaca berbasis IoT. Transmitter berfungsi **membaca data dari berbagai sensor cuaca** dan **mengirimkan data via LoRa** ke Gateway setiap 10 detik.

## 🔧 Hardware yang Digunakan

- **Mikrokontroler**: Arduino Nano
- **Modul Komunikasi**: LoRa SX1278 RA-02 (433MHz)
- **Sensor Cuaca**:
  - **AHT20**: Temperature & Humidity (I2C, akurasi tinggi)
  - **BMP280**: Atmospheric Pressure (I2C)
  - **Anemometer**: Wind Speed (pulse counter, interrupt-based)
  - **Raindrop Sensor**: Rain Detection (digital pin)
  - **LDR**: Light Intensity (analog pin)

## 📡 Pin Configuration (Arduino Nano)

### LoRa Module

```cpp
LORA_SS    = 10  // NSS/CS
LORA_RST   = 9   // Reset
LORA_DIO0  = 2   // DIO0 (interrupt)
```

### Sensors

```cpp
ANEMOMETER_PIN = 3   // Interrupt pin (pulse counter)
RAINDROP_PIN   = A0  // Digital Output dari sensor (LOW=Wet)
LDR_PIN        = A1  // Analog input (0-1023)

AHT20  -> I2C (SDA/SCL) - Default address
BMP280 -> I2C (SDA/SCL) - Address 0x76 atau 0x77
```

---

## 📊 Struktur Data

### WeatherData Structure

```cpp
struct WeatherData {
  float temperature;   // dari AHT20 (°C)
  float humidity;      // dari AHT20 (%)
  float pressure;      // dari BMP280 (hPa)
  float windSpeed;     // dari Anemometer (km/h)
  int rainLevel;       // dari Raindrop (0=Dry, 1=Wet)
  int lightLevel;      // dari LDR (0-1023 ADC)
};
```

### Format Transmisi LoRa

```
DEVICE_ID|temp|hum|press|wind|rain|light|CRC

Contoh:
TX001|28.50|75.30|1010.25|5.20|0|512|A3
  │     │     │      │      │   │  │   └─ CRC (XOR checksum, hex)
  │     │     │      │      │   │  └───── Light level (ADC 0-1023)
  │     │     │      │      │   └──────── Rain (0=Dry, 1=Wet)
  │     │     │      │      └──────────── Wind Speed (km/h)
  │     │     │      └─────────────────── Pressure (hPa)
  │     │     └────────────────────────── Humidity (%)
  │     └──────────────────────────────── Temperature (°C)
  └────────────────────────────────────── Device ID
```

---

## 🔄 Alur Kerja Program

### 1. **Setup (Inisialisasi)**

```cpp
void setup()
```

**Proses:**

1. **Serial Monitor** (9600 baud)
2. **Inisialisasi LoRa**:
   - Frequency: 433MHz
   - **Spreading Factor: 12** (jarak maksimal, ~10km)
   - **Bandwidth: 125kHz**
   - **Coding Rate: 4/8** (koreksi error maksimal)
   - **Tx Power: 20 dBm**
   - **Sync Word: 0x12** (harus sama dengan Gateway)
3. **Inisialisasi AHT20**:
   - I2C communication
   - Primary sensor untuk temperature & humidity
   - Status disimpan di flag `aht20Available`
4. **Inisialisasi BMP280**:
   - I2C address: coba 0x76, jika gagal coba 0x77
   - Konfigurasi oversampling & filter untuk akurasi
   - Status disimpan di flag `bmp280Available`
5. **Setup Anemometer**:
   - Interrupt pada pin 3 (CHANGE mode)
   - Counter untuk menghitung pulsa rotasi
6. **Setup Pin Analog**:
   - Raindrop sensor (digital read dari A0)
   - LDR (analog read dari A1)

### 2. **Loop Utama**

```cpp
void loop()
```

**Timer-based execution** (setiap 10 detik):

1. Baca semua sensor → `readAllSensors()`
2. Kirim data via LoRa → `transmitData()`
3. Print ke Serial Monitor → `printSensorData()`

---

## 📡 Detail Fungsi Pembacaan Sensor

### 1. AHT20 (Temperature & Humidity)

```cpp
sensors_event_t humidity, temp;
aht.getEvent(&humidity, &temp);
```

**Validasi:**

- Temperature: -40°C hingga 80°C
- Humidity: 0% hingga 100%
- Nilai diluar range → set ke 0.0

### 2. BMP280 (Pressure)

```cpp
data.pressure = bmp.readPressure() / 100.0F; // Pascal → hPa
```

**Validasi:**

- Pressure: 300 hPa hingga 1100 hPa (range atmosfer valid)
- Nilai diluar range → set ke 0.0

### 3. Anemometer (Wind Speed)

```cpp
void anemometerISR() {
  anemometerPulseCount++;
}
```

**Perhitungan Kecepatan Angin:**

1. **Hitung rotasi per detik** dari pulse count
2. **Normalisasi** ke basis 1 detik (timeDiff / 1000.0)
3. **Terapkan formula kalibrasi**:
   ```cpp
   windSpeedMs = (2.0 / 18.0) * (rotationsPerSecond / 10.0)
   ```
   - 2.0 m/s = kecepatan pada 18 pulse/second
   - 18.0 = jumlah pulse per rotasi sensor
4. **Konversi ke km/h**: `windSpeed = windSpeedMs * 3.6`

**Catatan**: Menggunakan interrupt untuk menghitung pulsa secara real-time tanpa blocking.

### 4. Raindrop Sensor

```cpp
int rainDigital = digitalRead(RAINDROP_PIN);
data.rainLevel = (rainDigital == LOW) ? 1 : 0;
```

**Logic:**

- **LOW (0V)** = Sensor basah → Rain = **1** (Wet)
- **HIGH (5V)** = Sensor kering → Rain = **0** (Dry)

### 5. LDR (Light Sensor)

```cpp
data.lightLevel = analogRead(LDR_PIN); // 0-1023
```

**Range:**

- 0 = gelap total
- 1023 = terang maksimal (10-bit ADC)

---

## 📤 Proses Transmisi Data

### CRC Checksum Generation

```cpp
uint8_t crc = 0;
for (int i = 0; i < payload.length(); i++) {
  crc ^= payload[i];  // XOR checksum
}
```

**Fungsi CRC:**

- Deteksi data corruption saat transmisi
- Simple XOR dari semua byte payload
- Gateway akan validasi dan reject jika tidak cocok

### LoRa Transmission

```cpp
LoRa.beginPacket();
LoRa.print(payload);
LoRa.endPacket();
```

**Karakteristik:**

- **Airtime**: ~2-3 detik per packet (karena SF12)
- **Range**: Hingga 10km (line of sight)
- **Reliability**: High error correction (CR 4/8)

---

## 🔧 Kalibrasi Sensor

### Anemometer Calibration

```cpp
#define WIND_SPEED_18_PULSE_SECOND 2.0  // m/s pada 18 pulse/s
#define ONE_ROTATION_SENSOR 18.0        // pulse per rotation
```

**Cara Kalibrasi:**

1. Ukur kecepatan angin referensi (misalnya dengan anemometer standar)
2. Hitung pulse per detik yang terbaca
3. Sesuaikan konstanta `WIND_SPEED_18_PULSE_SECOND`

### Raindrop Sensor Threshold

Sensor raindrop module biasanya memiliki potensiometer untuk mengatur sensitivitas:

- Putar **clockwise** = lebih sensitif (trigger lebih mudah)
- Putar **counter-clockwise** = kurang sensitif

---

## ⚙️ Konfigurasi

### Mengubah Device ID

```cpp
const String DEVICE_ID = "TX001"; // Ubah sesuai kebutuhan
```

### Mengubah Interval Transmit

```cpp
const unsigned long TRANSMIT_INTERVAL = 10000; // dalam milliseconds
```

**Perhatian**: Interval harus **SELARAS** dengan retry interval di Gateway!

---

## 📊 Serial Monitor Output

```
===== Sensor Readings (Optimized + Validated) =====
[AHT20] Temperature: 28.50 °C
[AHT20] Humidity: 75.30 %
[BMP280] Pressure: 1010.25 hPa
[Anemometer] Wind Speed: 5.20 km/h
[Raindrop] Rain Level: 0 (0=Dry, 1=Wet)
[LDR] Light Level: 512 (0-1023 ADC)
===================================================

Data transmitted: TX001|28.50|75.30|1010.25|5.20|0|512|A3
CRC: 0xA3
```

---

## 🐛 Troubleshooting

| Problem                      | Possible Cause           | Solution                                |
| ---------------------------- | ------------------------ | --------------------------------------- |
| AHT20 init failed            | I2C connection issue     | Check SDA/SCL wiring, pull-up resistors |
| BMP280 init failed           | Wrong I2C address        | Try both 0x76 and 0x77                  |
| Wind speed always 0          | Anemometer not connected | Check interrupt pin 3, ensure PULLUP    |
| Invalid temperature/humidity | Sensor out of range      | Check sensor placement, wiring          |
| Rain sensor tidak sensitif   | Threshold terlalu tinggi | Putar potentiometer searah jarum jam    |
| Data tidak diterima Gateway  | LoRa config mismatch     | Pastikan SF, BW, CR, SyncWord SAMA      |

---

## 🔒 Best Practices

### Power Management

- Gunakan voltage regulator stabil (5V untuk Arduino Nano)
- Pastikan supply cukup untuk peak current LoRa (120mA saat TX)

### Sensor Placement

- **AHT20/BMP280**: Lindungi dari hujan langsung, ventilasi baik
- **Anemometer**: Posisi terbuka, bebas obstacle
- **Raindrop**: Posisi miring 45° untuk drainase optimal
- **LDR**: Arahkan ke atas untuk cahaya ambient

### Maintenance

- Bersihkan raindrop sensor secara berkala (kotoran → false positive)
- Check rotasi anemometer (bearing bisa macet)
- Kalibrasi ulang setiap 6 bulan

---

## 📈 Optimizations

Program ini sudah dioptimasi dengan:

- ✅ **Interrupt-based anemometer** (non-blocking)
- ✅ **Atomic read-reset** counter (dengan `noInterrupts()`)
- ✅ **Range validation** untuk semua sensor
- ✅ **Simplified data structure** (lebih efisien)
- ✅ **CRC integrity check**
- ✅ **Long range LoRa config** (SF12 untuk jarak maksimal)

---

**Developer**: IoT Weather Monitoring Team  
**Last Updated**: December 2025  
**Version**: 2.0 (Optimized with AHT20)
