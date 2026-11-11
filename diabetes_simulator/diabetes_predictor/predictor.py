import pandas as pd
from pathlib import Path
import joblib


BASE_DIR = Path(__file__).resolve().parents[2]

model_path = BASE_DIR/'Trained Model'/'nb_pipe'/'diabetes_pipeline.pkl'
threshold_path = BASE_DIR/'Trained Model'/'nb_pipe'/'logreg_threshold.pkl'

class DiabetesPredictorModel:
    def __init__(self):
        self.model = joblib.load(model_path)
        self.threshold = joblib.load(threshold_path)


    def predict(self, user_features):
        df_dict = self.conversion(user_features)
        user_df = pd.DataFrame([df_dict])

        # Get the probability of diabetes (class 1)
        prob_positive = self.model.predict_proba(user_df)[:, 1][0]

        predicted_class = 1 if prob_positive >= self.threshold else 0

        return {
            'probability': round(prob_positive, 4),
            'risk_class': predicted_class,
            'prob_percent': round(prob_positive * 100, 1),
            'message': f'Diabetic with {prob_positive * 100:.2f}% Confidence' if predicted_class == 1 else f'Healthy with {(1 - prob_positive) * 100:.2f}% Confidence'
        }

    def conversion(self, the_list):
        the_dict = {
            'Pregnancies': the_list[0],
            'Glucose': the_list[1],
            'BloodPressure': the_list[2],
            'SkinThickness': the_list[3],
            'Insulin': the_list[4],
            'BMI': the_list[5],
            'DiabetesPedigreeFunction': the_list[6],
            'Age': the_list[7],
        }

        return the_dict