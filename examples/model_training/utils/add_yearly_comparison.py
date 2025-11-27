"""
Add yearly comparison visualization to hourly training notebook
"""
import json

# Read notebook
notebook_path = r'e:\Internet of Things\Tubes\weather-iot\examples\model_training\notebooks\weather_model_training_hourly.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# New cells for yearly comparison
new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## 13. Yearly Performance Comparison\n",
            "\n",
            "Analyze model performance across different years to identify trends and consistency."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Calculate metrics per year\n",
            "import warnings\n",
            "warnings.filterwarnings('ignore')\n",
            "\n",
            "# Add year column to test set for grouping\n",
            "X_test_with_year = X_test.copy()\n",
            "y_test_with_year = y_test.copy()\n",
            "\n",
            "# Get predictions for full test set\n",
            "y_pred_full = rf_model_hourly.predict(X_test)\n",
            "\n",
            "# Create DataFrame for analysis\n",
            "analysis_df = pd.DataFrame({\n",
            "    'year': X_test_with_year['year'],\n",
            "    'temp_actual': y_test_with_year['temperature'],\n",
            "    'temp_pred': y_pred_full[:, 0],\n",
            "    'humidity_actual': y_test_with_year['humidity'],\n",
            "    'humidity_pred': y_pred_full[:, 1],\n",
            "    'pressure_actual': y_test_with_year['pressure'],\n",
            "    'pressure_pred': y_pred_full[:, 2],\n",
            "    'wind_actual': y_test_with_year['wind_speed'],\n",
            "    'wind_pred': y_pred_full[:, 3]\n",
            "})\n",
            "\n",
            "# Calculate yearly metrics\n",
            "yearly_metrics = []\n",
            "\n",
            "for year in sorted(analysis_df['year'].unique()):\n",
            "    year_data = analysis_df[analysis_df['year'] == year]\n",
            "    \n",
            "    if len(year_data) < 10:  # Skip years with too few samples\n",
            "        continue\n",
            "    \n",
            "    metrics = {\n",
            "        'Year': int(year),\n",
            "        'Samples': len(year_data),\n",
            "        'Temp_MAE': mean_absolute_error(year_data['temp_actual'], year_data['temp_pred']),\n",
            "        'Temp_R2': r2_score(year_data['temp_actual'], year_data['temp_pred']),\n",
            "        'Humidity_MAE': mean_absolute_error(year_data['humidity_actual'], year_data['humidity_pred']),\n",
            "        'Humidity_R2': r2_score(year_data['humidity_actual'], year_data['humidity_pred']),\n",
            "        'Wind_MAE': mean_absolute_error(year_data['wind_actual'], year_data['wind_pred']),\n",
            "        'Wind_R2': r2_score(year_data['wind_actual'], year_data['wind_pred'])\n",
            "    }\n",
            "    yearly_metrics.append(metrics)\n",
            "\n",
            "yearly_df = pd.DataFrame(yearly_metrics)\n",
            "\n",
            "print(\"=\"*100)\n",
            "print(\"YEARLY PERFORMANCE COMPARISON\")\n",
            "print(\"=\"*100)\n",
            "print(yearly_df.to_string(index=False))\n",
            "print(\"=\"*100)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Visualize Yearly Performance"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Create comprehensive yearly comparison visualization\n",
            "fig, axes = plt.subplots(2, 2, figsize=(16, 10))\n",
            "\n",
            "years = yearly_df['Year']\n",
            "\n",
            "# Temperature Performance\n",
            "ax1 = axes[0, 0]\n",
            "ax1_twin = ax1.twinx()\n",
            "bars1 = ax1.bar(years, yearly_df['Temp_MAE'], color='#e74c3c', alpha=0.7, label='MAE')\n",
            "line1 = ax1_twin.plot(years, yearly_df['Temp_R2'], color='#2c3e50', marker='o', \n",
            "                      linewidth=2, markersize=8, label='R²')\n",
            "ax1.set_xlabel('Year', fontweight='bold')\n",
            "ax1.set_ylabel('MAE (°C)', fontweight='bold', color='#e74c3c')\n",
            "ax1_twin.set_ylabel('R² Score', fontweight='bold', color='#2c3e50')\n",
            "ax1.set_title('🌡️ Temperature - Yearly Performance', fontweight='bold', fontsize=12)\n",
            "ax1.tick_params(axis='y', labelcolor='#e74c3c')\n",
            "ax1_twin.tick_params(axis='y', labelcolor='#2c3e50')\n",
            "ax1.grid(True, alpha=0.3, axis='y')\n",
            "ax1.legend(loc='upper left')\n",
            "ax1_twin.legend(loc='upper right')\n",
            "\n",
            "# Humidity Performance\n",
            "ax2 = axes[0, 1]\n",
            "ax2_twin = ax2.twinx()\n",
            "bars2 = ax2.bar(years, yearly_df['Humidity_MAE'], color='#3498db', alpha=0.7, label='MAE')\n",
            "line2 = ax2_twin.plot(years, yearly_df['Humidity_R2'], color='#2c3e50', marker='s', \n",
            "                      linewidth=2, markersize=8, label='R²')\n",
            "ax2.set_xlabel('Year', fontweight='bold')\n",
            "ax2.set_ylabel('MAE (%)', fontweight='bold', color='#3498db')\n",
            "ax2_twin.set_ylabel('R² Score', fontweight='bold', color='#2c3e50')\n",
            "ax2.set_title('💧 Humidity - Yearly Performance', fontweight='bold', fontsize=12)\n",
            "ax2.tick_params(axis='y', labelcolor='#3498db')\n",
            "ax2_twin.tick_params(axis='y', labelcolor='#2c3e50')\n",
            "ax2.grid(True, alpha=0.3, axis='y')\n",
            "ax2.legend(loc='upper left')\n",
            "ax2_twin.legend(loc='upper right')\n",
            "\n",
            "# Wind Speed Performance\n",
            "ax3 = axes[1, 0]\n",
            "ax3_twin = ax3.twinx()\n",
            "bars3 = ax3.bar(years, yearly_df['Wind_MAE'], color='#2ecc71', alpha=0.7, label='MAE')\n",
            "line3 = ax3_twin.plot(years, yearly_df['Wind_R2'], color='#2c3e50', marker='^', \n",
            "                      linewidth=2, markersize=8, label='R²')\n",
            "ax3.set_xlabel('Year', fontweight='bold')\n",
            "ax3.set_ylabel('MAE (m/s)', fontweight='bold', color='#2ecc71')\n",
            "ax3_twin.set_ylabel('R² Score', fontweight='bold', color='#2c3e50')\n",
            "ax3.set_title('💨 Wind Speed - Yearly Performance', fontweight='bold', fontsize=12)\n",
            "ax3.tick_params(axis='y', labelcolor='#2ecc71')\n",
            "ax3_twin.tick_params(axis='y', labelcolor='#2c3e50')\n",
            "ax3.grid(True, alpha=0.3, axis='y')\n",
            "ax3.legend(loc='upper left')\n",
            "ax3_twin.legend(loc='upper right')\n",
            "\n",
            "# Sample Count per Year\n",
            "ax4 = axes[1, 1]\n",
            "bars4 = ax4.bar(years, yearly_df['Samples'], color='#9b59b6', alpha=0.7)\n",
            "ax4.set_xlabel('Year', fontweight='bold')\n",
            "ax4.set_ylabel('Number of Test Samples', fontweight='bold')\n",
            "ax4.set_title('📊 Test Data Distribution by Year', fontweight='bold', fontsize=12)\n",
            "ax4.grid(True, alpha=0.3, axis='y')\n",
            "\n",
            "# Add value labels on bars\n",
            "for bar in bars4:\n",
            "    height = bar.get_height()\n",
            "    ax4.text(bar.get_x() + bar.get_width()/2., height,\n",
            "             f'{int(height):,}', ha='center', va='bottom', fontsize=9)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('../outputs/yearly_performance_comparison.png', dpi=150, bbox_inches='tight')\n",
            "plt.show()\n",
            "\n",
            "print(\"✓ Saved as '../outputs/yearly_performance_comparison.png'\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Yearly Trends Summary"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Calculate overall statistics\n",
            "print(\"=\"*100)\n",
            "print(\"YEARLY PERFORMANCE SUMMARY\")\n",
            "print(\"=\"*100)\n",
            "\n",
            "print(\"\\n📈 Temperature:\")\n",
            "print(f\"  Average MAE across years: {yearly_df['Temp_MAE'].mean():.4f} °C\")\n",
            "print(f\"  Average R² across years: {yearly_df['Temp_R2'].mean():.4f}\")\n",
            "print(f\"  Best year (lowest MAE): {yearly_df.loc[yearly_df['Temp_MAE'].idxmin(), 'Year']:.0f} (MAE: {yearly_df['Temp_MAE'].min():.4f})\")\n",
            "print(f\"  Worst year (highest MAE): {yearly_df.loc[yearly_df['Temp_MAE'].idxmax(), 'Year']:.0f} (MAE: {yearly_df['Temp_MAE'].max():.4f})\")\n",
            "\n",
            "print(\"\\n💧 Humidity:\")\n",
            "print(f\"  Average MAE across years: {yearly_df['Humidity_MAE'].mean():.4f} %\")\n",
            "print(f\"  Average R² across years: {yearly_df['Humidity_R2'].mean():.4f}\")\n",
            "print(f\"  Best year (lowest MAE): {yearly_df.loc[yearly_df['Humidity_MAE'].idxmin(), 'Year']:.0f} (MAE: {yearly_df['Humidity_MAE'].min():.4f})\")\n",
            "print(f\"  Worst year (highest MAE): {yearly_df.loc[yearly_df['Humidity_MAE'].idxmax(), 'Year']:.0f} (MAE: {yearly_df['Humidity_MAE'].max():.4f})\")\n",
            "\n",
            "print(\"\\n💨 Wind Speed:\")\n",
            "print(f\"  Average MAE across years: {yearly_df['Wind_MAE'].mean():.4f} m/s\")\n",
            "print(f\"  Average R² across years: {yearly_df['Wind_R2'].mean():.4f}\")\n",
            "print(f\"  Best year (lowest MAE): {yearly_df.loc[yearly_df['Wind_MAE'].idxmin(), 'Year']:.0f} (MAE: {yearly_df['Wind_MAE'].min():.4f})\")\n",
            "print(f\"  Worst year (highest MAE): {yearly_df.loc[yearly_df['Wind_MAE'].idxmax(), 'Year']:.0f} (MAE: {yearly_df['Wind_MAE'].max():.4f})\")\n",
            "\n",
            "print(\"\\n📊 Data Coverage:\")\n",
            "print(f\"  Total test samples: {yearly_df['Samples'].sum():,}\")\n",
            "print(f\"  Years analyzed: {len(yearly_df)}\")\n",
            "print(f\"  Average samples per year: {yearly_df['Samples'].mean():.0f}\")\n",
            "\n",
            "print(\"=\"*100)\n",
            "\n",
            "# Check for trends\n",
            "temp_trend = \"improving\" if yearly_df['Temp_R2'].iloc[-3:].mean() > yearly_df['Temp_R2'].iloc[:3].mean() else \"declining\"\n",
            "print(f\"\\n📈 Recent Trend: Model performance appears to be {temp_trend} in recent years.\")\n",
            "print(\"=\"*100)"
        ]
    }
]

# Find the index where to insert (after section 12 - 72-hour forecast)
# We'll insert before the last metadata cells
insert_index = len(notebook['cells'])

# Insert new cells
for cell in new_cells:
    notebook['cells'].insert(insert_index, cell)
    insert_index += 1

# Save updated notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Successfully added yearly comparison cells to: {notebook_path}")
print(f"  Total cells now: {len(notebook['cells'])}")
print(f"  New cells added: {len(new_cells)}")
print("\nNew section added: '13. Yearly Performance Comparison'")
print("  - Yearly metrics table")
print("  - 4-panel visualization (Temp, Humidity, Wind, Samples)")
print("  - Yearly trends summary")
