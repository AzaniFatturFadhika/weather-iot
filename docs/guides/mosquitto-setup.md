# Panduan Setup Mosquitto MQTT Broker di WSL

Panduan ini menjelaskan cara menginstal dan mengkonfigurasi Mosquitto MQTT Broker di WSL (Windows Subsystem for Linux) untuk menerima data dari ESP32 Gateway Weather Station.

## 📋 Prerequisites

- WSL sudah terinstal (Ubuntu recommended)
- ESP32 Gateway dan WSL berada di jaringan yang sama
- Akses sudo di WSL

## 🔧 Langkah 1: Install Mosquitto di WSL

Buka WSL terminal dan jalankan:

```bash
# Update package list
sudo apt update

# Install Mosquitto broker dan client tools
sudo apt install mosquitto mosquitto-clients -y

# Cek versi yang terinstal
mosquitto -h
```

## 🔧 Langkah 2: Konfigurasi Mosquitto

### 2.1 Backup Konfigurasi Default

```bash
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup
```

### 2.2 Buat File Konfigurasi Baru

```bash
sudo nano /etc/mosquitto/conf.d/iot-weather.conf
```

### 2.3 Tambahkan Konfigurasi Berikut

```conf
# Port MQTT
listener 1883

# Izinkan koneksi dari semua IP (penting untuk ESP32 terhubung)
bind_address 0.0.0.0

# Izinkan koneksi tanpa autentikasi (untuk testing)
# PERINGATAN: Tidak aman untuk production!
allow_anonymous true

# Log settings
log_dest file /var/log/mosquitto/mosquitto.log
log_type all

# Persistence settings
persistence true
persistence_location /var/lib/mosquitto/
```

**Simpan file**: Tekan `Ctrl+O`, Enter, lalu `Ctrl+X`

> [!WARNING]
> Konfigurasi `allow_anonymous true` tidak aman untuk production. Untuk keamanan yang lebih baik, tambahkan username dan password (lihat bagian optional di bawah).

### 2.4 Set Permissions

```bash
sudo mkdir -p /var/log/mosquitto
sudo chown mosquitto:mosquitto /var/log/mosquitto
sudo chmod 755 /var/log/mosquitto
```

## 🚀 Langkah 3: Start Mosquitto Service

```bash
# Start service
sudo service mosquitto start

# Cek status
sudo service mosquitto status

# Jika ada error, restart
sudo service mosquitto restart
```

## 🌐 Langkah 4: Cari IP Address WSL

ESP32 Gateway perlu tahu IP address WSL untuk terhubung:

```bash
# Cari IP address WSL
ip addr show eth0 | grep "inet "
```

Contoh output:
```
inet 192.168.110.131/20 brd 192.168.111.255 scope global eth0
```

**IP Address WSL Anda**: `192.168.110.131` ✅

> [!IMPORTANT]
> Pastikan `MQTT_HOST` di `gateway.ino` **HANYA berisi IP address tanpa port**:
> ```cpp
> const char* MQTT_HOST = "192.168.110.131";  // ✅ BENAR
> const char* MQTT_HOST = "192.168.110.131:1883";  // ❌ SALAH
> ```
> Port didefinisikan terpisah di `MQTT_PORT = 1883;`

## 🔥 Langkah 5: Konfigurasi Windows Firewall (PENTING!)

Windows Firewall mungkin memblokir koneksi ke WSL. Buka **PowerShell sebagai Administrator**:

```powershell
# Allow incoming connection ke port 1883
New-NetFirewallRule -DisplayName "MQTT Mosquitto WSL" -Direction Inbound -Protocol TCP -LocalPort 1883 -Action Allow

# Atau jika sudah ada, enable rule
Set-NetFirewallRule -DisplayName "MQTT Mosquitto WSL" -Enabled True
```

## 🧪 Langkah 6: Testing Broker

### 6.1 Test Subscribe (Terminal 1)

Buka WSL terminal pertama untuk monitoring pesan:

```bash
# Subscribe ke semua topic weather station
mosquitto_sub -h localhost -t "weather/#" -v
```

### 6.2 Test Publish (Terminal 2)

Buka WSL terminal kedua untuk tes kirim pesan:

```bash
# Test publish ke topic weather/station/data
mosquitto_pub -h localhost -t "weather/station/data" -m '{"test": "hello from mosquitto"}'
```

Jika berhasil, terminal 1 akan menampilkan pesan tersebut! ✅

### 6.3 Test dari Windows (PowerShell)

Test apakah broker bisa diakses dari Windows:

```powershell
# Install Python MQTT client
pip install paho-mqtt

# Test dengan Python
python -c "import paho.mqtt.publish as publish; publish.single('test', 'Hello WSL', hostname='192.168.110.131')"
```

## 📡 Langkah 7: Monitor Data dari ESP32 Gateway

Setelah ESP32 Gateway menyala dan terhubung, monitor data real-time:

```bash
# Subscribe ke data cuaca
mosquitto_sub -h localhost -t "weather/station/data" -v

# Atau monitor semua topic
mosquitto_sub -h localhost -t "#" -v
```

Anda akan melihat data JSON seperti ini:

```json
{
  "device_id": "TX001",
  "timestamp": 123456,
  "temperature": {
    "dht22": 28.5,
    "bmp280": 28.3,
    "aht20": 28.4,
    "average": 28.4
  },
  "humidity": {
    "dht22": 65.2,
    "aht20": 64.8,
    "average": 65.0
  },
  "pressure": 1013.25,
  "wind_speed": 5.2,
  "rain_level": 100,
  "light_level": 800,
  "signal": {
    "rssi": -45,
    "snr": 9.5
  }
}
```

## 🔐 [OPTIONAL] Tambahkan Autentikasi

Untuk keamanan lebih baik, tambahkan username dan password:

```bash
# Buat password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd mqtt_user

# Enter password saat diminta
```

Update konfigurasi `/etc/mosquitto/conf.d/iot-weather.conf`:

```conf
listener 1883
bind_address 0.0.0.0

# Aktifkan autentikasi
allow_anonymous false
password_file /etc/mosquitto/passwd

log_dest file /var/log/mosquitto/mosquitto.log
log_type all
persistence true
persistence_location /var/lib/mosquitto/
```

Restart Mosquitto:

```bash
sudo service mosquitto restart
```

**Update gateway.ino**:

```cpp
const char* MQTT_USER = "mqtt_user";
const char* MQTT_PASSWORD = "your_password";
```

## 🛠️ Troubleshooting

### Problem: Mosquitto tidak bisa start

```bash
# Cek log error
sudo tail -f /var/log/mosquitto/mosquitto.log

# Cek konfigurasi
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

### Problem: ESP32 tidak bisa connect

1. **Cek IP WSL**: `ip addr show eth0`
2. **Cek MQTT_HOST di gateway.ino**: Pastikan TIDAK ada port (`:1883`)
3. **Ping dari Windows ke WSL**: `ping 192.168.110.131`
4. **Cek firewall**: Pastikan port 1883 terbuka
5. **Cek log Mosquitto**: `sudo tail -f /var/log/mosquitto/mosquitto.log`

### Problem: WSL IP berubah setelah restart

WSL IP bisa berubah. Solusi:

1. **Set static IP WSL** (recommended)
2. **Gunakan hostname Windows**: `YOUR-PC-NAME.local`
3. **Gunakan MQTT broker publik** untuk testing: `broker.hivemq.com`

## 🔄 Auto-start Mosquitto (Optional)

Agar Mosquitto start otomatis saat WSL dibuka:

```bash
# Tambahkan ke ~/.bashrc
echo "sudo service mosquitto start" >> ~/.bashrc
```

Atau gunakan systemd (jika WSL2):

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

## 📊 Tools Monitoring Tambahan

### 1. MQTT Explorer (GUI - Windows)

Download: [MQTT Explorer](http://mqtt-explorer.com/)

- Host: `192.168.110.131`
- Port: `1883`
- Username/Password: (jika ada)

### 2. Node-RED (Dashboard)

Install di WSL untuk membuat dashboard visual:

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Node-RED
npm install -g --unsafe-perm node-red

# Start Node-RED
node-red
```

Akses: `http://localhost:1880`

### 3. InfluxDB + Grafana (Time Series)

Untuk menyimpan dan visualisasi data historis:

```bash
# Install InfluxDB
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list

sudo apt update && sudo apt install influxdb2 -y

# Start InfluxDB
sudo service influxdb start
```

## ✅ Checklist Final

- [ ] Mosquitto terinstal di WSL
- [ ] Konfigurasi `/etc/mosquitto/conf.d/iot-weather.conf` sudah dibuat
- [ ] Service Mosquitto running
- [ ] IP WSL sudah dicek dan sesuai dengan `gateway.ino`
- [ ] **MQTT_HOST di gateway.ino TIDAK mengandung port `:1883`**
- [ ] Windows Firewall sudah dibuka untuk port 1883
- [ ] Test subscribe/publish berhasil
- [ ] ESP32 Gateway sudah dikonfigurasi dengan IP WSL yang benar
- [ ] Data dari ESP32 berhasil diterima di Mosquitto

## 🎯 Next Steps

1. **Setup Dashboard**: Gunakan MQTT Explorer atau Node-RED
2. **Database Integration**: Simpan data ke InfluxDB/MySQL untuk analisis
3. **Mobile App**: Buat aplikasi mobile yang subscribe ke MQTT
4. **Alerts**: Setup notifikasi jika suhu/kelembaban melebihi threshold

---

**Selamat! Mosquitto MQTT Broker Anda sudah siap menerima data dari ESP32 Weather Station!** 🎉
