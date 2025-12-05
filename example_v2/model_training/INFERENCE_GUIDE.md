# Panduan Inferensi Model Cuaca (V2.0)

Panduan ini menjelaskan cara menggunakan file `weather_model_v2.pkl` yang dihasilkan dari notebook `weather_model_training_advanced.ipynb` untuk melakukan prediksi cuaca.

## 1. Lokasi dan Struktur Model

Model disimpan dalam satu file `.pkl` (default: `weather_model_v2.pkl`) yang berisi dictionary dengan struktur berikut:

```python
{
    'regressor': MultiOutputRegressor(...),      # Model untuk Temp, Humidity, Wind, Pressure
    'classifier': RandomForestClassifier(...),   # Model untuk Weather Code
    'label_encoder': LabelEncoder(...),          # Encoder untuk Weather Code
    'features': [...],                           # List nama fitur yang digunakan saat training
    'targets_reg': [...],                        # List target regresi
    'version': '2.0'
}
```

## 2. Persyaratan Fitur (Feature Engineering)

Model V2.0 menggunakan **Lag Features**, **Rolling Means**, dan **Cyclical Time Features**. Anda memerlukan data historis (minimal 24 jam terakhir) untuk membuat fitur-fitur ini.

### Fitur yang Digunakan:
1.  **Waktu (Cyclical)**:
    -   `hour_sin`, `hour_cos`
    -   `month_sin`, `month_cos`
    -   `year`, `month`, `day`, `hour` (Original)
2.  **Lag Features** (Untuk setiap variabel: `temp`, `humidity`, `windspeed`, `sealevelpressure`):
    -   `_lag_1`: Nilai 1 jam yang lalu
    -   `_lag_24`: Nilai 24 jam yang lalu
3.  **Rolling Features** (Untuk setiap variabel):
    -   `_rolling_24`: Rata-rata 24 jam terakhir

## 3. Langkah-langkah Inferensi

### A. Load Model
Gunakan `pickle` atau `joblib` untuk memuat model.

```python
import pickle

model_path = 'models/weather_model_v2.pkl'
with open(model_path, 'rb') as f:
    model_data = pickle.load(f)

regressor = model_data['regressor']
classifier = model_data['classifier']
features = model_data['features']
```

### B. Siapkan Data Input
Anda perlu mengambil data historis 24 jam terakhir dari database.

```python
import pandas as pd
import numpy as np

def prepare_input(df_history):
    """
    df_history: DataFrame berisi 24 jam data terakhir dengan kolom:
                ['timestamp', 'temp', 'humidity', 'windspeed', 'sealevelpressure']
    """
    # Ambil baris terakhir sebagai basis waktu prediksi (jam berikutnya)
    last_row = df_history.iloc[-1]
    next_timestamp = last_row['timestamp'] + pd.Timedelta(hours=1)
    
    # 1. Fitur Waktu Cyclical
    hour = next_timestamp.hour
    month = next_timestamp.month
    
    input_data = {
        'year': next_timestamp.year,
        'month': month,
        'day': next_timestamp.day,
        'hour': hour,
        'hour_sin': np.sin(2 * np.pi * hour / 24),
        'hour_cos': np.cos(2 * np.pi * hour / 24),
        'month_sin': np.sin(2 * np.pi * month / 12),
        'month_cos': np.cos(2 * np.pi * month / 12)
    }
    
    # 2. Lag & Rolling Features untuk setiap target
    targets = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
    
    for col in targets:
        # Lag 1 (Nilai jam terakhir)
        input_data[f'{col}_lag_1'] = last_row[col]
        
        # Lag 24 (Nilai 24 jam lalu - baris pertama dari df_history 24 jam)
        input_data[f'{col}_lag_24'] = df_history.iloc[0][col]
        
        # Rolling 24 (Rata-rata 24 jam terakhir)
        input_data[f'{col}_rolling_24'] = df_history[col].mean()
        
    return pd.DataFrame([input_data])
```

### C. Lakukan Prediksi

```python
# Pastikan urutan kolom sesuai dengan saat training
X_input = prepare_input(df_history_24h)[features]

# 1. Prediksi Regresi (Temp, Humidity, Wind, Pressure)
reg_preds = regressor.predict(X_input)
# Output: [[temp, humidity, windspeed, pressure]]

# 2. Prediksi Klasifikasi (Weather Code)
class_pred = classifier.predict(X_input)
# Output: [weather_code] (Original code, e.g., 3, 61, 95)

print(f"Prediksi Cuaca: {class_pred[0]}")
print(f"Prediksi Suhu: {reg_preds[0][0]:.2f}°C")
```

## 4. Prediksi Masa Depan (Recursive Forecasting)
Untuk memprediksi lebih dari 1 jam ke depan (misal: 7 hari ke depan), gunakan metode **Recursive Forecasting**:

1.  Prediksi jam ke-(t+1).
2.  Tambahkan hasil prediksi ke dalam dataset historis (sebagai data "aktual" baru).
3.  Geser jendela data (buang data paling lama, masukkan data baru).
4.  Hitung ulang fitur Lag dan Rolling berdasarkan data yang diperbarui.
5.  Ulangi untuk jam ke-(t+2), dst.
