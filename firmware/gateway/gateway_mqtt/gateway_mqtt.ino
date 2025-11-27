/*
 * Weather Monitoring System - Gateway (Optimized + Normalized)
 * Hardware: ESP32-S3 + LoRa SX1278 RA-02 433MHz
 * 
 * Fungsi: Menerima data dari Transmitter (Optimized) via LoRa dan mengirimkan ke MQTT Broker via WiFi
 * Library: ESP32MQTTClient (thread-safe, based on ESP-IDF)
 * Reference: https://github.com/cyijun/ESP32MQTTClient
 * 
 * Features:
 * - Industry-standard JSON format with units and metadata
 * - NTP time synchronization for accurate timestamps
 * - Data validation and range checking
 * - Location metadata
 * - Sensor type identification
 */

#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <time.h>
#include <ESP32MQTTClient.h>
#include <ArduinoJson.h>

// ===== PIN CONFIGURATION ESP32-S3 =====
#define LORA_SCK   12
#define LORA_MISO  13
#define LORA_MOSI  11
#define LORA_SS    10
#define LORA_RST   9
#define LORA_DIO0  8

// ===== WIFI CONFIGURATION =====
const char* WIFI_SSID = "SUMUR BOTO 1";
const char* WIFI_PASSWORD = "semarang123";

// ===== MQTT CONFIGURATION =====
const char* MQTT_HOST = "broker.emqx.io";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "emqx";
const char* MQTT_PASSWORD = "public";
const char* MQTT_CLIENT_ID = "ESP32_Gateway_001";

// MQTT Topics
const char* MQTT_TOPIC_WEATHER = "weather/station/data";
const char* MQTT_TOPIC_STATUS = "weather/station/status";

// ===== STATION REGISTRY SYSTEM =====
// Struktur konfigurasi untuk setiap stasiun transmitter
struct StationConfig {
  String id;              // ID Stasiun (contoh: "TX001")
  String name;            // Nama yang mudah dibaca
  float latitude;         // Latitude GPS
  float longitude;        // Longitude GPS  
  float elevation;        // Elevasi dalam meter
  String sensors[6];      // Array nama sensor yang digunakan
  int sensorCount;        // Jumlah sensor
};

// Database registrasi stasiun (Central Hub)
// CATATAN: Tambahkan entri baru di sini saat menambah transmitter
StationConfig stationRegistry[] = {
  {
    "TX001",
    "Kec. Semarang Utara",
    -6.9600, 110.4200, 10.0,
    {"AHT20", "BMP280", "Anemometer", "Raindrop", "LDR"},
    5
  },
  // {
  //   "TX002",
  //   "Kec. Semarang Barat",
  //   -6.9850, 110.3950, 15.0,
  //   {"DHT22", "BMP280", "Rain gauge", "LDR"},
  //   4
  // },
  // {
  //   "TX003",
  //   "Kec. Genuk",
  //   -6.9450, 110.4500, 5.0,
  //   {"AHT20", "UV", "LDR", "Raindrop"},
  //   4
  // }
};

const int STATION_COUNT = 1;  // Update saat menambah/hapus stasiun

// Fallback values untuk stasiun yang tidak terdaftar
const float DEFAULT_LATITUDE = -6.9859;   // Politeknik Negeri Semarang
const float DEFAULT_LONGITUDE = 110.4093;
const float DEFAULT_ELEVATION = 15.0;
const char* DEFAULT_STATION_NAME = "Stasiun Tidak Dikenal";

// ===== NTP TIME CONFIGURATION =====
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 7 * 3600;     // GMT+7 untuk Indonesia
const int DAYLIGHT_OFFSET_SEC = 0;        // Indonesia tidak pakai DST

// ===== STATUS VARIABLES =====
unsigned long lastStatusPublish = 0;
const unsigned long STATUS_PUBLISH_INTERVAL = 60000;
bool timeInitialized = false;

// ===== LED INDICATOR =====
#define LED_BUILTIN 48

// ===== MQTT Client Instance =====
ESP32MQTTClient mqttClient;

// Forward declarations
void publishStatus();
void setupWiFi();
void handleLoRaPacket(int packetSize);
void parseAndPublish(String data, int rssi, float snr);

// ===== STATION HELPER FUNCTIONS =====
// Fungsi untuk mencari konfigurasi stasiun berdasarkan ID
StationConfig* getStationConfig(String stationID) {
  for (int i = 0; i < STATION_COUNT; i++) {
    if (stationRegistry[i].id == stationID) {
      return &stationRegistry[i];
    }
  }
  return nullptr;  // Stasiun tidak ditemukan dalam registry
}

// ===== MQTT Event Handlers (MUST BE GLOBAL) =====
void onMqttConnect(esp_mqtt_client_handle_t client) {
  if (mqttClient.isMyTurn(client)) {
    Serial.println("✓ MQTT Connected!");
    publishStatus();
  }
}

// Global event handler untuk ESP-IDF MQTT events
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
esp_err_t handleMQTT(esp_mqtt_event_handle_t event) {
  mqttClient.onEventCallback(event);
  return ESP_OK;
}
#else
void handleMQTT(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data) {
  auto *event = static_cast<esp_mqtt_event_handle_t>(event_data);
  mqttClient.onEventCallback(event);
}
#endif

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n===== Weather Gateway (Optimized) Starting =====");
  
  // Setup LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  
  // Setup LoRa
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(433E6)) {
    Serial.println("✗ LoRa init failed!");
    while (1) {
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      delay(200);
    }
  }
  
  // Konfigurasi LoRa (sama dengan Transmitter)
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setSyncWord(0x12);
  
  Serial.println("✓ LoRa initialized!");
  
  // Setup WiFi
  setupWiFi();
  
  // Setup NTP Time Sync
  Serial.println("\nConfiguring NTP time sync...");
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
  
  // Wait for time to be set
  Serial.print("Waiting for NTP time sync");
  int ntpRetries = 0;
  struct tm timeinfo;
  
  while (!getLocalTime(&timeinfo) && ntpRetries < 10) {
    Serial.print(".");
    delay(500);
    ntpRetries++;
  }
  
  if (ntpRetries < 10) {
    Serial.println("\n✓ NTP time synchronized!");
    Serial.print("  Current time: ");
    Serial.println(&timeinfo, "%Y-%m-%d %H:%M:%S");
    timeInitialized = true;
  } else {
    Serial.println("\n⚠ NTP sync timeout - using millis() for timestamp");
    timeInitialized = false;
  }
  
  // Setup MQTT Client
  Serial.println("\nConfiguring MQTT client...");
  
  mqttClient.setURL(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD);
  mqttClient.setMqttClientName(MQTT_CLIENT_ID);
  mqttClient.setKeepAlive(30);
  mqttClient.enableDebuggingMessages(true);
  
  // Start MQTT client
  bool mqttStarted = mqttClient.loopStart();
  
  if (mqttStarted) {
    Serial.println("✓ MQTT client started!");
  } else {
    Serial.println("✗ MQTT client failed to start!");
  }
  
  Serial.println("\n✓ Gateway ready!\n");
}

void loop() {
  // Maintain WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    setupWiFi();
  }
  
  // Check for LoRa packets
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    handleLoRaPacket(packetSize);
  }
  
  // Publish status periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastStatusPublish >= STATUS_PUBLISH_INTERVAL) {
    lastStatusPublish = currentMillis;
    publishStatus();
  }
  
  delay(10);
}

// Setup WiFi connection
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("  IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    Serial.println("\n✗ WiFi connection failed!");
    digitalWrite(LED_BUILTIN, LOW);
  }
}

// Handle received LoRa packet
void handleLoRaPacket(int packetSize) {
  String received = "";
  
  while (LoRa.available()) {
    received += (char)LoRa.read();
  }
  
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();
  
  Serial.println("\n===== LoRa Packet Received =====");
  Serial.println("Data: " + received);
  Serial.print("RSSI: "); Serial.print(rssi); Serial.println(" dBm");
  Serial.print("SNR: "); Serial.print(snr); Serial.println(" dB");
  Serial.println("================================\n");
  
  if (received.length() > 0) {
    parseAndPublish(received, rssi, snr);
  }
  
  // Blink LED
  digitalWrite(LED_BUILTIN, LOW);
  delay(50);
  digitalWrite(LED_BUILTIN, HIGH);
}

// Parse LoRa data and publish to MQTT (INDUSTRY STANDARD COMPLIANT)
void parseAndPublish(String data, int rssi, float snr) {
  // Format dari transmitter optimized: DEVICE_ID|temp|hum|press|wind|rain|light|CRC
  
  int fieldCount = 0;
  int lastIndex = 0;
  String fields[8];  // 8 fields termasuk CRC
  
  // Split string by delimiter '|'
  for (int i = 0; i <= data.length(); i++) {
    if (data.charAt(i) == '|' || i == data.length()) {
      fields[fieldCount] = data.substring(lastIndex, i);
      lastIndex = i + 1;
      fieldCount++;
      if (fieldCount >= 8) break;
    }
  }
  
  // Validasi jumlah field
  if (fieldCount < 8) {
    Serial.println("✗ Error: Format data tidak valid! Diharapkan 8 field (dengan CRC), diterima " + String(fieldCount));
    return;
  }
  
  // ===== CRC VALIDATION =====
  String receivedCRC = fields[7];
  
  // Reconstruct payload tanpa CRC
  String payloadWithoutCRC = fields[0];
  for (int i = 1; i < 7; i++) {
    payloadWithoutCRC += "|" + fields[i];
  }
  
  // Calculate expected CRC
  uint8_t expectedCRC = 0;
  for (int i = 0; i < payloadWithoutCRC.length(); i++) {
    expectedCRC ^= payloadWithoutCRC[i];
  }
  
  // Convert received CRC dari HEX string
  long receivedCRCValue = strtol(receivedCRC.c_str(), NULL, 16);
  
  // Validate CRC
  if (receivedCRCValue != expectedCRC) {
    Serial.println("✗ CRC MISMATCH! Data corrupted.");
    Serial.println("  Expected: 0x" + String(expectedCRC, HEX));
    Serial.println("  Received: 0x" + receivedCRC);
    return;  // Reject corrupted data
  }
  
  Serial.println("✓ CRC validated: 0x" + String(expectedCRC, HEX));
  
  // Parse values dengan validasi
  String stationID = fields[0];
  float tempValue = fields[1].toFloat();
  float humValue = fields[2].toFloat();
  float pressValue = fields[3].toFloat();
  float windValue = fields[4].toFloat();
  int rainValue = fields[5].toInt();
  int lightValue = fields[6].toInt();
  
  // Data validation (range checking)
  bool validData = true;
  
  if (tempValue < -40 || tempValue > 80) {
    Serial.println("⚠ Temperatur di luar range valid: " + String(tempValue));
    validData = false;
  }
  if (humValue < 0 || humValue > 100) {
    Serial.println("⚠ Kelembaban di luar range valid: " + String(humValue));
    validData = false;
  }
  if (pressValue < 300 || pressValue > 1100) {
    Serial.println("⚠ Tekanan di luar range valid: " + String(pressValue));
    validData = false;
  }
  
  // Skip publishing jika data tidak valid
  if (!validData) {
    Serial.println("✗ Validasi data gagal, skip publish");
    return;
  }
  
  // Lookup station configuration dari registry
  StationConfig* station = getStationConfig(stationID);
  
  // Buat JSON document dengan format Schema.org WeatherObservation
  StaticJsonDocument<1024> doc;  // Ukuran lebih besar untuk compliance
  
  // ===== SCHEMA.ORG COMPLIANCE =====
  doc["@context"] = "https://schema.org";
  doc["@type"] = "WeatherObservation";
  
  // Station metadata
  doc["stationID"] = stationID;
  doc["gatewayID"] = MQTT_CLIENT_ID;
  
  // Gunakan konfigurasi spesifik stasiun atau default
  if (station != nullptr) {
    doc["name"] = station->name;  // Schema.org uses "name"
    
    // Location dari registry (Schema.org GeoCoordinates)
    JsonObject location = doc.createNestedObject("geo");
    location["@type"] = "GeoCoordinates";
    location["latitude"] = station->latitude;
    location["longitude"] = station->longitude;
    location["elevation"] = station->elevation;
    
    // Daftar sensor dari registry (custom extension)
    JsonArray sensors = doc.createNestedArray("sensors");
    for (int i = 0; i < station->sensorCount; i++) {
      sensors.add(station->sensors[i]);
    }
    
    Serial.println("ℹ Menggunakan konfigurasi stasiun: " + station->name);
  } else {
    // Stasiun tidak dikenal - gunakan default
    Serial.println("⚠️ Stasiun tidak dikenal: " + stationID);
    doc["name"] = DEFAULT_STATION_NAME;
    
    JsonObject location = doc.createNestedObject("geo");
    location["@type"] = "GeoCoordinates";
    location["latitude"] = DEFAULT_LATITUDE;
    location["longitude"] = DEFAULT_LONGITUDE;
    location["elevation"] = DEFAULT_ELEVATION;
    
    JsonArray sensors = doc.createNestedArray("sensors");
    sensors.add("UNKNOWN");
  }
  
  // ===== TIMESTAMP (ISO 8601) =====
  // Schema.org uses "observationDate" not "observationTime"
  if (timeInitialized) {
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      char timestamp[30];
      strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%S+07:00", &timeinfo);
      doc["observationDate"] = timestamp;
    } else {
      doc["observationDate"] = "";
      doc["uptimeMs"] = millis();
    }
  } else {
    doc["observationDate"] = "";
    doc["uptimeMs"] = millis();
  }
  
  // ===== TEMPERATURE (QuantitativeValue with UN/CEFACT codes) =====
  JsonObject temperature = doc.createNestedObject("temperature");
  temperature["@type"] = "QuantitativeValue";
  temperature["value"] = serialized(String(tempValue, 2));
  temperature["unitCode"] = "CEL";        // UN/CEFACT: Celsius
  temperature["unitText"] = "°C";
  temperature["sensor"] = "AHT20";
  
  // ===== HUMIDITY (QuantitativeValue) =====
  JsonObject humidity = doc.createNestedObject("humidity");
  humidity["@type"] = "QuantitativeValue";
  humidity["value"] = serialized(String(humValue, 2));
  humidity["unitCode"] = "P1";            // UN/CEFACT: Percent
  humidity["unitText"] = "%";
  humidity["sensor"] = "AHT20";
  
  // ===== PRESSURE (QuantitativeValue) =====
  JsonObject pressure = doc.createNestedObject("atmosphericPressure");
  pressure["@type"] = "QuantitativeValue";
  pressure["value"] = serialized(String(pressValue, 2));
  pressure["unitCode"] = "HPA";           // UN/CEFACT: Hectopascal
  pressure["unitText"] = "hPa";
  pressure["sensor"] = "BMP280";
  
  // ===== WIND SPEED (QuantitativeValue) =====
  JsonObject windSpeed = doc.createNestedObject("windSpeed");
  windSpeed["@type"] = "QuantitativeValue";
  windSpeed["value"] = serialized(String(windValue, 2));
  windSpeed["unitCode"] = "KMH";          // UN/CEFACT: Kilometre per hour
  windSpeed["unitText"] = "km/h";
  windSpeed["sensor"] = "Anemometer";
  
  // ===== PRECIPITATION (Custom extension) =====
  JsonObject precipitation = doc.createNestedObject("precipitation");
  precipitation["@type"] = "QuantitativeValue";
  precipitation["rawLevel"] = rainValue;
  precipitation["unitCode"] = "ADC";
  precipitation["unitText"] = "ADC (0-1023)";
  precipitation["sensor"] = "Raindrop";
  precipitation["note"] = "0=basah, 1023=kering";
  
  // ===== ILLUMINANCE (Custom extension) =====
  JsonObject illuminance = doc.createNestedObject("illuminance");
  illuminance["@type"] = "QuantitativeValue";
  illuminance["rawLevel"] = lightValue;
  illuminance["unitCode"] = "ADC";
  illuminance["unitText"] = "ADC (0-1023)";
  illuminance["sensor"] = "LDR";
  illuminance["note"] = "0=gelap, 1023=terang";
  
  // ===== SIGNAL QUALITY (Custom extension) =====
  JsonObject signal = doc.createNestedObject("signal");
  signal["rssi"] = rssi;
  signal["snr"] = serialized(String(snr, 1));
  signal["protocol"] = "LoRa 433MHz";
  
  // Serialize JSON to string
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Publish to MQTT
  if (mqttClient.isConnected()) {
    bool published = mqttClient.publish(
      MQTT_TOPIC_WEATHER,
      jsonString.c_str(),
      0,
      false
    );
    
    if (published) {
      Serial.println("✓ Published to MQTT (Schema.org compliant):");
      Serial.println(jsonString);
    } else {
      Serial.println("✗ Failed to publish to MQTT!");
    }
  } else {
    Serial.println("✗ MQTT not connected, data not published!");
    Serial.print("  isConnected(): "); Serial.println(mqttClient.isConnected());
  }
}

// Publish gateway status
void publishStatus() {
  if (!mqttClient.isConnected()) {
    Serial.println("Skipping status publish - MQTT not connected");
    return;
  }
  
  StaticJsonDocument<256> doc;
  
  doc["gateway_id"] = MQTT_CLIENT_ID;
  doc["uptime"] = millis() / 1000;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["wifi_ip"] = WiFi.localIP().toString();
  doc["mqtt_connected"] = mqttClient.isConnected();
  doc["free_heap"] = ESP.getFreeHeap();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  bool published = mqttClient.publish(
    MQTT_TOPIC_STATUS,
    jsonString.c_str(),
    0,
    false
  );
  
  if (published) {
    Serial.println("✓ Status published to MQTT");
  } else {
    Serial.println("✗ Failed to publish status");
  }
}
