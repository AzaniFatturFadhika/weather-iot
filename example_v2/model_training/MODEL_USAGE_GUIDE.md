# Panduan Penggunaan Model Weather Prediction

Dokumentasi lengkap untuk menggunakan model prediksi cuaca yang telah ditraining berdasarkan `training_guide.md`.

---

## Daftar Model (.pkl)

| File | Ukuran | Deskripsi |
|------|--------|-----------|
| `weather_model_combined.pkl` | 10.7 MB | **Rekomendasi** - Semua model + metadata lengkap |
| `weather_model_hourly.pkl` | 5.9 MB | Model hourly (regressor + classifier) |
| `weather_model_daily.pkl` | 4.8 MB | Model daily (regressor + classifier) |
| `weather_model_hourly_regressor.pkl` | 1.8 MB | Regressor hourly saja |
| `weather_model_hourly_classifier.pkl` | 4.1 MB | Classifier hourly saja |
| `weather_model_daily_regressor.pkl` | 2.5 MB | Regressor daily saja |
| `weather_model_daily_classifier.pkl` | 2.3 MB | Classifier daily saja |

---

## 1. Quick Start

### Load Model Combined (Rekomendasi)

```python
import joblib
import numpy as np
import pandas as pd

# Load model
model = joblib.load('models/weather_model_combined.pkl')

# Akses komponen
hourly_regressor = model['hourly']['regressor']
hourly_classifier = model['hourly']['classifier']
hourly_features = model['hourly']['feature_columns']

daily_regressor = model['daily']['regressor']
daily_classifier = model['daily']['classifier']
daily_features = model['daily']['feature_columns']

# Metadata
weather_code_to_rain = model['weather_code_to_rain']
label_encoder = model.get('label_encoder')
```

---

## 2. Struktur Data Model

### 2.1 Model Hourly

**Target Regresi:** `temp`, `humidity`, `windspeed`, `sealevelpressure`

**Target Klasifikasi:** `weather_code` (10 kelas)

**Feature Columns (13 fitur):**
```python
hourly_feature_cols = [
    'hour', 'month',
    'temp_lag_1', 'temp_lag_24', 'temp_rolling_24',
    'humidity_lag_1', 'humidity_lag_24', 'humidity_rolling_24',
    'windspeed_lag_1', 'windspeed_lag_24', 'windspeed_rolling_24',
    'sealevelpressure_lag_1', 'sealevelpressure_lag_24'
]
```

### 2.2 Model Daily

**Target Regresi:** `temp_min`, `temp_max`, `temp_mean`, `humidity_avg`, `windspeed_avg`, `pressure_avg`

**Target Klasifikasi:** `weather_code_dominant`

**Feature Columns (12 fitur):**
```python
daily_feature_cols = [
    'month', 'day',
    'temp_min_lag_1', 'temp_max_lag_1', 'temp_mean_lag_1',
    'humidity_avg_lag_1', 'windspeed_avg_lag_1', 'pressure_avg_lag_1',
    'temp_min_lag_7', 'temp_max_lag_7', 'temp_mean_lag_7',
    'rain_total_lag_1'
]
```

---

## 3. Prediksi Hourly (Per-Jam)

### 3.1 Single Prediction

```python
import joblib
import numpy as np

# Load model
model = joblib.load('models/weather_model_hourly.pkl')
regressor = model['regressor']
classifier = model['classifier']
feature_cols = model['feature_columns']

# Siapkan data input (contoh: data jam 14:00)
input_data = {
    'hour': 14,
    'month': 12,
    'temp_lag_1': 28.5,           # Suhu 1 jam lalu
    'temp_lag_24': 27.0,          # Suhu 24 jam lalu
    'temp_rolling_24': 26.8,      # Rata-rata suhu 24 jam
    'humidity_lag_1': 75,
    'humidity_lag_24': 80,
    'humidity_rolling_24': 78,
    'windspeed_lag_1': 5.2,
    'windspeed_lag_24': 4.8,
    'windspeed_rolling_24': 5.0,
    'sealevelpressure_lag_1': 1010.5,
    'sealevelpressure_lag_24': 1011.0
}

# Convert ke numpy array
X = np.array([[input_data[col] for col in feature_cols]])

# Prediksi
reg_prediction = regressor.predict(X)[0]  # [temp, humidity, windspeed, pressure]
clf_prediction = classifier.predict(X)[0]  # weather_code (encoded)

print(f"Temperature: {reg_prediction[0]:.1f}°C")
print(f"Humidity: {reg_prediction[1]:.1f}%")
print(f"Wind Speed: {reg_prediction[2]:.1f} km/h")
print(f"Pressure: {reg_prediction[3]:.1f} hPa")
print(f"Weather Code: {clf_prediction}")
```

### 3.2 Multi-Step Recursive Forecast (72 Jam)

```python
def recursive_forecast_hourly(regressor, classifier, last_data, feature_cols, n_hours=72):
    """
    Prediksi rekursif N jam ke depan
    
    Args:
        regressor: Model regresi
        classifier: Model klasifikasi
        last_data: DataFrame baris terakhir data historis
        feature_cols: List nama fitur
        n_hours: Jumlah jam prediksi
    
    Returns:
        DataFrame hasil prediksi
    """
    predictions = []
    current = last_data.copy()
    
    for i in range(n_hours):
        X = current[feature_cols].values.reshape(1, -1)
        reg_pred = regressor.predict(X)[0]
        clf_pred = classifier.predict(X)[0]
        
        predictions.append({
            'hour_ahead': i + 1,
            'temp': reg_pred[0],
            'humidity': reg_pred[1],
            'windspeed': reg_pred[2],
            'sealevelpressure': reg_pred[3],
            'weather_code': clf_pred
        })
        
        # Update lag features untuk iterasi berikutnya
        current['temp_lag_1'] = reg_pred[0]
        current['humidity_lag_1'] = reg_pred[1]
        current['windspeed_lag_1'] = reg_pred[2]
        current['sealevelpressure_lag_1'] = reg_pred[3]
    
    return pd.DataFrame(predictions)

# Contoh penggunaan
forecast = recursive_forecast_hourly(regressor, classifier, last_row, feature_cols, 72)
print(forecast.head())
```

---

## 4. Prediksi Daily (Per-Hari)

### 4.1 Single Day Prediction

```python
import joblib
import numpy as np

# Load model
model = joblib.load('models/weather_model_daily.pkl')
regressor = model['regressor']
classifier = model['classifier']
feature_cols = model['feature_columns']

# Siapkan data input (prediksi untuk besok)
input_data = {
    'month': 12,
    'day': 6,
    'temp_min_lag_1': 22.5,      # Temp min kemarin
    'temp_max_lag_1': 31.0,
    'temp_mean_lag_1': 26.5,
    'humidity_avg_lag_1': 78,
    'windspeed_avg_lag_1': 5.5,
    'pressure_avg_lag_1': 1010.2,
    'temp_min_lag_7': 22.0,      # Temp min 7 hari lalu
    'temp_max_lag_7': 30.5,
    'temp_mean_lag_7': 26.0,
    'rain_total_lag_1': 2.5      # Total hujan kemarin (mm)
}

X = np.array([[input_data[col] for col in feature_cols]])

reg_pred = regressor.predict(X)[0]
clf_pred = classifier.predict(X)[0]

print(f"Prediksi untuk {input_data['month']}/{input_data['day']}:")
print(f"  Temp Min: {reg_pred[0]:.1f}°C")
print(f"  Temp Max: {reg_pred[1]:.1f}°C")
print(f"  Temp Mean: {reg_pred[2]:.1f}°C")
print(f"  Humidity: {reg_pred[3]:.1f}%")
print(f"  Wind Speed: {reg_pred[4]:.1f} km/h")
print(f"  Pressure: {reg_pred[5]:.1f} hPa")
print(f"  Weather Code: {clf_pred}")
```

---

## 5. Mapping Weather Code → Rain

```python
WEATHER_CODE_TO_RAIN = {
    0: 0.0,    # Clear
    1: 0.0,    # Partially cloudy
    2: 0.0,    # Partially cloudy
    3: 0.0,    # Overcast
    51: 0.2,   # Light rain
    53: 0.7,   # Moderate rain
    55: 1.1,   # Heavy showers
    61: 1.7,   # Rain, overcast
    63: 4.0,   # Rain, overcast (moderate)
    65: 10.3   # Heavy rain, overcast
}

WEATHER_CODE_TO_CONDITION = {
    0: 'Clear',
    1: 'Partially cloudy',
    2: 'Partially cloudy',
    3: 'Overcast',
    51: 'Light Rain',
    53: 'Moderate Rain',
    55: 'Heavy Showers',
    61: 'Rain, Overcast',
    63: 'Rain, Overcast',
    65: 'Heavy Rain'
}

def get_rain_from_weather_code(weather_code):
    """Derive nilai rain dari weather_code"""
    return WEATHER_CODE_TO_RAIN.get(weather_code, 0.0)

def is_rainy(weather_code):
    """Cek apakah hujan (weather_code >= 50)"""
    return weather_code >= 50

# Contoh
weather_code = 63
print(f"Rain: {get_rain_from_weather_code(weather_code)} mm")
print(f"Rainy: {is_rainy(weather_code)}")
print(f"Condition: {WEATHER_CODE_TO_CONDITION[weather_code]}")
```

---

## 6. Feature Engineering dari Data Mentah

Jika Anda memiliki data cuaca mentah terbaru dari sensor/API, gunakan fungsi berikut:

```python
def prepare_hourly_features(df):
    """
    Siapkan fitur untuk prediksi hourly dari data mentah
    
    Args:
        df: DataFrame dengan kolom: timestamp, hour, month, temp, humidity, 
            windspeed, sealevelpressure
    
    Returns:
        DataFrame dengan fitur lag dan rolling
    """
    df = df.sort_values('timestamp').copy()
    
    for col in ['temp', 'humidity', 'windspeed', 'sealevelpressure']:
        df[f'{col}_lag_1'] = df[col].shift(1)
        df[f'{col}_lag_24'] = df[col].shift(24)
        df[f'{col}_rolling_24'] = df[col].rolling(24).mean()
    
    return df.dropna()

def prepare_daily_features(df):
    """
    Siapkan fitur untuk prediksi daily dari data mentah
    
    Args:
        df: DataFrame hourly dengan timestamp, temp, humidity, windspeed, 
            sealevelpressure, weather_code, rain
    
    Returns:
        DataFrame daily dengan fitur lag
    """
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    daily = df.groupby('date').agg({
        'temp': ['min', 'max', 'mean'],
        'humidity': 'mean',
        'windspeed': 'mean',
        'sealevelpressure': 'mean',
        'weather_code': lambda x: x.mode()[0],
        'rain': 'sum'
    }).reset_index()
    
    daily.columns = ['date', 'temp_min', 'temp_max', 'temp_mean', 
                     'humidity_avg', 'windspeed_avg', 'pressure_avg',
                     'weather_code_dominant', 'rain_total']
    
    daily['month'] = pd.to_datetime(daily['date']).dt.month
    daily['day'] = pd.to_datetime(daily['date']).dt.day
    
    # Lag features
    for col in ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 
                'windspeed_avg', 'pressure_avg']:
        daily[f'{col}_lag_1'] = daily[col].shift(1)
    
    daily['temp_min_lag_7'] = daily['temp_min'].shift(7)
    daily['temp_max_lag_7'] = daily['temp_max'].shift(7)
    daily['temp_mean_lag_7'] = daily['temp_mean'].shift(7)
    daily['rain_total_lag_1'] = daily['rain_total'].shift(1)
    
    return daily.dropna()
```

---

## 7. Integrasi dengan Backend API

### WeatherPredictor Class

```python
import joblib
import numpy as np
from datetime import datetime

class WeatherPredictor:
    """Wrapper class untuk prediksi cuaca"""
    
    def __init__(self, model_path='models/weather_model_combined.pkl'):
        self.model = joblib.load(model_path)
        self.hourly_reg = self.model['hourly']['regressor']
        self.hourly_clf = self.model['hourly']['classifier']
        self.hourly_features = self.model['hourly']['feature_columns']
        self.daily_reg = self.model['daily']['regressor']
        self.daily_clf = self.model['daily']['classifier']
        self.daily_features = self.model['daily']['feature_columns']
        self.weather_map = self.model.get('weather_code_to_rain', {})
    
    def predict_hourly(self, features: dict) -> dict:
        """Prediksi cuaca per-jam"""
        X = np.array([[features[col] for col in self.hourly_features]])
        reg = self.hourly_reg.predict(X)[0]
        clf = self.hourly_clf.predict(X)[0]
        
        return {
            'temp': round(reg[0], 1),
            'humidity': round(reg[1], 1),
            'windspeed': round(reg[2], 1),
            'sealevelpressure': round(reg[3], 1),
            'weather_code': int(clf),
            'rain': self.weather_map.get(int(clf), 0.0),
            'is_rainy': int(clf) >= 50
        }
    
    def predict_daily(self, features: dict) -> dict:
        """Prediksi cuaca per-hari"""
        X = np.array([[features[col] for col in self.daily_features]])
        reg = self.daily_reg.predict(X)[0]
        clf = self.daily_clf.predict(X)[0]
        
        return {
            'temp_min': round(reg[0], 1),
            'temp_max': round(reg[1], 1),
            'temp_mean': round(reg[2], 1),
            'humidity_avg': round(reg[3], 1),
            'windspeed_avg': round(reg[4], 1),
            'pressure_avg': round(reg[5], 1),
            'weather_code_dominant': int(clf),
            'rain_total': self.weather_map.get(int(clf), 0.0),
            'is_rainy': int(clf) >= 50
        }

# Contoh penggunaan
predictor = WeatherPredictor()

result = predictor.predict_hourly({
    'hour': 14, 'month': 12,
    'temp_lag_1': 28.5, 'temp_lag_24': 27.0, 'temp_rolling_24': 26.8,
    'humidity_lag_1': 75, 'humidity_lag_24': 80, 'humidity_rolling_24': 78,
    'windspeed_lag_1': 5.2, 'windspeed_lag_24': 4.8, 'windspeed_rolling_24': 5.0,
    'sealevelpressure_lag_1': 1010.5, 'sealevelpressure_lag_24': 1011.0
})
print(result)
```

---

## 8. Catatan Penting

### 8.1 Batasan Model
- Model dilatih dengan data **2000-2024** dari lokasi spesifik
- Prediksi terbaik untuk **1-72 jam** (hourly) dan **1-7 hari** (daily)
- Akurasi menurun seiring jarak prediksi yang lebih jauh

### 8.2 Label Encoder
Weather code sudah di-encode saat training. Jika model menyimpan `label_encoder`:
```python
le = model.get('label_encoder')
original_code = le.inverse_transform([predicted_code])[0]
```

### 8.3 Requirements
```
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
joblib>=1.2.0
xgboost>=1.7.0  # Jika model menggunakan XGBoost
```

---

## 9. Troubleshooting

| Error | Penyebab | Solusi |
|-------|----------|--------|
| `Feature shape mismatch` | Jumlah fitur input tidak sesuai | Pastikan menggunakan `feature_columns` dari model |
| `KeyError` | Nama kolom salah | Cek nama kolom dengan `model['hourly']['feature_columns']` |
| `ValueError: Unknown label` | Weather code baru | Gunakan `weather_code_to_rain` mapping manual |
