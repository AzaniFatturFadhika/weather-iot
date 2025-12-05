# Training Guide v2.0 - Enhanced Weather Prediction Model

Panduan lengkap untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil dengan metodologi **Time-Series Forecasting** yang diperbarui.

> **v2.0 Changelog:** Menambahkan Cyclical Time Features, Class Balancing, Expanding Window CV, Interaction Features, dan Prophet.

---

## Visualisasi dalam Jurnal dan Kecocokan dengan Kerangka Notebook

| Bagian dalam Kerangka Notebook                         | Tujuan Visualisasi                                                                                  | Visualisasi dalam Jurnal                                        |
| :----------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| **5. Pelatihan dan Perbandingan Model**                | Tabel Perbandingan Metrik (MSE, MAE, RMSE, R²) untuk semua model.                                   | **Tabel 4:** _Performance metrics for different regression models_. |
| **6. Analisis Hasil dan Kinerja Individual Parameter** | Tabel Evaluasi Kinerja (MAE, RMSE, R²) untuk setiap parameter + Grafik Januari 2022 (gap 2 hari).   | **Tabel 5:** _Performance evaluation of weather parameter predictions_. |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual Actual vs Predicted untuk Suhu, Kelembaban, Angin, Tekanan.              | **Gambar 15-18:** _Actual vs. Predicted_ per parameter.         |
| **9. Visualisasi Dampak Data Inkremental**             | Grafik garis peningkatan R² seiring bertambahnya data (_Incremental Learning_).                    | **Gambar 21:** _Impact of incremental data on model performance_. |

---

## Sample Dataset

Dataset berisi data cuaca per-jam dari tahun 2000-2024 dengan struktur **23 kolom**:

### Kolom Hourly (Per-Jam)

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

### Kolom Daily (Per-Hari)

| Kolom                  | Tipe  | Deskripsi                               |
| ---------------------- | ----- | --------------------------------------- |
| `temp_max_daily`       | float | Suhu maksimum harian (°C)               |
| `temp_min_daily`       | float | Suhu minimum harian (°C)                |
| `weather_code_daily`   | int   | Kode cuaca dominan harian               |
| `temp_mean_daily`      | float | Suhu rata-rata harian (°C)              |
| `humidity_avg_daily`   | int   | Kelembaban rata-rata harian (%)         |
| `pressure_avg_daily`   | float | Tekanan rata-rata harian (hPa)          |
| `windspeed_avg_daily`  | float | Kecepatan angin rata-rata harian (km/h) |

> **Catatan:** Kolom daily (`*_daily`) memiliki nilai yang sama untuk semua baris dalam satu hari yang sama.

---

## Tipe Model: Regression & Classification

---

## 1. Persiapan Lingkungan dan Pemuatan Pustaka

- **Tujuan:** Mengimpor semua pustaka Python yang diperlukan.
- **Pustaka Kunci:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `sklearn`, `xgboost`, `joblib`.
- **Output yang Diharapkan:** Konfirmasi impor pustaka berhasil.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
import joblib
warnings.filterwarnings('ignore')

# Scikit-learn
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, f1_score, classification_report, confusion_matrix
)

# Regression Models
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# Classification Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# XGBoost
from xgboost import XGBRegressor, XGBClassifier

# [v2.0] Imbalanced Learning (opsional)
# pip install imbalanced-learn
# from imblearn.over_sampling import SMOTE

print("✅ Semua pustaka berhasil diimpor!")
```

---

## 2. Pengumpulan dan Pemuatan Data

- **Tujuan:** Memuat _dataset_ historis gabungan.
- **Langkah:**
  - Memuat data historis `historical_data_2000_2024.csv`.
  - Mengurutkan data berdasarkan waktu (`timestamp`) untuk memastikan urutan kronologis yang benar.
- **Output yang Diharapkan:** Tampilan beberapa baris pertama _dataset_ dan info struktur data.

```python
DATA_PATH = '../data/historical_data_2000_2024.csv'
df = pd.read_csv(DATA_PATH)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)

print(f"📊 Dataset loaded: {len(df):,} baris x {len(df.columns)} kolom")
print(f"📅 Rentang waktu: {df['timestamp'].min()} - {df['timestamp'].max()}")
df.head()
```

---

## 3. Analisis Data Eksplorasi (EDA)

- **Tujuan:** Memahami distribusi, korelasi, dan pola dalam data.
- **Langkah:**
  - **Statistik Deskriptif:** Menampilkan ringkasan statistik (`describe()`) untuk semua fitur numerik.
  - **Visualisasi Distribusi:** Membuat histogram untuk setiap parameter cuaca.
  - **Analisis Korelasi:** Menghasilkan heatmap korelasi untuk memahami hubungan antar variabel.
  - **Analisis Deret Waktu:** Membuat plot garis dari setiap parameter cuaca terhadap waktu.
- **Output yang Diharapkan:**
  - Tabel statistik deskriptif.
  - Serangkaian plot (histogram, heatmap, plot garis deret waktu).
  - Wawasan awal tentang data.

### 3.1 Analisis Korelasi: weather_code, conditions, dan rain/precipitation

**Temuan Kritis:** Terdapat hubungan **deterministik** antara `weather_code`, `conditions`, dan nilai `rain`/`precipitation`.

#### Tabel Mapping Weather Code ke Rain

| Weather Code | Kondisi (conditions)   | Rain Mean (mm) | Rain Range (mm) | Jumlah Data |
| :----------: | ---------------------- | :------------: | :-------------: | :---------: |
|      0       | Clear                  |      0.00      |       0.0       |   23,298    |
|      1       | Partially cloudy       |      0.00      |       0.0       |   28,622    |
|      2       | Partially cloudy       |      0.00      |       0.0       |   26,366    |
|      3       | Overcast               |      0.00      |       0.0       |   81,994    |
|      51      | Rain (Light)           |      0.21      |    0.1 - 0.4    |   37,108    |
|      53      | Rain (Moderate)        |      0.66      |    0.5 - 0.9    |   12,421    |
|      55      | Rain (Heavy Showers)   |      1.09      |    1.0 - 1.2    |    3,785    |
|      61      | Rain, Overcast         |      1.74      |    1.3 - 2.4    |    7,333    |
|      63      | Rain, Overcast         |      3.95      |    2.5 - 7.5    |    5,792    |
|      65      | Rain, Overcast (Heavy) |     10.28      |   7.6 - 33.4    |     585     |

#### Kesimpulan Korelasi

1. **rain = precipitation**: Nilai keduanya **identik** di seluruh dataset.
2. **weather_code → rain**: Korelasi deterministik. Kode ≥ 50 **selalu** memiliki nilai rain > 0.
3. **conditions → rain**: Konsisten. Kondisi yang mengandung "Rain" selalu memiliki nilai rain > 0.

#### Implikasi untuk Model

> **PENTING:** Karena hubungan deterministik ini, **tidak perlu memprediksi `rain` secara terpisah**. Cukup prediksi `weather_code`, lalu derive nilai rain menggunakan mapping:

```python
rain_map = {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3}
predicted_rain = rain_map[predicted_weather_code]

# Klasifikasi hujan biner
is_rain = 1 if weather_code >= 50 else 0
```

---

## 4. Pra-pemrosesan Data dan Feature Engineering

- **Tujuan:** Menyiapkan fitur yang relevan untuk prediksi deret waktu baik untuk **Hourly** maupun **Daily**.

### 4.1 Preprocessing Data Hourly

- **Langkah:**
  - **Format Waktu:** Memastikan kolom `timestamp` bertipe datetime.
  - **Label Encoding:** Mengubah `conditions` dan `weather_code` menjadi numerik.
  - **Feature Engineering Hourly:** Lag dan rolling features.
  - **Handling NaN:** Menghapus baris awal dengan nilai `NaN`.

```python
df_hourly = df.copy()

# Label Encoding
le_conditions = LabelEncoder()
df_hourly['conditions_encoded'] = le_conditions.fit_transform(df_hourly['conditions'])

le_weather_code = LabelEncoder()
df_hourly['weather_code_encoded'] = le_weather_code.fit_transform(df_hourly['weather_code'])
```

### 4.2 [v2.0] Cyclical Time Features (BARU)

> **PENTING:** Jam 23:00 dan 00:00 hanya selisih 1 jam, tapi angka 23 dan 0 jauh. Gunakan Sin/Cos untuk mengatasi ini.

```python
# Cyclical encoding untuk hour (0-23)
df_hourly['hour_sin'] = np.sin(2 * np.pi * df_hourly['hour'] / 24)
df_hourly['hour_cos'] = np.cos(2 * np.pi * df_hourly['hour'] / 24)

# Cyclical encoding untuk month (1-12)
df_hourly['month_sin'] = np.sin(2 * np.pi * df_hourly['month'] / 12)
df_hourly['month_cos'] = np.cos(2 * np.pi * df_hourly['month'] / 12)

# Cyclical encoding untuk day of year (1-366)
df_hourly['day_of_year'] = df_hourly['timestamp'].dt.dayofyear
df_hourly['doy_sin'] = np.sin(2 * np.pi * df_hourly['day_of_year'] / 365)
df_hourly['doy_cos'] = np.cos(2 * np.pi * df_hourly['day_of_year'] / 365)
```

### 4.3 [v2.0] Interaction Features (BARU)

```python
# Dew Point - indikator kuat untuk hujan
df_hourly['dew_point'] = df_hourly['temp'] - ((100 - df_hourly['humidity']) / 5)

# Temperature Range (untuk daily) - rentang kecil = mendung/hujan
df_hourly['temp_range'] = df_hourly['temp_max_daily'] - df_hourly['temp_min_daily']

# Humidity-Temperature Interaction
df_hourly['humid_temp_ratio'] = df_hourly['humidity'] / (df_hourly['temp'] + 1)
```

### 4.4 Lag Features Hourly

```python
hourly_target_cols = ['temp', 'humidity', 'windspeed', 'sealevelpressure']

for col in hourly_target_cols:
    df_hourly[f'{col}_lag_1'] = df_hourly[col].shift(1)
    df_hourly[f'{col}_lag_24'] = df_hourly[col].shift(24)
    df_hourly[f'{col}_rolling_24'] = df_hourly[col].rolling(window=24).mean()
    # [v2.0] Rolling std untuk variabilitas
    df_hourly[f'{col}_rolling_std_24'] = df_hourly[col].rolling(window=24).std()

# Hapus NaN
df_hourly = df_hourly.dropna().reset_index(drop=True)
```

### 4.5 Preprocessing Data Daily

```python
# Agregasi data hourly menjadi daily
df_daily = df.groupby(['year', 'month', 'day']).agg({
    'temp': ['min', 'max', 'mean'],
    'humidity': 'mean',
    'windspeed': 'mean',
    'sealevelpressure': 'mean',
    'weather_code': lambda x: x.mode()[0],
    'rain': 'sum'
}).reset_index()

# Flatten column names
df_daily.columns = ['year', 'month', 'day', 
                    'temp_min', 'temp_max', 'temp_mean',
                    'humidity_avg', 'windspeed_avg', 'pressure_avg',
                    'weather_code_dominant', 'rain_total']

# Label Encoding
le_weather_code_daily = LabelEncoder()
df_daily['weather_code_dominant_encoded'] = le_weather_code_daily.fit_transform(df_daily['weather_code_dominant'])
```

### 4.6 Lag Features Daily (ENHANCED)

```python
# Lag features dengan window lebih panjang
df_daily['temp_min_lag_1'] = df_daily['temp_min'].shift(1)
df_daily['temp_max_lag_1'] = df_daily['temp_max'].shift(1)
df_daily['temp_mean_lag_1'] = df_daily['temp_mean'].shift(1)
df_daily['humidity_avg_lag_1'] = df_daily['humidity_avg'].shift(1)
df_daily['windspeed_avg_lag_1'] = df_daily['windspeed_avg'].shift(1)
df_daily['pressure_avg_lag_1'] = df_daily['pressure_avg'].shift(1)

df_daily['temp_min_lag_7'] = df_daily['temp_min'].shift(7)
df_daily['temp_max_lag_7'] = df_daily['temp_max'].shift(7)
df_daily['temp_mean_lag_7'] = df_daily['temp_mean'].shift(7)
df_daily['rain_total_lag_1'] = df_daily['rain_total'].shift(1)

# [v2.0] Rolling mean untuk trend
df_daily['temp_rolling_3d'] = df_daily['temp_mean'].rolling(window=3).mean()
df_daily['temp_rolling_7d'] = df_daily['temp_mean'].rolling(window=7).mean()

for col in ['humidity_avg', 'windspeed_avg', 'pressure_avg']:
    df_daily[f'{col}_rolling_3d'] = df_daily[col].rolling(window=3).mean()
    df_daily[f'{col}_rolling_7d'] = df_daily[col].rolling(window=7).mean()

# Hapus NaN
df_daily = df_daily.dropna().reset_index(drop=True)
```

- **Output yang Diharapkan:**
  - `df_hourly`: Dataset hourly dengan lag, rolling, cyclical, dan interaction features
  - `df_daily`: Dataset daily dengan agregasi, lag, dan rolling features

---

## 5. Pelatihan dan Perbandingan Model

- **Tujuan:** Membandingkan berbagai algoritma untuk memilih model terbaik untuk:
  - **Model Hourly**: Prediksi per-jam (temp, humidity, windspeed, pressure, weather_code)
  - **Model Daily**: Prediksi per-hari (temp_min, temp_max, temp_mean, humidity_avg, windspeed_avg, pressure_avg, weather_code_dominant)

### 5.1 [v2.0] Expanding Window Cross-Validation (BARU)

> **PENTING:** Jangan gunakan simple 80-20 split. Gunakan Expanding Window untuk validasi yang lebih robust.

```python
from sklearn.model_selection import TimeSeriesSplit

# Expanding Window: Train terus bertambah, Test bergeser
tscv = TimeSeriesSplit(n_splits=5)

# Ilustrasi:
# Fold 1: Train [Jan-Jun], Test [Jul]
# Fold 2: Train [Jan-Jul], Test [Aug]
# Fold 3: Train [Jan-Aug], Test [Sep]

def evaluate_with_cv(model, X, y, cv=tscv):
    """Evaluasi model dengan Time Series Cross-Validation"""
    scores = {'r2': [], 'rmse': [], 'mae': []}
    
    for train_idx, test_idx in cv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        scores['r2'].append(r2_score(y_test, y_pred))
        scores['rmse'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
        scores['mae'].append(mean_absolute_error(y_test, y_pred))
    
    return {
        'R2_mean': np.mean(scores['r2']),
        'R2_std': np.std(scores['r2']),
        'RMSE_mean': np.mean(scores['rmse']),
        'MAE_mean': np.mean(scores['mae'])
    }
```

### 5.2 Pemisahan Data (Chronological Split)

```python
# HOURLY Data Split
hourly_train_size = int(len(df_hourly) * 0.8)
hourly_train = df_hourly[:hourly_train_size]
hourly_test = df_hourly[hourly_train_size:]

# DAILY Data Split
daily_train_size = int(len(df_daily) * 0.8)
daily_train = df_daily[:daily_train_size]
daily_test = df_daily[daily_train_size:]
```

### 5.3 Definisi Fitur dan Target

```python
# [v2.0] HOURLY Features dengan cyclical dan interaction
hourly_feature_cols = [
    'hour_sin', 'hour_cos', 'month_sin', 'month_cos',  # Cyclical
    'temp_lag_1', 'temp_lag_24', 'temp_rolling_24',
    'humidity_lag_1', 'humidity_lag_24', 'humidity_rolling_24',
    'windspeed_lag_1', 'windspeed_lag_24', 'windspeed_rolling_24',
    'sealevelpressure_lag_1', 'sealevelpressure_lag_24', 'sealevelpressure_rolling_24',
    'dew_point', 'humid_temp_ratio'  # Interaction
]
hourly_target_reg = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
hourly_target_clf = 'weather_code_encoded'

# [v2.0] DAILY Features dengan rolling 3d/7d
daily_feature_cols = [
    'month', 'day',
    'temp_min_lag_1', 'temp_max_lag_1', 'temp_mean_lag_1',
    'humidity_avg_lag_1', 'windspeed_avg_lag_1', 'pressure_avg_lag_1',
    'temp_min_lag_7', 'temp_max_lag_7', 'temp_mean_lag_7',
    'rain_total_lag_1',
    'temp_rolling_3d', 'temp_rolling_7d',  # [v2.0]
    'humidity_avg_rolling_3d', 'humidity_avg_rolling_7d'  # [v2.0]
]
daily_target_reg = ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg']
daily_target_clf = 'weather_code_dominant_encoded'
```

### 5.4 Komparasi Model Regresi

- **Target:** `temp`, `humidity`, `windspeed`, `sealevelpressure`
- **Algoritma yang Dibandingkan:**

| No | Algoritma               | Karakteristik                           |
| -- | ----------------------- | --------------------------------------- |
| 1  | Linear Regression       | Baseline, cepat, interpretable          |
| 2  | K-Neighbors Regressor   | Non-parametric, sensitif terhadap skala |
| 3  | Decision Tree Regressor | Non-linear, mudah overfit               |
| 4  | Random Forest Regressor | Ensemble, robust, umumnya terbaik       |
| 5  | XGBoost Regressor       | Gradient boosting, performa tinggi      |

- **Metrik Evaluasi:** MSE, MAE, RMSE, dan R²

### 5.5 [v2.0] Komparasi Model Klasifikasi dengan Class Balancing (BARU)

> **KRITIS:** Kelas minoritas (weather_code=65, Heavy Rain) sangat sedikit. **WAJIB** gunakan class balancing.

- **Target:** `weather_code` (10 kelas: 0, 1, 2, 3, 51, 53, 55, 61, 63, 65)
- **Algoritma yang Dibandingkan:**

| No | Algoritma                | Karakteristik                        |
| -- | ------------------------ | ------------------------------------ |
| 1  | Logistic Regression      | Baseline, multi-class dengan OvR     |
| 2  | Decision Tree Classifier | Cepat, mudah overfit                 |
| 3  | Random Forest Classifier | Ensemble, balanced accuracy          |
| 4  | XGBoost Classifier       | Gradient boosting, handle imbalanced |

```python
# [v2.0] Random Forest dengan class_weight
rf_clf = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',  # WAJIB!
    random_state=42,
    n_jobs=-1
)

# [v2.0] XGBoost dengan scale_pos_weight
from collections import Counter
class_counts = Counter(y_train)
majority = max(class_counts.values())
minority = min(class_counts.values())
scale_weight = majority / minority

xgb_clf = XGBClassifier(
    n_estimators=100,
    scale_pos_weight=scale_weight,
    random_state=42,
    n_jobs=-1,
    verbosity=0
)
```

- **Metrik Evaluasi:** Accuracy, F1-Score (macro/weighted), Precision, Recall

### 5.6 Output yang Diharapkan

- Tabel perbandingan metrik untuk **5 algoritma Regresi**.
- Tabel perbandingan metrik untuk **4 algoritma Klasifikasi**.
- **Kesimpulan:** Model terbaik untuk Regresi dan Klasifikasi.

---

## 6. Analisis Hasil dan Kinerja Individual Parameter

- **Tujuan:** Evaluasi mendalam model terbaik untuk setiap parameter secara individual.
- **Periode Analisis:** **Januari 2022** (1 bulan penuh)
- **Format Visualisasi:** Grafik time-series dengan **gap 2 hari** untuk kejelasan

### 6.1 Evaluasi Per-Parameter (Regresi)

Menampilkan metrik terpisah untuk setiap target:

| Parameter        | MAE   | RMSE  | R²    | Keterangan                       |
| ---------------- | ----- | ----- | ----- | -------------------------------- |
| Temperature      | -     | -     | -     | Target utama                     |
| Humidity         | -     | -     | -     | -                                |
| Wind Speed       | -     | -     | -     | Biasanya paling sulit diprediksi |
| Pressure         | -     | -     | -     | Relatif stabil                   |

### 6.2 Visualisasi Time-Series: Actual vs Predicted (Januari 2022)

> **WAJIB:** Tampilkan grafik perbandingan nilai aktual vs prediksi untuk setiap parameter regresi pada bulan **Januari 2022** dengan **gap 2 hari**.

#### Langkah Implementasi:

```python
# 1. Filter data untuk Januari 2022
jan_2022_mask = (df_hourly['year'] == 2022) & (df_hourly['month'] == 1)
df_jan_2022 = df_hourly[jan_2022_mask].copy()

# 2. Lakukan prediksi
X_jan = df_jan_2022[hourly_feature_cols]
y_jan_actual = df_jan_2022[hourly_target_reg]
y_jan_pred = best_reg_model.predict(X_jan)

# 3. Buat DataFrame hasil
df_jan_2022['temp_pred'] = y_jan_pred[:, 0]
df_jan_2022['humidity_pred'] = y_jan_pred[:, 1]
df_jan_2022['windspeed_pred'] = y_jan_pred[:, 2]
df_jan_2022['pressure_pred'] = y_jan_pred[:, 3]

# 4. Resample ke 2-hari untuk kejelasan visualisasi
df_jan_2d = df_jan_2022.set_index('timestamp').resample('2D').mean().reset_index()
```

#### Visualisasi 4 Parameter (Gap 2 Hari):

```python
fig, axes = plt.subplots(4, 1, figsize=(14, 16))

params = [
    ('temp', 'temp_pred', 'Temperature (°C)', 'red'),
    ('humidity', 'humidity_pred', 'Humidity (%)', 'blue'),
    ('windspeed', 'windspeed_pred', 'Wind Speed (km/h)', 'green'),
    ('sealevelpressure', 'pressure_pred', 'Pressure (hPa)', 'purple')
]

for ax, (actual_col, pred_col, title, color) in zip(axes, params):
    ax.plot(df_jan_2d['timestamp'], df_jan_2d[actual_col], 
            '-o', color=color, label='Aktual', linewidth=2, markersize=6)
    ax.plot(df_jan_2d['timestamp'], df_jan_2d[pred_col], 
            '--s', color=color, alpha=0.6, label='Prediksi', linewidth=2, markersize=6)
    
    ax.set_title(f'{title} - Januari 2022 (Gap 2 Hari)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel(title)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d Jan'))
    ax.tick_params(axis='x', rotation=45)

plt.suptitle('Perbandingan Aktual vs Prediksi - Januari 2022', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/jan_2022_actual_vs_pred.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### Ilustrasi Grafik:

```
Temperature (°C) - Januari 2022 (Gap 2 Hari)
│
│    ●───●                    ●───●
│   /     \      ●───●       /     \      ● Aktual
│  ●       ●    /     \     ●       ●
│           \  ●       ●   /
│            ●──         ──●
│  ○───○      ○───○      ○───○      ○───○  ○ Prediksi
│
└────┬────┬────┬────┬────┬────┬────┬────→ Tanggal
    01   03   05   07   09   11   13   15 Jan
              (Gap 2 Hari)
```

### 6.3 Evaluasi Klasifikasi (Weather Code)

- **Confusion Matrix:** Visualisasi prediksi vs aktual untuk setiap weather_code.
- **Classification Report:** Precision, Recall, F1-Score per kelas.
- **Analisis Kelas Imbalanced:** Perhatikan kelas minoritas (code 65: Heavy Rain hanya 585 data).

```python
# Confusion Matrix untuk Januari 2022
y_jan_clf_actual = df_jan_2022['weather_code_encoded']
y_jan_clf_pred = best_clf_model.predict(X_jan)

cm = confusion_matrix(y_jan_clf_actual, y_jan_clf_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=le_weather_code.classes_,
            yticklabels=le_weather_code.classes_)
plt.title('Confusion Matrix - Weather Code (Januari 2022)')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()
plt.savefig('outputs/jan_2022_confusion_matrix.png', dpi=150)
plt.show()

print(classification_report(y_jan_clf_actual, y_jan_clf_pred,
                          target_names=[str(c) for c in le_weather_code.classes_]))
```

### 6.4 Output yang Diharapkan

| Output               | Deskripsi                                       |
| -------------------- | ----------------------------------------------- |
| Tabel Metrik         | MAE, RMSE, R² per parameter                     |
| Grafik Time-Series   | 4 subplot Actual vs Predicted (gap 2 hari)      |
| Confusion Matrix     | Heatmap klasifikasi weather_code                |
| Classification Report| Precision, Recall, F1-Score per kelas           |

**Insight Contoh:**
- "Temperature prediction sangat akurat (R² > 0.95)"
- "Wind Speed paling sulit diprediksi (R² ~ 0.7)"
- "Model kesulitan membedakan weather_code 61 dan 63"

---

## 6.5 Retraining dengan Seluruh Dataset (Final Model)

> **PENTING:** Setelah model terbaik dipilih dari perbandingan, latih ulang dengan **100% data** untuk produksi.

- **Tujuan:** Memaksimalkan performa model final dengan memanfaatkan seluruh data yang tersedia.
- **Langkah:**

1. Pilih model terbaik dari hasil perbandingan.
2. Gabungkan kembali `train_df` dan `test_df` menjadi `full_df`.
3. Latih **4 model** dengan seluruh data:

```python
# Gabung data
X_hourly_full = df_hourly[hourly_feature_cols]
y_hourly_reg_full = df_hourly[hourly_target_reg]
y_hourly_clf_full = df_hourly[hourly_target_clf]

X_daily_full = df_daily[daily_feature_cols]
y_daily_reg_full = df_daily[daily_target_reg]
y_daily_clf_full = df_daily[daily_target_clf]

# ===== MODEL HOURLY =====
hourly_regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
hourly_regressor.fit(X_hourly_full, y_hourly_reg_full)

hourly_classifier = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
hourly_classifier.fit(X_hourly_full, y_hourly_clf_full)

# ===== MODEL DAILY =====
daily_regressor = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
daily_regressor.fit(X_daily_full, y_daily_reg_full)

daily_classifier = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
daily_classifier.fit(X_daily_full, y_daily_clf_full)
```

- **Catatan:** Tidak ada evaluasi pada tahap ini karena semua data sudah digunakan untuk training.

---

## 7. Penyimpanan Model Terbaik (7 File .pkl)

- **Tujuan:** Menyimpan model ke dalam **7 file `.pkl`** untuk fleksibilitas deployment.

### 7.1 Struktur File .pkl

#### A. Combined Model (`weather_model_combined.pkl`)

```python
combined_package = {
    'hourly': {
        'regressor': hourly_regressor,
        'classifier': hourly_classifier,
        'feature_columns': hourly_feature_cols,
        'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
        'target_classification': 'weather_code',
    },
    'daily': {
        'regressor': daily_regressor,
        'classifier': daily_classifier,
        'feature_columns': daily_feature_cols,
        'target_regression': ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg'],
        'target_classification': 'weather_code_dominant',
    },
    'label_encoder_hourly': le_weather_code,
    'label_encoder_daily': le_weather_code_daily,
    'label_encoder_conditions': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    # [v2.0] Tambahan metadata
    'cyclical_features': ['hour_sin', 'hour_cos', 'month_sin', 'month_cos'],
    'interaction_features': ['dew_point', 'humid_temp_ratio', 'temp_range'],
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'combined'
}
```

#### B. Hourly Model (`weather_model_hourly.pkl`)

```python
hourly_package = {
    'regressor': hourly_regressor,
    'classifier': hourly_classifier,
    'feature_columns': hourly_feature_cols,
    'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
    'target_classification': 'weather_code',
    'label_encoder': le_weather_code,
    'label_encoder_conditions': le_conditions,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'hourly'
}
```

#### C. Daily Model (`weather_model_daily.pkl`)

```python
daily_package = {
    'regressor': daily_regressor,
    'classifier': daily_classifier,
    'feature_columns': daily_feature_cols,
    'target_regression': ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg'],
    'target_classification': 'weather_code_dominant',
    'label_encoder': le_weather_code_daily,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'daily'
}
```

#### D. Model Terpisah (Regressor & Classifier)

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
    'label_encoder': le_weather_code,
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
    'label_encoder': le_weather_code_daily,
    'weather_code_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '2.1',
    'model_type': 'daily_classifier'
}
```

### 7.2 Menyimpan 7 File Model

```python
import joblib
import os
from datetime import datetime

os.makedirs('models', exist_ok=True)

# 3 FILE UTAMA
joblib.dump(combined_package, 'models/weather_model_combined.pkl')
joblib.dump(hourly_package, 'models/weather_model_hourly.pkl')
joblib.dump(daily_package, 'models/weather_model_daily.pkl')

# 4 FILE TERPISAH
joblib.dump(hourly_reg_package, 'models/weather_model_hourly_regressor.pkl')
joblib.dump(hourly_clf_package, 'models/weather_model_hourly_classifier.pkl')
joblib.dump(daily_reg_package, 'models/weather_model_daily_regressor.pkl')
joblib.dump(daily_clf_package, 'models/weather_model_daily_classifier.pkl')

print("📦 Total: 7 model files created!")
```

**Output yang Diharapkan:**

```
models/
├── weather_model_combined.pkl           # ~200-400 MB
├── weather_model_hourly.pkl             # ~100-200 MB
├── weather_model_daily.pkl              # ~100-200 MB
├── weather_model_hourly_regressor.pkl   # ~50-100 MB
├── weather_model_hourly_classifier.pkl  # ~50-100 MB
├── weather_model_daily_regressor.pkl    # ~50-100 MB
└── weather_model_daily_classifier.pkl   # ~50-100 MB
```

### 7.3 Memuat Model (Inference/Backend)

```python
import joblib

model_package = joblib.load('models/weather_model_combined.pkl')

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
```

### 7.4 Sinkronisasi dengan Backend API

```python
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

---

## 8. Implementasi Multi-Step Forecasting (Recursive Strategy)

- **Tujuan:** Mengatasi masalah "Forecast Horizon" dengan mengimplementasikan fungsi yang dapat memprediksi cuaca untuk rentang waktu di masa depan (misal: 24, 48, atau 72 jam ke depan).
- **Masalah Model Saat Ini:** Model yang dilatih hanya mampu melakukan prediksi *single-step* (memprediksi 1 jam ke depan).
- **Strategi: Recursive Forecasting**

```python
def recursive_forecast_hourly(model_reg, model_clf, last_known_data, feature_cols, n_hours=24):
    """
    Prediksi cuaca secara rekursif untuk n_hours ke depan.
    
    Args:
        model_reg: Model regresi yang sudah dilatih
        model_clf: Model klasifikasi yang sudah dilatih
        last_known_data: DataFrame dengan data terakhir yang diketahui
        feature_cols: List kolom fitur
        n_hours: Jumlah jam ke depan untuk diprediksi
    
    Returns:
        DataFrame dengan prediksi untuk n_hours ke depan
    """
    predictions = []
    current_data = last_known_data.copy()
    
    for i in range(n_hours):
        X = current_data[feature_cols].values.reshape(1, -1)
        
        # Prediksi
        reg_pred = model_reg.predict(X)[0]
        clf_pred = model_clf.predict(X)[0]
        
        pred_dict = {
            'hour_ahead': i + 1,
            'temp': reg_pred[0],
            'humidity': reg_pred[1],
            'windspeed': reg_pred[2],
            'sealevelpressure': reg_pred[3],
            'weather_code_encoded': clf_pred
        }
        predictions.append(pred_dict)
        
        # Update untuk iterasi berikutnya (recursive)
        current_data['temp_lag_1'] = reg_pred[0]
        current_data['humidity_lag_1'] = reg_pred[1]
        current_data['windspeed_lag_1'] = reg_pred[2]
        current_data['sealevelpressure_lag_1'] = reg_pred[3]
        current_data['hour'] = (current_data['hour'] + 1) % 24
        
    return pd.DataFrame(predictions)
```

- **Output yang Diharapkan:**
  - DataFrame yang berisi prediksi cuaca untuk setiap jam dalam rentang waktu.
  - Visualisasi perbandingan hasil prediksi rekursif dengan data aktual.

---

## 9. Visualisasi Multi-Step Forecast vs. Aktual

- **Tujuan:** Memvisualisasikan performa strategi *Recursive Forecasting* pada data uji.
- **Langkah:**
  - Pilih satu titik awal dari *test set* (contoh: 1 Januari 2023, jam 00:00).
  - Panggil fungsi prediksi rekursif untuk menghasilkan ramalan cuaca selama 72 jam ke depan.
  - Buat 4 grafik garis (untuk Suhu, Kelembaban, Angin, Tekanan).

```python
# Ambil 72 jam terakhir dari test set sebagai data aktual
actual_72h = hourly_test.tail(72).copy().reset_index(drop=True)

# Lakukan forecast dari titik sebelum 72 jam terakhir
start_point = hourly_test.iloc[-73:-72].copy()
forecast_72h = recursive_forecast_hourly(
    best_reg_model, 
    best_clf_model, 
    start_point, 
    hourly_feature_cols, 
    n_hours=72
)

# Plot perbandingan
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
params = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
titles = ['Temperature (°C)', 'Humidity (%)', 'Wind Speed (km/h)', 'Pressure (hPa)']

for ax, param, title in zip(axes.flatten(), params, titles):
    ax.plot(range(72), actual_72h[param].values, 'b-', label='Aktual', linewidth=2)
    ax.plot(range(72), forecast_72h[param].values, 'r--', label='Prediksi Rekursif', linewidth=2)
    ax.set_title(f'{title} - Actual vs Recursive Forecast')
    ax.set_xlabel('Hours Ahead')
    ax.set_ylabel(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.suptitle('Multi-Step Recursive Forecast vs Actual (72 Hours)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()
```

- **Visualisasi yang Diharapkan:**
  - Grafik garis prediksi (merah putus-putus) mengikuti garis aktual (biru solid).
  - Grafik menunjukkan degradasi performa seiring berjalannya waktu (akumulasi error).

---

## 10. Visualisasi Dampak Data Inkremental

- **Tujuan:** Demonstrasi konsep _Incremental Learning_.
- **Langkah:** Melatih model dengan pecahan data training (10%, 20%, ... 100%) dan mengukur R² pada data test yang tetap.

```python
fractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
r2_scores = []

for frac in fractions:
    n_samples = int(len(X_hourly_train) * frac)
    X_subset = X_hourly_train.iloc[:n_samples]
    y_subset = y_hourly_train_reg.iloc[:n_samples]
    
    temp_model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    temp_model.fit(X_subset, y_subset)
    
    y_pred = temp_model.predict(X_hourly_test)
    r2 = r2_score(y_hourly_test_reg, y_pred)
    r2_scores.append(r2)
    
    print(f"   {int(frac*100):3d}% data ({n_samples:,} samples): R² = {r2:.4f}")

# Plot hasil
plt.figure(figsize=(10, 6))
plt.plot([f*100 for f in fractions], r2_scores, 'bo-', linewidth=2, markersize=8)
plt.xlabel('Percentage of Training Data (%)', fontsize=12)
plt.ylabel('R² Score on Test Set', fontsize=12)
plt.title('Impact of Incremental Data on Model Performance', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xticks([f*100 for f in fractions])
plt.tight_layout()
plt.show()
```

- **Visualisasi yang Diharapkan:** Grafik tren naik menunjukkan semakin banyak data historis, semakin akurat modelnya.

---

## 11. [v2.0] Prophet untuk Daily Forecast (OPSIONAL)

> **Kapan Gunakan Prophet?** Jika ingin menangkap pola musiman (seasonality) dengan lebih baik.

```python
# pip install prophet
from prophet import Prophet

# Siapkan data format Prophet (ds = timestamp, y = target)
prophet_df = daily_df[['timestamp', 'temp_mean']].rename(
    columns={'timestamp': 'ds', 'temp_mean': 'y'}
)

# Train model
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)
model.fit(prophet_df)

# Prediksi 30 hari ke depan
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Visualisasi
model.plot(forecast)
model.plot_components(forecast)
```

---

## Rangkuman Perubahan v2.0

| No | Fitur Baru                     | Dampak                                      |
| -- | ------------------------------ | ------------------------------------------- |
| 1  | Cyclical Time Features         | Model memahami siklus temporal              |
| 2  | Dew Point Feature              | Indikator kuat untuk prediksi hujan         |
| 3  | Class Balancing                | Akurasi kelas minoritas naik signifikan     |
| 4  | Expanding Window CV            | Validasi lebih robust dan jujur             |
| 5  | Rolling 3d/7d untuk Daily      | Model non-linear dapat menangkap trend      |
| 6  | Visualisasi Januari 2022       | Analisis detail per-bulan dengan gap 2 hari |
| 7  | Prophet (opsional)             | Seasonality detection lebih baik            |

---

## Checklist Implementasi

- [ ] Tambahkan cyclical features (hour_sin, hour_cos, month_sin, month_cos)
- [ ] Tambahkan dew_point dan interaction features
- [ ] Ubah klasifikasi ke `class_weight='balanced'`
- [ ] Implementasi Expanding Window CV
- [ ] Tambahkan rolling_3d dan rolling_7d untuk daily
- [ ] Buat visualisasi Januari 2022 dengan gap 2 hari
- [ ] (Opsional) Eksperimen dengan Prophet
- [ ] Update struktur .pkl dengan fitur baru
