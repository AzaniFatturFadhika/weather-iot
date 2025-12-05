"""
Weather Prediction API Backend
================================
Backend untuk melakukan prediksi cuaca menggunakan time-series model
yang telah dilatih dengan fitur lag dan rolling mean.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import List, Optional

app = FastAPI()

# ============================================================================
# LOAD MODELS
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '../models/weather_model_v2.pkl')
HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, '../data_collections/datasets/historical_data_2000_2024.csv')

models = {}
historical_df = None

try:
    if os.path.exists(MODEL_PATH):
        models = joblib.load(MODEL_PATH)
        print(f"✓ Models loaded successfully from {MODEL_PATH}")
        print(f"  - Regressor: {models['model_type']['regressor']}")
        print(f"  - Classifier: {models['model_type']['classifier']}")
        print(f"  - Version: {models['version']}")
        print(f"  - Trained: {models['trained_date']}")
    else:
        print(f"⚠ Warning: Model file not found at {MODEL_PATH}")
except Exception as e:
    print(f"✗ Error loading models: {e}")

try:
    if os.path.exists(HISTORICAL_DATA_PATH):
        historical_df = pd.read_csv(HISTORICAL_DATA_PATH)
        historical_df['timestamp'] = pd.to_datetime(historical_df['timestamp'])
        historical_df = historical_df.sort_values('timestamp').reset_index(drop=True)
        print(f"✓ Historical data loaded: {len(historical_df):,} records")
        print(f"  - Date range: {historical_df['timestamp'].min()} to {historical_df['timestamp'].max()}")
    else:
        print(f"⚠ Warning: Historical data not found at {HISTORICAL_DATA_PATH}")
except Exception as e:
    print(f"✗ Error loading historical data: {e}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_recent_data(target_date: datetime, hours_back: int = 24):
    """
    Mengambil data historis terkini untuk membuat fitur lag dan rolling mean.
    
    Args:
        target_date: Tanggal target prediksi
        hours_back: Berapa jam ke belakang yang diambil
    
    Returns:
        DataFrame dengan data historis
    """
    if historical_df is None:
        return None
    
    # Cari data sebelum target_date
    mask = historical_df['timestamp'] < target_date
    recent_data = historical_df[mask].tail(hours_back)
    
    return recent_data


def create_lag_features(target_datetime: datetime, hour: int):
    """
    Membuat fitur lag dan rolling mean berdasarkan data historis.
    
    Args:
        target_datetime: Datetime target untuk prediksi
        hour: Jam dalam sehari (0-23)
    
    Returns:
        Dictionary berisi fitur lag untuk prediksi
    """
    if historical_df is None:
        # Jika tidak ada data historis, gunakan nilai default
        # (ini tidak ideal, sebaiknya selalu ada historical data)
        return create_default_lag_features()
    
    # Ambil data 48 jam terakhir sebelum target
    recent_data = get_recent_data(target_datetime, hours_back=48)
    
    if recent_data is None or len(recent_data) < 24:
        return create_default_lag_features()
    
    # Target columns untuk regression
    regression_targets = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
    
    lag_features = {}
    
    for col in regression_targets:
        # Lag 1 jam: data 1 jam sebelumnya
        if len(recent_data) >= 1:
            lag_features[f'{col}_lag_1'] = recent_data[col].iloc[-1]
        else:
            lag_features[f'{col}_lag_1'] = recent_data[col].mean()
        
        # Lag 24 jam: data 24 jam sebelumnya
        if len(recent_data) >= 24:
            lag_features[f'{col}_lag_24'] = recent_data[col].iloc[-24]
        else:
            lag_features[f'{col}_lag_24'] = recent_data[col].mean()
        
        # Rolling mean 24 jam
        if len(recent_data) >= 24:
            lag_features[f'{col}_rolling_mean_24'] = recent_data[col].tail(24).mean()
        else:
            lag_features[f'{col}_rolling_mean_24'] = recent_data[col].mean()
    
    return lag_features


def create_default_lag_features():
    """
    Membuat fitur lag default jika tidak ada data historis.
    Nilai default berdasarkan kondisi rata-rata.
    """
    regression_targets = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
    
    # Nilai default (bisa disesuaikan dengan kondisi rata-rata lokasi)
    defaults = {
        'temp': 25.0,
        'humidity': 75.0,
        'windspeed': 5.0,
        'sealevelpressure': 1010.0
    }
    
    lag_features = {}
    for col in regression_targets:
        lag_features[f'{col}_lag_1'] = defaults[col]
        lag_features[f'{col}_lag_24'] = defaults[col]
        lag_features[f'{col}_rolling_mean_24'] = defaults[col]
    
    return lag_features


def create_cyclical_features(hour: int, month: int):
    """
    Membuat fitur cyclical (sine/cosine) untuk hour dan month.
    """
    return {
        'hour_sin': np.sin(2 * np.pi * hour / 24),
        'hour_cos': np.cos(2 * np.pi * hour / 24),
        'month_sin': np.sin(2 * np.pi * month / 12),
        'month_cos': np.cos(2 * np.pi * month / 12)
    }


def classify_rain(condition: str) -> str:
    """
    Klasifikasi apakah kondisi cuaca mengindikasikan hujan atau tidak.
    """
    rain_keywords = ['rain', 'drizzle', 'shower', 'thunderstorm']
    condition_lower = condition.lower()
    
    for keyword in rain_keywords:
        if keyword in condition_lower:
            return "yes"
    return "no"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class HourlyPrediction(BaseModel):
    hour: int
    temp: float
    humidity: int
    wind_speed: float
    pressure: float
    condition: str
    rain: str


class DailySummary(BaseModel):
    date: str
    min_temp: float
    max_temp: float
    avg_temp: float
    avg_humidity: float
    dominant_condition: str
    rain_probability: float


class WeatherPredictionResponse(BaseModel):
    daily: DailySummary
    hourly: List[HourlyPrediction]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint untuk health check."""
    return {
        "status": "online",
        "service": "Weather Prediction API",
        "model_loaded": bool(models),
        "historical_data_loaded": historical_df is not None,
        "version": models.get('version', 'N/A') if models else 'N/A'
    }


@app.get("/model-info")
def get_model_info():
    """Endpoint untuk mendapatkan informasi model."""
    if not models:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    return {
        "version": models.get('version'),
        "trained_date": models.get('trained_date'),
        "regressor": models.get('model_type', {}).get('regressor'),
        "classifier": models.get('model_type', {}).get('classifier'),
        "performance": models.get('performance', {}),
        "features": models.get('feature_names', [])
    }


@app.get("/weather-data/get-predicted-data", response_model=WeatherPredictionResponse)
def get_predicted_weather_data(
    day: int, 
    month: int, 
    year: int, 
    hour: Optional[int] = None
):
    """
    Endpoint untuk mendapatkan prediksi cuaca.
    
    Args:
        day: Tanggal (1-31)
        month: Bulan (1-12)
        year: Tahun (contoh: 2025)
        hour: Jam spesifik (0-23), opsional. Jika tidak diberikan, return semua jam.
    
    Returns:
        JSON dengan prediksi harian dan per jam
    
    Example:
        GET /weather-data/get-predicted-data?day=7&month=2&year=2025
        GET /weather-data/get-predicted-data?day=7&month=2&year=2025&hour=14
    """
    # Validasi input
    if not models:
        raise HTTPException(
            status_code=500, 
            detail="Models not loaded. Please ensure model file exists."
        )
    
    try:
        regressor = models['regressor']
        classifier = models['classifier']
        le = models['label_encoder']
        feature_names = models['feature_names']
    except KeyError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Model file structure invalid: missing {e}"
        )
    
    # Validasi tanggal
    try:
        target_date = datetime(year, month, day)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {e}")
    
    # Generate predictions untuk semua jam (0-23)
    hours_to_predict = range(24) if hour is None else [hour]
    
    input_features_list = []
    
    for h in hours_to_predict:
        target_datetime = target_date.replace(hour=h)
        
        # Buat fitur base
        base_features = {
            'year': year,
            'month': month,
            'day': day,
            'hour': h
        }
        
        # Tambahkan cyclical features
        cyclical_features = create_cyclical_features(h, month)
        
        # Tambahkan lag features
        lag_features = create_lag_features(target_datetime, h)
        
        # Gabungkan semua fitur
        all_features = {**base_features, **cyclical_features, **lag_features}
        
        # Pastikan urutan fitur sesuai dengan training
        ordered_features = [all_features[feat] for feat in feature_names]
        input_features_list.append(ordered_features)
    
    # Convert ke numpy array
    X_input = np.array(input_features_list)
    
    try:
        # Prediksi Regression (temp, humidity, wind_speed, pressure)
        pred_reg = regressor.predict(X_input)
        
        # Prediksi Classification (weather_code -> conditions)
        pred_clf = classifier.predict(X_input)
        pred_conditions = le.inverse_transform(pred_clf)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
    
    # Siapkan hasil per jam
    hourly_results = []
    temps = []
    humidities = []
    rain_hours = 0
    
    for i, h in enumerate(hours_to_predict):
        temp = round(float(pred_reg[i][0]), 1)
        humidity = round(float(pred_reg[i][1]), 0)
        wind_speed = round(float(pred_reg[i][2]), 1)
        pressure = round(float(pred_reg[i][3]), 1)
        condition = str(pred_conditions[i])
        rain = classify_rain(condition)
        
        temps.append(temp)
        humidities.append(humidity)
        
        if rain == "yes":
            rain_hours += 1
        
        hourly_results.append(HourlyPrediction(
            hour=h,
            temp=temp,
            humidity=int(humidity),
            wind_speed=wind_speed,
            pressure=pressure,
            condition=condition,
            rain=rain
        ))
    
    # Agregasi harian
    daily_summary = DailySummary(
        date=f"{year}-{month:02d}-{day:02d}",
        min_temp=round(float(min(temps)), 1),
        max_temp=round(float(max(temps)), 1),
        avg_temp=round(float(sum(temps) / len(temps)), 1),
        avg_humidity=round(float(sum(humidities) / len(humidities)), 1),
        dominant_condition=max(set(pred_conditions), key=list(pred_conditions).count),
        rain_probability=round(rain_hours / len(hours_to_predict) * 100, 1)
    )
    
    return WeatherPredictionResponse(
        daily=daily_summary,
        hourly=hourly_results
    )


@app.get("/weather-data/get-range-prediction")
def get_range_prediction(
    start_day: int,
    start_month: int,
    start_year: int,
    days: int = 7
):
    """
    Endpoint untuk mendapatkan prediksi cuaca untuk rentang hari.
    
    Args:
        start_day: Tanggal mulai
        start_month: Bulan mulai
        start_year: Tahun mulai
        days: Jumlah hari ke depan (default: 7)
    
    Returns:
        List prediksi untuk setiap hari
    
    Example:
        GET /weather-data/get-range-prediction?start_day=1&start_month=1&start_year=2025&days=7
    """
    try:
        start_date = datetime(start_year, start_month, start_day)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {e}")
    
    predictions = []
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        
        try:
            prediction = get_predicted_weather_data(
                day=current_date.day,
                month=current_date.month,
                year=current_date.year
            )
            predictions.append(prediction)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting date {current_date}: {e}"
            )
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": (start_date + timedelta(days=days-1)).strftime("%Y-%m-%d"),
        "days": days,
        "predictions": predictions
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
