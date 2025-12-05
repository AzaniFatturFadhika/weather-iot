Berikut adalah kerangka urutan/struktur _notebook_ `ipynb` untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil, yang telah diperbarui untuk mendukung metodologi **Time-Series Forecasting** yang lebih akurat:

### Visualisasi dalam Jurnal dan Kecocokan dengan Kerangka Notebook

| Bagian dalam Kerangka Notebook                               | Tujuan Visualisasi (Sesuai Kerangka)                                                                                          | Visualisasi yang Ada dalam Jurnal                                               |
| :----------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| **4. Pelatihan dan Perbandingan Model**                | Tabel Perbandingan Metrik (MSE, MAE, RMSE, R²) untuk semua model.                                                            | **Tabel 4:** _Performance metrics for different regression models_.     |
| **5. Analisis Hasil dan Kinerja Individual Parameter** | Tabel Evaluasi Kinerja (MAE, RMSE,$R^2$) untuk setiap parameter yang diprediksi oleh model terbaik.                         | **Tabel 5:** _Performance evaluation of weather parameter predictions_. |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Suhu.                                     | **Gambar 15:** _Actual vs. Predicted temperature_.                      |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kelembaban.                               | **Gambar 16:** _Actual vs. Predicted humidity_.                         |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kecepatan Angin.                          | **Gambar 17:** _Actual vs. Predicted wind speed_.                       |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Tekanan.                                 | **Gambar 18:** _Actual vs. Predicted pressure_.                         |
| **7. Visualisasi Dampak Data Inkremental**             | Grafik garis yang menunjukkan peningkatan skor$R^2$ seiring bertambahnya jumlah _data points_ (_Incremental Learning_). | **Gambar 21:** _Impact of incremental data on model performance_.       |

## Kerangka Struktur Notebook (`.ipynb`) untuk Pelatihan Model Prediksi Cuaca (Diperbarui)

### 1\. Persiapan Lingkungan dan Pemuatan Pustaka

- **Tujuan:** Mengimpor semua pustaka Python yang diperlukan.
- **Pustaka Kunci:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `sklearn` (termasuk `TimeSeriesSplit`, `RandomForestRegressor`, dll), `joblib`.
- **Output yang Diharapkan:** Konfirmasi impor pustaka berhasil.

### 2\. Pengumpulan dan Pemuatan Data

- **Tujuan:** Memuat _dataset_ historis gabungan.
- **Langkah:**
  - Memuat data historis [historical_data_hourly.csv](..\data_collections\datasets\historical_data_hourly.csv).
  - Mengurutkan data berdasarkan waktu (`timestamp`) untuk memastikan urutan kronologis yang benar.
- **Output yang Diharapkan:** Tampilan beberapa baris pertama _dataset_ dan info struktur data.

### 3\. Pra-pemrosesan Data dan Feature Engineering (PENTING)

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

### 4\. Pelatihan dan Perbandingan Model (Komprehensif)

- **Tujuan:** Membandingkan berbagai algoritma untuk memilih model terbaik bagi Regresi (data kontinu) dan Klasifikasi (kondisi cuaca).
- **Langkah:**
  - **Pemisahan Data:** Menggunakan `Time-Series Split` (Data lama untuk Train, data baru untuk Test).
  - **Komparasi Regresi (Target: temp, hum, press, wind_speed):**
    - Melatih dan membandingkan algoritma:
      1. **Linear Regression**
      2. **K-Neighbors Regressor**
      3. **Decision Tree Regressor**
      4. **Random Forest Regressor**
    - **Evaluasi:** Bandingkan MSE, MAE, RMSE, dan $R^{2}$. Pilih yang terbaik (biasanya Random Forest).
  - **Komparasi Klasifikasi (Target: weather_code):**
    - Melatih dan membandingkan minimal 3 algoritma, contohnya:
      1. **Logistic Regression**
      2. **Decision Tree Classifier**
      3. **Random Forest Classifier**
    - **Evaluasi:** Bandingkan Accuracy, F1-Score. Pilih yang terbaik.
- **Output yang Diharapkan:**
  - Tabel perbandingan metrik untuk 4 algoritma Regresi.
  - Tabel perbandingan metrik untuk 3 algoritma Klasifikasi.
  - Kesimpulan pemilihan model terbaik untuk disimpan.

### 5\. Analisis Hasil dan Kinerja Individual Parameter

- **Tujuan:** Evaluasi mendalam model terbaik untuk semua parameter.
- **Langkah:**
  - Menampilkan metrik regresi untuk Suhu, Kelembaban, Angin, Tekanan.
  - Menampilkan metrik klasifikasi untuk Kondisi Cuaca (misal: akurasi prediksi "Hujan" vs "Cerah").
- **Output yang Diharapkan:** Tabel kinerja per parameter dan Confusion Matrix untuk prediksi cuaca.

### 6. Penyimpanan Model Terbaik (Single File)

- **Tujuan:** Menyimpan semua model yang telah dilatih ke dalam **SATU file `.pkl`** agar mudah dimuat oleh Backend.
- **Langkah:**
  - Membuat dictionary: `{'regressor': model_reg, 'classifier': model_clf, 'version': '2.0'}`.
  - Menyimpan dictionary tersebut menggunakan `joblib` atau `pickle`.
- **Output yang Diharapkan:** File `weather_model_v2.pkl` tersimpan di folder `models/`.

### 7. Visualisasi Perbandingan Aktual vs. Prediksi

- **Tujuan:** Memvisualisasikan performa model pada data uji (Januari 2020).
- **Langkah:**
  - Mengambil data Januari 2020.
  - Melakukan prediksi menggunakan fitur lag yang telah dibuat.
  - Agregasi ke level Harian (Daily Mean) untuk plot yang lebih bersih.
- **Visualisasi yang Diharapkan:** 4 Grafik garis (Suhu, Kelembaban, Angin, Tekanan) di mana garis Prediksi (Merah Putus-putus) mengikuti garis Aktual (Biru) dengan sangat dekat.

### 8. Visualisasi Dampak Data Inkremental

- **Tujuan:** Demonstrasi konsep _Incremental Learning_.
- **Langkah:** Melatih model dengan pecahan data training (10%, 20%, ... 100%) dan mengukur $R^{2}$ pada data test yang tetap.
- **Visualisasi yang Diharapkan:** Grafik tren naik yang menunjukkan semakin banyak data historis, semakin akurat modelnya.
