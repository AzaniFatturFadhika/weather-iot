# Training Guide v4.0 - Date-Based Seasonality Model

Panduan lengkap untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil dengan metodologi **Date-Based Seasonality**.

Model ini menggunakan pendekatan **Direct Mapping (Tanggal → Cuaca)**, di mana model mempelajari rata-rata historis dan pola musiman untuk memprediksi cuaca berdasarkan input waktu saja.

---

## Visualisasi dalam Jurnal dan Kecocokan dengan Kerangka Notebook

| Bagian dalam Kerangka Notebook                               | Tujuan Visualisasi                                                                                 | Visualisasi dalam Jurnal                                                        |
| :----------------------------------------------------------- | :------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **5. Pelatihan dan Perbandingan Model**                | Tabel Perbandingan Metrik (MSE, MAE, RMSE, R²) untuk semua model.                                 | **Tabel 4:** _Performance metrics for different regression models_.     |
| **6. Analisis Hasil dan Kinerja Individual Parameter** | Tabel Evaluasi Kinerja (MAE, RMSE, R²) untuk setiap parameter + Grafik Januari 2022 (gap 2 hari). | **Tabel 5:** _Performance evaluation of weather parameter predictions_. |
| **8. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual Actual vs Predicted untuk Suhu, Kelembaban, Angin, Tekanan.             | **Gambar 15-18:** _Actual vs. Predicted_ per parameter.                 |
| **9. Visualisasi Dampak Data Inkremental**             | Grafik garis peningkatan R² seiring bertambahnya data (_Incremental Learning_).                 | **Gambar 21:** _Impact of incremental data on model performance_.       |

---

## Sample Dataset

Dataset berisi data cuaca per-jam dari tahun 2000-2024 dengan struktur **23 kolom**:

### Kolom Hourly (Per-Jam)

| Kolom                                  | Tipe     | Deskripsi                              |
| -------------------------------------- | -------- | -------------------------------------- |
| `id`                                 | int      | ID unik                                |
| `timestamp`                          | datetime | Waktu pengukuran (per-jam)             |
| `hour`, `day`, `month`, `year` | int      | Komponen waktu                         |
| `temp`                               | float    | Suhu (°C)                             |
| `humidity`                           | int      | Kelembaban (%)                         |
| `windspeed`                          | float    | Kecepatan angin (km/h)                 |
| `sealevelpressure`                   | float    | Tekanan permukaan laut (hPa)           |
| `rain`                               | float    | Curah hujan (mm)                       |
| `precipitation`                      | float    | Presipitasi (mm) - identik dengan rain |
| `apparent_temperature`               | float    | Suhu yang dirasakan (°C)              |
| `surface_pressure`                   | float    | Tekanan permukaan (hPa)                |
| `conditions`                         | int      | Kode cuaca (0-65)                      |
| `conditions`                         | string   | Kondisi cuaca (teks)                   |

### Kolom Daily (Per-Hari)

| Kolom                   | Tipe  | Deskripsi                               |
| ----------------------- | ----- | --------------------------------------- |
| `temp_max_daily`      | float | Suhu maksimum harian (°C)              |
| `temp_min_daily`      | float | Suhu minimum harian (°C)               |
| `conditions_daily`    | int   | Kode cuaca dominan harian               |
| `temp_mean_daily`     | float | Suhu rata-rata harian (°C)             |
| `humidity_avg_daily`  | int   | Kelembaban rata-rata harian (%)         |
| `pressure_avg_daily`  | float | Tekanan rata-rata harian (hPa)          |
| `windspeed_avg_daily` | float | Kecepatan angin rata-rata harian (km/h) |

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
from sklearn.model_selection import train_test_split, cross_val_score
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

### 3.1 Analisis Korelasi: conditions, conditions, dan rain/precipitation

**Temuan Kritis:** Terdapat hubungan **deterministik** antara `conditions`, `conditions`, dan nilai `rain`/`precipitation`.

#### Tabel Mapping Weather Code ke Rain

| Weather Code | Kondisi (conditions) | Rain Mean (mm) | Rain Range (mm) | Jumlah Data |
| :----------: | -------------------- | :------------: | :-------------: | :---------: |
|      0      | Clear                |      0.00      |       0.0       |   23,298   |
|      1      | Partially cloudy     |      0.00      |       0.0       |   28,622   |
|      2      | Partially cloudy     |      0.00      |       0.0       |   26,366   |
|      3      | Overcast             |      0.00      |       0.0       |   81,994   |
|      51      | Rain                 |      0.21      |    0.1 - 0.4    |   37,108   |
|      53      | Rain                 |      0.66      |    0.5 - 0.9    |   12,421   |
|      55      | Rain                 |      1.09      |    1.0 - 1.2    |    3,785    |
|      61      | Rain, Overcast       |      1.74      |    1.3 - 2.4    |    7,333    |
|      63      | Rain, Overcast       |      3.95      |    2.5 - 7.5    |    5,792    |
|      65      | Rain, Overcast       |     10.28     |   7.6 - 33.4   |     585     |

#### Kesimpulan Korelasi

1. **rain = precipitation**: Nilai keduanya **identik** di seluruh dataset.
2. **conditions → rain**: Korelasi deterministik. Kode ≥ 50 **selalu** memiliki nilai rain > 0.
3. **conditions → rain**: Konsisten. Kondisi yang mengandung "Rain" selalu memiliki nilai rain > 0.

#### Implikasi untuk Model

> **PENTING:** Karena hubungan deterministik ini, **tidak perlu memprediksi `rain` secara terpisah**. Cukup prediksi `conditions`, lalu derive nilai rain menggunakan mapping:

```python
rain_map = {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3}
predicted_rain = rain_map[predicted_conditions]

# Klasifikasi hujan biner
is_rain = 1 if conditions >= 50 else 0
```

---

## 4. Pra-pemrosesan Data dan Feature Engineering

- **Tujuan:** Menyiapkan fitur input pembelajaran. Dalam model v4.0, input yang digunakan **HANYA** komponen waktu (Tanggal/Jam), tanpa data sensor historis.

### 4.1 Preprocessing Data Hourly

- **Langkah:**
  - **Format Waktu:** Memastikan kolom `timestamp` bertipe datetime.
  - **Label Encoding:** Mengubah `conditions` menjadi numerik.
  - **Fitur Input:** Hanya `day`, `month`, `year`, `hour`.

```python
df_hourly = df.copy()

# Label Encoding for Target
le_conditions = LabelEncoder()
df_hourly['conditions_encoded'] = le_conditions.fit_transform(df_hourly['conditions'])
```

### 4.2 Preprocessing Data Daily

```python
# Agregasi data hourly menjadi daily
df_daily = df.groupby(['year', 'month', 'day']).agg({
    'temp': ['min', 'max', 'mean'],
    'humidity': 'mean',
    'windspeed': 'mean',
    'sealevelpressure': 'mean',
    'conditions': lambda x: x.mode()[0],
    'rain': 'sum'
}).reset_index()

# Flatten column names
df_daily.columns = ['year', 'month', 'day', 
                    'temp_min', 'temp_max', 'temp_mean',
                    'humidity_avg', 'windspeed_avg', 'pressure_avg',
                    'conditions_dominant', 'rain_total']

# Label Encoding
le_conditions_daily = LabelEncoder()
df_daily['conditions_dominant_encoded'] = le_conditions_daily.fit_transform(df_daily['conditions_dominant'])
```

- **Output yang Diharapkan:**
  - `df_hourly`: Dataset hourly siap train.
  - `df_daily`: Dataset daily siap train.

---

## 5. Pelatihan dan Perbandingan Model

- **Tujuan:** Memilih model terbaik yang dapat memetakan **Tanggal → Cuaca**.
- **Strategi:** Menggunakan algoritma berbasis Tree (Random Forest / XGBoost) yang mampu menangkap pola non-linear dari fitur waktu (misal: Januari=Hujan, Juli=Panas).

### 5.1 Definisi Fitur dan Target

```python
# HOURLY Features - HANYA KOMPONEN WAKTU
hourly_feature_cols = ['day', 'month', 'year', 'hour']

hourly_target_reg = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
hourly_target_clf = 'conditions_encoded'

# DAILY Features - HANYA KOMPONEN WAKTU
daily_feature_cols = ['day', 'month', 'year']

daily_target_reg = ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg']
daily_target_clf = 'conditions_dominant_encoded'
```

### 5.2 Pemisahan Data (Train/Test Split)

Gunakan pembagian data acak (Random Split) karena model mempelajari pola global (musiman), bukan ketergantungan urutan waktu jangka pendek.

```python
# Hourly Split
X_hourly_train, X_hourly_test, y_hourly_train_reg, y_hourly_test_reg = train_test_split(
    df_hourly[hourly_feature_cols], 
    df_hourly[hourly_target_reg], 
    test_size=0.2, 
    random_state=42
)
y_hourly_train_clf, y_hourly_test_clf = train_test_split(
    df_hourly[hourly_target_clf], test_size=0.2, random_state=42
)

# Daily Split... (lakukan hal yang sama)
```

### 5.3 Komparasi Model Regresi & Klasifikasi

Bandingkan algoritma berikut:
1.  **Random Forest Regressor/Classifier** (Disarankan)
2.  **XGBoost Regressor/Classifier** (Disarankan)
3.  Linear/Logistic Regression (Baseline)

Gunakan `class_weight='balanced'` untuk klasifikasi agar prediksi kondisi cuaca yang jarang (misal: Hujan Lebat) tetap terdeteksi.

---

## 6. Analisis Hasil dan Kinerja Individual Parameter

- **Tujuan:** Evaluasi seberapa baik model "menghafal" pola cuaca berdasarkan tanggal.
- **Periode:** Januari 2022.

### 6.2 Visualisasi Time-Series: Actual vs Predicted (Januari 2022)

Tampilkan grafik perbandingan **Actual vs Predicted** untuk bulan Januari 2022.

(Gunakan kode visualisasi standar seperti `plt.plot(actual)` dan `plt.plot(predicted)`).

---

## 6.5 Retraining dengan Seluruh Dataset (Final Model)

> **PENTING:** Latih ulang dengan **100% data** agar model mendapatkan informasi penuh dari tahun 2000-2024.

Latih 4 model utama dengan seluruh data:
1.  Hourly Regressor
2.  Hourly Classifier
3.  Daily Regressor
4.  Daily Classifier

---

## 7. Penyimpanan Model Terbaik (7 File .pkl)

Simpan model ke dalam **7 file `.pkl`** untuk fleksibilitas deployment di backend.

### 7.1 Struktur Metadata File .pkl

#### A. Combined Model (`weather_model_combined_v4.pkl`)

```python
combined_package = {
    'hourly': {
        'regressor': hourly_regressor,
        'classifier': hourly_classifier,
        'feature_columns': hourly_feature_cols, # ['day', 'month', 'year', 'hour']
        'target_regression': hourly_target_reg,
        'target_classification': 'conditions',
    },
    'daily': {
        'regressor': daily_regressor,
        'classifier': daily_classifier,
        'feature_columns': daily_feature_cols, # ['day', 'month', 'year']
        'target_regression': daily_target_reg,
        'target_classification': 'conditions_dominant',
    },
    'label_encoder_hourly': le_conditions,
    'label_encoder_daily': le_conditions_daily,
    'conditions_to_rain': {0:0, 1:0, 2:0, 3:0, 51:0.2, 53:0.7, 55:1.1, 61:1.7, 63:4.0, 65:10.3},
    'version': '4.0',
    'trained_date': datetime.now().isoformat(),
    'model_type': 'combined_seasonality_date_based'
}
```

#### B. - G. File Terpisah Lainnya

Simpan 6 file lainnya (`hourly_v4`, `daily_v4`, `hourly_reg_v4`, dst.) mengikuti struktur yang sama.

### 7.2 Eksekusi Penyimpanan

```python
joblib.dump(combined_package, 'models/weather_model_combined_v4.pkl')
joblib.dump(hourly_package, 'models/weather_model_hourly_v4.pkl')
joblib.dump(daily_package, 'models/weather_model_daily_v4.pkl')
# ... dump sisa 4 file lainnya ...

print("📦 Total: 7 model files created (v4.0 Date-Based)!")
```

---

## 8. Implementasi Forecasting (Direct Strategy)

Tidak perlu loop rekursif. Cukup generate tanggal target dan lakukan prediksi langsung.

```python
def predict_future_weather_v4(model_reg, model_clf, start_date, n_hours=24):
    future_dates = [start_date + pd.Timedelta(hours=i) for i in range(n_hours)]
    
    # Buat DataFrame Input
    features = pd.DataFrame({
        'day': [d.day for d in future_dates],
        'month': [d.month for d in future_dates],
        'year': [d.year for d in future_dates],
        'hour': [d.hour for d in future_dates]
    })
    
    # Predict
    reg_pred = model_reg.predict(features) # [N, 4]
    clf_pred = model_clf.predict(features) # [N]
    
    # Format Output
    results = []
    for i, date in enumerate(future_dates):
        results.append({
            'timestamp': date,
            'temp': reg_pred[i][0],
            'humidity': reg_pred[i][1],
            'windspeed': reg_pred[i][2],
            'sealevelpressure': reg_pred[i][3],
            'conditions': clf_pred[i]
        })
        
    return pd.DataFrame(results)
```

---

## 9. Visualisasi Forecast vs Aktual

Lakukan visualisasi perbandingan hasil forecasting jangka panjang (misal 72 jam) dengan data aktual dari test set untuk memvalidasi performa model.

---

## 10. Checklist Implementasi

- [ ] Load Dataset
- [ ] Buat fitur waktu HANYA: `day`, `month`, `year`, `hour`
- [ ] Tentukan Target y (sama seperti v3)
- [ ] Split Data (Random Split)
- [ ] Train Model (Random Forest / XGBoost)
- [ ] Evaluasi Model
- [ ] Simpan 7 File Model dengan suffix `_v4`
