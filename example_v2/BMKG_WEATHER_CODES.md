#  BMKG Weather Codes Reference

Berikut adalah daftar kode cuaca (Weather Code) standar yang digunakan oleh BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) dalam format Open Data mereka.

| Kode         | Kondisi Cuaca (ID) | Kondisi Cuaca (EN)  | Deskripsi Singkat                                  |
| :----------- | :----------------- | :------------------ | :------------------------------------------------- |
| **0**  | Cerah              | Clear Skies         | Langit bersih, minim awan.                         |
| **1**  | Cerah Berawan      | Partly Cloudy       | Sebagian langit tertutup awan.                     |
| **2**  | Cerah Berawan      | Partly Cloudy       | Variasi dari cerah berawan.                        |
| **3**  | Berawan            | Mostly Cloudy       | Awan mendominasi langit.                           |
| **4**  | Berawan Tebal      | Overcast            | Langit tertutup awan tebal/mendung.                |
| **5**  | Udara Kabur        | Haze                | Partikel kering di udara mengurangi jarak pandang. |
| **10** | Asap               | Smoke               | Akibat pembakaran, mengurangi jarak pandang.       |
| **45** | Kabut              | Fog                 | Uap air terkondensasi dekat tanah.                 |
| **60** | Hujan Ringan       | Light Rain          | Intensitas rendah.                                 |
| **61** | Hujan Sedang       | Moderate Rain       | Intensitas sedang.                                 |
| **63** | Hujan Lebat        | Heavy Rain          | Intensitas tinggi.                                 |
| **80** | Hujan Lokal        | Isolated Shower     | Hujan di area terbatas/singkat.                    |
| **95** | Hujan Petir        | Severe Thunderstorm | Hujan disertai kilat/petir.                        |
| **97** | Hujan Petir        | Severe Thunderstorm | Variasi hujan petir.                               |

## Catatan Implementasi

* **Klasifikasi**: Gunakan kode ini sebagai label (target) untuk model klasifikasi `weather_classifier`.
* **Mapping**: Pastikan output prediksi model dikonversi kembali ke teks (ID/EN) menggunakan tabel ini untuk ditampilkan di Frontend/API.
