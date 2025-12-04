# Panduan Inferensi Model Cuaca

Panduan ini menjelaskan cara menggunakan file `.pkl` yang dihasilkan dari notebook training untuk melakukan prediksi cuaca.

## 1. Lokasi Model
Model disimpan dalam file `.pkl` (biasanya `weather_prediction_models.pkl`) yang berisi dictionary:
```python
{
    'temperature': RandomForestRegressor(...),
    'humidity': RandomForestRegressor(...),
    'wind_speed': RandomForestRegressor(...),
    'pressure': RandomForestRegressor(...)
}
```

## 2. Persyaratan Fitur (Feature Engineering)
Model dilatih menggunakan **Lag Features** dan **Rolling Means**. Artinya, Anda tidak bisa hanya memasukkan tanggal/jam untuk prediksi. Anda memerlukan data historis (minimal 24 jam terakhir).

Fitur yang digunakan model adalah:
- `hour`, `month`, `day`
- `[target]_lag_1`: Nilai 1 jam yang lalu
- `[target]_lag_2`: Nilai 2 jam yang lalu
- `[target]_lag_3`: Nilai 3 jam yang lalu
- `[target]_lag_24`: Nilai 24 jam yang lalu
- `[target]_rolling_mean_24`: Rata-rata 24 jam terakhir

## 3. Langkah-langkah Inferensi

### A. Load Model
Gunakan `joblib` untuk memuat model.
```python
import joblib
models = joblib.load('path/to/weather_prediction_models.pkl')
```

### B. Siapkan Data Input
Anda perlu mengambil data historis terbaru dari database sensor Anda.
Contoh fungsi persiapan data (lihat `inference_example.py` untuk kode lengkap):

```python
def prepare_input(df_history, target_col):
    # Ambil 24 data terakhir
    last_24 = df_history.tail(24)
    
    features = {
        'hour': current_time.hour,
        # ... fitur waktu lainnya
        f'{target_col}_lag_1': last_24.iloc[-1][target_col],
        # ... lag lainnya
        f'{target_col}_rolling_mean_24': last_24[target_col].mean()
    }
    return pd.DataFrame([features])
```

### C. Lakukan Prediksi
```python
model = models['temperature']
prediction = model.predict(X_input)
```

## 4. Prediksi Masa Depan (Recursive Forecasting)
Untuk memprediksi lebih dari 1 jam ke depan (misal 3 hari ke depan), Anda harus menggunakan metode **Recursive Forecasting**:
1. Prediksi jam ke-1.
2. Masukkan hasil prediksi jam ke-1 ke dalam data historis.
3. Gunakan data historis yang baru (termasuk prediksi jam ke-1) untuk memprediksi jam ke-2.
4. Ulangi langkah ini.

## Contoh Script
Script lengkap telah dibuat di: `examples/model_training/inference_example.py`.
Anda dapat menjalankannya untuk melihat simulasi prediksi.
