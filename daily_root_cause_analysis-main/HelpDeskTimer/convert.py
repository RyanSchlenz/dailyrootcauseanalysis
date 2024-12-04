import pandas as pd
import os
import sys
import io

# Adjust the module search path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import tmp_dir

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Print the temporary directory for debugging
print(f"Temporary directory is set to: {tmp_dir}")

# List of CSV files to convert, stored in the temporary directory
csv_files = [f'{tmp_dir}/aggregated_data.csv', f'{tmp_dir}/detailed_analysis.csv']

# Print the current working directory for debugging
print(f"Current Working Directory: {os.getcwd()}")

# Loop through each CSV file and check if it exists before converting it
for csv_file in csv_files:
    absolute_path = os.path.abspath(csv_file)
    print(f"Checking for CSV file (absolute path): {absolute_path}")  # Debugging print
    
    # Check if the file exists in the /tmp directory
    if os.path.exists(csv_file):
        # Extract the base name (without extension) for naming the output file
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        xlsx_file = f'{tmp_dir}/{base_name}.xlsx'  # Define the output Excel file path in tmp_dir
        
        # Print the output Excel file path for debugging
        print(f"Output Excel file will be saved to: {xlsx_file}")  # Debugging print

        # Read the CSV file into a DataFrame and print its columns
        df = pd.read_csv(csv_file)
        print("Columns in CSV file before conversion:")
        print(df.columns.tolist())  # Print the list of columns in the CSV file

        # Write the DataFrame to a separate Excel file
        df.to_excel(xlsx_file, index=False, engine='openpyxl')

        # Read the Excel file back into a DataFrame and print its columns
        df_excel = pd.read_excel(xlsx_file, engine='openpyxl')
        print("Columns in Excel file after conversion:")
        print(df_excel.columns.tolist())  # Print the list of columns in the Excel file

        # Confirmation message for each conversion
        print(f"CSV file '{csv_file}' has been successfully converted to '{xlsx_file}'")
    else:
        # If the file does not exist, print a message and move to the next file
        print(f"CSV file '{csv_file}' not found. Skipping to the next file.")

