# Weather Forecasting System - Panduan Lengkap

## 📋 Daftar Isi

* [Overview](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#overview)
* [Arsitektur System](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#arsitektur-system)
* [Instalasi](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#instalasi)
* [Training Model](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#training-model)
* [Menjalankan Backend](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#menjalankan-backend)
* [API Documentation](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#api-documentation)
* [Cara Kerja Model](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#cara-kerja-model)
* [Troubleshooting](https://claude.ai/chat/0ee3f714-8daa-4189-a3c3-66a4caa5b4c1#troubleshooting)

---

## 🎯 Overview

Sistem prediksi cuaca berbasis **Time-Series Forecasting** menggunakan machine learning untuk memprediksi:

### Target Prediksi:

1. **Regresi (Data Kontinu)** :

* Suhu (Temperature)
* Kelembaban (Humidity)
* Kecepatan Angin (Wind Speed)
* Tekanan Udara (Pressure)

1. **Klasifikasi** :

* Kondisi Cuaca (Cerah, Berawan, Hujan, dll)
* Status Hujan (Ya/Tidak)

### Fitur Unggulan:

✓  **Time-Series Features** : Menggunakan lag features dan rolling mean untuk menangkap pola temporal

✓  **Multiple Models** : Perbandingan 4 model regresi dan 3 model klasifikasi

✓  **High Accuracy** : Model terbaik dipilih berdasarkan metrik R² dan F1-Score

✓  **RESTful API** : Backend FastAPI yang siap production

✓  **Incremental Learning** : Mendukung update model dengan data baru

---

## 🏗️ Arsitektur System

```
weather-forecasting/
│
├── data_collections/
│   └── datasets/
│       └── historical_data_2000_2024.csv    # Data historis
│
├── models/
│   └── weather_model_v2.pkl                 # Model yang sudah dilatih
│
├── notebooks/
│   └── weather_training.ipynb               # Notebook untuk training
│
├── api/
│   └── weather_api.py                       # Backend FastAPI
│
├── visualizations/
│   ├── actual_vs_predicted.png              # Visualisasi hasil
│   └── incremental_learning.png
│
└── requirements.txt                         # Dependencies
```

---

## 🔧 Instalasi

### 1. Clone atau Download Project

### 2. Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn scikit-learn joblib fastapi uvicorn
```

**Atau gunakan requirements.txt:**

```bash
pip install -r requirements.txt
```

**Isi requirements.txt:**

```
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
joblib>=1.3.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
```

### 3. Persiapan Struktur Folder

Pastikan struktur folder sesuai dengan arsitektur di atas.

---

## 🎓 Training Model

### Langkah 1: Persiapan Data

Pastikan file `historical_data_2000_2024.csv` berada di folder yang benar:

```
data_collections/datasets/historical_data_2000_2024.csv
```

Format data harus memiliki kolom:

* `timestamp`, `temp`, `humidity`, `windspeed`, `sealevelpressure`
* `conditions`, `year`, `month`, `day`, `hour`

### Langkah 2: Jalankan Notebook Training

Buka `weather_training.ipynb` di Jupyter Notebook/Lab dan jalankan semua cell secara berurutan.

**Proses yang terjadi:**

1. **Load dan Pre-processing Data**
   * Membaca data historis
   * Membuat fitur lag (1 jam dan 24 jam)
   * Membuat rolling mean (24 jam)
   * Membuat cyclical features (sin/cos untuk hour dan month)
2. **Perbandingan Model Regresi**
   ```
   - Linear Regression
   - K-Neighbors Regressor
   - Decision Tree Regressor
   - Random Forest Regressor ✓ (Biasanya terbaik)
   ```
3. **Perbandingan Model Klasifikasi**
   ```
   - Logistic Regression
   - Decision Tree Classifier
   - Random Forest Classifier ✓ (Biasanya terbaik)
   ```
4. **Evaluasi Metrik**
   * **Regresi** : MSE, MAE, RMSE, R²
   * **Klasifikasi** : Accuracy, F1-Score
5. **Simpan Model**
   * Model terbaik disimpan ke `models/weather_model_v2.pkl`

### Output yang Diharapkan:

```
✓ Model berhasil disimpan ke: ../models/weather_model_v2.pkl
  - Regressor: Random Forest
  - Classifier: Random Forest
  - Ukuran file: ~50-200 MB
```

### Visualisasi yang Dihasilkan:

1. **actual_vs_predicted.png** : Grafik perbandingan prediksi vs aktual untuk 4 parameter
2. **incremental_learning.png** : Grafik dampak jumlah data terhadap performa model

---

## 🚀 Menjalankan Backend

### Langkah 1: Jalankan Server

```bash
cd api
python weather_api.py
```

**Atau dengan Uvicorn:**

```bash
uvicorn weather_api:app --reload --host 127.0.0.1 --port 8000
```

### Langkah 2: Verifikasi Server Berjalan

Buka browser dan akses:

```
http://127.0.0.1:8000
```

Response yang diharapkan:

```json
{
  "status": "online",
  "service": "Weather Prediction API",
  "model_loaded": true,
  "historical_data_loaded": true,
  "version": "2.0"
}
```

### Langkah 3: Akses API Documentation

FastAPI menyediakan dokumentasi interaktif otomatis:

```
http://127.0.0.1:8000/docs
```

---

## 📡 API Documentation

### 1. Get Model Info

**Endpoint:** `GET /model-info`

**Response:**

```json
{
  "version": "2.0",
  "trained_date": "2024-12-05 10:30:00",
  "regressor": "Random Forest",
  "classifier": "Random Forest",
  "performance": {
    "regression_avg_r2": 0.9523,
    "classification_f1": 0.8945
  }
}
```

---

### 2. Get Predicted Weather Data (Single Day)

**Endpoint:** `GET /weather-data/get-predicted-data`

**Parameters:**

* `day` (int, required): Tanggal (1-31)
* `month` (int, required): Bulan (1-12)
* `year` (int, required): Tahun
* `hour` (int, optional): Jam spesifik (0-23)

**Example Request:**

```
GET http://127.0.0.1:8000/weather-data/get-predicted-data?day=15&month=3&year=2025
```

**Response:**

```json
{
  "daily": {
    "date": "2025-03-15",
    "min_temp": 22.3,
    "max_temp": 31.8,
    "avg_temp": 27.5,
    "avg_humidity": 72.4,
    "dominant_condition": "Partly Cloudy",
    "rain_probability": 25.0
  },
  "hourly": [
    {
      "hour": 0,
      "temp": 23.5,
      "humidity": 85,
      "wind_speed": 4.2,
      "pressure": 1010.3,
      "condition": "Clear",
      "rain": "no"
    },
    {
      "hour": 1,
      "temp": 23.2,
      "humidity": 86,
      "wind_speed": 3.8,
      "pressure": 1010.1,
      "condition": "Clear",
      "rain": "no"
    }
    // ... 22 hours more
  ]
}
```

**Example Request (Specific Hour):**

```
GET http://127.0.0.1:8000/weather-data/get-predicted-data?day=15&month=3&year=2025&hour=14
```

**Response:**

```json
{
  "daily": {
    "date": "2025-03-15",
    "min_temp": 22.3,
    "max_temp": 31.8,
    "avg_temp": 27.5,
    "avg_humidity": 72.4,
    "dominant_condition": "Partly Cloudy",
    "rain_probability": 25.0
  },
  "hourly": [
    {
      "hour": 14,
      "temp": 31.8,
      "humidity": 58,
      "wind_speed": 8.5,
      "pressure": 1008.7,
      "condition": "Partly Cloudy",
      "rain": "no"
    }
  ]
}
```

---

### 3. Get Range Prediction (Multiple Days)

**Endpoint:** `GET /weather-data/get-range-prediction`

**Parameters:**

* `start_day` (int, required): Tanggal mulai
* `start_month` (int, required): Bulan mulai
* `start_year` (int, required): Tahun mulai
* `days` (int, optional): Jumlah hari (default: 7)

**Example Request:**

```
GET http://127.0.0.1:8000/weather-data/get-range-prediction?start_day=1&start_month=6&start_year=2025&days=5
```

**Response:**

```json
{
  "start_date": "2025-06-01",
  "end_date": "2025-06-05",
  "days": 5,
  "predictions": [
    {
      "daily": { /* data hari 1 */ },
      "hourly": [ /* 24 jam */ ]
    },
    {
      "daily": { /* data hari 2 */ },
      "hourly": [ /* 24 jam */ ]
    }
    // ... 3 days more
  ]
}
```

---

## 🧠 Cara Kerja Model

### 1. Feature Engineering

Model menggunakan **Time-Series Features** untuk menangkap pola temporal:

#### A. Lag Features

* **lag_1** : Nilai 1 jam yang lalu
* **lag_24** : Nilai 24 jam yang lalu (kondisi kemarin pada jam yang sama)

#### B. Rolling Mean

* **rolling_mean_24** : Rata-rata 24 jam terakhir (tren jangka pendek)

#### C. Cyclical Features

* **hour_sin, hour_cos** : Encoding cyclical untuk jam (0-23)
* **month_sin, month_cos** : Encoding cyclical untuk bulan (1-12)

**Contoh Fitur untuk Prediksi:**

```python
# Untuk memprediksi suhu jam 14:00 tanggal 15 Maret 2025:
features = {
    'year': 2025,
    'month': 3,
    'day': 15,
    'hour': 14,
    'hour_sin': sin(2π * 14/24),
    'hour_cos': cos(2π * 14/24),
    'temp_lag_1': 30.5,        # Suhu jam 13:00
    'temp_lag_24': 31.2,       # Suhu jam 14:00 kemarin
    'temp_rolling_mean_24': 28.7,  # Rata-rata 24 jam terakhir
    # ... fitur lain untuk humidity, windspeed, pressure
}
```

### 2. Proses Prediksi di Backend

```
User Request
    ↓
Ambil Data Historis 48 jam terakhir
    ↓
Generate Lag Features & Rolling Mean
    ↓
Generate Cyclical Features
    ↓
Gabungkan Semua Fitur
    ↓
Model Regresi → [Temp, Humidity, Wind, Pressure]
    ↓
Model Klasifikasi → [Kondisi Cuaca]
    ↓
Post-Processing (Rain Classification)
    ↓
Return JSON Response
```

### 3. Model yang Digunakan

**Default (Biasanya terbaik):**

* **Regresi** : Random Forest Regressor
* Mampu menangkap non-linear relationships
* Robust terhadap outliers
* Tidak mudah overfitting
* **Klasifikasi** : Random Forest Classifier
* Akurasi tinggi untuk multi-class
* Feature importance yang jelas

---

## 🐛 Troubleshooting

### Problem 1: Model file not found

**Error:**

```
⚠ Warning: Model file not found at ../models/weather_model_v2.pkl
```

**Solusi:**

1. Pastikan sudah menjalankan notebook training
2. Periksa path file di `weather_api.py`:
   ```python
   MODEL_PATH = os.path.join(BASE_DIR, '../models/weather_model_v2.pkl')
   ```
3. Sesuaikan path jika struktur folder berbeda

---

### Problem 2: Historical data not found

**Error:**

```
⚠ Warning: Historical data not found
```

**Solusi:**

1. Pastikan file `historical_data_2000_2024.csv` ada
2. Periksa path di `weather_api.py`:
   ```python
   HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, '../data_collections/datasets/historical_data_2000_2024.csv')
   ```

---

### Problem 3: Prediksi tidak akurat

**Solusi:**

1. **Tambah Data Training** : Model akan lebih akurat dengan data lebih banyak
2. **Feature Engineering Lebih Lanjut** : Tambahkan fitur seperti:

* Lag 48 jam, 72 jam
* Rolling mean window yang berbeda (12 jam, 48 jam)
* Interaksi antar fitur

1. **Hyperparameter Tuning** : Gunakan GridSearchCV untuk mencari parameter terbaik

---

### Problem 4: Server lambat

**Solusi:**

1. **Reduce Model Complexity** :

```python
   RandomForestRegressor(n_estimators=50, max_depth=10)
```

1. **Cache Predictions** : Simpan prediksi yang sering diminta
2. **Use Async** : Implementasikan async endpoints

---

## 📊 Metrik Performa yang Baik

### Regresi:

* **R² Score** : > 0.85 (Excellent), > 0.70 (Good)
* **RMSE Suhu** : < 2°C (Excellent), < 3°C (Good)
* **MAE Kelembaban** : < 5% (Excellent), < 10% (Good)

### Klasifikasi:

* **Accuracy** : > 0.85 (Excellent), > 0.75 (Good)
* **F1-Score** : > 0.80 (Excellent), > 0.70 (Good)

---

## 🔄 Update Model dengan Data Baru

Untuk update model dengan data terbaru:

1. Tambahkan data baru ke `historical_data_2000_2024.csv`
2. Jalankan ulang notebook training
3. Model baru akan otomatis tersimpan
4. Restart backend untuk load model baru

**Incremental Learning** (optional):

```python
# Dalam production, bisa gunakan partial_fit untuk SGD-based models
model.partial_fit(new_X, new_y)
```

---

## 📞 Support

Jika ada masalah atau pertanyaan:

1. Periksa log di console backend
2. Gunakan API documentation di `/docs`
3. Review visualisasi hasil training

---

## 📝 License

Project ini untuk keperluan edukasi dan penelitian.

---

**Happy Forecasting! 🌤️⛈️🌈**
