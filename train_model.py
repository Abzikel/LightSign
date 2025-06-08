# Import libraries
import joblib
import os
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

# Function to train and save the model
def train_model(dataset_path, model_output_path):
    # Load dataset and import it to a DataFrame
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    # Separate characteristics from labels
    X = df[[
        "WRIST_X", "WRIST_Y",
        "THUMB_TIP_X", "THUMB_TIP_Y",
        "INDEX_TIP_X", "INDEX_TIP_Y",
        "MIDDLE_TIP_X", "MIDDLE_TIP_Y"
    ]]
    Y = df["label"]


    # Train model using GradientBoosting
    print("Training model using GradientBoostingClassifier...")
    model = GradientBoostingClassifier()
    model.fit(X, Y)
    print("¡Model trained successfully!")

    # Save trained model
    joblib.dump(model, model_output_path)
    print(f"Model saved on: {model_output_path}")

# Main to execute and save the model
if __name__ == "__main__":
    # Constants to get the dataset and path to save trained model
    dataset_file = os.path.expanduser("gestures_dataset.csv")
    model_file = "gesture_model.joblib"

    # Verify the dataset exists
    if not os.path.exists(dataset_file):
        print(f"Error: The dataset file '{dataset_file}' was not found.")
        print(f"Verify the correct path of the file '{dataset_file}'.")
    else:
        train_model(dataset_file, model_file)
        