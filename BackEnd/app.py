import pickle
import pandas as pd
import numpy as np
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production as per requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------- Load Model & Artifacts -----------------

def load_artifacts(model_path, scaler_path, feature_order_path):
    """
    Loads the trained model, scaler, and feature order from pickle files.
    """
    try:
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)  # Load trained ML model
        with open(scaler_path, 'rb') as scaler_file:
            scaler = pickle.load(scaler_file)  # Load data scaler for normalization
        with open(feature_order_path, 'rb') as feature_file:
            feature_order = pickle.load(feature_file)  # Load feature order for input alignment
        return model, scaler, feature_order
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit program if files are not found


# Define file paths for model, scaler, and feature order
MODEL_PATH = "incident_model.pkl"
SCALER_PATH = "incident_scaler.pkl"
FEATURE_ORDER_PATH = "feature_order.pkl"

# Load model, scaler, and feature order into memory
model, scaler, feature_order = load_artifacts(MODEL_PATH, SCALER_PATH, FEATURE_ORDER_PATH)


# ----------------- Data Preprocessing -----------------

def prepare_input(date, assignment_group, feature_order):
    """
    Processes the input date and assignment group into a format suitable for model prediction.
    """
    try:
        # Extract day, month, and year from the date
        day, month, year = date.day, date.month, date.year

        # Create a DataFrame with the correct feature order and initialize all columns with zero
        input_data = pd.DataFrame(columns=feature_order)
        input_data.loc[0] = 0

        # Fill in the date-related features
        input_data.at[0, 'day'] = day
        input_data.at[0, 'month'] = month
        input_data.at[0, 'year'] = year

        # One-hot encode the assignment group
        one_hot_column = f'Assignment_group_{assignment_group}'
        if one_hot_column in feature_order:
            input_data.at[0, one_hot_column] = 1  # Set the respective one-hot column to 1
        else:
            print(f"Warning: '{assignment_group}' not found in training set.")
            return None  # Return None if the assignment group was not seen during training

        print("Processed Input Data:\n", input_data)  # Debugging output
        return input_data
    except Exception as e:
        print(f"Error in prepare_input: {e}")
        return None


# ----------------- Prediction -----------------

def predict_incident_percentage(model, scaler, input_data):
    """
    Predicts incident priority percentages using the trained model.
    """
    try:
        # Normalize the input data using the loaded scaler
        input_scaled = scaler.transform(input_data)

        # Get raw predictions from the trained model
        predicted_output = model.predict(input_scaled)
        print(f"Raw Model Output: {predicted_output}")  # For Debugging output

        # Convert output to a flat NumPy array
        predicted_percentages = np.array(predicted_output).flatten()
        print(f"Processed Predictions: {predicted_percentages}")  # For Debugging output

        # Ensure predictions do not have negative values
        predicted_percentages = np.maximum(predicted_percentages, 0)

        # Normalize predictions so they sum up to 100%
        total = np.sum(predicted_percentages)
        if total > 0:
            predicted_percentages = (predicted_percentages / total) * 100
        else:
            predicted_percentages = np.array([25, 25, 25, 25])  # Default equal distribution if total is 0

        # Round percentages to two decimal places for better readability
        predicted_percentages = np.round(predicted_percentages, 2) #rounding off

        print(f"Final Normalized Predictions: {predicted_percentages}")  # For Debugging output

        # Return predictions mapped to priority labels
        return dict(zip(["P1", "P2", "P3", "P4"], predicted_percentages))
    except Exception as e:
        print(f"Error in predict_incident_percentage: {e}")
        return {"error": str(e)}


# ----------------- API Endpoints -----------------

# Define request body format for FastAPI
class PredictionRequest(BaseModel):
    date: str  # Date of the incident in YYYY-MM-DD format
    assignment_group: str  # Assignment group name


@app.post("/predict")
def predict(request: PredictionRequest):
    """
    API endpoint to predict incident priority percentages based on input date and assignment group.
    """
    try:
        # Convert date string to datetime object
        try:
            incident_date = datetime.strptime(request.date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        assignment_group = request.assignment_group  # Extract assignment group from request

        # Prepare input data for the model
        input_data = prepare_input(incident_date, assignment_group, feature_order)
        if input_data is None:
            raise HTTPException(status_code=400, detail=f"Invalid assignment group: {assignment_group}")

        # Predict incident priority percentages
        predictions = predict_incident_percentage(model, scaler, input_data)

        # Return structured JSON response
        return {
            "date": request.date,
            "assignment_group": assignment_group,
            "predictions": predictions
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
