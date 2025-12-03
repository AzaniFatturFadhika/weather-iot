"""
Weather Prediction GUI Application
===================================
Display hourly weather predictions using trained ML model.
Features:
- Date/time range selection (from/to)
- Real-time prediction generation
- Interactive charts
- Data export (CSV/JSON)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pytz
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

class WeatherPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Prediction Dashboard - WIB")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Timezone WIB (UTC+7)
        self.wib = pytz.timezone('Asia/Jakarta')
        
        # Model path
        self.model_path = "E:\\Internet of Things\\Tubes\\weather-iot\\examples\\model_training\\models\\rf_model_hourly_pkl"
        self.model = None
        self.predictions_df = None
        
        # Load model
        self.load_model()
        
        # Create UI
        self.create_widgets()
        
    def load_model(self):
        """Load trained model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✓ Model loaded from {self.model_path}")
            else:
                messagebox.showerror("Error", 
                    f"Model file not found: {self.model_path}\n\n"
                    "Please ensure the model file is in the same directory as this script.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
    
    def create_widgets(self):
        """Create main UI components"""
        
        # Title with WIB timezone indicator
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_label = tk.Label(title_frame, text="🌤️ Weather Prediction Dashboard (WIB)", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)
        
        # Control Panel
        control_frame = tk.Frame(self.root, bg='#ecf0f1', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Date/Time Inputs
        tk.Label(control_frame, text="FROM:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1').grid(row=0, column=0, padx=10, pady=10, sticky='e')
        
        # From Date (WIB timezone)
        now_wib = datetime.now(self.wib)
        self.from_date = tk.StringVar(value=now_wib.strftime("%Y-%m-%d"))
        from_date_entry = ttk.Entry(control_frame, textvariable=self.from_date, width=12, font=('Arial', 10))
        from_date_entry.grid(row=0, column=1, padx=5, pady=10)
        tk.Label(control_frame, text="Date (YYYY-MM-DD)", font=('Arial', 8), 
                bg='#ecf0f1', fg='gray').grid(row=1, column=1)
        
        # From Hour
        self.from_hour = tk.IntVar(value=0)
        from_hour_spin = tk.Spinbox(control_frame, from_=0, to=23, textvariable=self.from_hour, 
                                    width=5, font=('Arial', 10))
        from_hour_spin.grid(row=0, column=2, padx=5, pady=10)
        tk.Label(control_frame, text="Hour (0-23)", font=('Arial', 8), 
                bg='#ecf0f1', fg='gray').grid(row=1, column=2)
        
        # Separator
        tk.Label(control_frame, text="→", font=('Arial', 16), 
                bg='#ecf0f1').grid(row=0, column=3, padx=20)
        
        # To Date
        tk.Label(control_frame, text="TO:", font=('Arial', 10, 'bold'), 
                bg='#ecf0f1').grid(row=0, column=4, padx=10, pady=10, sticky='e')
        
        # Default to 3 days ahead (WIB)
        tomorrow = (now_wib + timedelta(days=3)).strftime("%Y-%m-%d")
        self.to_date = tk.StringVar(value=tomorrow)
        to_date_entry = ttk.Entry(control_frame, textvariable=self.to_date, width=12, font=('Arial', 10))
        to_date_entry.grid(row=0, column=5, padx=5, pady=10)
        tk.Label(control_frame, text="Date (YYYY-MM-DD)", font=('Arial', 8), 
                bg='#ecf0f1', fg='gray').grid(row=1, column=5)
        
        # To Hour
        self.to_hour = tk.IntVar(value=23)
        to_hour_spin = tk.Spinbox(control_frame, from_=0, to=23, textvariable=self.to_hour, 
                                  width=5, font=('Arial', 10))
        to_hour_spin.grid(row=0, column=6, padx=5, pady=10)
        tk.Label(control_frame, text="Hour (0-23)", font=('Arial', 8), 
                bg='#ecf0f1', fg='gray').grid(row=1, column=6)
        
        # Predict Button
        predict_btn = tk.Button(control_frame, text="🔮 Generate Predictions", 
                               command=self.generate_predictions,
                               font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                               relief='raised', bd=3, padx=20, pady=8,
                               cursor='hand2')
        predict_btn.grid(row=0, column=7, padx=20, pady=10, rowspan=2)
        
        # Export Buttons
        export_frame = tk.Frame(control_frame, bg='#ecf0f1')
        export_frame.grid(row=0, column=8, padx=10, rowspan=2)
        
        tk.Button(export_frame, text="💾 Export CSV", command=self.export_csv,
                 font=('Arial', 9), bg='#27ae60', fg='white', padx=10, pady=5).pack(pady=2)
        tk.Button(export_frame, text="📄 Export JSON", command=self.export_json,
                 font=('Arial', 9), bg='#e67e22', fg='white', padx=10, pady=5).pack(pady=2)
        
        # Main Content Area
        content_frame = tk.Frame(self.root, bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left: Data Table
        table_frame = tk.LabelFrame(content_frame, text="📊 Prediction Data", 
                                    font=('Arial', 11, 'bold'), bg='white', relief='groove', bd=2)
        table_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Treeview for data
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(table_frame, yscrollcommand=tree_scroll.set, height=15)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        tree_scroll.config(command=self.tree.yview)
        
        # Configure columns
        self.tree['columns'] = ('DateTime', 'Temp', 'Humidity', 'Pressure', 'Wind', 'Rain')
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('DateTime', width=150, anchor='center')
        self.tree.column('Temp', width=80, anchor='center')
        self.tree.column('Humidity', width=80, anchor='center')
        self.tree.column('Pressure', width=80, anchor='center')
        self.tree.column('Wind', width=80, anchor='center')
        self.tree.column('Rain', width=80, anchor='center')
        
        # Headings
        self.tree.heading('DateTime', text='Date & Time')
        self.tree.heading('Temp', text='Temp (°C)')
        self.tree.heading('Humidity', text='Humidity (%)')
        self.tree.heading('Pressure', text='Pressure (hPa)')
        self.tree.heading('Wind', text='Wind (m/s)')
        self.tree.heading('Rain', text='Rain (mm)')
        
        # Right: Charts
        chart_frame = tk.LabelFrame(content_frame, text="📈 Visualization", 
                                   font=('Arial', 11, 'bold'), bg='white', relief='groove', bd=2)
        chart_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Matplotlib figure
        self.fig = Figure(figsize=(8, 10), dpi=90)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready", 
                                   font=('Arial', 9), bg='#34495e', fg='white',
                                   anchor='w', relief='sunken')
        self.status_bar.pack(fill='x', side='bottom')
    
    def generate_predictions(self):
        """Generate predictions for selected time range"""
        if self.model is None:
            messagebox.showerror("Error", "Model not loaded!")
            return
        
        try:
            # Parse dates in WIB timezone
            from_datetime = datetime.strptime(self.from_date.get(), "%Y-%m-%d")
            from_datetime = from_datetime.replace(hour=self.from_hour.get())
            from_datetime = self.wib.localize(from_datetime)
            
            to_datetime = datetime.strptime(self.to_date.get(), "%Y-%m-%d")
            to_datetime = to_datetime.replace(hour=self.to_hour.get())
            to_datetime = self.wib.localize(to_datetime)
            
            if from_datetime >= to_datetime:
                messagebox.showerror("Error", "FROM date/time must be before TO date/time!")
                return
            
            # Calculate hours
            hours_diff = int((to_datetime - from_datetime).total_seconds() / 3600) + 1
            
            if hours_diff > 720:  # 30 days
                messagebox.showwarning("Warning", 
                    f"Prediction range is large ({hours_diff} hours / {hours_diff/24:.1f} days).\n"
                    "This may take some time...")
            
            self.status_bar.config(text=f"Generating {hours_diff} hours of predictions...")
            self.root.update()
            
            # Generate predictions
            predictions = []
            current_time = from_datetime
            
            while current_time <= to_datetime:
                # Create input
                input_data = pd.DataFrame([[
                    current_time.hour,
                    current_time.day,
                    current_time.month,
                    current_time.year
                ]], columns=['hour', 'day', 'month', 'year'])
                
                # Predict
                pred = self.model.predict(input_data)[0]
                
                predictions.append({
                    'datetime': current_time,
                    'datetime_str': current_time.strftime('%Y-%m-%d %H:%M WIB'),
                    'temperature': pred[0],
                    'humidity': pred[1],
                    'pressure': pred[2],
                    'wind_speed': pred[3],
                    'rain': pred[4]
                })
                
                current_time += timedelta(hours=1)
            
            # Create DataFrame
            self.predictions_df = pd.DataFrame(predictions)
            
            # Update display
            self.update_table()
            self.update_chart()
            
            self.status_bar.config(text=f"✓ Generated {len(predictions)} predictions successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format:\n{str(e)}\n\nUse YYYY-MM-DD format.")
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{str(e)}")
            self.status_bar.config(text="Error occurred!")
    
    def update_table(self):
        """Update data table"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new data
        for idx, row in self.predictions_df.iterrows():
            self.tree.insert('', 'end', values=(
                row['datetime_str'],
                f"{row['temperature']:.1f}",
                f"{row['humidity']:.1f}",
                f"{row['pressure']:.1f}",
                f"{row['wind_speed']:.1f}",
                f"{row['rain']:.2f}"
            ))
    
    def update_chart(self):
        """Update visualization charts"""
        self.fig.clear()
        
        # Create 4 subplots
        ax1 = self.fig.add_subplot(4, 1, 1)
        ax2 = self.fig.add_subplot(4, 1, 2)
        ax3 = self.fig.add_subplot(4, 1, 3)
        ax4 = self.fig.add_subplot(4, 1, 4)
        
        hours = range(len(self.predictions_df))
        
        # Temperature
        ax1.plot(hours, self.predictions_df['temperature'], color='#e74c3c', linewidth=2)
        ax1.fill_between(hours, self.predictions_df['temperature'], alpha=0.3, color='#e74c3c')
        ax1.set_ylabel('Temp (°C)', fontweight='bold')
        ax1.set_title('🌡️ Temperature', fontweight='bold', loc='left')
        ax1.grid(True, alpha=0.3)
        
        # Humidity
        ax2.plot(hours, self.predictions_df['humidity'], color='#3498db', linewidth=2)
        ax2.fill_between(hours, self.predictions_df['humidity'], alpha=0.3, color='#3498db')
        ax2.set_ylabel('Humidity (%)', fontweight='bold')
        ax2.set_title('💧 Humidity', fontweight='bold', loc='left')
        ax2.grid(True, alpha=0.3)
        
        # Wind Speed
        ax3.plot(hours, self.predictions_df['wind_speed'], color='#2ecc71', linewidth=2)
        ax3.fill_between(hours, self.predictions_df['wind_speed'], alpha=0.3, color='#2ecc71')
        ax3.set_ylabel('Wind (m/s)', fontweight='bold')
        ax3.set_title('💨 Wind Speed', fontweight='bold', loc='left')
        ax3.grid(True, alpha=0.3)
        
        # Rain
        ax4.bar(hours, self.predictions_df['rain'], color='#9b59b6', alpha=0.7)
        ax4.set_ylabel('Rain (mm)', fontweight='bold')
        ax4.set_xlabel('Hours from start', fontweight='bold')
        ax4.set_title('🌧️ Rainfall', fontweight='bold', loc='left')
        ax4.grid(True, alpha=0.3, axis='y')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def export_csv(self):
        """Export predictions to CSV"""
        if self.predictions_df is None or len(self.predictions_df) == 0:
            messagebox.showwarning("Warning", "No predictions to export! Generate predictions first.")
            return
        
        now_wib = datetime.now(self.wib)
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"weather_predictions_{now_wib.strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            try:
                self.predictions_df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Exported to:\n{filename}")
                self.status_bar.config(text=f"✓ Exported to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_json(self):
        """Export predictions to JSON"""
        if self.predictions_df is None or len(self.predictions_df) == 0:
            messagebox.showwarning("Warning", "No predictions to export! Generate predictions first.")
            return
        
        now_wib = datetime.now(self.wib)
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"weather_predictions_{now_wib.strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            try:
                # Convert datetime to string for JSON
                export_df = self.predictions_df.copy()
                export_df['datetime'] = export_df['datetime'].astype(str)
                export_df.to_json(filename, orient='records', indent=2)
                messagebox.showinfo("Success", f"Exported to:\n{filename}")
                self.status_bar.config(text=f"✓ Exported to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

def main():
    root = tk.Tk()
    app = WeatherPredictionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
