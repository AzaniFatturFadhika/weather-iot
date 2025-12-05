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

Dataset berisi data cuaca per-jam dari tahun 2000-2024 dengan struktur kolom sebagai berikut:

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
| `weather_code`                       | int      | Kode cuaca (0-65)                      |
| `conditions`                         | string   | Kondisi cuaca (teks)                   |
| `temp_max_daily`                     | float    | Suhu maksimum harian (°C)             |
| `temp_min_daily`                     | float    | Suhu minimum harian (°C)              |
| `weather_code_daily`                 | int      | Kode cuaca harian                      |
| `temp_mean_daily`                    | float    | Suhu rata-rata harian (°C)            |

**Contoh Data (6 baris pertama):**

| id | timestamp           | hour | day | month | year | temp | humidity | windspeed | weather_code | conditions |
| -- | ------------------- | ---- | --- | ----- | ---- | ---- | -------- | --------- | ------------ | ---------- |
| 0  | 2000-01-01 00:00:00 | 0    | 1   | 1     | 2000 | 21.8 | 98       | 4.0       | 3            | Overcast   |
| 1  | 2000-01-01 01:00:00 | 1    | 1   | 1     | 2000 | 21.4 | 99       | 4.0       | 3            | Overcast   |
| 2  | 2000-01-01 02:00:00 | 2    | 1   | 1     | 2000 | 21.4 | 98       | 3.2       | 3            | Overcast   |
| 3  | 2000-01-01 03:00:00 | 3    | 1   | 1     | 2000 | 21.2 | 99       | 4.6       | 3            | Overcast   |
| 4  | 2000-01-01 04:00:00 | 4    | 1   | 1     | 2000 | 21.0 | 99       | 3.6       | 3            | Overcast   |
| 5  | 2000-01-01 05:00:00 | 5    | 1   | 1     | 2000 | 20.8 | 98       | 2.7       | 3            | Overcast   |

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

- **Tujuan:** Menyiapkan fitur yang relevan untuk prediksi deret waktu (_Time-Series_).
- **Langkah:**
  - **Format Waktu:** Memastikan kolom `timestamp` bertipe datetime.
  - **Label Encoding:** Mengubah `conditions` menjadi numerik.
  - **Feature Engineering (Baru):** Membuat fitur "Lag" (nilai masa lalu) dan "Rolling Mean" untuk menangkap pola tren.
    - `lag_1`: Nilai 1 jam yang lalu.
    - `lag_24`: Nilai 24 jam yang lalu.
    - `rolling_mean_24`: Rata-rata 24 jam terakhir.
  - **Handling NaN:** Menghapus baris awal yang memiliki nilai `NaN` akibat pembuatan fitur lag.
- **Output yang Diharapkan:** Dataset dengan kolom fitur tambahan (`temperature_lag_1`, dll) tampilkan beris pertama fata hasil pre-processing.

### 5\. Pelatihan dan Perbandingan Model (Komprehensif)

- **Tujuan:** Membandingkan berbagai algoritma untuk memilih model terbaik bagi Regresi (data kontinu) dan Klasifikasi (kondisi cuaca).

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

  1. Pilih model terbaik dari hasil perbandingan (misal: Random Forest).
  2. Gabungkan kembali `train_df` dan `test_df` menjadi `full_df`.
  3. Latih model dengan seluruh data:
     ```python
     # Final training dengan 100% data
     final_regressor = RandomForestRegressor(**best_params)
     final_regressor.fit(X_full, y_full)

     final_classifier = RandomForestClassifier(**best_params)
     final_classifier.fit(X_full, y_class_full)
     ```
  4. Simpan model final ke file `.pkl`.
- **Catatan:** Tidak ada evaluasi pada tahap ini karena semua data sudah digunakan untuk training. Evaluasi sudah dilakukan pada tahap 5-6.

### 7. Penyimpanan Model Terbaik (Single File)

- **Tujuan:** Menyimpan semua model dan metadata yang diperlukan ke dalam **SATU file `.pkl`** agar mudah dimuat oleh Backend untuk inference.

#### 7.1 Struktur File .pkl

Model disimpan dalam format dictionary dengan struktur berikut:

```python
model_package = {
    # Model
    'regressor': final_regressor,           # RandomForestRegressor (atau model terbaik)
    'classifier': final_classifier,         # RandomForestClassifier (atau model terbaik)
    
    # Metadata untuk Feature Engineering
    'feature_columns': feature_cols,        # List kolom fitur yang digunakan
    'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
    'target_classification': 'weather_code',
    
    # Encoder (untuk decode hasil prediksi)
    'label_encoder': le_conditions,         # LabelEncoder untuk conditions
    
    # Mapping weather_code ke rain (deterministik)
    'weather_code_to_rain': {
        0: 0, 1: 0, 2: 0, 3: 0,
        51: 0.2, 53: 0.7, 55: 1.1,
        61: 1.7, 63: 4.0, 65: 10.3
    },
    
    # Versi dan info
    'version': '2.0',
    'trained_date': datetime.now().isoformat(),
    'data_range': {'start': '2000-01-01', 'end': '2024-12-31'}
}
```

#### 7.2 Menyimpan Model (Training)

```python
import joblib
from datetime import datetime

# Simpan ke file .pkl
MODEL_PATH = 'models/weather_model_v2.pkl'
joblib.dump(model_package, MODEL_PATH)

print(f"✅ Model disimpan ke: {MODEL_PATH}")
print(f"   - Regressor: {type(model_package['regressor']).__name__}")
print(f"   - Classifier: {type(model_package['classifier']).__name__}")
```

#### 7.3 Memuat Model (Inference/Backend)

```python
import joblib

# Load model package
model_package = joblib.load('models/weather_model_v2.pkl')

# Akses komponen
regressor = model_package['regressor']
classifier = model_package['classifier']
feature_cols = model_package['feature_columns']
rain_map = model_package['weather_code_to_rain']

# Contoh prediksi
X_new = prepare_features(input_data, feature_cols)  # Siapkan fitur
pred_values = regressor.predict(X_new)              # Prediksi temp, hum, wind, pressure
pred_code = classifier.predict(X_new)               # Prediksi weather_code
pred_rain = rain_map.get(pred_code[0], 0)           # Derive rain dari weather_code
```

#### 7.4 Sinkronisasi dengan Backend API

Backend (`main.py`) harus menggunakan struktur yang sama:

```python
# Di main.py atau model_loader.py
class WeatherPredictor:
    def __init__(self, model_path: str):
        self.package = joblib.load(model_path)
        self.regressor = self.package['regressor']
        self.classifier = self.package['classifier']
        self.feature_cols = self.package['feature_columns']
        self.rain_map = self.package['weather_code_to_rain']
    
    def predict(self, features: dict) -> dict:
        X = self._prepare_features(features)
        
        # Regresi
        reg_pred = self.regressor.predict(X)[0]
        
        # Klasifikasi
        weather_code = self.classifier.predict(X)[0]
        
        return {
            'temp': reg_pred[0],
            'humidity': reg_pred[1],
            'windspeed': reg_pred[2],
            'pressure': reg_pred[3],
            'weather_code': int(weather_code),
            'rain': self.rain_map.get(int(weather_code), 0)
        }
```

- **Output yang Diharapkan:** File `weather_model_v2.pkl` tersimpan di folder `models/` dengan ukuran ~50-200 MB (tergantung model).

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
