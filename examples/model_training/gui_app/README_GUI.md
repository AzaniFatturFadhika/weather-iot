# Weather Prediction GUI Application

Simple desktop application untuk menampilkan prediksi cuaca menggunakan model ML yang sudah dilatih.

## Features

- 📅 **Date/Time Range Selector**: Pilih range waktu prediksi (from/to)
- 📊 **Data Table View**: Tampilan tabel prediksi detail per jam
- 📈 **Interactive Charts**: Visualisasi grafik untuk Temperature, Humidity, Wind Speed, Rain
- 💾 **Export Data**: Export hasil prediksi ke CSV atau JSON
- 🎨 **Modern UI**: Interface yang user-friendly dengan tkinter

## Requirements

Install dependencies:
```bash
pip install -r requirements_gui.txt
```

## Usage

1. **Pastikan model sudah dilatih**:
   - Jalankan notebook `weather_model_training_hourly.ipynb`
   - File `rf_model_hourly_pkl` harus ada di folder yang sama

2. **Jalankan aplikasi**:
   ```bash
   python weather_prediction_gui.py
   ```

3. **Cara menggunakan**:
   - Set tanggal/jam **FROM** (mulai)
   - Set tanggal/jam **TO** (selesai)
   - Klik **Generate Predictions**
   - Lihat hasil di tabel dan grafik
   - Export data jika diperlukan (CSV/JSON)

## Screenshots

### Main Interface
- Left panel: Tabel data prediksi per jam
- Right panel: 4 grafik (Temperature, Humidity, Wind, Rain)
- Top: Control panel untuk memilih range waktu

### Example Usage
```
FROM: 2025-11-27 18:00
TO:   2025-11-30 17:00
Result: 72 hours (3 days) of hourly predictions
```

## Notes

- Maximum recommended range: 30 days (~720 hours)
- Predictions based on `hour`, `day`, `month`, `year` features
- Model outputs: `temperature`, `humidity`, `pressure`, `wind_speed`, `rain`

## Troubleshooting

**Model not found error:**
- Pastikan file `rf_model_hourly_pkl` ada di folder yang sama dengan script
- Atau set path model di line 30 script

**Date format error:**
- Gunakan format: `YYYY-MM-DD` (contoh: `2025-11-27`)
- Hour range: 0-23

