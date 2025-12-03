# Notebook Output Path Updates

## ✅ Changes Made

### 1. `weather_model_training_hourly.ipynb`

**Model Paths Updated**:
```python
# Before
with open('rf_model_hourly_pkl', 'wb') as f:
    pickle.dump(rf_model_final, f)

# After
with open('../models/rf_model_hourly_pkl', 'wb') as f:
    pickle.dump(rf_model_final, f)
```

**Visualization Paths Updated**:
```python
# Before
plt.savefig('hourly_actual_vs_predicted.png', dpi=150)
plt.savefig('hourly_feature_importance.png', dpi=150)
plt.savefig('hourly_timeseries_7days.png', dpi=150)
plt.savefig('hourly_72hour_forecast.png', dpi=150)

# After  
plt.savefig('../outputs/hourly_actual_vs_predicted.png', dpi=150)
plt.savefig('../outputs/hourly_feature_importance.png', dpi=150)
plt.savefig('../outputs/hourly_timeseries_7days.png', dpi=150)
plt.savefig('../outputs/hourly_72hour_forecast.png', dpi=150)
```

---

### 2. `weather_model_training.ipynb`

**Model Paths Updated**:
```python
# Before
with open('rf_model_pkl', 'wb') as f:

# After
with open('../models/rf_model_pkl', 'wb') as f:
```

**Visualization Paths Updated**:
```python
# Before
plt.savefig('actual_vs_predicted.png', dpi=150)
plt.savefig('residual_analysis.png', dpi=150)
plt.savefig('feature_importance.png', dpi=150)
plt.savefig('time_series_comparison.png', dpi=150)
plt.savefig('7day_forecast.png', dpi=150)
plt.savefig('72hour_forecast.png', dpi=150)

# After
plt.savefig('../outputs/actual_vs_predicted.png', dpi=150)
plt.savefig('../outputs/residual_analysis.png', dpi=150)
plt.savefig('../outputs/feature_importance.png', dpi=150)
plt.savefig('../outputs/time_series_comparison.png', dpi=150)
plt.savefig('../outputs/7day_forecast.png', dpi=150)
plt.savefig('../outputs/72hour_forecast.png', dpi=150)
```

---

### 3. `import_weather.ipynb`

**Status**: ✅ Already correct - no changes needed

The import notebook saves data to `semarang_weather_2010_2025.csv` in the `data_collections/` directory, which is correct.

---

## 📁 New Output Structure

When notebooks are run from `notebooks/` directory:

```
model_training/
├── notebooks/                    # <-- Run notebooks from here
│   ├── weather_model_training.ipynb
│   └── weather_model_training_hourly.ipynb
│
├── models/                       # <-- Models saved here
│   ├── rf_model_pkl
│   └── rf_model_hourly_pkl
│
└── outputs/                      # <-- Visualizations saved here
    ├── actual_vs_predicted.png
    ├── hourly_72hour_forecast.png
    └── ... (all PNG files)
```

## 🎯 Benefits

1. **Clean Organization**: All outputs in proper directories
2. **No Clutter**: Notebook directory stays clean
3. **Easy to Find**: Models and outputs have dedicated locations
4. **Git-Friendly**: Easy to ignore large files via .gitignore

## 🚀 Usage

Simply run the notebooks as normal from `notebooks/` directory:

```bash
cd examples/model_training/notebooks
jupyter notebook weather_model_training_hourly.ipynb
```

All outputs will automatically be saved to the correct directories!

---

**Updated**: 2025-11-27  
**Script**: `utils/update_notebook_paths.py`
