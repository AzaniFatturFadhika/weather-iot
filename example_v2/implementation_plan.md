# Implementation Plan - Example V2: Hourly Weather Prediction

**Goal**: Create a synchronized system for hourly weather prediction, ensuring compatibility between the training notebook and the backend API.

## User Review Required
> [!IMPORTANT]
> **Model Architecture Change**: We will split the single model into two separate models:
> 1.  **Regressor**: For continuous variables (`temp`, `humidity`, `wind_speed`, `pressure`).
> 2.  **Classifier**: For categorical variable (`conditions`).
> This ensures accurate weather condition predictions (e.g., "Rain", "Clear") instead of rounding regression outputs.

> [!WARNING]
> **API Breaking Change**: The endpoint `/weather-data/get-predicted-data` will be updated to support hourly queries. The response structure might change slightly to accommodate hourly data points.

## Proposed Changes

## Proposed Changes

### 1. Data Processing & Dataset (`example_v2/data_processing/import_dataset_hourly.ipynb`)
*   **Synchronization**: Ensure the script fetches data for coordinates **-7.052, 110.435** (Semarang/Central Java).
*   **Timezone**: Convert all timestamps to **Asia/Jakarta**.
*   **Features**: Explicitly select columns: `timestamp`, `temperature` (temp), `humidity`, `sealevelpressure` (pressure), `windspeed`, `weathercode`.
*   **Output**: Ensure `historical_data_hourly.csv` follows this structure strictly.

### 2. Model Training (`example_v2/model_training/weather_model_training_advanced.ipynb`)
*   **Input Features**: `['year', 'month', 'day', 'hour']`.
*   **Target Variables**:
    *   **Hourly Regression**: `['temp', 'humidity', 'wind_speed', 'pressure']`.
    *   **Hourly Classification**: `['condition_encoded']` (derived from `weathercode`).
    *   **Daily Aggregation**: Calculate `temp_min` and `temp_max` per day from the hourly data to train a separate model OR use the hourly model to predict 24 hours and aggregate the result (Preferred for consistency).
*   **Model Architecture**:
    *   `regressor`: RandomForestRegressor for continuous variables.
    *   `classifier`: RandomForestClassifier for weather codes.
*   **Storage (CRITICAL)**: Save **ALL** models into a **SINGLE .pkl file** (`weather_model_v2.pkl`).
    *   Structure: `{'regressor': model_reg, 'classifier': model_clf, 'version': '2.0'}`.

### 3. Backend API (`example_v2/backend/main.py`)
*   **Model Loading**: Update to load the dictionary from `weather_model_v2.pkl` and access `['regressor']` and `['classifier']`.
*   **Endpoint `/weather-data/get-predicted-data`**:
    *   **Parameters**: `day`, `month`, `year`, optional `hour`.
    *   **Logic**:
        *   Generate feature vectors for the requested time range (e.g., next 24 hours).
        *   **Predict**: Run both Regressor and Classifier.
        *   **Aggregate**: Calculate `min_temp` and `max_temp` from the 24-hour predictions for the daily summary.
    *   **Response**: Return a JSON structure containing:
        *   `daily`: `{'min_temp': ..., 'max_temp': ...}`
        *   `hourly`: List of objects `{'hour': ..., 'temp': ..., 'conditions': ...}`.
*   **Future Proofing**: Structure the code to allow easy integration of an *Incremental Learning* module later (e.g., modularize the prediction logic).

## Verification Plan

### Automated Tests
*   **Notebook Execution**: Run `weather_model_training_advanced.ipynb` to ensure it runs without errors and produces the `.pkl` files.
*   **API Test**:
    *   Start the FastAPI server (`uvicorn example_v2.backend.main:app`).
    *   Send GET request to `/weather-data/get-predicted-data?day=...&month=...&year=...`.
    *   Verify response contains valid hourly data and correct weather conditions.

### Manual Verification
*   Inspect the generated `.pkl` files size and existence.
*   Check the API response JSON structure against the requirement.
