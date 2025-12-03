import nbformat
import os

notebook_path = r'd:\laragon\www\weather-iot\examples\model_training\notebooks\weather_model_training_improved_v2.ipynb'

def append_save_cell(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Check if cell already exists to avoid duplicates
    for cell in nb.cells:
        if "Save Models" in cell.source:
            print("Save cell already exists.")
            return

    # Create Markdown Cell
    markdown_cell = nbformat.v4.new_markdown_cell("## 8. Save Models")
    nb.cells.append(markdown_cell)

    # Create Code Cell
    code_source = """import pickle
import os

# Create models directory if it doesn't exist
models_dir = 'D://laragon//www//weather-iot//examples//model_training//models//'
os.makedirs(models_dir, exist_ok=True)

# Save Regression Model
reg_model_path = os.path.join(models_dir, 'weather_regression_model.pkl')
with open(reg_model_path, 'wb') as f:
    pickle.dump(reg_model, f)
print(f"Regression model saved to: {reg_model_path}")

# Save Classification Model
class_model_path = os.path.join(models_dir, 'weather_rain_classifier.pkl')
with open(class_model_path, 'wb') as f:
    pickle.dump(class_model, f)
print(f"Classification model saved to: {class_model_path}")"""

    code_cell = nbformat.v4.new_code_cell(code_source)
    nb.cells.append(code_cell)

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    
    print(f"Appended save cells to {notebook_path}")

if __name__ == "__main__":
    append_save_cell(notebook_path)
