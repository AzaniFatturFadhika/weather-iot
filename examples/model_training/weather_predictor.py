import pickle
import os
import pandas as pd
import numpy as np

class WeatherPredictor:
    def __init__(self, models_dir):
        """
        Initialize the WeatherPredictor by loading the trained models.
        
        Args:
            models_dir (str): Path to the directory containing the .pkl model files.
        """
        self.models_dir = models_dir
        self.reg_model_path = os.path.join(models_dir, 'weather_regression_model.pkl')
        self.class_model_path = os.path.join(models_dir, 'weather_rain_classifier.pkl')
        
        self.reg_model = self._load_model(self.reg_model_path)
        self.class_model = self._load_model(self.class_model_path)
        
    def _load_model(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")
        
        with open(path, 'rb') as f:
            return pickle.load(f)
            
    def predict(self, input_data):
        """
        Predict weather parameters and rain status.
        
        Args:
            input_data (pd.DataFrame or dict): Input features for prediction. 
                                               Must contain all features used in training.
        
        Returns:
            dict: Combined predictions.
        """
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
            
        # Ensure input columns match model requirements (basic check)
        # In a real scenario, you'd add more robust feature validation/preprocessing here
        
        # 1. Predict Regression Targets (Temperature, Humidity, Pressure, Wind Speed)
        reg_preds = self.reg_model.predict(input_data)
        
        # 2. Predict Rain Status (Classification)
        rain_pred = self.class_model.predict(input_data)
        rain_prob = self.class_model.predict_proba(input_data)[:, 1] # Probability of rain
        
        # Combine results
        # Assuming single row prediction for simplicity in return format
        result = {
            'temperature': reg_preds[0][0],
            'humidity': reg_preds[0][1],
            'pressure': reg_preds[0][2],
            'wind_speed': reg_preds[0][3],
            'is_raining': int(rain_pred[0]),
            'rain_probability': float(rain_prob[0])
        }
        
        return result

if __name__ == "__main__":
    # Example Usage
    models_directory = r'd:\laragon\www\weather-iot\examples\model_training\models'
    
    try:
        predictor = WeatherPredictor(models_directory)
        
        # Dummy input data (replace with actual feature values)
        # NOTE: You need to provide ALL features that the model was trained on.
        # This includes the engineered features like lags, rolling means, etc.
        # For this example, we'll create a dummy row with random values matching the feature count.
        # In production, you would need a preprocessing pipeline to generate these features from raw data.
        
        # Get feature names from the model (if available) or define them manually based on training
        # For Random Forest, n_features_in_ gives the count
        n_features = predictor.reg_model.n_features_in_
        dummy_input = pd.DataFrame(np.random.rand(1, n_features))
        
        # Warning: This is just to test the mechanism. The prediction value will be garbage 
        # because the input is random noise.
        print("Testing with dummy input...")
        prediction = predictor.predict(dummy_input)
        print("\nPrediction Result:")
        print(prediction)
        
    except Exception as e:
        print(f"Error: {e}")
