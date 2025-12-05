Berikut adalah kerangka urutan/struktur _notebook_ `ipynb` untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil, yang telah diperbarui untuk mendukung metodologi **Time-Series Forecasting** yang lebih akurat:

### Visualisasi dalam Jurnal dan Kecocokan dengan Kerangka Notebook

| Bagian dalam Kerangka Notebook                               | Tujuan Visualisasi (Sesuai Kerangka)                                                                                          | Visualisasi yang Ada dalam Jurnal                                               |
| :----------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **5. Pelatihan dan Perbandingan Model**                | Tabel Perbandingan Metrik (MSE, MAE, RMSE, R²) untuk semua model.                                                            | **Tabel 4:** _Performance metrics for different regression models_.     |
| **6. Analisis Hasil dan Kinerja Individual Parameter** | Tabel Evaluasi Kinerja (MAE, RMSE,$R^2$) untuk setiap parameter yang diprediksi oleh model terbaik.                         | **Tabel 5:** _Performance evaluation of weather parameter predictions_. |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Suhu.                                     | **Gambar 15:** _Actual vs. Predicted temperature_.                      |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kelembaban.                               | **Gambar 16:** _Actual vs. Predicted humidity_.                         |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kecepatan Angin.                          | **Gambar 17:** _Actual vs. Predicted wind speed_.                       |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Tekanan.                                 | **Gambar 18:** _Actual vs. Predicted pressure_.                         |
| **9. Visualisasi Dampak Data Inkremental**             | Grafik garis yang menunjukkan peningkatan skor$R^2$ seiring bertambahnya jumlah _data points_ (_Incremental Learning_). | **Gambar 21:** _Impact of incremental data on model performance_.       |

### Sample Dataset

Dataset berisi data cuaca per-jam dari tahun 2000-2024 dengan struktur **23 kolom** sebagai berikut:

#### Kolom Hourly (Per-Jam)

| Kolom                  | Tipe     | Deskripsi                              |
| ---------------------- | -------- | -------------------------------------- |
| `id`                   | int      | ID unik                                |
| `timestamp`            | datetime | Waktu pengukuran (per-jam)             |
| `hour`, `day`, `month`, `year` | int | Komponen waktu                    |
| `temp`                 | float    | Suhu (°C)                              |
| `humidity`             | int      | Kelembaban (%)                         |
| `windspeed`            | float    | Kecepatan angin (km/h)                 |
| `sealevelpressure`     | float    | Tekanan permukaan laut (hPa)           |
| `rain`                 | float    | Curah hujan (mm)                       |
| `precipitation`        | float    | Presipitasi (mm) - identik dengan rain |
| `apparent_temperature` | float    | Suhu yang dirasakan (°C)               |
| `surface_pressure`     | float    | Tekanan permukaan (hPa)                |
| `weather_code`         | int      | Kode cuaca (0-65)                      |
| `conditions`           | string   | Kondisi cuaca (teks)                   |

#### Kolom Daily (Per-Hari)

| Kolom                  | Tipe     | Deskripsi                              |
| ---------------------- | -------- | -------------------------------------- |
| `temp_max_daily`       | float    | Suhu maksimum harian (°C)              |
| `temp_min_daily`       | float    | Suhu minimum harian (°C)               |
| `weather_code_daily`   | int      | Kode cuaca dominan harian              |
| `temp_mean_daily`      | float    | Suhu rata-rata harian (°C)             |
| `humidity_avg_daily`   | int      | Kelembaban rata-rata harian (%)        |
| `pressure_avg_daily`   | float    | Tekanan rata-rata harian (hPa)         |
| `windspeed_avg_daily`  | float    | Kecepatan angin rata-rata harian (km/h)|

**Contoh Data (5 baris pertama):**

| id | timestamp           | hour | temp | humidity | windspeed | weather_code | temp_max_daily | temp_min_daily | temp_mean_daily | humidity_avg_daily | pressure_avg_daily | windspeed_avg_daily |
| -- | ------------------- | ---- | ---- | -------- | --------- | ------------ | -------------- | -------------- | --------------- | ------------------ | ------------------ | ------------------- |
| 0  | 2000-01-01 00:00:00 | 0    | 21.8 | 98       | 4.0       | 3            | 27.5           | 20.8           | 24.1            | 91                 | 1007.3             | 6.3                 |
| 1  | 2000-01-01 01:00:00 | 1    | 21.4 | 99       | 4.0       | 3            | 27.5           | 20.8           | 24.1            | 91                 | 1007.3             | 6.3                 |
| 2  | 2000-01-01 02:00:00 | 2    | 21.4 | 98       | 3.2       | 3            | 27.5           | 20.8           | 24.1            | 91                 | 1007.3             | 6.3                 |
| 3  | 2000-01-01 03:00:00 | 3    | 21.2 | 99       | 4.6       | 3            | 27.5           | 20.8           | 24.1            | 91                 | 1007.3             | 6.3                 |
| 4  | 2000-01-01 04:00:00 | 4    | 21.0 | 99       | 3.6       | 3            | 27.5           | 20.8           | 24.1            | 91                 | 1007.3             | 6.3                 |

> **Catatan:** Kolom daily (`*_daily`) memiliki nilai yang sama untuk semua baris dalam satu hari yang sama.

---

## Tipe Model: Regression & Classification

## Kerangka Struktur Notebook (`.ipynb`) untuk Pelatihan Model Prediksi Cuaca (Diperbarui)

### 1\. Persiapan Lingkungan dan Pemuatan Pustaka

- **Tujuan:** Mengimpor semua pustaka Python yang diperlukan.
- **Pustaka Kunci:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `sklearn` (termasuk `TimeSeriesSplit`, `RandomForestRegressor`, dll), `joblib`.
- **Output yang Diharapkan:** Konfirmasi impor pustaka berhasil.

### 2\. Pengumpulan dan Pemuatan Data

- **Tujuan:** Memuat _dataset_ historis gabungan.
- **Langkah:**
  - Memuat data historis [historical_data.csv](..\data_collections\datasets\historical_data_2000_2024.csv).
  - Mengurutkan data berdasarkan waktu (`timestamp`) untuk memastikan urutan kronologis yang benar.
- **Output yang Diharapkan:** Tampilan beberapa baris pertama _dataset_ dan info struktur data.

### 3. Analisis Data Eksplorasi (EDA)

- **Tujuan:** Memahami distribusi, korelasi, dan pola dalam data.
- **Langkah:**
  - **Statistik Deskriptif:** Menampilkan ringkasan statistik (`describe()`) untuk semua fitur numerik.
  - **Visualisasi Distribusi:** Membuat histogram atau plot kepadatan untuk setiap parameter cuaca (suhu, kelembaban, dll.) untuk melihat distribusinya.
  - **Analisis Korelasi:** Menghasilkan heatmap korelasi untuk memahami hubungan antar variabel, terutama hubungan rain dengan weather_code dan conditions.
  - **Analisis Deret Waktu:** Membuat plot garis dari setiap parameter cuaca terhadap waktu untuk mengidentifikasi tren, musiman, atau anomali.
  - **Analisis Korelasi weather_code, conditions, dan rain/precipitation:** (Lihat sub-bagian 3.1)
- **Output yang Diharapkan:**
  - Tabel statistik deskriptif.
  - Serangkaian plot (histogram, heatmap, plot garis deret waktu).
  - Wawasan awal tentang data, seperti "suhu menunjukkan pola musiman yang jelas" atau "kelembaban dan curah hujan berkorelasi positif."

#### 3.1 Analisis Korelasi: weather_code, conditions, dan rain/precipitation

**Temuan Kritis:** Terdapat hubungan **deterministik** (bukan probabilistik) antara `weather_code`, `conditions`, dan nilai `rain`/`precipitation`.

##### Tabel Mapping Weather Code ke Rain

| Weather Code | Kondisi (conditions)   | Rain Mean (mm) | Rain Range (mm) | Jumlah Data |
| :----------: | ---------------------- | :------------: | :-------------: | :---------: |
|      0      | Clear                  |      0.00      |       0.0       |   23,298   |
|      1      | Partially cloudy       |      0.00      |       0.0       |   28,622   |
|      2      | Partially cloudy       |      0.00      |       0.0       |   26,366   |
|      3      | Overcast               |      0.00      |       0.0       |   81,994   |
|      51      | Rain (Light)           |      0.21      |    0.1 - 0.4    |   37,108   |
|      53      | Rain (Moderate)        |      0.66      |    0.5 - 0.9    |   12,421   |
|      55      | Rain (Heavy Showers)   |      1.09      |    1.0 - 1.2    |    3,785    |
|      61      | Rain, Overcast         |      1.74      |    1.3 - 2.4    |    7,333    |
|      63      | Rain, Overcast         |      3.95      |    2.5 - 7.5    |    5,792    |
|      65      | Rain, Overcast (Heavy) |     10.28     |   7.6 - 33.4   |     585     |

##### Kesimpulan Korelasi

1. **rain = precipitation**: Nilai keduanya **identik** di seluruh dataset.
2. **weather_code → rain**: Korelasi deterministik. Kode ≥ 50 **selalu** memiliki nilai rain > 0.
3. **conditions → rain**: Konsisten. Kondisi yang mengandung "Rain" selalu memiliki nilai rain > 0.

##### Implikasi untuk Model

> **PENTING:** Karena hubungan deterministik ini, **tidak perlu memprediksi `rain` secara terpisah**. Cukup prediksi `weather_code`, lalu derive nilai rain menggunakan mapping:

```python
rain_map = {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3}
predicted_rain = rain_map[predicted_weather_code]
```

Untuk klasifikasi hujan biner (hujan/tidak hujan):

```python
is_rain = 1 if weather_code >= 50 else 0
```

### 4\. Pra-pemrosesan Data dan Feature Engineering (PENTING)

- **Tujuan:** Menyiapkan fitur yang relevan untuk prediksi deret waktu (_Time-Series_) baik untuk **Hourly** maupun **Daily**.

#### 4.1 Preprocessing Data Hourly

- **Langkah:**
  - **Format Waktu:** Memastikan kolom `timestamp` bertipe datetime.
  - **Label Encoding:** Mengubah `conditions` menjadi numerik.
  - **Feature Engineering Hourly:**
    - `temp_lag_1`: Nilai 1 jam yang lalu
    - `temp_lag_24`: Nilai 24 jam yang lalu (kemarin jam yang sama)
    - `temp_rolling_24`: Rata-rata 24 jam terakhir
    - (Sama untuk humidity, windspeed, sealevelpressure)
  - **Handling NaN:** Menghapus baris awal dengan nilai `NaN`.

#### 4.2 Preprocessing Data Daily (BARU)

Dataset sudah memiliki kolom daily: `temp_max_daily`, `temp_min_daily`, `weather_code_daily`, `temp_mean_daily`. Namun kita perlu membuat dataset daily terpisah.

```python
# Agregasi data hourly menjadi daily
daily_df = df_processed.groupby(['year', 'month', 'day']).agg({
    'temp': ['min', 'max', 'mean'],
    'humidity': 'mean',
    'windspeed': 'mean',
    'sealevelpressure': 'mean',
    'weather_code': lambda x: x.mode()[0],  # Dominan weather_code
    'rain': 'sum'  # Total curah hujan
}).reset_index()

# Flatten column names
daily_df.columns = ['year', 'month', 'day', 
                    'temp_min', 'temp_max', 'temp_mean',
                    'humidity_avg', 'windspeed_avg', 'pressure_avg',
                    'weather_code_dominant', 'rain_total']

# Feature Engineering Daily
daily_df['temp_min_lag_1'] = daily_df['temp_min'].shift(1)   # Kemarin
daily_df['temp_max_lag_1'] = daily_df['temp_max'].shift(1)
daily_df['temp_mean_lag_1'] = daily_df['temp_mean'].shift(1)
daily_df['temp_min_lag_7'] = daily_df['temp_min'].shift(7)   # Seminggu lalu
daily_df['temp_max_lag_7'] = daily_df['temp_max'].shift(7)
daily_df['temp_mean_lag_7'] = daily_df['temp_mean'].shift(7)
daily_df['rain_total_lag_1'] = daily_df['rain_total'].shift(1)
```

- **Output yang Diharapkan:** 
  - `df_hourly`: Dataset hourly dengan lag & rolling features
  - `df_daily`: Dataset daily dengan agregasi dan lag features

### 5\. Pelatihan dan Perbandingan Model (Komprehensif)

- **Tujuan:** Membandingkan berbagai algoritma untuk memilih model terbaik untuk:
  - **Model Hourly**: Prediksi per-jam (temp, humidity, windspeed, pressure, weather_code)
  - **Model Daily**: Prediksi per-hari (temp_min, temp_max, temp_mean, humidity_avg, windspeed_avg, pressure_avg, weather_code_dominant)

#### 5.1 Pemisahan Data (Time-Series Split)

- **Metode:** Chronological Split (BUKAN random split) untuk menghindari data leakage.
- **Rasio:** 80% Train (data historis lama) dan 20% Test (data terbaru).
- **Implementasi:**
  ```python
  # Chronological Split - Data HARUS diurutkan berdasarkan timestamp
  train_size = int(len(df) * 0.8)
  train_df = df[:train_size]   # Data 2000-2019 (contoh)
  test_df = df[train_size:]    # Data 2020-2024 (contoh)
  ```

> **PENTING:** Jangan gunakan `train_test_split()` dengan `shuffle=True` pada data time-series karena akan menyebabkan data leakage.

#### 5.2 Komparasi Model Regresi

- **Target:** `temp`, `humidity`, `windspeed`, `sealevelpressure`
- **Algoritma yang Dibandingkan:**

| No | Algoritma               | Karakteristik                           |
| -- | ----------------------- | --------------------------------------- |
| 1  | Linear Regression       | Baseline, cepat, interpretable          |
| 2  | K-Neighbors Regressor   | Non-parametric, sensitif terhadap skala |
| 3  | Decision Tree Regressor | Non-linear, mudah overfit               |
| 4  | Random Forest Regressor | Ensemble, robust, umumnya terbaik       |
| 5  | XGBoost Regressor       | Gradient boosting, performa tinggi      |

- **Metrik Evaluasi:** MSE, MAE, RMSE, dan $R^{2}$
- **Cross-Validation:** Gunakan `TimeSeriesSplit` untuk validasi lebih robust:
  ```python
  from sklearn.model_selection import TimeSeriesSplit, cross_val_score
  tscv = TimeSeriesSplit(n_splits=5)
  scores = cross_val_score(model, X, y, cv=tscv, scoring='r2')
  ```

#### 5.3 Komparasi Model Klasifikasi

- **Target:** `weather_code` (10 kelas: 0, 1, 2, 3, 51, 53, 55, 61, 63, 65)
- **Algoritma yang Dibandingkan:**

| No | Algoritma                | Karakteristik                        |
| -- | ------------------------ | ------------------------------------ |
| 1  | Logistic Regression      | Baseline, multi-class dengan OvR     |
| 2  | Decision Tree Classifier | Cepat, mudah overfit                 |
| 3  | Random Forest Classifier | Ensemble, balanced accuracy          |
| 4  | XGBoost Classifier       | Gradient boosting, handle imbalanced |

- **Metrik Evaluasi:** Accuracy, F1-Score (macro/weighted), Precision, Recall

#### 5.4 Output yang Diharapkan

- Tabel perbandingan metrik untuk **5 algoritma Regresi**.
- Tabel perbandingan metrik untuk **4 algoritma Klasifikasi**.
- **Kesimpulan:** Model terbaik untuk Regresi dan Klasifikasi (biasanya Random Forest atau XGBoost).

---

### 6\. Analisis Hasil dan Kinerja Individual Parameter

- **Tujuan:** Evaluasi mendalam model terbaik untuk setiap parameter secara individual. misal pada bulan tertentu, januari 2022

#### 6.1 Evaluasi Per-Parameter (Regresi)

Menampilkan metrik terpisah untuk setiap target:

| Parameter   | MAE | RMSE | R² | Keterangan                       |
| ----------- | --- | ---- | --- | -------------------------------- |
| Temperature | -   | -    | -   | Target utama                     |
| Humidity    | -   | -    | -   | -                                |
| Wind Speed  | -   | -    | -   | Biasanya paling sulit diprediksi |
| Pressure    | -   | -    | -   | Relatif stabil                   |

#### 6.2 Evaluasi Klasifikasi (Weather Code)

- **Confusion Matrix:** Visualisasi prediksi vs aktual untuk setiap weather_code.
- **Classification Report:** Precision, Recall, F1-Score per kelas.
- **Analisis Kelas Imbalanced:** Perhatikan kelas minoritas (code 65: Heavy Rain hanya 585 data).

#### 6.3 Output yang Diharapkan

- Tabel kinerja per parameter.
- Confusion Matrix (heatmap).
- Insight: "Model kesulitan membedakan weather_code 61 dan 63" (contoh).

---

### 6.5 Retraining dengan Seluruh Dataset (Final Model)

> **PENTING:** Setelah model terbaik dipilih dari perbandingan, latih ulang dengan **100% data** untuk produksi.

- **Tujuan:** Memaksimalkan performa model final dengan memanfaatkan seluruh data yang tersedia.
- **Langkah:**

  1. Pilih model terbaik dari hasil perbandingan (misal: Random Forest untuk semua).
  2. Gabungkan kembali `train_df` dan `test_df` menjadi `full_df`.
  3. Latih **4 model** dengan seluruh data:

```python
# ===== MODEL HOURLY =====
# Regresi Hourly: temp, humidity, windspeed, pressure
hourly_regressor = RandomForestRegressor(**best_params)
hourly_regressor.fit(X_hourly_full, y_hourly_reg_full)

# Klasifikasi Hourly: weather_code
hourly_classifier = RandomForestClassifier(**best_params)
hourly_classifier.fit(X_hourly_full, y_hourly_clf_full)

# ===== MODEL DAILY =====
# Regresi Daily: temp_min, temp_max, temp_mean, humidity_avg, etc.
daily_regressor = RandomForestRegressor(**best_params)
daily_regressor.fit(X_daily_full, y_daily_reg_full)

# Klasifikasi Daily: weather_code_dominant
daily_classifier = RandomForestClassifier(**best_params)
daily_classifier.fit(X_daily_full, y_daily_clf_full)
```

  4. Simpan semua model ke file `.pkl` (lihat bagian 7).

- **Catatan:** Tidak ada evaluasi pada tahap ini karena semua data sudah digunakan untuk training.

### 7. Penyimpanan Model Terbaik (3 File .pkl)

- **Tujuan:** Menyimpan model ke dalam **3 file `.pkl`** untuk fleksibilitas deployment:
  1. **`weather_model_combined.pkl`** - Semua model dalam satu file (Hourly + Daily)
  2. **`weather_model_hourly.pkl`** - Model hourly saja
  3. **`weather_model_daily.pkl`** - Model daily saja

#### 7.1 Struktur File .pkl

##### A. Combined Model (`weather_model_combined.pkl`)

```python
combined_package = {
    # ========== MODEL HOURLY ==========
    'hourly': {
        'regressor': hourly_regressor,
        'classifier': hourly_classifier,
        'feature_columns': hourly_feature_cols,
        'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
        'target_classification': 'weather_code',
    },
    
    # ========== MODEL DAILY ==========
    'daily': {
        'regressor': daily_regressor,
        'classifier': daily_classifier,
        'feature_columns': daily_feature_cols,
        'target_regression': ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg'],
        'target_classification': 'weather_code_dominant',
    },
    
    # ========== METADATA ==========
    'label_encoder': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'combined'
}
```

##### B. Hourly Model (`weather_model_hourly.pkl`)

```python
hourly_package = {
    'regressor': hourly_regressor,
    'classifier': hourly_classifier,
    'feature_columns': hourly_feature_cols,
    'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
    'target_classification': 'weather_code',
    'label_encoder': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'hourly'
}
```

##### C. Daily Model (`weather_model_daily.pkl`)

```python
daily_package = {
    'regressor': daily_regressor,
    'classifier': daily_classifier,
    'feature_columns': daily_feature_cols,
    'target_regression': ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg'],
    'target_classification': 'weather_code_dominant',
    'label_encoder': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'daily'
}
```

##### D. Model Terpisah (Regressor & Classifier)

Untuk fleksibilitas maksimal, simpan juga model regressor dan classifier secara terpisah:

```python
# Hourly - Regressor Only
hourly_reg_package = {
    'model': hourly_regressor,
    'feature_columns': hourly_feature_cols,
    'target': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
    'version': '2.1',
    'model_type': 'hourly_regressor'
}

# Hourly - Classifier Only
hourly_clf_package = {
    'model': hourly_classifier,
    'feature_columns': hourly_feature_cols,
    'target': 'weather_code',
    'label_encoder': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'model_type': 'hourly_classifier'
}

# Daily - Regressor Only
daily_reg_package = {
    'model': daily_regressor,
    'feature_columns': daily_feature_cols,
    'target': ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg'],
    'version': '2.1',
    'model_type': 'daily_regressor'
}

# Daily - Classifier Only
daily_clf_package = {
    'model': daily_classifier,
    'feature_columns': daily_feature_cols,
    'target': 'weather_code_dominant',
    'label_encoder': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'model_type': 'daily_classifier'
}
```

#### 7.2 Menyimpan 7 File Model (Training)

```python
import joblib
import os
from datetime import datetime

# Pastikan folder models ada
os.makedirs('models', exist_ok=True)

# ===== 3 FILE UTAMA =====
# 1. Combined Model (Hourly + Daily)
joblib.dump(combined_package, 'models/weather_model_combined.pkl')
print("✅ Combined model saved")

# 2. Hourly Model (Regressor + Classifier)
joblib.dump(hourly_package, 'models/weather_model_hourly.pkl')
print("✅ Hourly model saved")

# 3. Daily Model (Regressor + Classifier)
joblib.dump(daily_package, 'models/weather_model_daily.pkl')
print("✅ Daily model saved")

# ===== 4 FILE TERPISAH (REGRESSOR & CLASSIFIER) =====
# 4. Hourly Regressor Only
joblib.dump(hourly_reg_package, 'models/weather_model_hourly_regressor.pkl')
print("✅ Hourly regressor saved")

# 5. Hourly Classifier Only
joblib.dump(hourly_clf_package, 'models/weather_model_hourly_classifier.pkl')
print("✅ Hourly classifier saved")

# 6. Daily Regressor Only
joblib.dump(daily_reg_package, 'models/weather_model_daily_regressor.pkl')
print("✅ Daily regressor saved")

# 7. Daily Classifier Only
joblib.dump(daily_clf_package, 'models/weather_model_daily_classifier.pkl')
print("✅ Daily classifier saved")

print(f"\n📦 Total: 7 model files created!")
```

**Output yang Diharapkan:**
```
models/
├── weather_model_combined.pkl           # ~200-400 MB (4 model)
├── weather_model_hourly.pkl             # ~100-200 MB (2 model)
├── weather_model_daily.pkl              # ~100-200 MB (2 model)
├── weather_model_hourly_regressor.pkl   # ~50-100 MB (1 model)
├── weather_model_hourly_classifier.pkl  # ~50-100 MB (1 model)
├── weather_model_daily_regressor.pkl    # ~50-100 MB (1 model)
└── weather_model_daily_classifier.pkl   # ~50-100 MB (1 model)
```

#### 7.3 Memuat Model (Inference/Backend)

```python
import joblib

# Load model package
model_package = joblib.load('models/weather_model_v2.pkl')

# Akses komponen HOURLY
hourly_reg = model_package['hourly']['regressor']
hourly_clf = model_package['hourly']['classifier']
hourly_features = model_package['hourly']['feature_columns']

# Akses komponen DAILY
daily_reg = model_package['daily']['regressor']
daily_clf = model_package['daily']['classifier']
daily_features = model_package['daily']['feature_columns']

# Metadata
rain_map = model_package['weather_code_to_rain']

# Contoh prediksi HOURLY
X_hourly = prepare_hourly_features(input_data, hourly_features)
pred_hourly = hourly_reg.predict(X_hourly)  # [temp, humidity, windspeed, pressure]
pred_code_hourly = hourly_clf.predict(X_hourly)[0]

# Contoh prediksi DAILY
X_daily = prepare_daily_features(input_data, daily_features)
pred_daily = daily_reg.predict(X_daily)  # [temp_min, temp_max, temp_mean, ...]
pred_code_daily = daily_clf.predict(X_daily)[0]
```

#### 7.4 Sinkronisasi dengan Backend API

Backend (`main.py`) harus menggunakan class yang mendukung dual-model:

```python
# Di main.py atau model_loader.py
class WeatherPredictor:
    def __init__(self, model_path: str):
        self.package = joblib.load(model_path)
        
        # Hourly models
        self.hourly_reg = self.package['hourly']['regressor']
        self.hourly_clf = self.package['hourly']['classifier']
        self.hourly_features = self.package['hourly']['feature_columns']
        
        # Daily models
        self.daily_reg = self.package['daily']['regressor']
        self.daily_clf = self.package['daily']['classifier']
        self.daily_features = self.package['daily']['feature_columns']
        
        # Metadata
        self.rain_map = self.package['weather_code_to_rain']
    
    def predict_hourly(self, features: dict) -> dict:
        """Prediksi cuaca per-jam"""
        X = self._prepare_features(features, self.hourly_features)
        reg_pred = self.hourly_reg.predict(X)[0]
        weather_code = self.hourly_clf.predict(X)[0]
        
        return {
            'temp': reg_pred[0],
            'humidity': reg_pred[1],
            'windspeed': reg_pred[2],
            'pressure': reg_pred[3],
            'weather_code': int(weather_code),
            'rain': self.rain_map.get(int(weather_code), 0)
        }
    
    def predict_daily(self, features: dict) -> dict:
        """Prediksi cuaca per-hari"""
        X = self._prepare_features(features, self.daily_features)
        reg_pred = self.daily_reg.predict(X)[0]
        weather_code = self.daily_clf.predict(X)[0]
        
        return {
            'temp_min': reg_pred[0],
            'temp_max': reg_pred[1],
            'temp_mean': reg_pred[2],
            'humidity_avg': reg_pred[3],
            'windspeed_avg': reg_pred[4],
            'pressure_avg': reg_pred[5],
            'weather_code_dominant': int(weather_code),
            'rain_total': self.rain_map.get(int(weather_code), 0)
        }
```

- **Output yang Diharapkan:** File `weather_model_v2.pkl` tersimpan di folder `models/` dengan ukuran ~100-400 MB (karena 4 model).

### 8. Implementasi Multi-Step Forecasting (Recursive Strategy)

- **Tujuan:** Mengatasi masalah "Forecast Horizon" dengan mengimplementasikan fungsi yang dapat memprediksi cuaca untuk rentang waktu di masa depan (misal: 24, 48, atau 72 jam ke depan) berdasarkan data terakhir yang tersedia. Strategi ini memungkinkan pengguna untuk meminta prediksi dari tanggal/jam tertentu ke tanggal/jam di masa depan.
- **Masalah Model Saat Ini:** Model yang dilatih hanya mampu melakukan prediksi *single-step* (memprediksi 1 jam ke depan). Model seperti `Linear Regression` cenderung hanya meniru nilai dari jam sebelumnya (*persistence model*), yang tidak berguna untuk prediksi jangka panjang.
- **Strategi yang Diusulkan: Recursive Forecasting**
  1. **Model Dasar:** Kita tetap menggunakan model *single-step* yang sudah dilatih.
  2. **Proses Iteratif:**
     - Fungsi prediksi akan menerima input berupa: model yang sudah dilatih, baris data terakhir yang diketahui, dan jangka waktu prediksi (misal: 72 jam).
     - **Langkah 1 (Prediksi T+1):** Gunakan data terakhir yang diketahui untuk memprediksi cuaca pada jam `T+1`.
     - **Langkah 2 (Prediksi T+2):** Untuk memprediksi `T+2`, buat baris data baru di mana fitur-fitur lag (`*_lag_1`, `*_lag_24`) dan rolling mean (`*_rolling_mean_24`) diperbarui secara dinamis. Nilai `*_lag_1` akan diisi dari **hasil prediksi pada T+1**.
     - **Langkah 3 dan Seterusnya:** Ulangi proses ini, di mana setiap prediksi baru digunakan sebagai input untuk prediksi jam berikutnya. Lakukan ini sebanyak jangka waktu prediksi yang diinginkan.
- **Output yang Diharapkan:**
  - Sebuah DataFrame yang berisi prediksi cuaca untuk setiap jam dalam rentang waktu yang ditentukan.
  - Visualisasi baru yang membandingkan hasil prediksi rekursif dengan data aktual pada *test set*. Ini akan menunjukkan bagaimana performa model menurun seiring waktu (karena akumulasi eror), yang merupakan cerminan kinerja dunia nyata yang lebih baik.

### 9. Visualisasi Multi-Step Forecast vs. Aktual

- **Tujuan:** Memvisualisasikan performa strategi *Recursive Forecasting* pada data uji.
- **Langkah:**
  - Pilih satu titik awal dari *test set* (contoh: 1 Januari 2023, jam 00:00).
  - Panggil fungsi prediksi rekursif untuk menghasilkan ramalan cuaca selama 72 jam ke depan dari titik tersebut.
  - Buat 4 grafik garis (untuk Suhu, Kelembaban, Angin, Tekanan), di mana setiap grafik berisi:
    1. Garis data **Aktual** dari *test set* selama 72 jam tersebut (sebagai pembanding/benchmark).
    2. Garis data **Prediksi Rekursif** yang dihasilkan oleh fungsi.
- **Visualisasi yang Diharapkan:**
  - Grafik yang menunjukkan garis prediksi (misal: merah putus-putus) mencoba mengikuti garis aktual (misal: biru solid).
  - Grafik ini akan secara jelas menunjukkan degradasi performa seiring berjalannya waktu, memberikan wawasan yang jujur tentang kemampuan prediksi jangka panjang model tersebut.

### 10. Visualisasi Dampak Data Inkremental

- **Tujuan:** Demonstrasi konsep _Incremental Learning_.
- **Langkah:** Melatih model dengan pecahan data training (10%, 20%, ... 100%) dan mengukur $R^{2}$ pada data test yang tetap.
- **Visualisasi yang Diharapkan:** Grafik tren naik yang menunjukkan semakin banyak data historis, semakin akurat modelnya.
