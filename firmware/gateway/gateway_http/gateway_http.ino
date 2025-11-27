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

// ===== BACKEND CONFIGURATION =====
// Ganti dengan IP address komputer yang menjalankan backend (jika local)
// atau domain server jika sudah di-hosting.
// Contoh: "http://192.168.1.100:8000"
const char* BACKEND_URL = "http://192.168.1.100:8000"; 

// ===== LED INDICATOR =====
#define LED_BUILTIN 48

void setupWiFi();
void handleLoRaPacket(int packetSize);
void sendToBackend(float temp, float hum, float press, float wind, int rain, int light);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n===== Weather Gateway (HTTP Legacy) Starting =====");
  
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
  
  if (received.length() > 0) {
    // Parse data
    // Format: DEVICE_ID|temp|hum|press|wind|rain|light|CRC
    
    int fieldCount = 0;
    int lastIndex = 0;
    String fields[8];
    
    for (int i = 0; i <= received.length(); i++) {
      if (received.charAt(i) == '|' || i == received.length()) {
        fields[fieldCount] = received.substring(lastIndex, i);
        lastIndex = i + 1;
        fieldCount++;
        if (fieldCount >= 8) break;
      }
    }
    
    if (fieldCount >= 7) { // Minimal 7 field tanpa CRC check ketat untuk demo
      float temp = fields[1].toFloat();
      float hum = fields[2].toFloat();
      float press = fields[3].toFloat();
      float wind = fields[4].toFloat();
      int rain = fields[5].toInt();
      int light = fields[6].toInt();
      
      // Kirim ke backend
      sendToBackend(temp, hum, press, wind, rain, light);
    } else {
      Serial.println("✗ Invalid data format");
    }
  }
  
  // Blink LED
  digitalWrite(LED_BUILTIN, LOW);
  delay(50);
  digitalWrite(LED_BUILTIN, HIGH);
}

void sendToBackend(float temp, float hum, float press, float wind, int rain, int light) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Construct URL with query parameters
    // Endpoint: /weather-data/create?temp=...&humidity=...
    String url = String(BACKEND_URL) + "/weather-data/create?";
    url += "temp=" + String(temp, 2);
    url += "&humidity=" + String(hum, 2);
    url += "&pressure=" + String(press, 2);
    url += "&windSpeed=" + String(wind, 2);
    
    // Konversi nilai analog rain ke boolean isRaining (sesuai logika backend lama)
    // Asumsi: nilai rendah = basah (sensor resistif)
    int isRaining = (rain < 500) ? 1 : 0; 
    url += "&isRaining=" + String(isRaining);
    
    url += "&lightIntensity=" + String(light);
    
    Serial.print("Sending HTTP GET: ");
    Serial.println(url);
    
    http.begin(url);
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}
