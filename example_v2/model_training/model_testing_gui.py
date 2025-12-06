# -*- coding: utf-8 -*-
"""
Weather Model Testing GUI v1
============================
GUI untuk model cuaca yang di-training dengan Lag & Rolling Features.
Sesuai dengan MODEL_USAGE_GUIDE.md.

FITUR MODEL:
- Hourly (13 fitur): hour, month, temp_lag_*, humidity_lag_*, windspeed_lag_*, pressure_lag_*, rolling_24
- Daily (12 fitur): month, day, temp_*_lag_1, temp_*_lag_7, humidity_avg_lag_1, rain_total_lag_1

Requirements:
    pip install joblib numpy pandas tkcalendar
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

# ===================== CONSTANTS =====================
WEATHER_CODE_TO_RAIN = {
    0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0,
    51: 0.2, 53: 0.7, 55: 1.1,
    61: 1.7, 63: 4.0, 65: 10.3
}

WEATHER_CODE_TO_CONDITION = {
    0: 'Clear', 1: 'Partially Cloudy', 2: 'Partially Cloudy', 3: 'Overcast',
    51: 'Light Rain', 53: 'Moderate Rain', 55: 'Heavy Showers',
    61: 'Rain, Overcast', 63: 'Rain, Overcast', 65: 'Heavy Rain'
}

# Default model path (v1)
DEFAULT_MODEL_PATH = r'models/weather_model_combined.pkl'

class WeatherModelGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Model Testing GUI v1 (Lag/Rolling Features)")
        self.root.geometry("1000x800")
        
        self.model = None
        self.model_path = DEFAULT_MODEL_PATH
        self.predictions_cache = []
        
        # --- Expected Features (from MODEL_USAGE_GUIDE.md) ---
        self.hourly_features = [
            'hour', 'month',
            'temp_lag_1', 'temp_lag_24', 'temp_rolling_24',
            'humidity_lag_1', 'humidity_lag_24', 'humidity_rolling_24',
            'windspeed_lag_1', 'windspeed_lag_24', 'windspeed_rolling_24',
            'sealevelpressure_lag_1', 'sealevelpressure_lag_24'
        ]
        
        self.daily_features = [
            'month', 'day',
            'temp_min_lag_1', 'temp_max_lag_1', 'temp_mean_lag_1',
            'humidity_avg_lag_1', 'windspeed_avg_lag_1', 'pressure_avg_lag_1',
            'temp_min_lag_7', 'temp_max_lag_7', 'temp_mean_lag_7',
            'rain_total_lag_1'
        ]
        
        # Default values for recursive forecast (baseline)
        self.default_hourly = {
            'hour': 0, 'month': 1,
            'temp_lag_1': 28.5, 'temp_lag_24': 27.0, 'temp_rolling_24': 27.5,
            'humidity_lag_1': 75, 'humidity_lag_24': 78, 'humidity_rolling_24': 76,
            'windspeed_lag_1': 5.0, 'windspeed_lag_24': 5.5, 'windspeed_rolling_24': 5.2,
            'sealevelpressure_lag_1': 1010.5, 'sealevelpressure_lag_24': 1011.0
        }
        self.default_daily = {
            'month': 1, 'day': 1,
            'temp_min_lag_1': 22.5, 'temp_max_lag_1': 31.0, 'temp_mean_lag_1': 26.5,
            'humidity_avg_lag_1': 78, 'windspeed_avg_lag_1': 5.5, 'pressure_avg_lag_1': 1010.0,
            'temp_min_lag_7': 22.0, 'temp_max_lag_7': 30.5, 'temp_mean_lag_7': 26.0,
            'rain_total_lag_1': 2.5
        }
        
        self.create_widgets()
        
        if os.path.exists(self.model_path):
            self.load_model(self.model_path)

    def create_widgets(self):
        # Top: Model Selection
        model_frame = ttk.LabelFrame(self.root, text="Model Configuration")
        model_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(model_frame, text="Model:").pack(side='left', padx=5)
        self.path_var = tk.StringVar(value=self.model_path)
        ttk.Entry(model_frame, textvariable=self.path_var, width=60).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(model_frame, text="Browse", command=self.browse_model).pack(side='left', padx=5)
        ttk.Button(model_frame, text="Load", command=lambda: self.load_model(self.path_var.get())).pack(side='left', padx=5)
        
        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Range Forecast
        self.range_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.range_frame, text="  Forecast Range  ")
        self.create_range_tab()
        
        # Tab 2: Single Hourly
        self.hourly_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hourly_frame, text="  Single Hourly  ")
        self.create_hourly_tab()
        
        # Tab 3: Single Daily
        self.daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.daily_frame, text="  Single Daily  ")
        self.create_daily_tab()
        
        # Tab 4: Info
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="  Model Info  ")
        self.create_info_tab()
        
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w').pack(side='bottom', fill='x', padx=5, pady=2)

    # --- Model Loading ---
    def browse_model(self):
        f = filedialog.askopenfilename(filetypes=[("Pickle", "*.pkl")])
        if f:
            self.path_var.set(f)
            self.load_model(f)

    def load_model(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File not found: {path}")
            return
        try:
            raw = joblib.load(path)
            self.model = self._normalize_model(raw)
            self.model_path = path
            
            # Override features if model specifies them
            if self.model['hourly'].get('feature_columns'):
                self.hourly_features = self.model['hourly']['feature_columns']
            if self.model['daily'].get('feature_columns'):
                self.daily_features = self.model['daily']['feature_columns']
                
            self.status_var.set(f"Loaded: {os.path.basename(path)}")
            self.show_model_info()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _normalize_model(self, raw):
        norm = {
            'hourly': {'regressor': None, 'classifier': None, 'feature_columns': []},
            'daily': {'regressor': None, 'classifier': None, 'feature_columns': []},
            'weather_code_to_rain': WEATHER_CODE_TO_RAIN
        }
        # Combined
        if 'hourly' in raw and 'daily' in raw:
            norm['hourly'] = raw['hourly']
            norm['daily'] = raw['daily']
            norm['weather_code_to_rain'] = raw.get('weather_code_to_rain', WEATHER_CODE_TO_RAIN)
        # Partial (hourly or daily package)
        elif 'regressor' in raw:
            is_daily = 'daily' in raw.get('model_type', '')
            key = 'daily' if is_daily else 'hourly'
            norm[key] = raw
        return norm

    # --- Tab 1: Range Forecast ---
    def create_range_tab(self):
        ttk.Label(self.range_frame, text="Recursive Multi-Step Forecast", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        ctrl = ttk.LabelFrame(self.range_frame, text="Settings")
        ctrl.pack(fill='x', padx=10, pady=5)
        
        row1 = ttk.Frame(ctrl)
        row1.pack(fill='x', padx=5, pady=5)
        
        now = datetime.now()
        ttk.Label(row1, text="From:").pack(side='left')
        if TKCALENDAR_AVAILABLE:
            self.from_date = DateEntry(row1, width=12, date_pattern='yyyy-mm-dd')
            self.from_date.set_date(now)
        else:
            self.from_date = ttk.Entry(row1, width=12)
            self.from_date.insert(0, now.strftime('%Y-%m-%d'))
        self.from_date.pack(side='left', padx=5)
        
        self.from_hour = ttk.Spinbox(row1, from_=0, to=23, width=4)
        self.from_hour.set(now.hour)
        self.from_hour.pack(side='left')
        
        ttk.Label(row1, text="To:").pack(side='left', padx=10)
        if TKCALENDAR_AVAILABLE:
            self.to_date = DateEntry(row1, width=12, date_pattern='yyyy-mm-dd')
            self.to_date.set_date(now + timedelta(days=1))
        else:
            self.to_date = ttk.Entry(row1, width=12)
            self.to_date.insert(0, (now + timedelta(days=1)).strftime('%Y-%m-%d'))
        self.to_date.pack(side='left', padx=5)
        
        self.to_hour = ttk.Spinbox(row1, from_=0, to=23, width=4)
        self.to_hour.set(now.hour)
        self.to_hour.pack(side='left')
        
        row2 = ttk.Frame(ctrl)
        row2.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(row2, text="Quick:").pack(side='left')
        ttk.Button(row2, text="+24h", command=lambda: self.quick_select(24)).pack(side='left', padx=2)
        ttk.Button(row2, text="+72h", command=lambda: self.quick_select(72)).pack(side='left', padx=2)
        ttk.Button(row2, text="+7d", command=lambda: self.quick_select(168)).pack(side='left', padx=2)
        
        row3 = ttk.Frame(ctrl)
        row3.pack(fill='x', padx=5, pady=5)
        
        self.pred_type = tk.StringVar(value='hourly')
        ttk.Radiobutton(row3, text="Hourly", variable=self.pred_type, value='hourly').pack(side='left', padx=10)
        ttk.Radiobutton(row3, text="Daily", variable=self.pred_type, value='daily').pack(side='left', padx=10)
        
        ttk.Button(row3, text="GENERATE", command=self.run_range_predict).pack(side='left', padx=20)
        ttk.Button(row3, text="Export CSV", command=self.export_csv).pack(side='left', padx=5)
        
        self.range_result = scrolledtext.ScrolledText(self.range_frame, height=20, font=('Consolas', 10))
        self.range_result.pack(fill='both', expand=True, padx=10, pady=5)

    def quick_select(self, hours):
        dt = self.get_dt(self.from_date, self.from_hour)
        target = dt + timedelta(hours=hours)
        if TKCALENDAR_AVAILABLE:
            self.to_date.set_date(target)
        else:
            self.to_date.delete(0, tk.END)
            self.to_date.insert(0, target.strftime('%Y-%m-%d'))
        self.to_hour.set(target.hour)

    def get_dt(self, d_widget, h_widget):
        if TKCALENDAR_AVAILABLE:
            d = d_widget.get_date()
        else:
            d = datetime.strptime(d_widget.get(), '%Y-%m-%d').date()
        return datetime.combine(d, datetime.min.time()) + timedelta(hours=int(h_widget.get()))

    def run_range_predict(self):
        if not self.model:
            return messagebox.showerror("Error", "Load model first")
        
        start = self.get_dt(self.from_date, self.from_hour)
        end = self.get_dt(self.to_date, self.to_hour)
        
        if end <= start:
            return messagebox.showerror("Error", "End must be > Start")
        
        ptype = self.pred_type.get()
        pkg = self.model[ptype]
        
        if not pkg['regressor'] or not pkg['classifier']:
            return messagebox.showerror("Error", f"Model missing {ptype} components")
        
        if ptype == 'hourly':
            self.predict_hourly_recursive(start, end)
        else:
            self.predict_daily_recursive(start, end)

    def predict_hourly_recursive(self, start, end):
        """Recursive forecast for hourly using lag features"""
        hours = int((end - start).total_seconds() / 3600)
        
        reg = self.model['hourly']['regressor']
        clf = self.model['hourly']['classifier']
        features = self.hourly_features
        
        # Initialize state from defaults
        state = self.default_hourly.copy()
        
        # Storage for rolling calculation (last 24 values)
        temp_history = [state['temp_lag_1']] * 24
        humid_history = [state['humidity_lag_1']] * 24
        wind_history = [state['windspeed_lag_1']] * 24
        
        self.predictions_cache = []
        lines = [f"{'Time':<18} | {'Temp':>6} | {'Humid':>6} | {'Wind':>6} | {'Press':>8} | Condition"]
        lines.append("-" * 70)
        
        current = start
        for i in range(hours):
            state['hour'] = current.hour
            state['month'] = current.month
            
            # Build input
            X = pd.DataFrame([[state.get(f, 0) for f in features]], columns=features)
            
            y_reg = reg.predict(X)[0]  # [temp, humid, wind, press]
            y_clf = clf.predict(X)[0]
            
            code = int(y_clf)
            cond = WEATHER_CODE_TO_CONDITION.get(code, str(code))
            
            lines.append(f"{current.strftime('%Y-%m-%d %H:%M'):<18} | {y_reg[0]:>6.1f} | {y_reg[1]:>6.1f} | {y_reg[2]:>6.1f} | {y_reg[3]:>8.1f} | {cond}")
            
            self.predictions_cache.append({
                'Time': current,
                'Temp': y_reg[0], 'Humidity': y_reg[1],
                'Wind': y_reg[2], 'Pressure': y_reg[3],
                'Code': code, 'Condition': cond
            })
            
            # --- Update State (Recursive Step) ---
            # Shift history
            temp_history.pop(0)
            temp_history.append(y_reg[0])
            humid_history.pop(0)
            humid_history.append(y_reg[1])
            wind_history.pop(0)
            wind_history.append(y_reg[2])
            
            # Update lag_1
            state['temp_lag_1'] = y_reg[0]
            state['humidity_lag_1'] = y_reg[1]
            state['windspeed_lag_1'] = y_reg[2]
            state['sealevelpressure_lag_1'] = y_reg[3]
            
            # Update lag_24 (value from 24 hours ago in history)
            state['temp_lag_24'] = temp_history[0]
            state['humidity_lag_24'] = humid_history[0]
            state['windspeed_lag_24'] = wind_history[0]
            
            # Update rolling_24 (average of history)
            state['temp_rolling_24'] = np.mean(temp_history)
            state['humidity_rolling_24'] = np.mean(humid_history)
            state['windspeed_rolling_24'] = np.mean(wind_history)
            
            current += timedelta(hours=1)
        
        self.range_result.delete("1.0", tk.END)
        self.range_result.insert(tk.END, "\n".join(lines))
        self.status_var.set(f"Generated {hours} hourly forecasts")

    def predict_daily_recursive(self, start, end):
        """Recursive forecast for daily"""
        days = (end.date() - start.date()).days + 1
        
        reg = self.model['daily']['regressor']
        clf = self.model['daily']['classifier']
        features = self.daily_features
        
        state = self.default_daily.copy()
        
        # Track last 7 days for lag_7 calculation
        min_history = [state['temp_min_lag_1']] * 7
        max_history = [state['temp_max_lag_1']] * 7
        mean_history = [state['temp_mean_lag_1']] * 7
        
        self.predictions_cache = []
        lines = [f"{'Date':<12} | {'Min':>5} | {'Max':>5} | {'Mean':>5} | {'Hum':>5} | {'Wind':>5} | Condition"]
        lines.append("-" * 70)
        
        current = start.date()
        for i in range(days):
            state['month'] = current.month
            state['day'] = current.day
            
            X = pd.DataFrame([[state.get(f, 0) for f in features]], columns=features)
            
            y_reg = reg.predict(X)[0]  # [min, max, mean, humid, wind, press]
            y_clf = clf.predict(X)[0]
            
            code = int(y_clf)
            cond = WEATHER_CODE_TO_CONDITION.get(code, str(code))
            
            lines.append(f"{current.strftime('%Y-%m-%d'):<12} | {y_reg[0]:>5.1f} | {y_reg[1]:>5.1f} | {y_reg[2]:>5.1f} | {y_reg[3]:>5.1f} | {y_reg[4]:>5.1f} | {cond}")
            
            self.predictions_cache.append({
                'Date': current,
                'TempMin': y_reg[0], 'TempMax': y_reg[1], 'TempMean': y_reg[2],
                'Humidity': y_reg[3], 'Wind': y_reg[4], 'Pressure': y_reg[5],
                'Condition': cond
            })
            
            # --- Update State (Recursive) ---
            min_history.pop(0)
            min_history.append(y_reg[0])
            max_history.pop(0)
            max_history.append(y_reg[1])
            mean_history.pop(0)
            mean_history.append(y_reg[2])
            
            state['temp_min_lag_1'] = y_reg[0]
            state['temp_max_lag_1'] = y_reg[1]
            state['temp_mean_lag_1'] = y_reg[2]
            state['humidity_avg_lag_1'] = y_reg[3]
            state['windspeed_avg_lag_1'] = y_reg[4]
            state['pressure_avg_lag_1'] = y_reg[5]
            
            state['temp_min_lag_7'] = min_history[0]
            state['temp_max_lag_7'] = max_history[0]
            state['temp_mean_lag_7'] = mean_history[0]
            
            state['rain_total_lag_1'] = self.model['weather_code_to_rain'].get(code, 0.0)
            
            current += timedelta(days=1)
        
        self.range_result.delete("1.0", tk.END)
        self.range_result.insert(tk.END, "\n".join(lines))
        self.status_var.set(f"Generated {days} daily forecasts")

    def export_csv(self):
        if not self.predictions_cache:
            return
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f:
            pd.DataFrame(self.predictions_cache).to_csv(f, index=False)
            messagebox.showinfo("OK", "Exported")

    # --- Tab 2: Single Hourly ---
    def create_hourly_tab(self):
        ttk.Label(self.hourly_frame, text="Single Hour Prediction", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        self.h_inputs = {}
        f = ttk.LabelFrame(self.hourly_frame, text="Input Features")
        f.pack(fill='x', padx=10, pady=5)
        
        row = 0
        for feat in self.hourly_features:
            ttk.Label(f, text=f"{feat}:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
            e = ttk.Entry(f, width=12)
            e.insert(0, str(self.default_hourly.get(feat, 0)))
            e.grid(row=row, column=1, padx=5, pady=2)
            self.h_inputs[feat] = e
            row += 1
        
        ttk.Button(self.hourly_frame, text="PREDICT", command=self.predict_single_hourly).pack(pady=10)
        self.h_result = ttk.Label(self.hourly_frame, text="...", font=('Segoe UI', 12))
        self.h_result.pack()

    def predict_single_hourly(self):
        if not self.model or not self.model['hourly']['regressor']:
            return
        vals = {k: float(e.get()) for k, e in self.h_inputs.items()}
        X = pd.DataFrame([[vals.get(f, 0) for f in self.hourly_features]], columns=self.hourly_features)
        
        y_reg = self.model['hourly']['regressor'].predict(X)[0]
        y_clf = self.model['hourly']['classifier'].predict(X)[0]
        
        cond = WEATHER_CODE_TO_CONDITION.get(int(y_clf), str(y_clf))
        self.h_result.config(text=f"Temp: {y_reg[0]:.1f}C | Humid: {y_reg[1]:.1f}% | Wind: {y_reg[2]:.1f} | {cond}")

    # --- Tab 3: Single Daily ---
    def create_daily_tab(self):
        ttk.Label(self.daily_frame, text="Single Day Prediction", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        self.d_inputs = {}
        f = ttk.LabelFrame(self.daily_frame, text="Input Features")
        f.pack(fill='x', padx=10, pady=5)
        
        row = 0
        for feat in self.daily_features:
            ttk.Label(f, text=f"{feat}:").grid(row=row, column=0, sticky='w', padx=5, pady=2)
            e = ttk.Entry(f, width=12)
            e.insert(0, str(self.default_daily.get(feat, 0)))
            e.grid(row=row, column=1, padx=5, pady=2)
            self.d_inputs[feat] = e
            row += 1
        
        ttk.Button(self.daily_frame, text="PREDICT", command=self.predict_single_daily).pack(pady=10)
        self.d_result = ttk.Label(self.daily_frame, text="...", font=('Segoe UI', 12))
        self.d_result.pack()

    def predict_single_daily(self):
        if not self.model or not self.model['daily']['regressor']:
            return
        vals = {k: float(e.get()) for k, e in self.d_inputs.items()}
        X = pd.DataFrame([[vals.get(f, 0) for f in self.daily_features]], columns=self.daily_features)
        
        y_reg = self.model['daily']['regressor'].predict(X)[0]
        y_clf = self.model['daily']['classifier'].predict(X)[0]
        
        cond = WEATHER_CODE_TO_CONDITION.get(int(y_clf), str(y_clf))
        self.d_result.config(text=f"Min: {y_reg[0]:.1f} | Max: {y_reg[1]:.1f} | Mean: {y_reg[2]:.1f} | {cond}")

    # --- Tab 4: Info ---
    def create_info_tab(self):
        self.info_text = scrolledtext.ScrolledText(self.info_frame, font=('Consolas', 10))
        self.info_text.pack(fill='both', expand=True, padx=5, pady=5)

    def show_model_info(self):
        self.info_text.delete("1.0", tk.END)
        if not self.model:
            return
        
        lines = ["=== Model Info ===", f"Path: {self.model_path}", ""]
        
        lines.append("[HOURLY]")
        if self.model['hourly']['regressor']:
            lines.append(f"  Regressor: {self.model['hourly']['regressor'].__class__.__name__}")
        if self.model['hourly']['classifier']:
            lines.append(f"  Classifier: {self.model['hourly']['classifier'].__class__.__name__}")
        lines.append(f"  Features: {self.hourly_features}")
        
        lines.append("\n[DAILY]")
        if self.model['daily']['regressor']:
            lines.append(f"  Regressor: {self.model['daily']['regressor'].__class__.__name__}")
        if self.model['daily']['classifier']:
            lines.append(f"  Classifier: {self.model['daily']['classifier'].__class__.__name__}")
        lines.append(f"  Features: {self.daily_features}")
        
        lines.append("\n[WEATHER CODES]")
        for code, cond in WEATHER_CODE_TO_CONDITION.items():
            lines.append(f"  {code}: {cond} ({WEATHER_CODE_TO_RAIN.get(code, 0)}mm)")
        
        self.info_text.insert(tk.END, "\n".join(lines))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherModelGUI(root)
    root.mainloop()
