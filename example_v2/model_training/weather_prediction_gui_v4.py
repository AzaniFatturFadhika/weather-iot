# -*- coding: utf-8 -*-
"""
Weather Prediction GUI v4.1 (Date-Based Model)
==============================================
GUI Khusus untuk Model v4.0 (Date-Based Seasonality).
Mendukung input: Day, Month, Year, Hour.
Menghandle berbagai variasi file model .pkl (Combined, Hourly, Daily, Individual).

Fitur:
- Tabbed Interface (Range, Hourly, Daily, Info)
- Flexible Model Loading (Automatic Normalization)
- Automatic Feature Generation
- CSV Export
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Matplotlib imports for graphing
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Try importing tkcalendar
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

# ===================== CONSTANTS =====================
# Mapping WMO Code -> Rain Amount (approx mm/h or impact)
WEATHER_CODE_TO_RAIN = {
    0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0,
    51: 0.2, 53: 0.7, 55: 1.1,
    61: 1.7, 63: 4.0, 65: 10.3
}

# Mapping WMO Code -> Condition Name
WEATHER_CODE_TO_CONDITION = {
    0: 'Clear', 1: 'Partially Cloudy', 2: 'Partially Cloudy', 3: 'Overcast',
    51: 'Light Rain', 53: 'Moderate Rain', 55: 'Heavy Showers',
    61: 'Rain, Overcast', 63: 'Rain, Overcast', 65: 'Heavy Rain'
}

DEFAULT_MODEL_PATH = r'models/v4_weather_model_combined.pkl'

class WeatherPredictionGUI_v4:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Prediction GUI v4.1 (Date-Based)")
        self.root.geometry("1000x850")
        
        # State
        self.model = None
        self.model_path = ""
        self.predictions_cache = []
        
        # Define Features & Targets (Hardcoded as per v4 specs)
        self.hourly_features = ['day', 'month', 'year', 'hour']
        self.daily_features = ['day', 'month', 'year']
        
        self.hourly_targets_reg = ['temp', 'humidity', 'windspeed', 'sealevelpressure']
        self.daily_targets_reg = ['temp_min', 'temp_max', 'temp_mean', 'humidity_avg', 'windspeed_avg', 'pressure_avg']
        
        # Setup UI
        self.create_widgets()
        
        # Default Load
        if os.path.exists(DEFAULT_MODEL_PATH):
            self.load_model(DEFAULT_MODEL_PATH)
            
    def create_widgets(self):
        # 1. Top Bar: Model Selection
        model_frame = ttk.LabelFrame(self.root, text="Model Configuration (v4)")
        model_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(model_frame, text="Model File:").pack(side='left', padx=5)
        self.path_var = tk.StringVar()
        entry = ttk.Entry(model_frame, textvariable=self.path_var, width=60)
        entry.pack(side='left', padx=5, fill='x', expand=True)
        
        ttk.Button(model_frame, text="Browse...", command=self.browse_model).pack(side='left', padx=5)
        ttk.Button(model_frame, text="Load", command=lambda: self.load_model(self.path_var.get())).pack(side='left', padx=5)
        
        # 2. Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Range Forecast
        self.range_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.range_frame, text="  Forecast by Date Range  ")
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
        
        # 3. Status Bar
        self.status_var = tk.StringVar(value="Please load a v4 model.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side='bottom', fill='x', padx=5, pady=2)

    # --- Logic: Model Loading & Normalization ---
    def browse_model(self):
        f = filedialog.askopenfilename(filetypes=[("Model Files", "*.pkl;*.joblib"), ("Pickle Files", "*.pkl"), ("Joblib Files", "*.joblib"), ("All Files", "*.*")])
        if f:
            self.path_var.set(f)
            self.load_model(f)

    def load_model(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", "File not found.")
            return
            
        try:
            self.status_var.set(f"Loading {os.path.basename(path)}...")
            self.root.update()
            
            raw_model = joblib.load(path)
            self.model = self._normalize_model(raw_model)
            self.model_path = path
            
            # Refresh Info
            self.show_model_info()
            self.status_var.set(f"Loaded: {os.path.basename(path)}")
            
        except Exception as e:
            self.status_var.set("Load Failed.")
            messagebox.showerror("Load Error", str(e))

    def _normalize_model(self, raw):
        """
        Normalize various v4 Save Formats into a standard structure:
        {
           'hourly': {'regressor': ..., 'classifier': ...},
           'daily': {'regressor': ..., 'classifier': ...},
           'encoders': {'hourly': ..., 'daily': ...},
           'meta': {'version': ..., 'date': ...}
        }
        """
        norm = {
            'hourly': {'regressor': None, 'classifier': None},
            'daily': {'regressor': None, 'classifier': None},
            'encoders': {},
            'meta': {}
        }
        
        # Metadata extraction
        norm['meta']['version'] = raw.get('version', 'Unknown')
        norm['meta']['date'] = raw.get('trained_date', 'Unknown')
        
        # Case 1: Combined Package (Standard)
        if 'hourly' in raw and 'daily' in raw and isinstance(raw['hourly'], dict):
            # Hourly
            norm['hourly']['regressor'] = raw['hourly'].get('regressor')
            norm['hourly']['classifier'] = raw['hourly'].get('classifier')
            # Daily
            norm['daily']['regressor'] = raw['daily'].get('regressor')
            norm['daily']['classifier'] = raw['daily'].get('classifier')
            # Encoders
            norm['encoders']['hourly'] = raw.get('label_encoder_hourly')
            norm['encoders']['daily'] = raw.get('label_encoder_daily')
            
        # Case 2: Hourly/Daily Package (Partial)
        elif 'regressor' in raw and 'classifier' in raw:
            # Check keys or assume based on filename/content
            # v4 partials have 'feature_columns' usually
            cols = raw.get('feature_columns', [])
            is_hourly = 'hour' in cols
            
            key = 'hourly' if is_hourly else 'daily'
            norm[key]['regressor'] = raw['regressor']
            norm[key]['classifier'] = raw['classifier']
            norm['encoders'][key] = raw.get('label_encoder')
            
        # Case 3: Single Estimator (Rare, specific debugging)
        # Assuming just one model object provided directly would be tough without wrapping,
        # usually v4 always wraps in dict.
        
        return norm

    # --- Tab 1: Range Forecast ---
    def create_range_tab(self):
        ttk.Label(self.range_frame, text="Forecast by Date Range", font=('Segoe UI', 14, 'bold')).pack(pady=10)
        
        # Controls
        ctrl_frame = ttk.LabelFrame(self.range_frame, text="Settings")
        ctrl_frame.pack(fill='x', padx=10, pady=5)
        
        now = datetime.now()
        
        # Range Inputs
        date_row = ttk.Frame(ctrl_frame)
        date_row.pack(fill='x', padx=5, pady=5)
        
        # From
        ttk.Label(date_row, text="From:").pack(side='left')
        if TKCALENDAR_AVAILABLE:
            self.from_date = DateEntry(date_row, width=12, date_pattern='yyyy-mm-dd')
            self.from_date.set_date(now)
        else:
            self.from_date = ttk.Entry(date_row, width=12)
            self.from_date.insert(0, now.strftime("%Y-%m-%d"))
        self.from_date.pack(side='left', padx=5)
        
        self.from_hour = ttk.Spinbox(date_row, from_=0, to=23, width=4)
        self.from_hour.set(now.hour)
        self.from_hour.pack(side='left')
        
        # To
        ttk.Label(date_row, text="To:").pack(side='left', padx=10)
        if TKCALENDAR_AVAILABLE:
            self.to_date = DateEntry(date_row, width=12, date_pattern='yyyy-mm-dd')
            self.to_date.set_date(now + timedelta(days=1))
        else:
            self.to_date = ttk.Entry(date_row, width=12)
            self.to_date.insert(0, (now + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.to_date.pack(side='left', padx=5)
        
        self.to_hour = ttk.Spinbox(date_row, from_=0, to=23, width=4)
        self.to_hour.set(now.hour)
        self.to_hour.pack(side='left')
        
        # Quick Select
        btn_row = ttk.Frame(ctrl_frame)
        btn_row.pack(fill='x', padx=5, pady=5)
        ttk.Label(btn_row, text="Quick:").pack(side='left')
        ttk.Button(btn_row, text="+24h", command=lambda: self.quick_select(24)).pack(side='left', padx=2)
        ttk.Button(btn_row, text="+3d", command=lambda: self.quick_select(72)).pack(side='left', padx=2)
        ttk.Button(btn_row, text="+7d", command=lambda: self.quick_select(168)).pack(side='left', padx=2)
        
        # Type
        type_row = ttk.Frame(ctrl_frame)
        type_row.pack(fill='x', padx=5, pady=5)
        self.pred_type = tk.StringVar(value="hourly")
        ttk.Radiobutton(type_row, text="Hourly Forecast", variable=self.pred_type, value="hourly").pack(side='left', padx=10)
        ttk.Radiobutton(type_row, text="Daily Forecast", variable=self.pred_type, value="daily").pack(side='left', padx=10)
        
        ttk.Button(type_row, text="GENERATE", command=self.run_range_predict).pack(side='left', padx=20)
        ttk.Button(type_row, text="Export CSV", command=self.export_csv).pack(side='left', padx=5)
        
        # Results - Table
        self.range_result = scrolledtext.ScrolledText(self.range_frame, height=12, font=('Consolas', 9))
        self.range_result.pack(fill='x', padx=10, pady=5)
        
        # Results - Graph Canvas
        self.range_graph_frame = ttk.Frame(self.range_frame)
        self.range_graph_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.range_canvas = None  # Will hold FigureCanvasTkAgg

    def quick_select(self, hours):
        dt_from = self.get_dt(self.from_date, self.from_hour)
        dt_to = dt_from + timedelta(hours=hours)
        if TKCALENDAR_AVAILABLE:
            self.to_date.set_date(dt_to)
        else:
            self.to_date.delete(0, tk.END)
            self.to_date.insert(0, dt_to.strftime("%Y-%m-%d"))
        self.to_hour.set(dt_to.hour)

    def get_dt(self, d_widget, h_widget):
        if TKCALENDAR_AVAILABLE:
            d = d_widget.get_date()
        else:
            d = datetime.strptime(d_widget.get(), "%Y-%m-%d").date()
        return datetime.combine(d, datetime.min.time()) + timedelta(hours=int(h_widget.get()))

    def run_range_predict(self):
        if not self.model: return messagebox.showerror("Error", "No model loaded")
        
        start = self.get_dt(self.from_date, self.from_hour)
        end = self.get_dt(self.to_date, self.to_hour)
        
        if end <= start: return messagebox.showerror("Error", "End must be > Start")
        
        ptype = self.pred_type.get()
        pkg = self.model[ptype]
        
        if not pkg['regressor'] or not pkg['classifier']:
            return messagebox.showerror("Error", f"Model does not contain {ptype} components.")

        # Logic
        if ptype == 'hourly':
            self.predict_hourly_range(start, end)
        else:
            self.predict_daily_range(start, end)

    def predict_hourly_range(self, start, end):
        hours = int((end - start).total_seconds() / 3600)
        if hours > 24*30:
            if not messagebox.askyesno("Confirm", f"Predict {hours} hours?"): return
            
        timestamps = [start + timedelta(hours=i) for i in range(hours)]
        
        # Create Input DF
        df = pd.DataFrame({
            'day': [t.day for t in timestamps],
            'month': [t.month for t in timestamps],
            'year': [t.year for t in timestamps],
            'hour': [t.hour for t in timestamps]
        })
        
        # Predict
        reg = self.model['hourly']['regressor']
        clf = self.model['hourly']['classifier']
        
        # Order columns explicitly
        X = df[self.hourly_features]
        
        y_reg = reg.predict(X)
        y_clf = clf.predict(X)
        
        # Decode
        le = self.model['encoders'].get('hourly')
        if le:
            conds = le.inverse_transform(y_clf.astype(int))
        else:
            conds = y_clf
            
        # Format Results
        lines = []
        lines.append(f"{'Time':<18} | {'Temp':>6} | {'Humid':>6} | {'Wind':>6} | {'Press':>8} | {'Condition'}")
        lines.append("-" * 80)
        
        self.predictions_cache = []
        
        for i, t in enumerate(timestamps):
            c_name = conds[i] if isinstance(conds[i], str) else WEATHER_CODE_TO_CONDITION.get(conds[i], str(conds[i]))
            row_str = f"{t.strftime('%Y-%m-%d %H:%M'):<18} | {y_reg[i][0]:>6.1f} | {y_reg[i][1]:>6.1f} | {y_reg[i][2]:>6.1f} | {y_reg[i][3]:>8.1f} | {c_name}"
            lines.append(row_str)
            
            self.predictions_cache.append({
                'Time': t, 
                'Temp': y_reg[i][0], 'Humidity': y_reg[i][1], 
                'Wind': y_reg[i][2], 'Pressure': y_reg[i][3], 
                'Condition': c_name
            })
            
        self.range_result.delete("1.0", tk.END)
        self.range_result.insert(tk.END, "\n".join(lines))
        
        # Generate Graph
        self._plot_hourly_graph(timestamps, y_reg, conds)

    def predict_daily_range(self, start, end):
        days = (end.date() - start.date()).days + 1
        dates = [start.date() + timedelta(days=i) for i in range(days)]
        
        df = pd.DataFrame({
            'day': [d.day for d in dates],
            'month': [d.month for d in dates],
            'year': [d.year for d in dates]
        })
        
        # Predict
        reg = self.model['daily']['regressor']
        clf = self.model['daily']['classifier']
        
        X = df[self.daily_features]
        y_reg = reg.predict(X)
        y_clf = clf.predict(X)
        
        le = self.model['encoders'].get('daily')
        if le:
            conds = le.inverse_transform(y_clf.astype(int))
        else:
            conds = y_clf

        lines = []
        # Target Reg: min, max, mean, humid, wind, press
        lines.append(f"{'Date':<12} | {'Min':>5} | {'Max':>5} | {'Mean':>5} | {'Hum':>5} | {'Wind':>5} | {'Cond'}")
        lines.append("-" * 80)
        
        self.predictions_cache = []
        
        for i, d in enumerate(dates):
            c_name = conds[i] if isinstance(conds[i], str) else WEATHER_CODE_TO_CONDITION.get(conds[i], str(conds[i]))
            
            # y_reg columns: temp_min, temp_max, temp_mean, humidity_avg, windspeed_avg, pressure_avg
            # We display first few
            r = y_reg[i]
            row_str = f"{d.strftime('%Y-%m-%d'):<12} | {r[0]:>5.1f} | {r[1]:>5.1f} | {r[2]:>5.1f} | {r[3]:>5.1f} | {r[4]:>5.1f} | {c_name}"
            lines.append(row_str)
            
            self.predictions_cache.append({
                'Date': d, 'TempMin': r[0], 'TempMax': r[1], 'TempMean': r[2], 
                'HumidAvg': r[3], 'WindAvg': r[4], 'PressAvg': r[5],
                'Condition': c_name
            })
            
        self.range_result.delete("1.0", tk.END)
        self.range_result.insert(tk.END, "\n".join(lines))
        
        # Generate Graph
        self._plot_daily_graph(dates, y_reg, conds)


    def _plot_hourly_graph(self, timestamps, y_reg, conds):
        """Generate multi-subplot graph for hourly forecast"""
        # Clear previous canvas
        if self.range_canvas:
            self.range_canvas.get_tk_widget().destroy()
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 8), dpi=80)
        
        # Temperature
        ax1 = fig.add_subplot(4, 1, 1)
        ax1.plot([t for t in timestamps], [r[0] for r in y_reg], 'r-', linewidth=2, label='Temperature')
        ax1.set_ylabel('Temp (°C)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title('Hourly Weather Forecast', fontweight='bold')
        
        # Humidity
        ax2 = fig.add_subplot(4, 1, 2)
        ax2.plot([t for t in timestamps], [r[1] for r in y_reg], 'b-', linewidth=2, label='Humidity')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Wind Speed
        ax3 = fig.add_subplot(4, 1, 3)
        ax3.plot([t for t in timestamps], [r[2] for r in y_reg], 'g-', linewidth=2, label='Wind Speed')
        ax3.set_ylabel('Wind (m/s)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Pressure
        ax4 = fig.add_subplot(4, 1, 4)
        ax4.plot([t for t in timestamps], [r[3] for r in y_reg], 'm-', linewidth=2, label='Pressure')
        ax4.set_ylabel('Pressure (hPa)')
        ax4.set_xlabel('Time')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # Format x-axis
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        
        # Embed in tkinter
        self.range_canvas = FigureCanvasTkAgg(fig, self.range_graph_frame)
        self.range_canvas.draw()
        self.range_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _plot_daily_graph(self, dates, y_reg, conds):
        """Generate multi-subplot graph for daily forecast"""
        # Clear previous canvas
        if self.range_canvas:
            self.range_canvas.get_tk_widget().destroy()
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 8), dpi=80)
        
        # Temperature Range (Min/Max/Mean)
        ax1 = fig.add_subplot(4, 1, 1)
        ax1.plot(dates, [r[0] for r in y_reg], 'b-', linewidth=2, label='Min Temp', marker='o')
        ax1.plot(dates, [r[1] for r in y_reg], 'r-', linewidth=2, label='Max Temp', marker='o')
        ax1.plot(dates, [r[2] for r in y_reg], 'orange', linewidth=2, label='Mean Temp', marker='o')
        ax1.fill_between(dates, [r[0] for r in y_reg], [r[1] for r in y_reg], alpha=0.2)
        ax1.set_ylabel('Temp (°C)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_title('Daily Weather Forecast', fontweight='bold')
        
        # Humidity Average
        ax2 = fig.add_subplot(4, 1, 2)
        ax2.plot(dates, [r[3] for r in y_reg], 'b-', linewidth=2, label='Humidity Avg', marker='s')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Wind Speed Average
        ax3 = fig.add_subplot(4, 1, 3)
        ax3.plot(dates, [r[4] for r in y_reg], 'g-', linewidth=2, label='Wind Speed Avg', marker='^')
        ax3.set_ylabel('Wind (m/s)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        
        # Pressure Average
        ax4 = fig.add_subplot(4, 1, 4)
        ax4.plot(dates, [r[5] for r in y_reg], 'm-', linewidth=2, label='Pressure Avg', marker='d')
        ax4.set_ylabel('Pressure (hPa)')
        ax4.set_xlabel('Date')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        # Format x-axis
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        fig.tight_layout()
        
        # Embed in tkinter
        self.range_canvas = FigureCanvasTkAgg(fig, self.range_graph_frame)
        self.range_canvas.draw()
        self.range_canvas.get_tk_widget().pack(fill='both', expand=True)

    def export_csv(self):
        if not self.predictions_cache: return
        f = filedialog.asksaveasfilename(defaultextension=".csv")
        if f:
            pd.DataFrame(self.predictions_cache).to_csv(f, index=False)
            messagebox.showinfo("OK", "Exported.")

    # --- Tab 2: Single Hourly ---
    def create_hourly_tab(self):
        # Quick input for one hour
        f = ttk.Frame(self.hourly_frame)
        f.pack(pady=20)
        
        ttk.Label(f, text="Date:").grid(row=0, column=0)
        if TKCALENDAR_AVAILABLE:
            self.sh_date = DateEntry(f)
        else:
            self.sh_date = ttk.Entry(f)
            self.sh_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sh_date.grid(row=0, column=1)
        
        ttk.Label(f, text="Hour:").grid(row=0, column=2)
        self.sh_hour = ttk.Spinbox(f, from_=0, to=23, width=5)
        self.sh_hour.set(datetime.now().hour)
        self.sh_hour.grid(row=0, column=3)
        
        ttk.Button(f, text="PREDICT", command=self.run_single_hourly).grid(row=1, column=0, columnspan=4, pady=10)
        
        self.sh_result = ttk.Label(self.hourly_frame, text="...", font=('Segoe UI', 12))
        self.sh_result.pack(pady=5)
        
        self.sh_graph_frame = ttk.Frame(self.hourly_frame)
        self.sh_graph_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.sh_canvas = None

    def run_single_hourly(self):
        dt = self.get_dt(self.sh_date, self.sh_hour)
        # Reuse range logic for ease, but simple display
        if not self.model or not self.model['hourly']['regressor']: return
        
        X = pd.DataFrame([{'day': dt.day, 'month': dt.month, 'year': dt.year, 'hour': dt.hour}])
        X = X[self.hourly_features]
        
        reg = self.model['hourly']['regressor'].predict(X)[0]
        clf = self.model['hourly']['classifier'].predict(X)[0]
        
        le = self.model['encoders'].get('hourly')
        cond = le.inverse_transform([int(clf)])[0] if le else clf
        
        res = f"Time: {dt}\nTemp: {reg[0]:.1f} C\nHumid: {reg[1]:.1f} %\nWind: {reg[2]:.1f}\nCond: {cond}"
        self.sh_result.config(text=res)
        
        # Plot Single Hourly
        if self.sh_canvas: self.sh_canvas.get_tk_widget().destroy()
        
        fig = Figure(figsize=(6, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        metrics = ['Temp (C)', 'Humid (%)', 'Wind (m/s)', 'Press (hPa/10)']
        # Scale pressure to fit graph better
        values = [reg[0], reg[1], reg[2], reg[3]/10.0]
        colors = ['red', 'blue', 'green', 'purple']
        
        ax.bar(metrics, values, color=colors, alpha=0.7)
        for i, v in enumerate(values):
            ax.text(i, v + 0.5, f"{v:.1f}", ha='center', fontweight='bold')
            
        ax.set_title(f"Forecast for {dt.strftime('%H:%M')} - {cond}")
        ax.grid(True, axis='y', alpha=0.3)
        
        self.sh_canvas = FigureCanvasTkAgg(fig, self.sh_graph_frame)
        self.sh_canvas.draw()
        self.sh_canvas.get_tk_widget().pack(fill='both', expand=True)

    # --- Tab 3: Single Daily ---
    def create_daily_tab(self):
        f = ttk.Frame(self.daily_frame)
        f.pack(pady=20)
        
        ttk.Label(f, text="Date:").grid(row=0, column=0)
        if TKCALENDAR_AVAILABLE:
            self.sd_date = DateEntry(f)
        else:
            self.sd_date = ttk.Entry(f)
            self.sd_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sd_date.grid(row=0, column=1)
        
        ttk.Button(f, text="PREDICT", command=self.run_single_daily).grid(row=1, column=0, columnspan=2, pady=10)
        
        self.sd_result = ttk.Label(self.daily_frame, text="...", font=('Segoe UI', 12))
        self.sd_result.pack(pady=5)
        
        self.sd_graph_frame = ttk.Frame(self.daily_frame)
        self.sd_graph_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.sd_canvas = None

    def run_single_daily(self):
        if TKCALENDAR_AVAILABLE:
            d = self.sd_date.get_date()
        else:
            d = datetime.strptime(self.sd_date.get(), "%Y-%m-%d").date()
            
        if not self.model or not self.model['daily']['regressor']: return
        
        X = pd.DataFrame([{'day': d.day, 'month': d.month, 'year': d.year}])
        X = X[self.daily_features]
        
        reg = self.model['daily']['regressor'].predict(X)[0]
        clf = self.model['daily']['classifier'].predict(X)[0]
        
        le = self.model['encoders'].get('daily')
        cond = le.inverse_transform([int(clf)])[0] if le else clf
        
        res = f"Date: {d}\nMin/Max: {reg[0]:.1f} / {reg[1]:.1f} C\nCond: {cond}"
        self.sd_result.config(text=res)
        
        # Plot Single Daily
        if self.sd_canvas: self.sd_canvas.get_tk_widget().destroy()
        
        fig = Figure(figsize=(6, 4), dpi=80)
        
        # Temp Range
        ax1 = fig.add_subplot(1, 2, 1)
        labels = ['Min', 'Mean', 'Max']
        temps = [reg[0], reg[2], reg[1]]
        ax1.bar(labels, temps, color=['blue', 'orange', 'red'], alpha=0.7)
        for i, v in enumerate(temps):
            ax1.text(i, v + 0.1, f"{v:.1f}", ha='center', fontweight='bold')
        ax1.set_title("Temperature (°C)")
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Other Averages
        ax2 = fig.add_subplot(1, 2, 2)
        labels2 = ['Humid (%)', 'Wind (m/s)']
        values2 = [reg[3], reg[4]]
        ax2.bar(labels2, values2, color=['cyan', 'green'], alpha=0.7)
        for i, v in enumerate(values2):
            ax2.text(i, v + 0.1, f"{v:.1f}", ha='center', fontweight='bold')
        ax2.set_title("Averages")
        ax2.grid(True, axis='y', alpha=0.3)
        
        fig.suptitle(f"Forecast for {d} - {cond}", fontweight='bold')
        fig.tight_layout()
        
        self.sd_canvas = FigureCanvasTkAgg(fig, self.sd_graph_frame)
        self.sd_canvas.draw()
        self.sd_canvas.get_tk_widget().pack(fill='both', expand=True)

    # --- Tab 4: Info ---
    def create_info_tab(self):
        self.txt_info = scrolledtext.ScrolledText(self.info_frame, font=('Consolas', 10))
        self.txt_info.pack(fill='both', expand=True, padx=5, pady=5)
        
    def show_model_info(self):
        self.txt_info.delete("1.0", tk.END)
        if not self.model: return
        
        lines = []
        lines.append("=" * 80)
        lines.append("MODEL v4 INFORMATION")
        lines.append("=" * 80)
        lines.append(f"Version:       {self.model['meta'].get('version', 'N/A')}")
        lines.append(f"Trained Date:  {self.model['meta'].get('date', 'N/A')}")
        lines.append(f"Model File:    {os.path.basename(self.model_path)}")
        lines.append("")
        
        # Hourly Component Details
        lines.append("=" * 80)
        lines.append("HOURLY COMPONENT")
        lines.append("=" * 80)
        
        h_reg = self.model['hourly']['regressor']
        h_clf = self.model['hourly']['classifier']
        
        if h_reg:
            lines.append(f"\nRegressor Type: {type(h_reg).__name__}")
            lines.append(f"  Features:     {self.hourly_features}")
            lines.append(f"  Targets:      {self.hourly_targets_reg}")
            if hasattr(h_reg, 'n_features_in_'):
                lines.append(f"  N Features:   {h_reg.n_features_in_}")
            # Extract key params
            if hasattr(h_reg, 'get_params'):
                params = h_reg.get_params()
                key_params = ['n_estimators', 'max_depth', 'min_samples_split', 'random_state']
                params_str = ", ".join([f"{k}={params.get(k)}" for k in key_params if k in params])
                if params_str:
                    lines.append(f"  Parameters:   {params_str}")
        else:
            lines.append("\nRegressor: Not Available")
        
        if h_clf:
            lines.append(f"\nClassifier Type: {type(h_clf).__name__}")
            if hasattr(h_clf, 'n_features_in_'):
                lines.append(f"  N Features:   {h_clf.n_features_in_}")
            if hasattr(h_clf, 'classes_'):
                lines.append(f"  N Classes:    {len(h_clf.classes_)}")
            if hasattr(h_clf, 'get_params'):
                params = h_clf.get_params()
                key_params = ['n_estimators', 'max_depth', 'class_weight', 'random_state']
                params_str = ", ".join([f"{k}={params.get(k)}" for k in key_params if k in params])
                if params_str:
                    lines.append(f"  Parameters:   {params_str}")
        else:
            lines.append("\nClassifier: Not Available")
        
        # Label Encoder for Hourly
        h_le = self.model['encoders'].get('hourly')
        if h_le and hasattr(h_le, 'classes_'):
            lines.append(f"\nWeather Conditions (Hourly): {len(h_le.classes_)} classes")
            lines.append(f"  Classes: {', '.join(map(str, h_le.classes_))}")
        
        # Daily Component Details
        lines.append("\n" + "=" * 80)
        lines.append("DAILY COMPONENT")
        lines.append("=" * 80)
        
        d_reg = self.model['daily']['regressor']
        d_clf = self.model['daily']['classifier']
        
        if d_reg:
            lines.append(f"\nRegressor Type: {type(d_reg).__name__}")
            lines.append(f"  Features:     {self.daily_features}")
            lines.append(f"  Targets:      {self.daily_targets_reg}")
            if hasattr(d_reg, 'n_features_in_'):
                lines.append(f"  N Features:   {d_reg.n_features_in_}")
            if hasattr(d_reg, 'get_params'):
                params = d_reg.get_params()
                key_params = ['n_estimators', 'max_depth', 'min_samples_split', 'random_state']
                params_str = ", ".join([f"{k}={params.get(k)}" for k in key_params if k in params])
                if params_str:
                    lines.append(f"  Parameters:   {params_str}")
        else:
            lines.append("\nRegressor: Not Available")
        
        if d_clf:
            lines.append(f"\nClassifier Type: {type(d_clf).__name__}")
            if hasattr(d_clf, 'n_features_in_'):
                lines.append(f"  N Features:   {d_clf.n_features_in_}")
            if hasattr(d_clf, 'classes_'):
                lines.append(f"  N Classes:    {len(d_clf.classes_)}")
            if hasattr(d_clf, 'get_params'):
                params = d_clf.get_params()
                key_params = ['n_estimators', 'max_depth', 'class_weight', 'random_state']
                params_str = ", ".join([f"{k}={params.get(k)}" for k in key_params if k in params])
                if params_str:
                    lines.append(f"  Parameters:   {params_str}")
        else:
            lines.append("\nClassifier: Not Available")
        
        # Label Encoder for Daily
        d_le = self.model['encoders'].get('daily')
        if d_le and hasattr(d_le, 'classes_'):
            lines.append(f"\nWeather Conditions (Daily): {len(d_le.classes_)} classes")
            lines.append(f"  Classes: {', '.join(map(str, d_le.classes_))}")
        
        # Weather Code Reference
        lines.append("\n" + "=" * 80)
        lines.append("WEATHER CODE REFERENCE")
        lines.append("=" * 80)
        lines.append(f"\n{'Code':<6} | {'Condition':<20} | {'Rain (mm/h)':>12}")
        lines.append("-" * 45)
        for code in sorted(WEATHER_CODE_TO_CONDITION.keys()):
            cond = WEATHER_CODE_TO_CONDITION[code]
            rain = WEATHER_CODE_TO_RAIN.get(code, 0.0)
            lines.append(f"{code:<6} | {cond:<20} | {rain:>12.1f}")
        
        self.txt_info.insert(tk.END, "\n".join(lines))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherPredictionGUI_v4(root)
    root.mainloop()
