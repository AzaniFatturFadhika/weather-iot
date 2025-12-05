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

Dataset:
id	timestamp	hour	day	month	year	temp	humidity	windspeed	sealevelpressure	rain	precipitation	apparent_temperature	surface_pressure	weather_code	conditions	temp_max_daily	temp_min_daily	weather_code_daily	temp_mean_daily
0	2000-01-01 00:00:00	0	1	1	2000	21.8	98	4.0	1008.4	0.0	0.0	25.9	984.5	3	Overcast	27.5	20.8	53	24.1
1	2000-01-01 01:00:00	1	1	1	2000	21.4	99	4.0	1007.9	0.0	0.0	25.3	983.9	3	Overcast	27.5	20.8	53	24.1
2	2000-01-01 02:00:00	2	1	1	2000	21.4	98	3.2	1007.4	0.0	0.0	25.4	983.4	3	Overcast	27.5	20.8	53	24.1
3	2000-01-01 03:00:00	3	1	1	2000	21.2	99	4.6	1007.0	0.0	0.0	24.9	983.0	3	Overcast	27.5	20.8	53	24.1
4	2000-01-01 04:00:00	4	1	1	2000	21.0	99	3.6	1006.9	0.0	0.0	24.7	982.9	3	Overcast	27.5	20.8	53	24.1
5	2000-01-01 05:00:00	5	1	1	2000	20.8	98	2.7	1006.6	0.0	0.0	24.5	982.6	3	Overcast	27.5	20.8	53	24.1

Regression

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
- **Output yang Diharapkan:**
  - Tabel statistik deskriptif.
  - Serangkaian plot (histogram, heatmap, plot garis deret waktu).
  - Wawasan awal tentang data, seperti "suhu menunjukkan pola musiman yang jelas" atau "kelembaban dan curah hujan berkorelasi positif."

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
- **Langkah:**
  - **Pemisahan Data:** Menggunakan `Time-Series Split` (Data lama untuk Train, data baru untuk Test).
  - **Komparasi Regresi (Target: temp, hum, press, wind_speed):**
    - Melatih dan membandingkan algoritma:
      1. **Linear Regression**
      2. **K-Neighbors Regressor**
      3. **Decision Tree Regressor**
      4. **Random Forest Regressor**
      5. **XGBoost Reggressor**
    - **Evaluasi:** Bandingkan semua parameter performa seperti MSE, MAE, RMSE, dan $R^{2}$. Pilih yang terbaik (biasanya Random Forest).
  - **Komparasi Klasifikasi (Target: weather_code):**
    - Melatih dan membandingkan algoritma:
      1. **Logistic Regression**
      2. **Decision Tree Classifier**
      3. **Random Forest Classifier**
      4. **XGBoost Classifier**
    - **Evaluasi:** Bandingkan semua parameter performa seperti Accuracy, F1-Score. Pilih yang terbaik.
- **Output yang Diharapkan:**
  - Tabel perbandingan metrik untuk 4 algoritma Regresi.
  - Tabel perbandingan metrik untuk 4 algoritma Klasifikasi.
  - Kesimpulan pemilihan model terbaik untuk disimpan.

### 6\. Analisis Hasil dan Kinerja Individual Parameter

- **Tujuan:** Evaluasi mendalam model terbaik untuk semua parameter.
- **Langkah:**
  - Menampilkan metrik regresi untuk Suhu, Kelembaban, Angin, Tekanan.
  - Menampilkan metrik klasifikasi untuk Kondisi Cuaca (misal: akurasi prediksi "Hujan" vs "Cerah").
- **Output yang Diharapkan:** Tabel kinerja per parameter dan Confusion Matrix untuk prediksi cuaca.

### 7. Penyimpanan Model Terbaik (Single File)

- **Tujuan:** Menyimpan semua model yang telah dilatih ke dalam **SATU file `.pkl`** agar mudah dimuat oleh Backend.
- **Langkah:**
  - Membuat dictionary: `{'regressor': model_reg, 'classifier': model_clf, 'version': '2.0'}`.
  - Menyimpan dictionary tersebut menggunakan `joblib` atau `pickle`.
- **Output yang Diharapkan:** File `weather_model_v2.pkl` tersimpan di folder `models/`.

### 8. Implementasi Multi-Step Forecasting (Recursive Strategy)

- **Tujuan:** Mengatasi masalah "Forecast Horizon" dengan mengimplementasikan fungsi yang dapat memprediksi cuaca untuk rentang waktu di masa depan (misal: 24, 48, atau 72 jam ke depan) berdasarkan data terakhir yang tersedia. Strategi ini memungkinkan pengguna untuk meminta prediksi dari tanggal/jam tertentu ke tanggal/jam di masa depan.
- **Masalah Model Saat Ini:** Model yang dilatih hanya mampu melakukan prediksi *single-step* (memprediksi 1 jam ke depan). Model seperti `Linear Regression` cenderung hanya meniru nilai dari jam sebelumnya (*persistence model*), yang tidak berguna untuk prediksi jangka panjang.
- **Strategi yang Diusulkan: Recursive Forecasting**
  1.  **Model Dasar:** Kita tetap menggunakan model *single-step* yang sudah dilatih.
  2.  **Proses Iteratif:**
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
    1.  Garis data **Aktual** dari *test set* selama 72 jam tersebut (sebagai pembanding/benchmark).
    2.  Garis data **Prediksi Rekursif** yang dihasilkan oleh fungsi.
- **Visualisasi yang Diharapkan:**
  - Grafik yang menunjukkan garis prediksi (misal: merah putus-putus) mencoba mengikuti garis aktual (misal: biru solid).
  - Grafik ini akan secara jelas menunjukkan degradasi performa seiring berjalannya waktu, memberikan wawasan yang jujur tentang kemampuan prediksi jangka panjang model tersebut.

### 10. Visualisasi Dampak Data Inkremental

- **Tujuan:** Demonstrasi konsep _Incremental Learning_.
- **Langkah:** Melatih model dengan pecahan data training (10%, 20%, ... 100%) dan mengukur $R^{2}$ pada data test yang tetap.
- **Visualisasi yang Diharapkan:** Grafik tren naik yang menunjukkan semakin banyak data historis, semakin akurat modelnya.
