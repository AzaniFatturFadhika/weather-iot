# Model Usage Guide v4.0 (Date-Based Seasonality)

This guide documents the usage of the **v4.0 Weather Prediction Model**, which uses a **Direct Date Mapping** strategy. Unlike previous versions, this model does NOT require lag features (e.g., "temperature 1 hour ago") as inputs. It predicts weather conditions solely based on time components (`day`, `month`, `year`, `hour`), making it ideal for forecasting future dates where prior sensor data is unavailable.

## 1. Model Artifacts

| File Name | Path | Description |
| :--- | :--- | :--- |
| **Combined Model** | `models/v4_weather_model_combined.pkl` | Contains both Hourly and Daily models, plus LabelEncoders. |

### 1.1 Internal Structure (`combined_package`)
The `.pkl` file is a dictionary acting as a single container for all components:

```python
combined_package = {
    'hourly': {
        'regressor': <RandomForestRegressor>,
        'classifier': <RandomForestClassifier>,
        'feature_columns': ['day', 'month', 'year', 'hour'],
        'target_regression': ['temp', 'humidity', 'windspeed', 'sealevelpressure'],
        'target_classification': 'conditions' # Encoded
    },
    'daily': {
        'regressor': <RandomForestRegressor>,
        'classifier': <RandomForestClassifier>,
        'feature_columns': ['day', 'month', 'year'],
        'target_regression': ['temp_min', 'temp_max', 'temp_mean', ...],
        'target_classification': 'conditions_dominant' # Encoded
    },
    'label_encoder_hourly': <LabelEncoder>, # For Hourly 'conditions'
    'label_encoder_daily': <LabelEncoder>,  # For Daily 'conditions_dominant'
    'version': '4.0',
    'trained_date': '...'
}
```

---

## 2. Loading the Model

```python
import joblib
import pandas as pd
import numpy as np

# Load the package
model_path = 'models/v4_weather_model_combined.pkl'
model_pkg = joblib.load(model_path)

print(f"Loaded Standard v{model_pkg['version']} Model")
```

---

## 3. Making Predictions (Hourly)

To predict hourly weather, you only need to provide the target timestamp.

### Step 3.1: Prepare Input Data
Create a DataFrame with `day`, `month`, `year`, `hour`.

```python
from datetime import datetime, timedelta

# Example: Predict next 24 hours from Now
start_time = datetime.now()
future_dates = [start_time + timedelta(hours=i) for i in range(24)]

# Create Input DataFrame
X_input = pd.DataFrame({
    'day': [d.day for d in future_dates],
    'month': [d.month for d in future_dates],
    'year': [d.year for d in future_dates],
    'hour': [d.hour for d in future_dates]
})

# Ensure column order matches training
hourly_features = model_pkg['hourly']['feature_columns'] # ['day', 'month', 'year', 'hour']
X_input = X_input[hourly_features] 
```

### Step 3.2: Run Inference
Use the Regressor for numerical values and Classifier for weather conditions.

```python
# Extract models
h_reg = model_pkg['hourly']['regressor']
h_clf = model_pkg['hourly']['classifier']

# 1. Predict Regression Targets (Temp, Humidity, etc.)
# Returns shape (n_samples, 4) -> ['temp', 'humidity', 'windspeed', 'pressure']
pred_reg = h_reg.predict(X_input)

# 2. Predict Classification Target (Condition Code)
pred_clf_encoded = h_clf.predict(X_input)
```

### Step 3.3: Decode Results
Convert the integer class labels back to readable strings (e.g., 0 -> "Clear", 1 -> "Rain").

```python
# Extract Encoder
le_hourly = model_pkg['label_encoder_hourly']

# Decode
pred_conditions = le_hourly.inverse_transform(pred_clf_encoded.astype(int))

# Combine into readable Table
results = pd.DataFrame({
    'Time': future_dates,
    'Temp (C)': pred_reg[:, 0],
    'Humidity (%)': pred_reg[:, 1],
    'Wind (km/h)': pred_reg[:, 2],
    'Pressure (hPa)': pred_reg[:, 3],
    'Condition': pred_conditions
})

print(results.head())
```

---

## 4. Making Predictions (Daily)

Daily prediction works identically but uses `day`, `month`, `year` (no hour).

```python
# 1. Prepare Features
target_date = datetime(2023, 12, 25) # Example
X_daily = pd.DataFrame([{
    'day': target_date.day,
    'month': target_date.month,
    'year': target_date.year
}])

# 2. Predict
d_reg = model_pkg['daily']['regressor']
d_clf = model_pkg['daily']['classifier']
le_daily = model_pkg['label_encoder_daily']

pred_vals = d_reg.predict(X_daily)[0] # [min, max, mean, humid, wind, press]
pred_class = d_clf.predict(X_daily)[0]

# 3. Decode
condition_name = le_daily.inverse_transform([int(pred_class)])[0]

print(f"Forecast for {target_date.date()}: {condition_name}")
print(f"Temp Range: {pred_vals[0]:.1f}C - {pred_vals[1]:.1f}C")
```

---

## 5. Using the GUI

A graphical interface is available for easy testing: `weather_prediction_gui_v4.py`.

1.  Run the script: `python weather_prediction_gui_v4.py`
2.  Click **Browse** to select `models/v4_weather_model_combined.pkl`.
3.  Click **Load**.
4.  Select a **Date Range** (From/To).
5.  Click **Generate Prediction**.
6.  The table will populate with the forecast. You can export it to CSV.
