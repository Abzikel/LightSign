# Import libraries
import os
import pandas as pd

# Folder to get the "datasets"
datasets_folder = os.path.join(os.getcwd(), "datasets")

# List of files to combine
files_to_combine = [
    "NUMBER_1.csv",
    "NUMBER_2.csv",
    "NUMBER_3.csv",
    "THUMB_UP.csv",
    "THUMB_DOWN.csv"
]

# List to hold all DataFrames
all_dataframes = []

# Loop through each file, read it, and add to the list
for index, filename in enumerate(files_to_combine):
    # Get the file path
    file_path = os.path.join(datasets_folder, filename)

    # Check if the file exists before trying to read it
    if not os.path.exists(file_path):
        # Skip to the next file if not found
        print(f"⚠️ Warning: File not found - {file_path}. Skipping.")
        continue

    # Convert file to a dataframe
    df = pd.read_csv(file_path, header = 0)
    all_dataframes.append(df)

# Check if any dataframes were loaded
if not all_dataframes:
    print("No datasets were loaded. Cannot combine anything.")
else:
    # Concatenate all DataFrames into one
    combined_dataset = pd.concat(all_dataframes, ignore_index=True)

    # Define the output file path in the project root
    output_filename = "gestures_dataset.csv"
    output_path = os.path.join(os.getcwd(), output_filename)

    # Save the final combined dataset
    combined_dataset.to_csv(output_path, index=False)
    print(f"Combined dataset saved to: {output_path}")
