Berikut adalah kerangka urutan/struktur _notebook_ `ipynb` untuk melakukan _training_ _dataset_, evaluasi model, dan visualisasi hasil, merujuk pada metodologi dan temuan yang dijelaskan dalam dokumen:

[1-s2.0-S2590005625001018-main-indo.pdf](....\docs\reference\1-s2.0-S2590005625001018-main-indo.pdf)

Berikut adalah visualisasi yang ditampilkan dalam jurnal artikel terkait data _training_ dan perbandingan hasil model, serta kecocokannya dengan kerangka _notebook_ yang Anda rancang:

### Visualisasi dalam Jurnal dan Kecocokan dengan Kerangka Notebook

| Bagian dalam Kerangka Notebook                         | Tujuan Visualisasi (Sesuai Kerangka)                                                                                         | Visualisasi yang Ada dalam Jurnal                                       |
| :----------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| **4. Pelatihan dan Perbandingan Model**                | Tabel Perbandingan Metrik (MSE, MAE, RMSE, R²) untuk semua model.                                                            | **Tabel 4:** _Performance metrics for different regression models_.     |
| **5. Analisis Hasil dan Kinerja Individual Parameter** | Tabel Evaluasi Kinerja (MAE, RMSE,$R^2$) untuk setiap parameter yang diprediksi oleh model terbaik.                          | **Tabel 5:** _Performance evaluation of weather parameter predictions_. |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Suhu.                                      | **Gambar 15:** _Actual vs. Predicted temperature_.                      |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kelembaban.                                | **Gambar 16:** _Actual vs. Predicted humidity_.                         |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kecepatan Angin.                           | **Gambar 17:** _Actual vs. Predicted wind speed_.                       |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Tekanan.                                   | **Gambar 18:** _Actual vs. Predicted pressure_.                         |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Status Hujan.                              | (BELUM ADA)                                                             |
| **6. Visualisasi Perbandingan Aktual vs. Prediksi**    | Output perbandingan visual*Actual vs Predicted* untuk semua fitur yang diprediksi Kondisi Cuaca (Berdasarkan weather_code)). | (BELUM ADA)                                                             |
| **7. Visualisasi Dampak Data Inkremental**             | Grafik garis yang menunjukkan peningkatan skor$R^2$ seiring bertambahnya jumlah _data points_ (_Incremental Learning_).      | **Gambar 21:** _Impact of incremental data on model performance_.       |

**Catatan:** Jurnal tersebut tidak mencantumkan visualisasi eksplisit untuk Pra-pemrosesan Data (seperti distribusi atau korelasi data mentah), tetapi memberikan narasi rinci tentang langkah-langkah _Label Encoding_, _Dropping_ _Null_ _Data_, dan _Filling_ _Null_ _Data_.

## Kerangka Struktur Notebook (`.ipynb`) untuk Pelatihan Model Prediksi Cuaca

### 1\. Persiapan Lingkungan dan Pemuatan Pustaka

- **Tujuan:** Mengimpor semua pustaka Python yang diperlukan untuk pemrosesan data, pelatihan model, evaluasi, dan visualisasi.
- **Pustaka Kunci yang Diperlukan:** `pandas`, `numpy`, `matplotlib`, `seaborn`, `sklearn` (termasuk `train_test_split`, `LabelEncoder`, `LinearRegression`, `DecisionTreeRegressor`, `KNeighborsRegressor`, `RandomForestRegressor`, dan metrik), `joblib` (untuk menyimpan model).
- **Output yang Diharapkan:** Konfirmasi impor pustaka berhasil.

### 2\. Pengumpulan dan Pemuatan Data (Sesuai Bagian 3.1)

- **Tujuan:** Memuat _dataset_ historis gabungan.
- **Langkah:**
  - Memuat data historis [historical_data_hourly.csv](..\data_collections\datasets\historical_data_hourly.csv). Dataset sudah menggunakan timezone Asia/Jakarta. Koordinat Lokasi di Kota Semarang.
  - Memuat data sensor waktu nyata (meskipun hanya data historis yang digunakan untuk pelatihan utama, kerangka kerja harus mencerminkan sumber data).
- **Output yang Diharapkan:** Tampilan beberapa baris pertama _dataset_ (`df.head()`) dan jumlah total catatan.

### 3\. Pra-pemrosesan Data (Sesuai Bagian 3.2)

- **Tujuan:** Membersihkan, menstandarkan, dan mempersiapkan data untuk pelatihan model regresi.
- **Langkah:**
  - **Memilih Kolom:** Memilih kolom fitur yang akan digunakan.
  - **Memformat Pola Data:** Menstandarkan format tanggal yang tidak konsisten
  - **_Label Encoding_**: Mengubah variabel kategori **kondisi cuaca** (_conditions_ dalam format _string_) menjadi nilai numerik, misalnya "0" untuk cerah (_sunny_) dan "1" untuk berawan (_cloudy_), karena model regresi hanya bekerja dengan nilai numerik.
- **Output yang Diharapkan:** Tampilan _dataset_ yang telah bersih dan diformat, siap untuk pelatihan.

### 4\. Pelatihan dan Perbandingan Model (Sesuai Bagian 5.3)

- **Tujuan:** Melatih dan membandingkan empat model regresi untuk memilih yang terbaik.
- **Langkah:**
  - **Definisi Fitur (X) dan Target (Y):** Target adalah variabel kontinu: _temperature_, _humidity_, _wind speed_, dan _atmospheric pressure_. (rencana tambahan untuk isRaining dan Condition klasifikasi)
  - **Pembagian Data:** Membagi data menjadi 80% _training_ dan 20% _testing_.
  - **Pelatihan Model:** Melatih empat model regresi: **Linear Regression, Decision Tree Regressor, K-Nearest Neighbors Regressor,** dan **Random Forest Regressor**.
  - **Evaluasi:** Mengevaluasi kinerja model menggunakan metrik standar: **Mean Squared Error (MSE), Mean Absolute Error (MAE), Root Mean Squared Error (RMSE),** dan **R-squared ($R^{2}$) score** (Akurasi).
- **Output yang Diharapkan:**
  - **Tabel Perbandingan Metrik (Mirip Tabel 4):** Menunjukkan nilai MSE, MAE, RMSE, dan Akurasi ($R^{2}$) untuk setiap model, yang menegaskan **Random Forest Regressor** sebagai model terbaik (MSE: 23.09, MAE: 1.97, RMSE: 4.81, $R^{2}$: 0.908).

### 5\. Analisis Hasil dan Kinerja Individual Parameter (Sesuai Bagian 5.4)

- **Tujuan:** Menampilkan kinerja model terbaik (_Random Forest Regressor_) pada setiap parameter cuaca individual yang diprediksi.
- **Langkah:**
  - Melatih ulang _Random Forest Regressor_ untuk setiap variabel target (_Temperature_, _Humidity_, _Wind speed_, _Pressure_).
  - Menghitung dan mencatat metrik evaluasi (MAE, RMSE, $R^{2}$) untuk setiap parameter.
- **Output yang Diharapkan:**
  - **Tabel Evaluasi Kinerja Parameter (Mirip Tabel 5):** Menunjukkan MAE, RMSE, dan $R^{2}$ untuk **Suhu** ($R^{2}=0.91$), **Kelembaban** ($R^{2}=0.88$), **Kecepatan Angin** ($R^{2}=0.87$), dan **Tekanan** ($R^{2}=0.89$).
  - Visualisasi perbandingan menggunakan library pyhon untuk barplot.

### 6. Penyimpanan Model Terbaik

- **Tujuan:** Menyimpan model _Random Forest Regressor_ yang telah dilatih dan dianggap terbaik untuk digunakan pada _backend_ (FastAPI) ([weatherapp_backend](..\weatherapp_backend\main.py)).
- **Langkah:** Menyimpan objek model terbaik ke dalam file **`.pkl`** menggunakan `joblib` atau `pickle`.
- **Output yang Diharapkan:** Konfirmasi model terbaik telah disimpan ke satu file **`.pkl/_pkl`**.

### 7. Visualisasi Perbandingan Aktual vs. Prediksi (Sesuai Bagian 5.3)

- **Tujuan:** Memvisualisasikan seberapa dekat nilai yang diprediksi oleh model terbaik (Random Forest) dengan nilai aktual untuk periode data uji.
- **Langkah:** Membuat plot garis terpisah untuk setiap parameter cuaca yang diprediksi. Periode yang divisualisasikan dalam dokumen adalah **Januari 2020**. (Tampilkan label tanggal pada grafik sumbu x dengan jeda setiap 4 hari). data yang divisualisasikan adalah per-hari.
- **Visualisasi yang Diharapkan:**
  - **Grafik 1 (Mirip Gambar 15):** **Actual vs Predicted Temperature** (Garis biru untuk Aktual, Garis merah putus-putus untuk Prediksi).
  - **Grafik 2 (Mirip Gambar 16):** **Actual vs Predicted Humidity** (Garis biru untuk Aktual, Garis merah putus-putus untuk Prediksi).
  - **Grafik 3 (Mirip Gambar 17):** **Actual vs Predicted Wind Speed** (Garis biru untuk Aktual, Garis merah putus-putus untuk Prediksi).
  - **Grafik 4 (Mirip Gambar 18):** **Actual vs Predicted Pressure** (Garis biru untuk Aktual, Garis merah putus-putus untuk Prediksi).

### 8. Visualisasi Dampak Data Inkremental (Sesuai Bagian 5.6)

- **Tujuan:** Menunjukkan bagaimana akurasi model meningkat seiring bertambahnya jumlah _data points_ untuk mendukung pendekatan _Incremental Learning_.
- **Visualisasi yang Diharapkan:**
  - **Grafik 5 (Mirip Gambar 21):** Grafik garis yang menunjukkan peningkatan skor $R^{2}$ (%) seiring bertambahnya jumlah _Data Points_.
