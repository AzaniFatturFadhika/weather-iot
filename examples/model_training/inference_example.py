import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta

# Konfigurasi Path
# Sesuaikan path ini dengan lokasi file .pkl dan dataset Anda
MODEL_PATH = 'D:\laragon\www\weather-iot\examples\model_training\models\weather_prediction_models.pkl' 
DATA_PATH = 'D:\laragon\www\weather-iot\examples\data_collections\datasets\historical_data_hourly.csv'

def load_models(model_path):
    """Memuat dictionary model yang telah disimpan."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please run the training notebook first.")
    
    print(f"Loading models from {model_path}...")
    return joblib.load(model_path)

def prepare_input_features(df_history, target_col, target_date):
    """
    Mempersiapkan fitur untuk inferensi satu langkah ke depan.
    Harus cocok dengan logic 'create_lag_features' di notebook training.
    """
    # Pastikan data terurut
    df_history = df_history.sort_values('timestamp').reset_index(drop=True)
    
    # Ambil data terakhir yang diperlukan untuk lag dan rolling
    # Max lag = 24, Max rolling window = 24
    # Kita butuh setidaknya 25 data terakhir
    last_data = df_history.tail(30).copy()
    
    # Buat fitur dasar waktu dari target_date
    features = {
        'hour': target_date.hour,
        'month': target_date.month,
        'day': target_date.day
    }
    
    # Hitung Lag Features
    # Lag 1 artinya nilai 1 jam yang lalu (row terakhir dari history)
    # Pastikan kolom target ada di df_history
    if target_col not in last_data.columns:
         raise ValueError(f"Column {target_col} not found in history data")

    features[f'{target_col}_lag_1'] = last_data.iloc[-1][target_col]
    features[f'{target_col}_lag_2'] = last_data.iloc[-2][target_col]
    features[f'{target_col}_lag_3'] = last_data.iloc[-3][target_col]
    features[f'{target_col}_lag_24'] = last_data.iloc[-24][target_col]
    
    # Hitung Rolling Mean (Window 24)
    # Rolling mean dari 24 jam terakhir
    features[f'{target_col}_rolling_mean_24'] = last_data[target_col].tail(24).mean()
    
    # Jika ada fitur tambahan seperti condition_encoded, harus ditambahkan juga
    # Di sini kita asumsikan model hanya pakai fitur numerik di atas untuk penyederhanaan
    # atau kita ambil mode dari 24 jam terakhir untuk kondisi
    if 'condition_encoded' in last_data.columns:
         features['condition_encoded'] = last_data['condition_encoded'].mode()[0]

    return pd.DataFrame([features])

def predict_next_step(models, df_history, current_timestamp):
    """
    Melakukan prediksi untuk satu timestamp ke depan untuk semua target.
    """
    predictions = {}
    targets = ['temperature', 'humidity', 'wind_speed', 'pressure']
    
    # Mapping nama kolom di dataframe history (jika berbeda dengan target name model)
    # Di notebook: temp -> temperature, windspeed -> wind_speed, sealevelpressure -> pressure
    # Pastikan df_history sudah di-rename kolomnya sesuai training
    
    for target in targets:
        if target not in models:
            print(f"Warning: Model for {target} not found.")
            continue
            
        model = models[target]
        
        # Siapkan fitur
        try:
            X_input = prepare_input_features(df_history, target, current_timestamp)
        except ValueError as e:
            print(f"Skipping {target}: {e}")
            continue
        
        # Pastikan urutan kolom sesuai dengan saat training
        # Model sklearn biasanya butuh urutan kolom yang sama.
        # Kita akan gunakan feature_names_in_ jika tersedia (sklearn versi baru)
        
        if hasattr(model, "feature_names_in_"):
            # Isi missing columns dengan 0 jika ada (untuk robustness)
            for col in model.feature_names_in_:
                if col not in X_input.columns:
                    X_input[col] = 0
            X_input = X_input[model.feature_names_in_]
        
        # Prediksi
        pred_value = model.predict(X_input)[0]
        predictions[target] = pred_value
        
    return predictions

def main():
    # 1. Load Models
    try:
        models = load_models(MODEL_PATH)
    except Exception as e:
        print(f"Error loading models: {e}")
        print("Pastikan Anda sudah menjalankan notebook training dan file .pkl sudah terbentuk.")
        return

    # 2. Load Historical Data (Simulasi data real-time dari sensor/database)
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found at {DATA_PATH}")
        return
        
    print(f"Loading historical data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Preprocessing minimal agar sama dengan training
    if {'year', 'month', 'day', 'hour'}.issubset(df.columns):
        df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    
    column_mapping = {
        'temp': 'temperature',
        'windspeed': 'wind_speed',
        'sealevelpressure': 'pressure'
    }
    df = df.rename(columns=column_mapping)
    df = df.sort_values('timestamp')
    
    # Simulasi: Kita berada di waktu terakhir data
    last_timestamp = df['timestamp'].iloc[-1]
    next_timestamp = last_timestamp + timedelta(hours=1)
    
    print(f"\nLast data timestamp: {last_timestamp}")
    print(f"Predicting for: {next_timestamp}")
    
    # 3. Lakukan Prediksi
    predictions = predict_next_step(models, df, next_timestamp)
    
    print("\nPredictions:")
    for target, value in predictions.items():
        print(f"  {target.capitalize()}: {value:.2f}")

    # 4. Simulasi Recursive Prediction (Prediksi 3 jam ke depan)
    print("\n--- Recursive Prediction (Next 3 Hours) ---")
    current_df = df.copy()
    current_ts = next_timestamp
    
    for i in range(3):
        print(f"\nStep {i+1}: Predicting for {current_ts}")
        preds = predict_next_step(models, current_df, current_ts)
        
        # Tampilkan hasil
        print(f"  Preds: {preds}")
        
        # Update dataframe history dengan hasil prediksi untuk langkah selanjutnya
        # Kita perlu membuat baris baru
        new_row = preds.copy()
        new_row['timestamp'] = current_ts
        new_row['hour'] = current_ts.hour
        new_row['day'] = current_ts.day
        new_row['month'] = current_ts.month
        new_row['year'] = current_ts.year
        
        # Isi kolom lain yang mungkin diperlukan dengan nilai default atau forward fill
        # Perlu memastikan semua kolom yang ada di df asli ada di new_row
        for col in current_df.columns:
            if col not in new_row:
                new_row[col] = current_df[col].iloc[-1] # Forward fill sederhana
                
        current_df = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Maju 1 jam
        current_ts += timedelta(hours=1)

if __name__ == "__main__":
    main()
