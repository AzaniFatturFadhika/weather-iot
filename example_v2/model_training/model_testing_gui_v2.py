# -*- coding: utf-8 -*-
"""
Weather Model Testing GUI v2.1 (for V2 Models)
===============================================
GUI khusus untuk model yang di-training dengan model_weather_training_v2.ipynb
Mendukung fitur-fitur baru:
- Rolling window 3h, 6h, 24h
- Cyclical encoding (hour_sin/cos, month_sin/cos)
- Interaction features (dew_point, humid_temp_ratio)
- Linear Regression & Logistic Regression support

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

# Try to import tkcalendar
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False
    print("tkcalendar not installed. Run: pip install tkcalendar")

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

# Default path to v2 models
DEFAULT_MODEL_PATH = r'D:/laragon/www/weather-iot/example_v2/model_training/models/v2_weather_model_combined.pkl'

class WeatherModelV2GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Model Testing GUI v2.1 (V2 Models)")
        self.root.geometry("1000x850")
        self.root.resizable(True, True)
        
        # Model state
        self.model = None
        self.model_path = DEFAULT_MODEL_PATH
        self.hourly_features = []
        self.daily_features = []
        
        # Default feature values for V2 models (with rolling_3, rolling_6)
        self.default_hourly = {
            'hour_sin': 0.0, 'hour_cos': 1.0,
            'month_sin': 0.0, 'month_cos': 1.0,
            'temp_lag_1': 28.5, 'temp_lag_24': 27.0,
            'temp_rolling_3': 28.0, 'temp_rolling_6': 27.5, 'temp_rolling_24': 26.8,
            'humidity_lag_1': 75, 'humidity_lag_24': 80,
            'humidity_rolling_3': 76, 'humidity_rolling_6': 77, 'humidity_rolling_24': 78,
            'windspeed_lag_1': 5.2, 'windspeed_lag_24': 4.8,
            'windspeed_rolling_3': 5.0, 'windspeed_rolling_6': 5.1, 'windspeed_rolling_24': 5.0,
            'sealevelpressure_lag_1': 1010.5, 'sealevelpressure_lag_24': 1011.0,
            'sealevelpressure_rolling_3': 1010.7, 'sealevelpressure_rolling_6': 1010.8,
            'sealevelpressure_rolling_24': 1011.0,
            'dew_point': 23.5, 'humid_temp_ratio': 2.63
        }
        
        self.default_daily = {
            'month': 1, 'day': 1,
            'temp_min_lag_1': 22.5, 'temp_max_lag_1': 31.0, 'temp_mean_lag_1': 26.5,
            'humidity_avg_lag_1': 78, 'windspeed_avg_lag_1': 5.5, 'pressure_avg_lag_1': 1010.2,
            'temp_min_lag_7': 22.0, 'temp_max_lag_7': 30.5, 'temp_mean_lag_7': 26.0,
            'rain_total_lag_1': 2.5,
            'temp_rolling_3d': 26.0, 'temp_rolling_7d': 25.5,
            'humidity_rolling_3d': 76, 'humidity_rolling_7d': 77
        }
        
        # Create UI
        self.create_widgets()
        
        # Load default model if exists
        if os.path.exists(self.model_path):
            self.load_model(self.model_path)
    
    def create_widgets(self):
        # --- Top Bar (Model Selection) ---
        top_frame = ttk.LabelFrame(self.root, text="Model Configuration (V2)")
        top_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(top_frame, text="Current Model:").pack(side='left', padx=5)
        
        self.path_entry = ttk.Entry(top_frame, width=70)
        self.path_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.path_entry.insert(0, self.model_path)
        
        ttk.Button(top_frame, text="Browse...", command=self.browse_model).pack(side='left', padx=5)
        ttk.Button(top_frame, text="Load", command=lambda: self.load_model(self.path_entry.get())).pack(side='left', padx=5)
        
        # --- Main Notebook ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Date Range Forecast
        self.range_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.range_frame, text="  Forecast by Date Range  ")
        self.create_range_tab()
        
        # Tab 2: Hourly Prediction
        self.hourly_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hourly_frame, text="  Single Hourly  ")
        self.create_hourly_tab()
        
        # Tab 3: Daily Prediction
        self.daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.daily_frame, text="  Single Daily  ")
        self.create_daily_tab()
        
        # Tab 4: Model Info
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="  Model Info  ")
        self.create_info_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - V2 Models")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(fill='x', side='bottom', padx=5, pady=2)
    
    def browse_model(self):
        """Open file dialog to select model"""
        initial_dir = os.path.dirname(self.path_entry.get())
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
            
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Weather Model V2 (.pkl)",
            filetypes=(("Pickle Files", "*.pkl"), ("All Files", "*.*"))
        )
        
        if filename:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, filename)
            self.load_model(filename)
            
    def load_model(self, path):
        """Load model from path and normalize structure"""
        if not os.path.exists(path):
            messagebox.showerror("Error", f"Model file not found: {path}")
            return
            
        try:
            raw_model = joblib.load(path)
            self.model_path = path
            
            # Normalize model structure
            self.model = self._normalize_model(raw_model)
            
            # Update features lists
            if self.model['hourly'].get('feature_columns'):
                self.hourly_features = self.model['hourly']['feature_columns']
            if self.model['daily'].get('feature_columns'):
                self.daily_features = self.model['daily']['feature_columns']
            
            self.status_var.set(f"Loaded V2: {os.path.basename(path)}")
            self.show_model_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
            self.status_var.set("Error loading model!")

    def _normalize_model(self, raw_model):
        """Normalize loaded model into standard structure"""
        normalized = {
            'hourly': {'regressor': None, 'classifier': None, 'feature_columns': []},
            'daily': {'regressor': None, 'classifier': None, 'feature_columns': []},
            'version': raw_model.get('version', 'Unknown'),
            'type': raw_model.get('model_type', 'Unknown'),
            'trained_date': raw_model.get('trained_date', 'Unknown')
        }
        
        # Case 1: Combined Model
        if 'hourly' in raw_model and 'daily' in raw_model:
            return raw_model
            
        # Case 2: Hourly/Daily Package
        elif 'regressor' in raw_model and 'classifier' in raw_model:
            m_type = raw_model.get('model_type', '')
            if 'daily' in m_type:
                normalized['daily'] = raw_model
            else:
                normalized['hourly'] = raw_model
                
        # Case 3: Single Model
        elif 'model' in raw_model:
            m_type = raw_model.get('model_type', '')
            target_pkg = 'daily' if 'daily' in m_type else 'hourly'
            component = 'classifier' if 'classifier' in m_type else 'regressor'
            
            normalized[target_pkg][component] = raw_model['model']
            normalized[target_pkg]['feature_columns'] = raw_model.get('feature_columns', [])
                
        return normalized

    def calculate_cyclical_features(self, hour, month):
        """Calculate cyclical features from hour and month"""
        return {
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'month_sin': np.sin(2 * np.pi * month / 12),
            'month_cos': np.cos(2 * np.pi * month / 12)
        }
    
    def calculate_interaction_features(self, temp, humidity):
        """Calculate interaction features"""
        dew_point = temp - ((100 - humidity) / 5)
        humid_temp_ratio = humidity / (temp + 1) if temp > -1 else 0
        return {
            'dew_point': dew_point,
            'humid_temp_ratio': humid_temp_ratio
        }

    def create_range_tab(self):
        """Create Date Range Forecast Tab"""
        ttk.Label(self.range_frame, text="Weather Forecast by Date Range (V2)",
                  font=('Segoe UI', 16, 'bold')).pack(pady=10)
        
        # Date selection frame
        date_frame = ttk.LabelFrame(self.range_frame, text="Select Forecast Period")
        date_frame.pack(fill='x', padx=10, pady=5)
        
        now = datetime.now()
        
        # FROM section
        from_frame = ttk.Frame(date_frame)
        from_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(from_frame, text="FROM (Start):", font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        if TKCALENDAR_AVAILABLE:
            self.from_date = DateEntry(from_frame, width=12, date_pattern='yyyy-mm-dd',
                                     year=now.year, month=now.month, day=now.day)
            self.from_date.pack(side='left', padx=5)
        else:
            ttk.Label(from_frame, text="Date (YYYY-MM-DD):").pack(side='left', padx=5)
            self.from_date = ttk.Entry(from_frame, width=12)
            self.from_date.pack(side='left', padx=5)
            self.from_date.insert(0, now.strftime("%Y-%m-%d"))
        
        ttk.Label(from_frame, text="Hour:").pack(side='left', padx=10)
        self.from_hour = ttk.Spinbox(from_frame, from_=0, to=23, width=5, format="%02.0f")
        self.from_hour.pack(side='left', padx=2)
        self.from_hour.set(now.hour)
        
        ttk.Label(from_frame, text=":").pack(side='left')
        
        self.from_minute = ttk.Spinbox(from_frame, from_=0, to=59, width=5, format="%02.0f")
        self.from_minute.pack(side='left', padx=2)
        self.from_minute.set(now.minute)
        
        # TO section
        to_frame = ttk.Frame(date_frame)
        to_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(to_frame, text="TO (End):", font=('Segoe UI', 11, 'bold')).pack(side='left', padx=5)
        
        if TKCALENDAR_AVAILABLE:
            self.to_date = DateEntry(to_frame, width=12, date_pattern='yyyy-mm-dd',
                                     year=now.year, month=now.month, day=now.day)
            self.to_date.pack(side='left', padx=5)
        else:
            ttk.Label(to_frame, text="Date (YYYY-MM-DD):").pack(side='left', padx=5)
            self.to_date = ttk.Entry(to_frame, width=12)
            self.to_date.pack(side='left', padx=5)
            self.to_date.insert(0, (now + timedelta(days=3)).strftime("%Y-%m-%d"))
        
        ttk.Label(to_frame, text="Hour:").pack(side='left', padx=10)
        self.to_hour = ttk.Spinbox(to_frame, from_=0, to=23, width=5, format="%02.0f")
        self.to_hour.pack(side='left', padx=2)
        self.to_hour.set(now.hour)
        
        ttk.Label(to_frame, text=":").pack(side='left')
        
        self.to_minute = ttk.Spinbox(to_frame, from_=0, to=59, width=5, format="%02.0f")
        self.to_minute.pack(side='left', padx=2)
        self.to_minute.set(0)
        
        # Quick select buttons
        quick_frame = ttk.Frame(date_frame)
        quick_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(quick_frame, text="Quick Select (from Start):").pack(side='left', padx=5)
        ttk.Button(quick_frame, text="+6 hours", command=lambda: self.quick_select(6)).pack(side='left', padx=3)
        ttk.Button(quick_frame, text="+12 hours", command=lambda: self.quick_select(12)).pack(side='left', padx=3)
        ttk.Button(quick_frame, text="+24 hours", command=lambda: self.quick_select(24)).pack(side='left', padx=3)
        ttk.Button(quick_frame, text="+3 days", command=lambda: self.quick_select(72)).pack(side='left', padx=3)
        ttk.Button(quick_frame, text="+7 days", command=lambda: self.quick_select(168)).pack(side='left', padx=3)
        
        # Forecast type selection
        type_frame = ttk.Frame(date_frame)
        type_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(type_frame, text="Forecast Type:").pack(side='left', padx=5)
        self.forecast_type = tk.StringVar(value="hourly")
        ttk.Radiobutton(type_frame, text="Hourly (per-jam)", variable=self.forecast_type, 
                        value="hourly").pack(side='left', padx=10)
        ttk.Radiobutton(type_frame, text="Daily (per-hari)", variable=self.forecast_type, 
                        value="daily").pack(side='left', padx=10)
        
        # Generate button
        btn_frame = ttk.Frame(self.range_frame)
        btn_frame.pack(pady=15)
        
        self.generate_btn = ttk.Button(btn_frame, text="Generate Forecast", 
                                        command=self.generate_range_forecast)
        self.generate_btn.pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Clear Results", command=self.clear_range_results).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_forecast).pack(side='left', padx=10)
        
        # Info label
        self.range_info = ttk.Label(self.range_frame, text="", font=('Segoe UI', 10))
        self.range_info.pack(pady=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(self.range_frame, text="Forecast Results")
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.range_result = scrolledtext.ScrolledText(result_frame, height=18, font=('Consolas', 10))
        self.range_result.pack(fill='both', expand=True, padx=5, pady=5)
    
    def get_from_datetime(self):
        """Get FROM datetime from inputs"""
        if TKCALENDAR_AVAILABLE:
            date = self.from_date.get_date()
        else:
            date = datetime.strptime(self.from_date.get(), "%Y-%m-%d").date()
        
        hour = int(self.from_hour.get())
        minute = int(self.from_minute.get())
        
        return datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def get_to_datetime(self):
        """Get TO datetime from inputs"""
        if TKCALENDAR_AVAILABLE:
            date = self.to_date.get_date()
        else:
            date = datetime.strptime(self.to_date.get(), "%Y-%m-%d").date()
        
        hour = int(self.to_hour.get())
        minute = int(self.to_minute.get())
        
        return datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def quick_select(self, hours):
        """Quick select TO date based on hours from FROM date"""
        try:
            start_dt = self.get_from_datetime()
            target = start_dt + timedelta(hours=hours)
            
            if TKCALENDAR_AVAILABLE:
                self.to_date.set_date(target.date())
            else:
                self.to_date.delete(0, tk.END)
                self.to_date.insert(0, target.strftime("%Y-%m-%d"))
            
            self.to_hour.set(target.hour)
            self.to_minute.set(target.minute)
            
            self.update_range_info()
        except:
            pass
    
    def update_range_info(self):
        """Update info about selected range"""
        try:
            from_dt = self.get_from_datetime()
            to_dt = self.get_to_datetime()
            
            delta = to_dt - from_dt
            hours = int(delta.total_seconds() / 3600)
            days = delta.days
            
            if hours > 0:
                self.range_info.config(text=f"Duration: {hours} hours ({days} days, {hours % 24} hours)")
            else:
                self.range_info.config(text="Invalid range: TO must be after FROM")
        except:
            self.range_info.config(text="")
    
    def create_hourly_tab(self):
        """Create Single Hourly Prediction Tab"""
        ttk.Label(self.hourly_frame, text="Single Hour Prediction (V2)",
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Time selection
        time_frame = ttk.LabelFrame(self.hourly_frame, text="Target Time")
        time_frame.pack(fill='x', padx=10, pady=5)
        
        row1 = ttk.Frame(time_frame)
        row1.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(row1, text="Hour (0-23):").pack(side='left', padx=5)
        self.single_hour = ttk.Spinbox(row1, from_=0, to=23, width=8)
        self.single_hour.pack(side='left', padx=5)
        self.single_hour.set(datetime.now().hour)
        
        ttk.Label(row1, text="Month:").pack(side='left', padx=15)
        self.single_month = ttk.Spinbox(row1, from_=1, to=12, width=8)
        self.single_month.pack(side='left', padx=5)
        self.single_month.set(datetime.now().month)
        
        # Feature values
        adv_frame = ttk.LabelFrame(self.hourly_frame, text="Current Conditions")
        adv_frame.pack(fill='x', padx=10, pady=5)
        
        self.hourly_inputs = {}
        
        row2 = ttk.Frame(adv_frame)
        row2.pack(fill='x', padx=5, pady=3)
        ttk.Label(row2, text="Current Temp (C):").pack(side='left', padx=5)
        self.hourly_inputs['temp_lag_1'] = ttk.Entry(row2, width=10)
        self.hourly_inputs['temp_lag_1'].pack(side='left', padx=5)
        self.hourly_inputs['temp_lag_1'].insert(0, "28.5")
        
        ttk.Label(row2, text="Humidity (%):").pack(side='left', padx=15)
        self.hourly_inputs['humidity_lag_1'] = ttk.Entry(row2, width=10)
        self.hourly_inputs['humidity_lag_1'].pack(side='left', padx=5)
        self.hourly_inputs['humidity_lag_1'].insert(0, "75")
        
        row3 = ttk.Frame(adv_frame)
        row3.pack(fill='x', padx=5, pady=3)
        ttk.Label(row3, text="Wind Speed (km/h):").pack(side='left', padx=5)
        self.hourly_inputs['windspeed_lag_1'] = ttk.Entry(row3, width=10)
        self.hourly_inputs['windspeed_lag_1'].pack(side='left', padx=5)
        self.hourly_inputs['windspeed_lag_1'].insert(0, "5.2")
        
        ttk.Label(row3, text="Pressure (hPa):").pack(side='left', padx=15)
        self.hourly_inputs['sealevelpressure_lag_1'] = ttk.Entry(row3, width=10)
        self.hourly_inputs['sealevelpressure_lag_1'].pack(side='left', padx=5)
        self.hourly_inputs['sealevelpressure_lag_1'].insert(0, "1010.5")
        
        # Buttons
        btn_frame = ttk.Frame(self.hourly_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Predict", command=self.predict_single_hourly).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_hourly).pack(side='left', padx=5)
        
        # Result
        result_frame = ttk.LabelFrame(self.hourly_frame, text="Prediction Result")
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.hourly_result = scrolledtext.ScrolledText(result_frame, height=12, font=('Consolas', 11))
        self.hourly_result.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_daily_tab(self):
        """Create Single Daily Prediction Tab"""
        ttk.Label(self.daily_frame, text="Single Day Prediction (V2)",
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Date selection
        date_frame = ttk.LabelFrame(self.daily_frame, text="Target Date")
        date_frame.pack(fill='x', padx=10, pady=5)
        
        row1 = ttk.Frame(date_frame)
        row1.pack(fill='x', padx=5, pady=10)
        
        now = datetime.now()
        if TKCALENDAR_AVAILABLE:
            ttk.Label(row1, text="Date:").pack(side='left', padx=5)
            self.daily_date = DateEntry(row1, width=12, date_pattern='yyyy-mm-dd')
            self.daily_date.pack(side='left', padx=5)
        else:
            ttk.Label(row1, text="Month:").pack(side='left', padx=5)
            self.daily_month = ttk.Spinbox(row1, from_=1, to=12, width=8)
            self.daily_month.pack(side='left', padx=5)
            self.daily_month.set(now.month)
            
            ttk.Label(row1, text="Day:").pack(side='left', padx=15)
            self.daily_day = ttk.Spinbox(row1, from_=1, to=31, width=8)
            self.daily_day.pack(side='left', padx=5)
            self.daily_day.set(now.day)
        
        # Advanced options
        adv_frame = ttk.LabelFrame(self.daily_frame, text="Yesterday's Conditions")
        adv_frame.pack(fill='x', padx=10, pady=5)
        
        self.daily_inputs = {}
        
        row2 = ttk.Frame(adv_frame)
        row2.pack(fill='x', padx=5, pady=3)
        ttk.Label(row2, text="Yesterday Temp Min:").pack(side='left', padx=5)
        self.daily_inputs['temp_min_lag_1'] = ttk.Entry(row2, width=10)
        self.daily_inputs['temp_min_lag_1'].pack(side='left', padx=5)
        self.daily_inputs['temp_min_lag_1'].insert(0, "22.5")
        
        ttk.Label(row2, text="Temp Max:").pack(side='left', padx=5)
        self.daily_inputs['temp_max_lag_1'] = ttk.Entry(row2, width=10)
        self.daily_inputs['temp_max_lag_1'].pack(side='left', padx=5)
        self.daily_inputs['temp_max_lag_1'].insert(0, "31.0")
        
        ttk.Label(row2, text="Humidity Avg:").pack(side='left', padx=5)
        self.daily_inputs['humidity_avg_lag_1'] = ttk.Entry(row2, width=10)
        self.daily_inputs['humidity_avg_lag_1'].pack(side='left', padx=5)
        self.daily_inputs['humidity_avg_lag_1'].insert(0, "78")
        
        # Buttons
        btn_frame = ttk.Frame(self.daily_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Predict", command=self.predict_single_daily).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_daily).pack(side='left', padx=5)
        
        # Result
        result_frame = ttk.LabelFrame(self.daily_frame, text="Prediction Result")
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.daily_result = scrolledtext.ScrolledText(result_frame, height=12, font=('Consolas', 11))
        self.daily_result.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_info_tab(self):
        """Create Model Info Tab"""
        ttk.Label(self.info_frame, text="Model Information (V2)",
                  font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        self.info_text = scrolledtext.ScrolledText(self.info_frame, height=25, font=('Consolas', 10))
        self.info_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        ttk.Button(self.info_frame, text="Refresh", command=lambda: self.show_model_info()).pack(pady=5)

    def show_model_info(self):
        """Show full details of the loaded model"""
        if not self.model:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "No model loaded. Please load a model first.")
            return

        self.info_text.delete(1.0, tk.END)
        lines = []
        
        lines.append("=" * 60)
        lines.append(f"MODEL INFO (V2): {os.path.basename(self.model_path)}")
        lines.append("=" * 60)
        lines.append(f"Type:         {self.model.get('type', 'Unknown')}")
        lines.append(f"Version:      {self.model.get('version', 'Unknown')}")
        lines.append(f"Trained Date: {self.model.get('trained_date', 'Unknown')}")
        lines.append("-" * 60)
        
        # Hourly Component
        lines.append("\n[HOURLY MODEL COMPONENT]")
        if self.model.get('hourly'):
            h_data = self.model['hourly']
            h_reg = h_data.get('regressor')
            h_clf = h_data.get('classifier')
            
            if h_reg:
                lines.append(f"  Regressor:  {h_reg.__class__.__name__}")
            else:
                lines.append("  Regressor:  NOT AVAILABLE")
                
            if h_clf:
                lines.append(f"  Classifier: {h_clf.__class__.__name__}")
            else:
                lines.append("  Classifier: NOT AVAILABLE")
                
            if h_data.get('feature_columns'):
                lines.append(f"  Features: {len(h_data['feature_columns'])} columns")
                lines.append(f"    {', '.join(h_data['feature_columns'][:5])}...")

        # Daily Component
        lines.append("\n[DAILY MODEL COMPONENT]")
        if self.model.get('daily'):
            d_data = self.model['daily']
            d_reg = d_data.get('regressor')
            d_clf = d_data.get('classifier')
            
            if d_reg:
                lines.append(f"  Regressor:  {d_reg.__class__.__name__}")
            else:
                lines.append("  Regressor:  NOT AVAILABLE")
                
            if d_clf:
                lines.append(f"  Classifier: {d_clf.__class__.__name__}")
            else:
                lines.append("  Classifier: NOT AVAILABLE")

            if d_data.get('feature_columns'):
                lines.append(f"  Features: {len(d_data['feature_columns'])} columns")
                lines.append(f"    {', '.join(d_data['feature_columns'][:5])}...")

        # Reference
        lines.append("\n" + "=" * 60)
        lines.append("REFERENCE: Weather Codes")
        lines.append("-" * 60)
        lines.append(f"{'Code':<5} | {'Condition':<20} | {'Rain (mm)'}")
        for code, cond in WEATHER_CODE_TO_CONDITION.items():
            rain = WEATHER_CODE_TO_RAIN.get(code, 0)
            lines.append(f"{code:<5} | {cond:<20} | {rain}")
            
        self.info_text.insert(tk.END, "\n".join(lines))
    
    def generate_range_forecast(self):
        """Generate forecast for date range"""
        if self.model is None:
            messagebox.showerror("Error", "Model not loaded!")
            return
        
        try:
            from_dt = self.get_from_datetime()
            to_dt = self.get_to_datetime()
            
            if to_dt <= from_dt:
                messagebox.showerror("Error", "TO date must be after FROM date!")
                return
            
            forecast_type = self.forecast_type.get()
            
            if forecast_type == "hourly":
                self.generate_hourly_range(from_dt, to_dt)
            else:
                self.generate_daily_range(from_dt, to_dt)
                
        except Exception as e:
            messagebox.showerror("Error", f"Forecast failed: {str(e)}")
    
    def generate_hourly_range(self, from_dt, to_dt):
        """Generate hourly forecast for range"""
        if not self.model['hourly']['regressor'] or not self.model['hourly']['classifier']:
             messagebox.showerror("Error", "Current model does not support Hourly prediction")
             return

        delta = to_dt - from_dt
        n_hours = int(delta.total_seconds() / 3600)
        
        if n_hours > 168:
            if not messagebox.askyesno("Warning", f"Forecasting {n_hours} hours may be slow. Continue?"):
                return
        
        reg = self.model['hourly']['regressor']
        clf = self.model['hourly']['classifier']
        features = self.hourly_features
        
        # Build initial features
        current = self.default_hourly.copy()
        predictions = []
        current_dt = from_dt
        
        self.status_var.set("Generating hourly forecast...")
        self.root.update()
        
        for i in range(n_hours):
            # Update cyclical features
            cyclical = self.calculate_cyclical_features(current_dt.hour, current_dt.month)
            current.update(cyclical)
            
            # Update interaction features
            temp = current.get('temp_lag_1', 28.5)
            humid = current.get('humidity_lag_1', 75)
            interaction = self.calculate_interaction_features(temp, humid)
            current.update(interaction)
            
            # Use DataFrame to preserve feature names
            X = pd.DataFrame([[current.get(f, 0) for f in features]], columns=features)
            reg_pred = reg.predict(X)[0]
            clf_pred = clf.predict(X)[0]
            
            weather_code = int(clf_pred)
            predictions.append({
                'datetime': current_dt.strftime("%Y-%m-%d %H:%M"),
                'temp': reg_pred[0],
                'humidity': reg_pred[1],
                'windspeed': reg_pred[2],
                'pressure': reg_pred[3],
                'weather_code': weather_code,
                'condition': WEATHER_CODE_TO_CONDITION.get(weather_code, 'Unknown'),
                'rain': WEATHER_CODE_TO_RAIN.get(weather_code, 0.0)
            })
            
            # Update for next iteration
            current['temp_lag_1'] = reg_pred[0]
            current['humidity_lag_1'] = reg_pred[1]
            current['windspeed_lag_1'] = reg_pred[2]
            current['sealevelpressure_lag_1'] = reg_pred[3]
            
            current_dt += timedelta(hours=1)
        
        # Display results
        self.range_result.delete(1.0, tk.END)
        result = []
        result.append("=" * 85)
        result.append(f"HOURLY FORECAST (V2): {from_dt.strftime('%Y-%m-%d %H:%M')} to {to_dt.strftime('%Y-%m-%d %H:%M')}")
        result.append(f"Model: {os.path.basename(self.model_path)}")
        result.append(f"Total: {n_hours} hours")
        result.append("=" * 85)
        result.append(f"{'DateTime':<18} | {'Temp':>6} | {'Humid':>6} | {'Wind':>6} | {'Press':>8} | {'Condition':<16} | {'Rain'}")
        result.append("-" * 85)
        
        for p in predictions:
            result.append(f"{p['datetime']:<18} | {p['temp']:>5.1f}C | {p['humidity']:>5.1f}% | {p['windspeed']:>5.1f} | {p['pressure']:>7.1f} | {p['condition']:<16} | {p['rain']:.1f}mm")
        
        self.range_result.insert(tk.END, "\n".join(result))
        self.status_var.set(f"Hourly forecast generated: {n_hours} hours")
        self.predictions_cache = predictions
    
    def generate_daily_range(self, from_dt, to_dt):
        """Generate daily forecast for range"""
        if not self.model['daily']['regressor'] or not self.model['daily']['classifier']:
             messagebox.showerror("Error", "Current model does not support Daily prediction")
             return
              
        n_days = (to_dt.date() - from_dt.date()).days + 1
        
        reg = self.model['daily']['regressor']
        clf = self.model['daily']['classifier']
        features = self.daily_features
        
        current = self.default_daily.copy()
        predictions = []
        current_date = from_dt.date()
        
        self.status_var.set("Generating daily forecast...")
        self.root.update()
        
        for i in range(n_days):
            current['month'] = current_date.month
            current['day'] = current_date.day
            
            # Use DataFrame to preserve feature names
            X = pd.DataFrame([[current.get(f, 0) for f in features]], columns=features)
            reg_pred = reg.predict(X)[0]
            clf_pred = clf.predict(X)[0]
            
            weather_code = int(clf_pred)
            predictions.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'temp_min': reg_pred[0],
                'temp_max': reg_pred[1],
                'temp_mean': reg_pred[2],
                'humidity': reg_pred[3],
                'windspeed': reg_pred[4],
                'pressure': reg_pred[5],
                'weather_code': weather_code,
                'condition': WEATHER_CODE_TO_CONDITION.get(weather_code, 'Unknown')
            })
            
            # Update for next day
            current['temp_min_lag_1'] = reg_pred[0]
            current['temp_max_lag_1'] = reg_pred[1]
            current['temp_mean_lag_1'] = reg_pred[2]
            current['humidity_avg_lag_1'] = reg_pred[3]
            current['windspeed_avg_lag_1'] = reg_pred[4]
            current['pressure_avg_lag_1'] = reg_pred[5]
            
            current_date += timedelta(days=1)
        
        # Display
        self.range_result.delete(1.0, tk.END)
        result = []
        result.append("=" * 90)
        result.append(f"DAILY FORECAST (V2): {from_dt.strftime('%Y-%m-%d')} to {to_dt.strftime('%Y-%m-%d')}")
        result.append(f"Model: {os.path.basename(self.model_path)}")
        result.append(f"Total: {n_days} days")
        result.append("=" * 90)
        result.append(f"{'Date':<12} | {'Min':>6} | {'Max':>6} | {'Mean':>6} | {'Humid':>6} | {'Wind':>6} | {'Condition'}")
        result.append("-" * 90)
        
        for p in predictions:
            result.append(f"{p['date']:<12} | {p['temp_min']:>5.1f}C | {p['temp_max']:>5.1f}C | {p['temp_mean']:>5.1f}C | {p['humidity']:>5.1f}% | {p['windspeed']:>5.1f} | {p['condition']}")
        
        self.range_result.insert(tk.END, "\n".join(result))
        self.status_var.set(f"Daily forecast generated: {n_days} days")
        self.predictions_cache = predictions
    
    def clear_range_results(self):
        self.range_result.delete(1.0, tk.END)
        self.predictions_cache = []
    
    def export_forecast(self):
        """Export forecast to CSV"""
        if not hasattr(self, 'predictions_cache') or not self.predictions_cache:
            messagebox.showwarning("Warning", "No forecast data to export!")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Forecast",
                defaultextension=".csv",
                initialfile=f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
            )
            
            if not filename:
                return

            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.predictions_cache[0].keys())
                writer.writeheader()
                writer.writerows(self.predictions_cache)
            
            messagebox.showinfo("Success", f"Forecast exported to {filename}")
            self.status_var.set(f"Exported: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def predict_single_hourly(self):
        """Single hour prediction"""
        if self.model is None or not self.model['hourly']['regressor']:
             messagebox.showerror("Error", "Model not loaded or does not support Hourly prediction!")
             return
        
        try:
            features = self.hourly_features
            current = self.default_hourly.copy()
            
            hour = float(self.single_hour.get())
            month = float(self.single_month.get())
            
            # Calculate cyclical features
            cyclical = self.calculate_cyclical_features(hour, month)
            current.update(cyclical)
            
            # Override with user inputs
            for key, widget in self.hourly_inputs.items():
                try:
                    current[key] = float(widget.get())
                except:
                    pass
            
            # Calculate interaction features
            temp = current.get('temp_lag_1', 28.5)
            humid = current.get('humidity_lag_1', 75)
            interaction = self.calculate_interaction_features(temp, humid)
            current.update(interaction)
            
            # Use DataFrame to preserve feature names
            X = pd.DataFrame([[current.get(f, 0) for f in features]], columns=features)
            
            reg = self.model['hourly']['regressor']
            clf = self.model['hourly']['classifier']
            
            reg_pred = reg.predict(X)[0]
            clf_pred = clf.predict(X)[0]
            
            weather_code = int(clf_pred)
            
            self.hourly_result.delete(1.0, tk.END)
            result = []
            result.append("=" * 45)
            result.append(f"HOURLY PREDICTION V2")
            result.append(f"Model: {os.path.basename(self.model_path)}")
            result.append("=" * 45)
            result.append(f"\nHour: {int(hour)}, Month: {int(month)}")
            result.append("\n--- Predictions ---")
            result.append(f"  Temperature:  {reg_pred[0]:.1f} C")
            result.append(f"  Humidity:     {reg_pred[1]:.1f} %")
            result.append(f"  Wind Speed:   {reg_pred[2]:.1f} km/h")
            result.append(f"  Pressure:     {reg_pred[3]:.1f} hPa")
            result.append(f"  Weather:      {WEATHER_CODE_TO_CONDITION.get(weather_code, 'Unknown')}")
            result.append(f"  Rain:         {WEATHER_CODE_TO_RAIN.get(weather_code, 0):.1f} mm")
            
            self.hourly_result.insert(tk.END, "\n".join(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def predict_single_daily(self):
        """Single day prediction"""
        if self.model is None or not self.model['daily']['regressor']:
             messagebox.showerror("Error", "Model not loaded or does not support Daily prediction!")
             return
        
        try:
            features = self.daily_features
            current = self.default_daily.copy()
            
            if TKCALENDAR_AVAILABLE:
                date = self.daily_date.get_date()
                current['month'] = float(date.month)
                current['day'] = float(date.day)
            else:
                current['month'] = float(self.daily_month.get())
                current['day'] = float(self.daily_day.get())
            
            # Override with user inputs
            for key, widget in self.daily_inputs.items():
                try:
                    current[key] = float(widget.get())
                except:
                    pass
            
            # Use DataFrame to preserve feature names
            X = pd.DataFrame([[current.get(f, 0) for f in features]], columns=features)
            
            reg = self.model['daily']['regressor']
            clf = self.model['daily']['classifier']
            
            reg_pred = reg.predict(X)[0]
            clf_pred = clf.predict(X)[0]
            
            weather_code = int(clf_pred)
            
            self.daily_result.delete(1.0, tk.END)
            result = []
            result.append("=" * 45)
            result.append(f"DAILY PREDICTION V2")
            result.append(f"Model: {os.path.basename(self.model_path)}")
            result.append("=" * 45)
            result.append(f"\nDate: {int(current['month'])}/{int(current['day'])}")
            result.append("\n--- Predictions ---")
            result.append(f"  Temp Min:     {reg_pred[0]:.1f} C")
            result.append(f"  Temp Max:     {reg_pred[1]:.1f} C")
            result.append(f"  Temp Mean:    {reg_pred[2]:.1f} C")
            result.append(f"  Humidity:     {reg_pred[3]:.1f} %")
            result.append(f"  Wind Speed:   {reg_pred[4]:.1f} km/h")
            result.append(f"  Pressure:     {reg_pred[5]:.1f} hPa")
            result.append(f"  Weather:      {WEATHER_CODE_TO_CONDITION.get(weather_code, 'Unknown')}")
            
            self.daily_result.insert(tk.END, "\n".join(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def reset_hourly(self):
        """Reset hourly inputs"""
        for key, widget in self.hourly_inputs.items():
            widget.delete(0, tk.END)
            widget.insert(0, str(self.default_hourly.get(key, 0)))
        self.hourly_result.delete(1.0, tk.END)

    def reset_daily(self):
        """Reset daily inputs"""
        for key, widget in self.daily_inputs.items():
            widget.delete(0, tk.END)
            widget.insert(0, str(self.default_daily.get(key, 0)))
        self.daily_result.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Segoe UI', 10))
    style.configure('TButton', font=('Segoe UI', 10, 'bold'))
    
    app = WeatherModelV2GUI(root)
    root.mainloop()
