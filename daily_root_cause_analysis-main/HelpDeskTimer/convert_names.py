import pandas as pd

# Define the path to the input CSV file
input_file_path = 'zendesk_product_names.csv'  # Change this to your input file path

# Read the CSV file into a DataFrame
df = pd.read_csv(input_file_path)

# Ensure the columns are properly named and modify the tag column to match the value column
df['tag'] = df['value']  # Set the tag column to the value column

# Save the modified DataFrame to a new CSV file
output_file_path = 'converted_names.csv'
df.to_csv(output_file_path, index=False)

print(f"Modified data saved to {output_file_path}")
