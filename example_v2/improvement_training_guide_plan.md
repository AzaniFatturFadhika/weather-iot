

poin penting:

1. Proses Data Splitting (Time-Series): gunakan E**xpanding Window Cross-Validation** atau  **Rolling Window Cross-Validation** .
2. Kesimpulan & Rekomendasi:

   a. Untuk  **Klasifikasi Hourly** :  **Perlu Perbaikan** . Belum layak untuk kebutuhan kritis.

   b. Untuk  **Daily** :  **Cukup** , namun anomali di mana model Linear mengalahkan Non-Linear perlu diperhatikan (bisa jadi fitur lag harian perlu ditambah window-nya, misal 3 hari atau 7 hari rata-rata).
3. Perbaiki Klasifikasi (Prioritas Utama): Gunakan teknik **Class Balancing** (seperti class_weight='balanced' pada model atau teknik SMOTE) karena kejadian cuaca ekstrem (hujan lebat) pasti jarang terjadi (minoritas).
4. Feature Engineering Lanjutan:

   a. Tambahkan fitur waktu siklikal (Cyclical Time Features) seperti Sin/Cos untuk Jam dan Bulan agar model mengerti bahwa jam 23.00 dekat dengan jam 00.00.

   b. (opsional) Tambahkan Interaction Features, contoh: Dew Point (Titik Embun) yang dihitung dari Suhu dan Kelembapan.
5. Gunakan Prophet atau LSTM (Opsional):

   a. Untuk data Daily, model khusus time-series seperti **Facebook Prophet** atau **LSTM (Long Short-Term Memory)** seringkali menangkap pola musiman (seasonality) lebih baik daripada regresi biasa.

---

Poin-poin yang Anda rangkum  **sudah sangat tepat dan strategis** . Rangkuman ini pada dasarnya adalah "peta jalan" (roadmap) untuk mengubah proyek hobi/akademis menjadi standar industri ( *production-grade* ).

Berikut adalah analisis saya mengenai mengapa poin-poin tersebut krusial dan bagaimana cara eksekusinya agar efektif pada notebook Anda:

### 1. Data Splitting: Expanding Window Cross-Validation

Mengapa ini game changer?

Metode split 80-20 yang sederhana (hold-out) memiliki risiko bias. Bisa jadi 20% data terakhir adalah musim kemarau panjang, sehingga model terlihat sangat akurat padahal hanya menebak "tidak hujan".

* **Implementasi:** Gunakan `TimeSeriesSplit` dari Scikit-learn.
* **Ilustrasi:**
  * *Iterasi 1:* Train: Jan-Mar, Test: Apr
  * *Iterasi 2:* Train: Jan-Apr, Test: Mei
  * *Iterasi 3:* Train: Jan-Mei, Test: Jun
* **Benefit:** Anda akan mendapatkan rata-rata performa yang lebih jujur terhadap perubahan musim.

### 2. Analisis Anomali Model Daily (Linear vs. Non-Linear)

Mengapa Linear menang?

Ini adalah fenomena umum pada data yang agregat-nya tinggi. Rata-rata harian seringkali membuang noise, sehingga hubungan antar variabel menjadi lebih mulus (linear).

* **Saran Aksi:** Jika Anda ingin XGBoost/Random Forest mengalahkan Linear Regression, Anda harus memberikan konteks  **temporal yang lebih panjang** .
  * Tambahkan `rolling_mean_3d` (rata-rata 3 hari terakhir).
  * Tambahkan `rolling_mean_7d` (rata-rata 1 minggu terakhir).
  * Ini membantu model non-linear menangkap pola tren jangka pendek, bukan hanya korelasi instan.

### 3. Perbaikan Klasifikasi (Prioritas Utama: Class Balancing)

Ini adalah poin paling kritis.

Dalam kasus cuaca, False Negative (model memprediksi cerah, ternyata badai) jauh lebih berbahaya daripada False Positive.

* **Solusi Termudah:** Pada `XGBClassifier` atau `RandomForestClassifier`, tambahkan parameter `scale_pos_weight` (untuk XGBoost) atau `class_weight='balanced'` (untuk RF/Logistic Reg). Ini memaksa model untuk memberi "denda" lebih besar jika salah memprediksi hujan lebat.
* **Solusi Lanjutan:** Jika `class_weight` belum cukup, gunakan teknik **SMOTE** (Synthetic Minority Over-sampling Technique) hanya pada data *Training* untuk memperbanyak contoh data hujan lebat secara sintetis.

### 4. Feature Engineering Lanjutan

Ini adalah cara paling efektif meningkatkan akurasi tanpa mengganti model.

a. Cyclical Features (Sin/Cos)

Jam 23:00 dan 00:00 itu dekat, tapi bagi model matematika, angka 23 dan 0 itu jauh.

* **Implementasi Python:**
  **Python**

  ```
  import numpy as np
  df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
  df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
  # Lakukan hal yang sama untuk 'month' (pembagi 12)
  ```

b. Interaction Features (Fisika Atmosfer)

Model ML butuh bantuan untuk memahami fisika.

* **Dew Point (Titik Embun):** Indikator kuat untuk hujan. Jika *Dew Point* dekat dengan  *Temperature* , kelembapan tinggi dan hujan sangat mungkin terjadi.
  * Rumus pendekatan sederhana: **$T_{dew} = T - ((100 - RH)/5)$**
* **Temperature Difference:** `temp_max - temp_min` (Rentang suhu harian). Rentang kecil biasanya indikasi cuaca mendung/hujan, rentang besar indikasi cerah.

### 5. Prophet atau LSTM

**Kapan harus pindah ke sini?**

* Gunakan **Prophet** jika Anda ingin melihat *seasonality* tahunan dengan jelas (misal: tren hujan selalu naik di bulan Desember-Februari). Prophet sangat kuat menangubani *outlier* dan  *missing data* .
* Gunakan **LSTM** jika Anda memiliki data *Hourly* yang sangat panjang dan ingin memprediksi urutan kejadian (misal: jika 3 jam lalu mendung, 2 jam lalu gerimis, 1 jam lalu hujan ringan -> maka jam ini hujan lebat). Namun, LSTM butuh *tuning* yang jauh lebih rumit dan waktu training lama.

---

### **Rekomendasi Urutan Pengerjaan**

Jika Anda ingin merevisi notebook ini untuk portofolio atau implementasi nyata, kerjakan dengan urutan prioritas ini (berdasarkan dampak terbesar vs usaha termudah):

1. **Feature Engineering:** Tambahkan Sin/Cos time dan Dew Point. (Usaha: Rendah, Dampak: Tinggi).
2. **Class Balancing:** Tambahkan parameter weight pada model klasifikasi. (Usaha: Sangat Rendah, Dampak: Sangat Tinggi untuk kasus hujan).
3. **Expanding Window CV:** Ubah cara evaluasi agar lebih valid. (Usaha: Menengah, Dampak: Validasi menjadi robust).
4. **Hyperparameter Tuning:** Baru setelah fitur dan evaluasi benar, optimalkan parameter model XGBoost/RF Anda.

Kesimpulannya, rencana Anda sudah sangat matang dan menyentuh aspek-aspek vital dalam  *Time-Series Machine Learning* .
