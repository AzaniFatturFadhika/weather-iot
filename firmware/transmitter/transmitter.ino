/*
 * Weather Monitoring System - Transmitter (Optimized)
 * Hardware: Arduino Nano + LoRa SX1278 RA-02 433MHz
 * Sensors: AHT20 (Temp+Humidity), BMP280 (Pressure), Anemometer, Raindrop, LDR
 * 
 * Optimizations:
 * - Uses AHT20 for temperature and humidity (best accuracy)
 * - Uses BMP280 only for pressure
 * - Removed DHT22 to reduce redundancy
 * - Simplified data structure and transmission
 */

#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_AHTX0.h>

// ===== PIN CONFIGURATION =====
// LoRa SX1278 RA-02
#define LORA_SS    10    // NSS/CS
#define LORA_RST   9     // RESET
#define LORA_DIO0  2     // DIO0

// Anemometer (Pulse Counter)
#define ANEMOMETER_PIN  3  // Interrupt pin

// Raindrop Sensor
#define RAINDROP_PIN    A0 // Hubungkan ke pin DO (Digital Output) sensor

// LDR (Light Dependent Resistor)
#define LDR_PIN         A1

// ===== SENSOR OBJECTS =====
Adafruit_BMP280 bmp;    // Untuk Pressure
Adafruit_AHTX0 aht;     // Untuk Temperature & Humidity

// ===== SENSOR STATUS FLAGS =====
bool bmp280Available = false;
bool aht20Available = false;

// ===== ANEMOMETER VARIABLES =====
volatile unsigned long anemometerPulseCount = 0;
unsigned long lastAnemometerRead = 0;
const unsigned long ANEMOMETER_READ_INTERVAL = 1000; // Baca setiap 1 detik

// Kalibrasi Anemometer
#define WIND_SPEED_18_PULSE_SECOND 2.0 // in m/s
#define ONE_ROTATION_SENSOR 18.0       // pulse per rotation

// ===== TRANSMISSION SETTINGS =====
// const unsigned long TRANSMIT_INTERVAL = 10000; // Kirim data setiap 10 detik
// const unsigned long TRANSMIT_INTERVAL = 10000; // Kirim data setiap 10 detik
const unsigned long TRANSMIT_INTERVAL = 10000; // Kirim data setiap 10 detik (Increased for SF12 airtime)
unsigned long lastTransmit = 0;

// ===== DEVICE ID =====
const String DEVICE_ID = "TX001"; // ID unik untuk transmitter ini

// ===== STRUKTUR DATA (SIMPLIFIED) =====
struct WeatherData {
  float temperature;      // dari AHT20
  float humidity;         // dari AHT20
  float pressure;         // dari BMP280
  float windSpeed;        // dari Anemometer (km/h)
  int rainLevel;          // dari Raindrop sensor (0=Dry, 1=Wet)
  int lightLevel;         // dari LDR (0-1023)
};

void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println("Weather Transmitter (Optimized) Starting...");
  
  // Inisialisasi LoRa
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  
  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa init failed!");
    while (1);
  }

  // Konfigurasi LoRa (Long Range Mode)
  LoRa.setSpreadingFactor(12); // Max Range (was 7)
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(8);      // Max Error Correction (was 5)
  LoRa.setSyncWord(0x12);
  LoRa.setTxPower(20);
  
  Serial.println("LoRa initialized!");
  
  // Inisialisasi AHT20 (Primary sensor untuk Temp & Humidity)
  if (aht.begin()) {
    aht20Available = true;
    Serial.println("AHT20 initialized! (Primary sensor for Temp & Humidity)");
  } else {
    aht20Available = false;
    Serial.println("AHT20 init failed! Temperature & Humidity will not be available.");
  }
  
  // Inisialisasi BMP280 (Primary sensor untuk Pressure)
  if (bmp.begin(0x76)) {
    bmp280Available = true;
    Serial.println("BMP280 initialized at 0x76! (Primary sensor for Pressure)");
  } 
  else if (bmp.begin(0x77)) {
    bmp280Available = true;
    Serial.println("BMP280 initialized at 0x77! (Primary sensor for Pressure)");
  } 
  else {
    bmp280Available = false;
    Serial.println("BMP280 init failed! Pressure will not be available.");
  }
  
  // Konfigurasi BMP280
  if (bmp280Available) {
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,
                    Adafruit_BMP280::STANDBY_MS_500);
  }
  
  // Setup Anemometer interrupt
  pinMode(ANEMOMETER_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ANEMOMETER_PIN), anemometerISR, CHANGE);
  
  // Setup analog pins
  pinMode(RAINDROP_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  
  Serial.println("All sensors initialized!");
  Serial.println("Starting data transmission...");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Kirim data setiap TRANSMIT_INTERVAL
  if (currentMillis - lastTransmit >= TRANSMIT_INTERVAL) {
    lastTransmit = currentMillis;
    
    // Baca semua sensor
    WeatherData data = readAllSensors();
    
    // Kirim data via LoRa
    transmitData(data);
    
    // Print data ke Serial untuk debugging
    printSensorData(data);
  }
}

// Interrupt Service Routine untuk Anemometer
void anemometerISR() {
  anemometerPulseCount++;
}

// Fungsi untuk membaca semua sensor (OPTIMIZED + VALIDATED)
WeatherData readAllSensors() {
  WeatherData data;
  
  // ===== Baca AHT20 (Temperature & Humidity) =====
  if (aht20Available) {
    sensors_event_t humidity, temp;
    aht.getEvent(&humidity, &temp);
    data.temperature = temp.temperature;
    data.humidity = humidity.relative_humidity;
    
    // Validasi dengan range checking
    if (isnan(data.temperature) || data.temperature < -40 || data.temperature > 80) {
      Serial.println("Warning: AHT20 temperature out of range or invalid");
      data.temperature = 0.0;
    }
    if (isnan(data.humidity) || data.humidity < 0 || data.humidity > 100) {
      Serial.println("Warning: AHT20 humidity out of range or invalid");
      data.humidity = 0.0;
    }
  } else {
    data.temperature = 0.0;
    data.humidity = 0.0;
  }
  
  // ===== Baca BMP280 (Pressure only) =====
  if (bmp280Available) {
    data.pressure = bmp.readPressure() / 100.0F; // Pascal ke hPa
    
    // Validasi dengan range checking (valid atmospheric pressure: 300-1100 hPa)
    if (isnan(data.pressure) || data.pressure < 300 || data.pressure > 1100) {
      Serial.println("Warning: BMP280 pressure out of range or invalid");
      data.pressure = 0.0;
    }
  } else {
    data.pressure = 0.0;
  }
  
  // ===== Hitung kecepatan angin =====
  unsigned long currentMillis = millis();
  unsigned long timeDiff = currentMillis - lastAnemometerRead;
  
  if (timeDiff >= ANEMOMETER_READ_INTERVAL) {
    // Disable interrupts untuk membaca dan reset counter secara atomik
    noInterrupts();
    unsigned long rotations = anemometerPulseCount;
    anemometerPulseCount = 0;
    interrupts();
    
    lastAnemometerRead = currentMillis;
    
    // Normalisasi rotasi ke basis 1 detik
    float rotationsPerSecond = (float)rotations / (timeDiff / 1000.0);
    
    // Terapkan rumus kalibrasi (hasil dalam m/s)
    float windSpeedMs = (WIND_SPEED_18_PULSE_SECOND / ONE_ROTATION_SENSOR) * (rotationsPerSecond / 10.0);
    
    // Konversi ke km/h
    data.windSpeed = windSpeedMs * 3.6;
  } else {
    data.windSpeed = 0;
  }
  
  // ===== Baca sensor analog & digital =====
  // Raindrop (Digital Mode): Read DO pin. LOW = Wet, HIGH = Dry
  int rainDigital = digitalRead(RAINDROP_PIN);
  data.rainLevel = (rainDigital == LOW) ? 1 : 0;
  
  data.lightLevel = analogRead(LDR_PIN);
  
  return data;
}

// Fungsi untuk mengirim data via LoRa (SIMPLIFIED FORMAT + CRC)
void transmitData(WeatherData data) {
  // Format: DEVICE_ID|temp|hum|press|wind|rain|light|CRC
  String payload = DEVICE_ID + "|";
  payload += String(data.temperature, 2) + "|";
  payload += String(data.humidity, 2) + "|";
  payload += String(data.pressure, 2) + "|";
  payload += String(data.windSpeed, 2) + "|";
  payload += String(data.rainLevel) + "|";
  payload += String(data.lightLevel);
  
  // Calculate CRC8 checksum untuk data integrity
  uint8_t crc = 0;
  for (int i = 0; i < payload.length(); i++) {
    crc ^= payload[i];  // Simple XOR checksum
  }
  
  // Append CRC ke payload
  payload += "|" + String(crc, HEX);
  
  // Kirim packet
  LoRa.beginPacket();
  LoRa.print(payload);
  LoRa.endPacket();
  
  Serial.println("Data transmitted: " + payload);
  Serial.println("CRC: 0x" + String(crc, HEX));
}

// Fungsi untuk print data ke Serial Monitor
void printSensorData(WeatherData data) {
  Serial.println("\n===== Sensor Readings (Optimized + Validated) =====");
  Serial.print("[AHT20] Temperature: "); Serial.print(data.temperature, 2); Serial.println(" °C");
  Serial.print("[AHT20] Humidity: "); Serial.print(data.humidity, 2); Serial.println(" %");
  Serial.print("[BMP280] Pressure: "); Serial.print(data.pressure, 2); Serial.println(" hPa");
  Serial.print("[Anemometer] Wind Speed: "); Serial.print(data.windSpeed, 2); Serial.println(" km/h");
  Serial.print("[Raindrop] Rain Level: "); Serial.print(data.rainLevel); Serial.println(" (0=Dry, 1=Wet)");
  Serial.print("[LDR] Light Level: "); Serial.print(data.lightLevel); Serial.println(" (0-1023 ADC)");
  Serial.println("===================================================\n");
}
