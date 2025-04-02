import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# Set a random seed to ensure reproducibility of results
np.random.seed(42)


# ----------------- Data Loading & Preprocessing -----------------

def load_data(file_path):
    """
    Loads the dataset from an Excel file and performs basic cleaning.

    - Ensures required columns ('Date', 'Priority', 'Assignment_group') are present.
    - Converts 'Date' column to datetime format.
    - Drops any rows with missing values in the essential columns.

    Returns:
        Cleaned DataFrame with only necessary columns.
    """
    df = pd.read_excel(file_path, engine='openpyxl')

    # Ensure required columns exist
    required_columns = {'Date', 'Priority', 'Assignment_group'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing columns: {required_columns - set(df.columns)}")

    # Convert 'Date' to datetime format and drop rows with missing values
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date', 'Priority', 'Assignment_group'], inplace=True)

    return df[['Date', 'Assignment_group', 'Priority']].rename(
        columns={'Date': 'date', 'Priority': 'priority'}
    )


def transform_data(df):
    """
    Transforms the dataset by extracting date features and encoding categorical data.

    - Extracts day, month, and year from the 'date' column.
    - One-hot encodes the 'priority' column.
    - One-hot encodes the 'Assignment_group' column.
    - Drops unnecessary columns after encoding.

    Returns:
        Processed DataFrame with numerical values ready for model training.
    """
    # Extract date components
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year

    # One-hot encode 'priority'
    priority_dummies = pd.get_dummies(df['priority'], prefix='P')
    df = pd.concat([df, priority_dummies], axis=1)

    # One-hot encode 'Assignment_group'
    df = pd.get_dummies(df, columns=['Assignment_group'], drop_first=False)

    # Drop original 'date' and 'priority' columns as they are no longer needed
    df.drop(columns=['date', 'priority'], inplace=True)

    return df


def preprocess_data(file_path):
    """
    Loads and preprocesses the data for training.

    - Calls `load_data()` to clean the data.
    - Calls `transform_data()` to encode features and prepare data for modeling.

    Returns:
        Fully processed DataFrame ready for model training.
    """
    df = load_data(file_path)
    return transform_data(df)


# ----------------- Model Training & Saving -----------------

def train_model(X, y):
    """
    Trains a Linear Regression model to predict incident priority distributions.

    - Normalizes input features using Min-Max Scaling.
    - Splits the dataset into training (80%) and testing (20%).
    - Trains a Linear Regression model.
    - Evaluates the model using Mean Squared Error (MSE).

    Returns:
        Trained model and scaler object.
    """
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Split dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate model performance
    mse = mean_squared_error(y_test, model.predict(X_test))
    print(f"Model Mean Squared Error: {mse:.2f}")

    return model, scaler


def save_artifact(obj, file_path):
    """
    Saves a Python object (such as a model or scaler) to a file using pickle.

    Parameters:
        obj: The Python object to be saved.
        file_path: The destination file path.
    """
    with open(file_path, 'wb') as file:
        print(f"Pickle created as {file_path} for {obj}")
        pickle.dump(obj, file)


def train_and_save_model(data_path, model_path, scaler_path, feature_path):
    """
    Loads data, trains a model, and saves the trained artifacts.

    - Loads and preprocesses the dataset.
    - Separates features (X) and target labels (y).
    - Trains a Linear Regression model.
    - Saves the trained model, scaler, and feature order.

    Returns:
        List of feature names used in training.
    """
    df = preprocess_data(data_path)

    # Separate input features (X) and target labels (y)
    x = df.drop(columns=[col for col in df.columns if col.startswith("P_")])
    y = df[[col for col in df.columns if col.startswith("P_")]]

    # Train model and scaler
    model, scaler = train_model(x, y)

    # Save model artifacts
    save_artifact(model, model_path)
    save_artifact(scaler, scaler_path)
    save_artifact(x.columns.tolist(), feature_path)

    return x.columns.tolist()


# ----------------- Main Execution -----------------

if __name__ == "__main__":
    """
    Main execution block:
    - Defines file paths.
    - Trains and saves the model.
    - Outputs a success message when training is complete.
    """
    DATA_PATH = 'telephonyinc_servicenow.xlsx'
    MODEL_PATH = 'incident_model.pkl'
    SCALER_PATH = 'incident_scaler.pkl'
    FEATURE_PATH = 'feature_order.pkl'

    feature_order = train_and_save_model(DATA_PATH, MODEL_PATH, SCALER_PATH, FEATURE_PATH)
    print("Model training complete. Artifacts saved.")
