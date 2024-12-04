import os
import pandas as pd
import sys
import io

# Path configuration
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from project_config import tmp_dir

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Define paths for input and output CSV files
input_csv_file_path = f'{tmp_dir}/mapped_filtered_subjects.csv'
output_csv_file_path = f'{tmp_dir}/aggregated_data.csv'
detailed_analysis_csv_file_path = f'{tmp_dir}/detailed_analysis.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(input_csv_file_path)

# Data preprocessing
df['Product - Service Desk Tool'] = df['Product - Service Desk Tool'].astype(str).replace('nan', '').str.strip()
df['Ticket created - Day of month'] = df['Ticket created - Day of month'].astype(float).fillna(0).astype(int)
df['Ticket created - Month'] = df['Ticket created - Month'].astype(str).str.strip()

# Create a 'Date' column from day, month, and year columns
df['Date'] = df.apply(lambda row: f"{row['Ticket created - Month']}/{int(row['Ticket created - Day of month']):02d}/{int(row['Ticket created - Year'])}", axis=1)

# Replace month names with numerical values
month_mapping = {
    'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
    'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
}
df['Date'] = df['Date'].replace(month_mapping, regex=True)

# Convert the 'Date' column to datetime format and drop invalid dates
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')
df = df.dropna(subset=['Date'])
df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')

# Define a mapping for category combinations
# Define a mapping for category combinations
category_mapping = {
    'Mobile Device': 'MOBI',
    'Azure': 'Azure Virtual Desktop (AVD)',
    'Outlook': 'Exchange',
    'Fax': 'Faxage',
    'Hardware': 'Equipment/Hardware',
    'bitlocker': 'Equipment/Hardware',
    'Equipment': 'Equipment/Hardware',
    'hardware': 'Equipment/Hardware',
    'No Touch Device (NTD)': 'Equipment/Hardware',
    'FedEx': 'Equipment/Hardware',
    'fedex_shipping': 'Equipment/Hardware',
    'Laptop Troubleshooting': 'Equipment/Hardware',
    'monitor_troubleshooting_support': 'Equipment/Hardware',
    'Equipment Order': 'Equipment/Hardware',
    'BitLocker': 'Equipment/Hardware',
    'mobile_device_new': 'Equipment/Hardware',
    'Internet Account': 'Network',
    'Service Provider': 'Network',
    'WiFi Connection': 'Network',
    'network_new': 'Network',
    'veeam_admin': 'Network',
    'No Response - Requester': 'End User Training',
    'Unknown End User': 'End User Training',
    'Voicemail': 'End User Training',
    'no_response_-_requester': 'End User Training',
    'welcome_home_admin': 'End User Training',
    'voicemail': 'End User Training',
    'Citrix': 'Azure Virtual Desktop (AVD)',
    'citrix_new': 'Azure Virtual Desktop (AVD)',
    'J-Drive': 'Drive Access',
    'g-drive_new': 'Drive Access',
    'file_explorer': 'Drive Access',
    'h-drive_file_manager': 'Drive Access',
    'H-Drive': 'Drive Access',
    'G-Drive': 'Drive Access',
    'Microsoft Edge': 'Microsoft 365 Products',
    'entra_m365_admin_tools': 'Microsoft 365 Products',
    'legacy_excel_reports': 'Microsoft 365 Products',
    'microsoft_office_365_tools': 'Microsoft 365 Products',
    'Windows': 'Microsoft 365 Products',
    'windows_new': 'Microsoft 365 Products',
    'Teams': 'Microsoft 365 Products',
    'teams_new': 'Microsoft 365 Products',
    'Other (please list below)': 'End User Training',
    'docusign_admin': 'End User Training',
    'other__please_list_below_': 'End User Training',
    'zoom_new': 'End User Training',
    'Google Chrome': 'End User Training',
    'google_chrome': 'End User Training',
    'unknown_end_user': 'End User Training',
    'Fuze': 'Fuze/8x8',
    'fuze': 'Fuze/8x8',
    'ip_phones_admin': 'Fuze/8x8',
    'Microsoft Office 365 Tools': 'Microsoft 365 Products',
    'Pennant University': 'Pennant/Hartford Guide',
    'pennant_university_admin': 'Pennant/Hartford Guide',
    'PointCare': 'HCHB',
    'pointcare_new': 'HCHB',
    'Provider Link': 'HCHB',
    'hchb_new': 'HCHB',
    'knowledge_link': 'HCHB',
    'SPAM': 'End User Training',
    'spam_new': 'End User Training',
    'Verizon': 'MOBI',
    'verizon_admin': 'MOBI',
    'Smartsheets': 'Smartsheet',
    'smartsheets': 'Smartsheet',
    'Automation Mobile Device Hire': 'UAP',
    'Automation Mobile Device Term': 'UAP',
    'automation_mobile_device_term': 'UAP',
    'automation_mobile_device_hire': 'UAP',
    'day_1_concierge': 'UAP',
    'Tiger Connect': 'MOBI',
    'mobi_mobiledevice': 'MOBI',
    'Welcome Home': 'PCC',
    'pcc_new': 'PCC',
    'Pennant Guide': 'Pennant/Hartford Guide',
    'pennant_guide_user_error_help': 'Pennant/Hartford Guide',
    'ADUC': 'ADUC',
    'aduc_new': 'SSO Password Reset',
    'account_change': 'ADUC',
    'time_clock_admin': 'End User Training',
    'tableau': 'End User Training',
    'workday_new': 'Workday',
    'forcura_admin': 'Forcura',
    'printer/scanner/copier': 'Printer/Scanner/Copier',
    'SSO Self Service': 'SSO Self Service'
}

df['Product - Service Desk Tool'] = df['Product - Service Desk Tool'].map(category_mapping).fillna(df['Product - Service Desk Tool'])

# Ensure 'Tickets' column exists; if not, add a placeholder for counting
if 'Tickets' not in df.columns:
    df['Tickets'] = 1

# Group by 'Date' and 'Product - Service Desk Tool' to aggregate ticket counts
aggregated_df = df.groupby(['Date', 'Product - Service Desk Tool']).agg({'Tickets': 'sum'}).reset_index()
aggregated_df.rename(columns={'Tickets': 'Ticket Count'}, inplace=True)

# Initialize final rows for the aggregated data
final_rows = []

# Create totals per day and spacing between dates
for date, group in aggregated_df.groupby('Date'):
    final_rows.append(group)
    total_count = group['Ticket Count'].sum()
    total_row = pd.DataFrame({'Date': [date], 'Product - Service Desk Tool': ['Total'], 'Ticket Count': [total_count]})
    final_rows.append(total_row)
    final_rows.append(pd.DataFrame({'Date': [''], 'Product - Service Desk Tool': [''], 'Ticket Count': ['']}))

final_df = pd.concat(final_rows, ignore_index=True)
final_df.to_csv(output_csv_file_path, index=False)

# Detailed analysis for ticket counts over 15, excluding UAP
tickets_over_15 = aggregated_df[(aggregated_df['Ticket Count'] > 15) & (aggregated_df['Product - Service Desk Tool'] != 'UAP')]

if not tickets_over_15.empty:
    # Merge to include ticket subjects from the original DataFrame
    detailed_analysis = tickets_over_15.merge(df[['Date', 'Product - Service Desk Tool', 'Ticket subject']], on=['Date', 'Product - Service Desk Tool'], how='left')
    
    # Initialize rows for detailed analysis
    detailed_rows = []
    last_date = None

    # Add spacing between different dates in detailed analysis
    for date, group in detailed_analysis.groupby('Date'):
        if last_date is not None and last_date != date:
            detailed_rows.append(pd.DataFrame({'Date': [''], 'Product - Service Desk Tool': [''], 'Ticket subject': ['']}))
        detailed_rows.append(group)
        last_date = date

    # Concatenate and save detailed analysis data
    detailed_df = pd.concat(detailed_rows, ignore_index=True)
    detailed_df.to_csv(detailed_analysis_csv_file_path, index=False)
    print("Data aggregation and detailed analysis completed.")
else:
    print("Data aggregation completed. No ticket categories have over 15 tickets.")
