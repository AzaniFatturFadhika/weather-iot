# Training Guide v4.0 - Date-Based Seasonality Model

Panduan lengkap untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil dengan metodologi **Date-Based Seasonality**.

Model ini menggunakan pendekatan **Direct Mapping (Tanggal → Cuaca)**, di mana model mempelajari rata-rata historis dan pola musiman untuk memprediksi cuaca berdasarkan input waktu saja tanpa ketergantungan pada data sensor sebelumnya (lag/rolling features).

---

## Sample Dataset

Dataset berisi data cuaca dari tahun 2000-2024.

### Kolom Input (Features)

Dalam versi ini, fitur yang digunakan **TUNGGAL** adalah komponen waktu.

| Tipe Prediksi              | Fitur Input (_Features_)             |
| :------------------------- | :------------------------------------- |
| **Hourly (Per-Jam)** | `day`, `month`, `year`, `hour` |
| **Daily (Per-Hari)** | `day`, `month`, `year`           |

### Kolom Target

Model memprediksi variabel berikut:

| Tipe Target                         | Variabel                                                    |
| :---------------------------------- | :---------------------------------------------------------- |
| **Regression (Numerik)**      | `temp`, `humidity`, `windspeed`, `sealevelpressure` |
| **Classification (Kategori)** | `conditions` (weather_description)                        |

---

## Alur Kerja Notebook (`model_weather_training_v4.ipynb`)

Berikut adalah langkah-langkah detail yang dijalankan dalam notebook.

### 1. Persiapan Lingkungan

Mengimpor pustaka kunci:

* **Data Processing:** `pandas`, `numpy`, `joblib`
* **Visualization:** `matplotlib`, `seaborn`
* **Machine Learning:** `scikit-learn`, `xgboost` (opsional)

### 2. Pemuatan & Pembersihan Data

* Memuat dataset CSV historis 2000-2024.
* Mengonversi kolom `timestamp` ke format datetime.
* **Handling Missing Values:** Menggunakan interpolasi linear untuk mengisi celah data yang hilang.
* **Feature Engineering:** Mengekstrak komponen `day`, `month`, `year`, dan `hour` dari timestamp.

### 3. Agregasi Data Harian

Selain data per-jam, notebook juga membuat dataset harian (`df_daily`) dengan agregasi:

* `temp`: min, max, mean
* `humidity`, `windspeed`, `pressure`: mean
* `conditions`: nilai modus (paling sering muncul) hari itu.

### 4. Encoding Variabel Kategorikal

Target klasifikasi (`conditions`) berupa teks ("Partially cloudy", "Rain", dll) dikonversi menjadi angka menggunakan `LabelEncoder`.

### 5. Definisi & Pemisahan Data

* **Input Features:** Hanya menggunakan komponen waktu.
* **Training/Test Split:** Menggunakan **Random Split (80% Train, 20% Test)**.
  * *Alasan:* Karena model ini memetakan _waktu ke cuaca_ (pola global), pengacakan data membantu model mempelajari pola musiman dari seluruh rentang tahun (2000-2024) secara merata, bukan hanya memotong di tahun tertentu.

---

### 6. Pelatihan & Evaluasi Model

Notebook melatih beberapa algoritma secara otomatis untuk mencari yang terbaik.

#### A. Algoritma Regression

Digunakan untuk memprediksi suhu, kelembaban, dll.

1. **Linear Regression** (Baseline)
2. **K-Neighbors Regressor**
3. **Decision Tree Regressor**
4. **Random Forest Regressor** (Biasanya memberikan hasil terbaik)
5. **XGBoost Regressor**

**Metrik Evaluasi:**

* **MAE (Mean Absolute Error):** Rata-rata kesalahan absolut.
* **RMSE (Root Mean Squared Error):** Penalti lebih besar untuk kesalahan besar.
* **R² Score:** Seberapa baik model menjelaskan variansi data (Mendekati 1.0 = Sempurna).

#### B. Algoritma Classification

Digunakan untuk memprediksi kondisi cuaca (Hujan, Cerah, Berawan).

1. **Logistic Regression** (Standard & Balanced)
2. **Decision Tree Classifier**
3. **Random Forest Classifier** (Standard & Balanced)
4. **XGBoost Classifier**

**Metrik Evaluasi:**

* **Accuracy:** Persentase prediksi benar.
* **F1-Score (Weighted):** Keseimbangan antara presisi dan recall, penting untuk kelas yang tidak seimbang (imbalanced classes) seperti "Hujan Lebat" yang jarang terjadi.

---

### 7. Penyimpanan Model (Saving)

Model terbaik (biasanya Random Forest) disimpan dalam format `.pkl` terkompresi menggunakan struktur **Combined Package**.

**File:** `models/v4_weather_model_combined.pkl`

**Struktur Internal:**

```python
{
    'hourly': {
        'regressor': <Model Regresi Terbaik>,
        'classifier': <Model Klasifikasi Terbaik>,
        'feature_columns': ['day', 'month', 'year', 'hour'],
        'target_regression': [...],
        'target_classification': 'conditions'
    },
    'daily': {
        'regressor': <Model Regresi Terbaik>,
        'classifier': <Model Klasifikasi Terbaik>,
        'feature_columns': ['day', 'month', 'year'],
        ...
    },
    'label_encoder_hourly': <Encoder untuk kondisi jam>,
    'label_encoder_daily': <Encoder untuk kondisi hari>,
    'version': '4.0'
}
```

---

### 8. Visualisasi & Validasi

Notebook menghasilkan visualisasi untuk memverifikasi kinerja model:

1. **Feature Importance:** Menunjukkan seberapa penting `day`, `month`, `year`, atau `hour` dalam menentukan cuaca. (Biasanya `hour` sangat penting untuk suhu).
2. **Confusion Matrix:** Melihat kesalahan klasifikasi (misal: sering salah sebut "Cerah" padahal "Berawan").
3. **Forecast vs Actual:** Grafik garis yang membandingkan prediksi model terhadap data aktual selama 72 jam terakhir dari test set.

---

## Cara Menggunakan Model

Gunakan GUI yang telah disediakan untuk melakukan prediksi tanpa mengoding:
Script: `weather_prediction_gui_v4.py`

1. Jalankan script.
2. Load file `models/v4_weather_model_combined.pkl`.
3. Pilih tab **Forecast by Date Range**.
4. Tentukan tanggal awal dan akhir.
5. Klik **Generate**.
