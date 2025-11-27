# Model Training Directory

This directory contains all resources for weather prediction model training and deployment.

## 📁 Directory Structure

```
model_training/
├── 📓 notebooks/           # Jupyter notebooks for model training
│   ├── weather_model_training.ipynb          # Daily aggregated model
│   └── weather_model_training_hourly.ipynb   # Hourly model (recommended)
│
├── 🤖 models/              # Trained ML models
│   ├── rf_model_pkl                # Daily model (RandomForest)
│   └── rf_model_hourly_pkl         # Hourly model (RandomForest)
│
├── 🖥️ gui_app/             # Desktop GUI application
│   ├── weather_prediction_gui.py   # Main GUI application
│   ├── requirements_gui.txt        # Dependencies
│   └── README_GUI.md               # GUI documentation
│
├── 📊 outputs/             # Training outputs & visualizations
│   ├── actual_vs_predicted.png
│   ├── feature_importance.png
│   ├── residual_analysis.png etc
│   ├── time_series_comparison.png
│   ├── 7day_forecast.png
│   ├── 72hour_forecast.png
│   └── ... (all visualization outputs)
│
└── 🛠️ utils/               # Utility scripts
    └── add_hourly_cells.py         # Notebook cell generator

```

## 🚀 Quick Start

### 1. Train Model (Hourly)

```bash
# Open and run the hourly notebook
jupyter notebook notebooks/weather_model_training_hourly.ipynb
```

**Output**: `models/rf_model_hourly_pkl`

### 2. Run GUI Application

```bash
cd gui_app
pip install -r requirements_gui.txt
python weather_prediction_gui.py
```

## 📝 Notebooks

### Daily Model (`weather_model_training.ipynb`)
- Trains on **daily aggregated** data
- Features: `[day, month, year]`
- Outputs: 7 weather parameters
- Use case: Daily forecasts

### Hourly Model (`weather_model_training_hourly.ipynb`) ⭐ **Recommended**
- Trains on **raw hourly** data
- Features: `[hour, day, month, year]`
- Outputs: 5 weather parameters (temp, humidity, pressure, wind, rain)
- Use case: Hourly forecasts, detailed predictions

## 📊 Model Outputs

Both models generate comprehensive visualizations in `outputs/`:
- Actual vs Predicted scatter plots
- Residual analysis
- Feature importance
- Time series comparisons
- Forecast visualizations

## 🖥️ GUI Application

Desktop application for interactive weather prediction.

**Features**:
- Date/time range selector (FROM/TO)
- Real-time prediction generation
- Interactive charts (Temperature, Humidity, Wind, Rain)
- Data table view
- Export to CSV/JSON

**See**: `gui_app/README_GUI.md` for detailed instructions.

## 📦 Requirements

### Notebooks
```bash
pandas, numpy, scikit-learn, matplotlib, seaborn, pickle
```

### GUI App
```bash
pip install -r gui_app/requirements_gui.txt
```

## 🎯 Workflow

1. **Collect Data** → `../data_collections/semarang_weather_2010_2025.csv`
2. **Train Model** → Run notebook → Save to `models/`
3. **Use Predictions** → Run GUI app or integrate model into backend
4. **View Results** → Check `outputs/` for visualizations

## 📌 Notes

- **Model Size**: Hourly model ~300MB, Daily model ~88MB
- **Training Time**: ~5-15 minutes depending on hardware
- **Prediction Speed**: Real-time (< 1ms per hour)
- **Accuracy**: Check R² scores in notebook outputs (typically > 0.85)

## 🔧 Troubleshooting

**Model file not found**:
- Ensure you've run the notebook completely
- Check `models/` directory for `.pkl` files

**Import errors**:
- Install dependencies: `pip install -r gui_app/requirements_gui.txt`

**Large file warnings**:
- Models are large (300MB) - this is normal for RandomForest on large datasets
- Consider using Git LFS if pushing to repository

---

**Last Updated**: 2025-11-27
