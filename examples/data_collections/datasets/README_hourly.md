# Historical Weather Data (Hourly) - Dataset Description

## Overview

This dataset contains hourly weather observations for Semarang, Indonesia from January 1, 2000 to December 4, 2025.

## Source

- **API**: Open-Meteo Archive API (`archive-api.open-meteo.com`)
- **Location**: Semarang, Central Java, Indonesia
- **Coordinates**: -7.0520702239386175, 110.43532807750137
- **Timezone**: Asia/Jakarta (UTC+7)

## Dataset Statistics

- **Total Records**: 227,280 hourly observations
- **Date Range**: January 1, 2000 - December 4, 2025
- **File Size**: ~11.7 MB

## Columns

| Column             | Type   | Description              | Range/Values |
| ------------------ | ------ | ------------------------ | ------------ |
| `id`               | int    | Unique identifier        | 0 - 227,279  |
| `hour`             | int    | Hour of day (local time) | 0 - 23       |
| `day`              | int    | Day of month             | 1 - 31       |
| `month`            | int    | Month                    | 1 - 12       |
| `year`             | int    | Year                     | 2000 - 2025  |
| `temp`             | float  | Temperature (°C)         | ~18 - 38     |
| `humidity`         | int    | Relative Humidity (%)    | 0 - 100      |
| `windspeed`        | float  | Wind Speed (km/h)        | 0 - ~50      |
| `sealevelpressure` | float  | Sea Level Pressure (hPa) | ~1000 - 1020 |
| `weather_code`     | int    | WMO Weather Code         | 0 - 65       |
| `conditions`       | string | Weather Condition Label  | See below    |

## Weather Code Mapping

| Code       | Condition              |
| ---------- | ---------------------- |
| 0          | Clear                  |
| 1, 2       | Partially cloudy       |
| 3          | Overcast               |
| 51, 53, 55 | Rain (Drizzle)         |
| 61, 63, 65 | Rain, Overcast         |
| 80, 81, 82 | Rain, Partially cloudy |
| 95, 96, 99 | Rain (Thunderstorm)    |

## Usage Example

```python
import pandas as pd

df = pd.read_csv('historical_data_hourly.csv')
print(df.head())
```
