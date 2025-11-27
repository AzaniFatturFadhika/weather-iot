# Model Training - Outputs

This directory contains all visualization outputs generated during model training and evaluation.

## 📊 Files

### Daily Model Outputs
- `actual_vs_predicted.png` - Scatter plots comparing actual vs predicted values
- `residual_analysis.png` - Histogram of prediction errors
- `feature_importance.png` - Importance of day/month/year features
- `time_series_comparison.png` - 100-day comparison of predictions
- `7day_forecast.png` - 7-day weather forecast visualization

### Hourly Model Outputs
- `hourly_actual_vs_predicted.png` - Actual vs predicted for hourly data
- `hourly_feature_importance.png` - Hour/day/month/year feature importance
- `hourly_timeseries_7days.png` - 7-day hourly comparison
- `hourly_72hour_forecast.png` - 72-hour (3-day) detailed forecast

## 🎯 Usage

These visualizations are automatically generated when running the training notebooks.

To regenerate:
```bash
jupyter notebook ../notebooks/weather_model_training.ipynb
# or
jupyter notebook ../notebooks/weather_model_training_hourly.ipynb
```

## 📌 Notes

- PNG files are high resolution (150 DPI) suitable for reports/presentations
- File sizes range from 35KB to 650KB
- All plots use consistent color schemes for easy interpretation
