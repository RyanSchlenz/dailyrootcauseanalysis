import pandas as pd
import sys
import io
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import tmp_dir

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Define the paths for the input and output CSV files in the temporary storage
    input_csv_file_path = f'{tmp_dir}/extracted_data.csv'  # Adjusted for temp storage
    output_csv_file_path = f'{tmp_dir}/filtered_groups.csv'  # Adjusted for temp storage

    # Load the CSV file into a DataFrame, ensuring the 'Ticket created - Year' column is included
    df = pd.read_csv(input_csv_file_path)

    # Ensure relevant columns are treated as strings
    df['Ticket group'] = df['Ticket group'].astype(str)
    df['Product - Service Desk Tool'] = df['Product - Service Desk Tool'].astype(str)

    # Update 'Product - Service Desk Tool' based on 'Ticket group'
    df.loc[df['Ticket group'].isin(['Equipment', 'Equipment Waiting', 'mobile_device_new']), 'Product - Service Desk Tool'] = 'Equipment'
    df.loc[df['Ticket group'] == 'Fuze', 'Product - Service Desk Tool'] = 'Fuze'
    df.loc[df['Ticket group'].isin(['Hartford UAP', 'UAP', 'automation_mobile_device_term']), 'Product - Service Desk Tool'] = 'UAP'
    df.loc[df['Ticket group'] == 'Network', 'Product - Service Desk Tool'] = 'Network'
    df.loc[df['Ticket group'] == 'workday_new', 'Product - Service Desk Tool'] = 'Workday'
    df.loc[df['Ticket group'].isin(['teams_new']), 'Product - Service Desk Tool'] = 'Teams'
    df.loc[df['Ticket group'].isin(['pointcare_new']), 'Product - Service Desk Tool'] = 'HCHB'

    # Assign blank value for 'Product - Service Desk Tool' if it is 'No Product' or 'other__please_list_below_'
    df.loc[df['Product - Service Desk Tool'] == 'No Product', 'Product - Service Desk Tool'] = ''
    df.loc[df['Product - Service Desk Tool'] == 'other__please_list_below_', 'Product - Service Desk Tool'] = ''

    # Save the updated DataFrame to a new CSV file, including all original columns
    df.to_csv(output_csv_file_path, index=False)

    print(f"Filtered Groups CSV file saved to {output_csv_file_path}")

if __name__ == "__main__":
    main()
