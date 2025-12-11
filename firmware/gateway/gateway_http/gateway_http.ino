/*
 * Weather Monitoring System - Gateway (HTTP Legacy Version)
 * Hardware: ESP32-S3 + LoRa SX1278 RA-02 433MHz
 * 
 * Fungsi: Menerima data dari Transmitter via LoRa dan mengirimkan ke Backend Legacy via HTTP GET
 * 
 * Endpoint Target: /weather-data/create
 * Parameter: temp, humidity, isRaining, lightIntensity, windSpeed, pressure
 */

#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "time.h"

// ===== DATA BUFFERING & NTP =====
float lastTemp = 0, lastHum = 0, lastPress = 0, lastWind = 0;
int lastRain = 0, lastLight = 0;
bool newDataAvailable = false;
unsigned long lastSendAttemptMs = 0;
const unsigned long SEND_RETRY_INTERVAL_MS = 10000; // selaras dengan interval TX (10s)

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 7 * 3600; // UTC+7 (WIB)
const int   daylightOffset_sec = 0;

// ===== PIN CONFIGURATION ESP32-S3 =====
#define LORA_SCK   12
#define LORA_MISO  13
#define LORA_MOSI  11
#define LORA_SS    10
#define LORA_RST   8
#define LORA_DIO0  9

// ===== WIFI CONFIGURATION =====
const char* WIFI_SSID = "KelompokCuaca";
const char* WIFI_PASSWORD = "esTeHangetSegar";

// ===== BACKEND CONFIGURATION =====
// Mendukung pengiriman ke 2 endpoint sekaligus
// Endpoint 1: Primary
const char* BACKEND_URL_1 = "https://api.azanifattur.biz.id";
// Endpoint 2: Secondary
const char* BACKEND_URL_2 = "https://api.wrseno.my.id";

// Array untuk iterasi
const char* BACKEND_URLS[] = {BACKEND_URL_1, BACKEND_URL_2};
const int NUM_ENDPOINTS = 2;

// ===== LED INDICATOR =====
#define LED_BUILTIN 48
#define LORA_LED 4  // Indikator LED untuk data LoRa masuk


void setupWiFi();
void handleLoRaPacket(int packetSize);
int sendToAllEndpoints(float temp, float hum, float press, float wind, int rain, int light);
bool sendToEndpoint(const char* backendUrl, float temp, float hum, float press, float wind, int rain, int light);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n===== Weather Gateway (HTTP Legacy) Starting =====");
  
  // Setup LED
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  pinMode(LORA_LED, OUTPUT);
  digitalWrite(LORA_LED, LOW);

  
  // Setup LoRa
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  LoRa.setSPIFrequency(1E6); // Reduce SPI frequency to 1MHz to fix garbage data
  
  if (!LoRa.begin(433E6)) {
    Serial.println("✗ LoRa init failed!");
    while (1) {
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
      delay(200);
    }
  }
  
  // Konfigurasi LoRa (Long Range Mode - Match Transmitter)
  LoRa.setSpreadingFactor(12); // Max Range
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(8);      // Max Error Correction
  LoRa.setSyncWord(0x12);
  LoRa.setTxPower(20);
  
  Serial.println("✓ LoRa initialized!");
  
  // Setup WiFi
  setupWiFi();
  
  Serial.println("\n✓ Gateway ready! Waiting for LoRa packets...\n");
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

  // Retry kirim data buffer tiap 10 detik agar selaras dengan interval transmitter
  unsigned long nowMs = millis();
  if (newDataAvailable && (nowMs - lastSendAttemptMs >= SEND_RETRY_INTERVAL_MS)) {
    Serial.println("\n[RETRY] Sending buffered data...");
    int sentCount = sendToAllEndpoints(lastTemp, lastHum, lastPress, lastWind, lastRain, lastLight);
    bool sent = (sentCount > 0);
    lastSendAttemptMs = nowMs;
    if (sent) {
      newDataAvailable = false;
    }
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
    Serial.println(WiFi.localIP());
    digitalWrite(LED_BUILTIN, HIGH);
    
    // Init NTP
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    Serial.println("✓ NTP Initialized (UTC+7)");
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
  Serial.println("Raw Data: " + received);
  Serial.print("RSSI: "); Serial.print(rssi); Serial.println(" dBm");
  Serial.print("SNR: "); Serial.print(snr); Serial.println(" dB");
  
  if (received.length() > 0) {
    // Nyalakan LED (Start Processing)
    digitalWrite(LORA_LED, HIGH);
    
    // 1. Validate CRC
    // Format: DEVICE_ID|temp|hum|press|wind|rain|light|CRC
    int lastPipeIndex = received.lastIndexOf('|');
    
    if (lastPipeIndex == -1) {
       Serial.println("✗ Invalid format: No CRC separator found");
       digitalWrite(LORA_LED, LOW);
       return;
    }

    String dataPayload = received.substring(0, lastPipeIndex);
    String receivedCrcHex = received.substring(lastPipeIndex + 1);
    
    // Calculate CRC (XOR Checksum)
    uint8_t calculatedCrc = 0;
    for (int i = 0; i < dataPayload.length(); i++) {
      calculatedCrc ^= dataPayload[i];
    }
    
    // Convert received Hex string to byte
    uint8_t receivedCrc = (uint8_t) strtol(receivedCrcHex.c_str(), NULL, 16);
    
    if (calculatedCrc != receivedCrc) {
      Serial.print("✗ CRC Mismatch! Calc: 0x"); Serial.print(calculatedCrc, HEX);
      Serial.print(", Recv: 0x"); Serial.println(receivedCrc, HEX);
      digitalWrite(LORA_LED, LOW);
      return;
    }
    
    Serial.println("✓ CRC Valid!");
    
    // 2. Parse Data
    // Format: DEVICE_ID|temp|hum|press|wind|rain|light
    int fieldCount = 0;
    int lastIndex = 0;
    String fields[7]; // ID, temp, hum, press, wind, rain, light
    
    for (int i = 0; i <= dataPayload.length(); i++) {
      if (dataPayload.charAt(i) == '|' || i == dataPayload.length()) {
        fields[fieldCount] = dataPayload.substring(lastIndex, i);
        lastIndex = i + 1;
        fieldCount++;
        if (fieldCount >= 7) break;
      }
    }
    
    if (fieldCount >= 7) {
      String deviceId = fields[0];
      float temp = fields[1].toFloat();
      float hum = fields[2].toFloat();
      float press = fields[3].toFloat();
      float wind = fields[4].toFloat();
      int rain = fields[5].toInt();
      int light = fields[6].toInt();
      
      // 3. Print Detailed Data
      Serial.println("\n--- Decoded Weather Data ---");
      Serial.println("Device ID   : " + deviceId);
      Serial.println("Temperature : " + String(temp, 2) + " °C");
      Serial.println("Humidity    : " + String(hum, 2) + " %");
      Serial.println("Pressure    : " + String(press, 2) + " hPa");
      Serial.println("Wind Speed  : " + String(wind, 2) + " km/h");
      Serial.println("Rain Status : " + String(rain == 1 ? "Wet (Raining)" : "Dry"));
      Serial.println("Light Level : " + String(light));
      Serial.println("----------------------------");
      
      // Simpan data terbaru, coba kirim langsung, buffer jika gagal
      lastTemp = temp;
      lastHum = hum;
      lastPress = press;
      lastWind = wind;
      lastRain = rain;
      lastLight = light;
      newDataAvailable = true;
      lastSendAttemptMs = millis();

      int sentCount = sendToAllEndpoints(lastTemp, lastHum, lastPress, lastWind, lastRain, lastLight);
      bool sent = (sentCount > 0);
      if (sent) {
        newDataAvailable = false;
      }
      Serial.println("Data processed from LoRa (buffered for retry if needed)");
    } else {
      Serial.println("✗ Invalid data format: Not enough fields");
    }
  }
  
  // Matikan LED setelah selesai proses
  digitalWrite(LORA_LED, LOW);
}

// Kirim data ke SEMUA endpoint, return jumlah yang berhasil
int sendToAllEndpoints(float temp, float hum, float press, float wind, int rain, int light) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi Disconnected - Cannot send to any endpoint");
    return 0;
  }

  int successCount = 0;
  
  Serial.println("\n--- Sending to Multiple Endpoints ---");
  
  for (int i = 0; i < NUM_ENDPOINTS; i++) {
    Serial.print("[Endpoint ");
    Serial.print(i + 1);
    Serial.print("/");
    Serial.print(NUM_ENDPOINTS);
    Serial.print("] ");
    Serial.println(BACKEND_URLS[i]);
    
    bool success = sendToEndpoint(BACKEND_URLS[i], temp, hum, press, wind, rain, light);
    
    if (success) {
      successCount++;
      Serial.println("  ✓ Success");
    } else {
      Serial.println("  ✗ Failed");
    }
  }
  
  Serial.print("--- Total: ");
  Serial.print(successCount);
  Serial.print("/");
  Serial.print(NUM_ENDPOINTS);
  Serial.println(" endpoints succeeded ---\n");
  
  return successCount;
}

// Kirim data ke satu endpoint
bool sendToEndpoint(const char* backendUrl, float temp, float hum, float press, float wind, int rain, int light) {
  HTTPClient http;
  
  // Construct URL with query parameters
  String url = String(backendUrl) + "/weather-data/create?";
  url += "temp=" + String(temp, 2);
  url += "&humidity=" + String(hum, 2);
  url += "&pressure=" + String(press, 2);
  url += "&windSpeed=" + String(wind, 2);
  
  // Nilai rain sudah berupa 0 (Dry) atau 1 (Wet) dari transmitter
  url += "&isRaining=" + String(rain);
  url += "&lightIntensity=" + String(light);
  
  Serial.print("  URL: ");
  Serial.println(url);
  
  http.begin(url);
  http.setTimeout(10000); // 10 second timeout per endpoint
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("  Response: ");
    Serial.print(httpResponseCode);
    Serial.print(" - ");
    Serial.println(response.substring(0, 100)); // Limit response output
    http.end();
    return httpResponseCode >= 200 && httpResponseCode < 300;
  } else {
    Serial.print("  Error: ");
    Serial.println(httpResponseCode);
    http.end();
    return false;
  }
}
