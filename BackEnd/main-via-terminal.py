import pickle
import pandas as pd
import numpy as np
import sys
from datetime import datetime


# ----------------- Load Model & Artifacts -----------------
def load_artifacts(model_path, scaler_path, feature_order_path):
    """
    Loads the trained model, scaler, and feature order from pickle files.

    Parameters:
        model_path (str): Path to the saved model file.
        scaler_path (str): Path to the saved scaler file.
        feature_order_path (str): Path to the saved feature order file.

    Returns:
        tuple: Loaded model, scaler, and feature order list.

    Raises:
        FileNotFoundError: If any of the required files are missing.
    """
    try:
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
        with open(scaler_path, 'rb') as scaler_file:
            scaler = pickle.load(scaler_file)
        with open(feature_order_path, 'rb') as feature_file:
            feature_order = pickle.load(feature_file)
        return model, scaler, feature_order
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit program if files are not found


# ----------------- Data Preprocessing -----------------
def prepare_input(date, assignment_group, feature_order):
    """
    Processes the user-provided date and assignment group into a format suitable for model prediction.

    Parameters:
        date (datetime): The incident date provided by the user.
        assignment_group (str): The assignment group entered by the user.
        feature_order (list): The list of feature names used during model training.

    Returns:
        pd.DataFrame: A DataFrame with one-hot encoded features for the model.
                      Returns None if the assignment group is not found in the training data.
    """
    day, month, year = date.day, date.month, date.year

    # Create a DataFrame with the same feature columns as used during training
    input_data = pd.DataFrame(columns=feature_order)
    input_data.loc[0] = 0  # Initialize all columns with zero
    input_data.at[0, 'day'] = day
    input_data.at[0, 'month'] = month
    input_data.at[0, 'year'] = year

    # One-hot encode the assignment group
    one_hot_column = f'Assignment_group_{assignment_group}'
    if one_hot_column in feature_order:
        input_data.at[0, one_hot_column] = 1
    else:
        print(f"Warning: '{assignment_group}' not found in training set.")
        return None  # Return None if the assignment group was not seen in training

    return input_data


# ----------------- Prediction -----------------
def predict_incident_percentage(model, scaler, input_data):
    """
    Predicts incident priority percentages using the trained model.

    Parameters:
        model (sklearn model): The trained machine learning model.
        scaler (sklearn scaler): The trained MinMaxScaler for input normalization.
        input_data (pd.DataFrame): Preprocessed input data.

    Returns:
        dict: A dictionary with predicted percentages for P1, P2, P3, and P4 categories.
    """
    input_scaled = scaler.transform(input_data)  # Normalize input
    predicted_percentages = model.predict(input_scaled)[0]

    # Ensure no negative values in prediction
    predicted_percentages = np.maximum(predicted_percentages, 0)

    # Normalize percentages to sum up to 100
    total = np.sum(predicted_percentages)
    if total > 0:
        predicted_percentages = (predicted_percentages / total) * 100
    else:
        predicted_percentages = np.array([25, 25, 25, 25])  # Equal split if total is zero

    return dict(zip(["P1", "P2", "P3", "P4"], predicted_percentages))


# -----------------  User Input Handling -----------------
def get_user_input():
    """
    Handles user input for the date and validates its format.

    Returns:
        datetime: The validated incident date.
    """
    while True:
        user_date_input = input("Enter the date (YYYY-MM-DD): ").strip()
        try:
            return datetime.strptime(user_date_input, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter a valid date in YYYY-MM-DD format.")


def display_prediction(future_date, assignment_group, predictions):
    """
    Displays the predicted incident priority percentages in a formatted output.

    Parameters:
        future_date (datetime): The date for which predictions are made.
        assignment_group (str): The assignment group for the prediction.
        predictions (dict): Dictionary containing predicted percentages for each priority level.
    """
    print(f"\nPredicted Incident Percentages on {future_date.date()} for '{assignment_group}':")
    for priority, percentage in predictions.items():
        print(f"  - {priority}: {percentage:.2f}%")


# ----------------- Main Execution -----------------
if __name__ == "__main__":
    """
    Main script execution. Loads model artifacts, collects user input, 
    preprocesses data, runs predictions, and displays results.
    """

    # Load model and preprocessing artifacts
    model, scaler, feature_order = load_artifacts(
        "incident_model.pkl", "incident_scaler.pkl", "feature_order.pkl"
    )

    # Get user inputs
    while True:
        # Always ask for date and assignment group at least once
        future_date = get_user_input()
        assignment_group = input("Enter Assignment Group: ").strip()

        # Prepare input and make predictions
        input_data = prepare_input(future_date, assignment_group, feature_order)

        if input_data is not None:
            predictions = predict_incident_percentage(model, scaler, input_data)
            display_prediction(future_date, assignment_group, predictions)
        else:
            print(f"Prediction could not be made for '{assignment_group}'. Check if it is a valid assignment group.")

        # Ask if the user wants to continue
        continue_choice = input("Do you want to make another prediction? (yes/no): ").strip().lower()

        if continue_choice != "yes":
            print("Exiting program.")
            break  # Exit loop if user doesn't enter 'yes'
