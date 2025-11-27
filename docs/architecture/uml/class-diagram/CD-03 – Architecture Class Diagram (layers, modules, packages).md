Berikut **architecture class diagram** untuk sistem prakiraan cuaca IoT & ML-mu dalam format **Mermaid** (fokus ke komponen arsitektur: device, backend, ML, dan mobile app).

```mermaid
classDiagram
direction LR

%% =========================
%% LAYER: DEVICE / EDGE (IoT)
%% =========================
class WeatherStation {
  +stationId: UUID
  +locationId: UUID
  +latitude: float
  +longitude: float
  +getLocation()
}

class IoTNode {
  <<device>>
  +nodeId: UUID
  +hardwareMCU: string  %% Arduino Nano
  +loRaFrequency: float
  +energyStatus: string
  +readSensors()
  +fuseSensorData()
  +sendLoRaPacket()
}

class Sensor {
  <<device>>
  +sensorType: string   %% DHT22/BMP280/AHT20
  +hardwareId: string
  +readValue()
  +calibrate()
}

class Gateway {
  <<edge>>
  +gatewayId: UUID
  +hardwareMCU: string  %% ESP32-S3
  +wifiStatus: string
  +receiveLoRa()
  +postToBackend()
}

WeatherStation "1" -- "1" IoTNode : ditempatkan
IoTNode "1" -- "1..*" Sensor : menggunakan
IoTNode --> Gateway : kirim LoRa


%% =========================
%% LAYER: BACKEND (FastAPI + MySQL)
%% =========================
class WeatherApiController {
  <<controller>>
  +ingestReading(json)
  +getRealtime(stationId)
  +getHistory(stationId, range)
  +getForecast(stationId)
}

class AuthController {
  <<controller>>
  +register(dto)
  +login(credentials)
  +refreshToken()
}

class WeatherService {
  <<service>>
  +saveReading(dto)
  +getRealtime(stationId)
  +getHistory(stationId)
  +evaluateAlerts(reading)
}

class ForecastService {
  <<service>>
  +generateForecast(stationId)
  +getLatestForecast(stationId)
}

class NotificationService {
  <<service>>
  +createAlert(reading)
  +pushAlert(user, message)
}

class UserRepository {
  <<repository>>
  +save(user)
  +findByEmail(email)
  +findById(id)
}

class ReadingRepository {
  <<repository>>
  +save(reading)
  +findLatestByStation(stationId)
  +findHistoryByStation(stationId)
}

class ForecastRepository {
  <<repository>>
  +save(forecast)
  +findLatestByStation(stationId)
}

class MySQLDatabase {
  <<database>>
  +usersTable
  +readingsTable
  +forecastsTable
  +executeQuery(sql)
}

Gateway --> WeatherApiController : HTTP/JSON
WeatherApiController --> WeatherService
WeatherApiController --> ForecastService
AuthController --> UserRepository
WeatherService --> ReadingRepository
WeatherService --> NotificationService
ReadingRepository --> MySQLDatabase
ForecastService --> ForecastRepository
ForecastRepository --> MySQLDatabase
UserRepository --> MySQLDatabase


%% =========================
%% LAYER: ML ENGINE
%% =========================
class MLModel {
  <<ml>>
  +algorithm: string    %% RandomForestRegressor
  +method: string       %% IncrementalLearning
  +r2Score: float
  +trainInitial(data)
  +incrementalTrain(data)
  +predict(features)
}

class FeatureEngineer {
  <<ml>>
  +buildFeatures(readings)
  +buildTrainingSet()
}

FeatureEngineer --> MySQLDatabase : load\nhistorical data
FeatureEngineer --> MLModel : supply features
ForecastService --> MLModel : memanggil\npredict()
MLModel --> MySQLDatabase : simpan\nmodel metrics


%% =========================
%% LAYER: MOBILE APP (Flutter)
%% =========================
class MobileApplication {
  <<flutter>>
  +run()
  +navigateToRealtime()
  +navigateToHistory()
  +navigateToForecast()
}

class ApiClient {
  <<client>>
  +baseUrl: string
  +get(path)
  +post(path, body)
}

class AuthManager {
  <<client>>
  +accessToken: string
  +login(email, password)
  +logout()
  +refreshToken()
}

class RealtimeView {
  <<ui>>
  +renderCurrentWeather()
  +showStatus()
}

class HistoryView {
  <<ui>>
  +renderChart()
  +filterRange()
}

class ForecastView {
  <<ui>>
  +renderForecastCard()
  +showTrend()
}

class AlertManager {
  <<client>>
  +subscribeTopic(stationId)
  +handlePushNotification()
}

MobileApplication --> AuthManager
MobileApplication --> RealtimeView
MobileApplication --> HistoryView
MobileApplication --> ForecastView
MobileApplication --> AlertManager

AuthManager --> ApiClient
RealtimeView --> ApiClient
HistoryView --> ApiClient
ForecastView --> ApiClient
AlertManager --> ApiClient

ApiClient --> WeatherApiController : REST
ApiClient --> AuthController : REST

%% =========================
%% CROSS-LAYER LINK
%% =========================
WeatherStation "1" --> "*" ForecastRepository : baca\nforecast per stasiun
MobileApplication --> WeatherStation : pilih\nstasiun (ID)
```

Kalau mau, nanti kita bisa buat versi “disederhanakan” (lebih sedikit kelas) khusus untuk dimasukkan ke laporan/skripsi, dan versi lengkap (seperti di atas) untuk dokumentasi teknis internal.