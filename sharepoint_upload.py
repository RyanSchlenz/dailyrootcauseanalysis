import msal
from dataclasses import dataclass
import logging
import pandas as pd
import io
from office365.sharepoint.client_context import ClientContext, ClientCredential
from office365.sharepoint.files.file import File
import os
import sys
from openpyxl.utils import get_column_letter
import requests

# Adjust the module search path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import configuration from project_config.py
from project_config import config

# Access SharePoint settings
sharepoint = config['sharepoint']
tenant_id = sharepoint['tenant_id']

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

@dataclass
class JSONToken:
    tokenType: str
    accessToken: str

def authenticate_to_graph():
    logging.info("Authenticating to Microsoft Graph...")
    tenant_id = sharepoint['tenant_id']
    logging.info(f"Tenant ID: {tenant_id}")  # Log the tenant ID

    app = msal.ConfidentialClientApplication(
        sharepoint['client_id'],
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=sharepoint['client_secret'],
    )

    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in result:
        logging.info("Access token acquired successfully.")
        return result['access_token']
    else:
        logging.error("Error acquiring token: %s", result.get("error_description"))
        raise Exception("Authentication failed")

def load_dataframe_from_sharepoint(ctx, folder_relative_path, target_file_name):
    logging.info(f"Loading {target_file_name} from SharePoint folder '{folder_relative_path}'...")
    file_url = f"{folder_relative_path}/{target_file_name}"
    logging.info(f"Attempting to access file at path: {file_url}")

    try:
        response = File.open_binary(ctx, file_url)
        df_dict = pd.read_excel(io.BytesIO(response.content), sheet_name=None)
        
        # Validate data presence in file
        if not df_dict or all(df.empty for df in df_dict.values()):
            raise FileNotFoundError(f"File '{target_file_name}' is empty or could not be found.")
        
        logging.info(f"Loaded data from {target_file_name} successfully.")
        return df_dict

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTPError: {e.response.status_code} for URL: {e.response.url}")
        raise

def save_dataframe_to_sharepoint(ctx, folder_relative_path, file_name, df_dict):
    logging.info(f"Uploading {file_name} to SharePoint folder '{folder_relative_path}'...")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                worksheet = writer.sheets[sheet_name]
                df.columns = df.columns.str.strip()
                logging.info(f"Columns in DataFrame for '{sheet_name}': {df.columns.tolist()}")
                adjust_column_widths(worksheet, df)
            else:
                logging.warning(f"DataFrame for sheet '{sheet_name}' is empty. Skipping...")

    buffer.seek(0)
    file_content = buffer.read()
    folder = ctx.web.get_folder_by_server_relative_url(folder_relative_path)
    folder.upload_file(file_name, file_content).execute_query()
    logging.info(f"Uploaded {file_name} successfully to SharePoint.")

def adjust_column_widths(worksheet, dataframe):
    for i, col in enumerate(dataframe.columns, start=1):  # Using 1-based index for Excel
        col_name_str = str(col)
        column_data = dataframe[col].astype(str).fillna('')
        max_length = column_data.apply(len).max()
        max_length = max(max_length, len(col_name_str))
        col_letter = get_column_letter(i)  # Convert index to Excel letter format
        worksheet.column_dimensions[col_letter].width = max_length + 2  # Add some padding

def sync_and_update_excel():
    logging.info("Starting synchronization and update process...")

    # Authentication and context setup
    site_url = sharepoint['site_url']
    client_id = sharepoint['client_id']
    client_secret = sharepoint['client_secret']
    ctx = ClientContext(site_url).with_credentials(ClientCredential(client_id, client_secret))

    # Define SharePoint paths
    folder_relative_path = sharepoint['remote_path']
    sharepoint_file_name = sharepoint['sharepoint_file_name']
    backup_file_name = "zendesk_ticket_analysis_backup.xlsx"  # Define the backup file name
    sheet_name_daily = sharepoint['sheet_name_daily']  # Get the sheet name from config

    df_dict = load_dataframe_from_sharepoint(ctx, folder_relative_path, sharepoint_file_name)
    daily_tracker = df_dict.get(sheet_name_daily)

    if daily_tracker is None or daily_tracker.empty:
        logging.error("daily_tracker is None or empty.")
        return  # Stop if no data in daily_tracker

    # Process daily tracker data
    daily_tracker = daily_tracker.iloc[:, :3]
    daily_tracker.columns = ['Date', 'Product - Service Desk Tool', 'Ticket Count']
    daily_tracker['Ticket Count'] = pd.to_numeric(daily_tracker['Ticket Count'], errors='coerce').fillna(0)

    daily_tracker['Date'] = pd.to_datetime(daily_tracker['Date'], errors='coerce').dt.strftime('%m/%d/%Y')

    ticket_counts = daily_tracker.groupby(['Date', 'Product - Service Desk Tool'], as_index=False)['Ticket Count'].sum()
    existing_dates = set(ticket_counts['Date'].unique())

    aggregated_data = pd.read_excel("/tmp/aggregated_data.xlsx", header=0).dropna(how='all')
    aggregated_data.columns = aggregated_data.columns.str.strip()
    aggregated_data['Ticket Count'] = pd.to_numeric(aggregated_data['Ticket Count'], errors='coerce').fillna(0)
    aggregated_data['Date'] = pd.to_datetime(aggregated_data['Date'], errors='coerce').dt.strftime('%m/%d/%Y')

    new_rows_daily = aggregated_data[~aggregated_data['Date'].isin(existing_dates)]
    if not new_rows_daily.empty:
        daily_tracker = pd.concat([daily_tracker, pd.DataFrame([["", "", ""]]), new_rows_daily], ignore_index=True)
        logging.info("Appended new rows to daily_ticket_tracker.")

    detailed_tracker = df_dict.get('detailed_daily_ticket_tracker')

    if detailed_tracker is not None:
        detailed_tracker = detailed_tracker.iloc[:, :4]
        detailed_tracker.columns = ['Date', 'Product - Service Desk Tool', 'Ticket Count', 'Ticket subject']
        detailed_tracker['Ticket Count'] = pd.to_numeric(detailed_tracker['Ticket Count'], errors='coerce').fillna(0)
        detailed_tracker['Date'] = pd.to_datetime(detailed_tracker['Date'], errors='coerce').dt.strftime('%m/%d/%Y')

    if os.path.exists("/tmp/detailed_analysis.xlsx"):
        detailed_analysis = pd.read_excel("/tmp/detailed_analysis.xlsx", header=0)
        detailed_analysis.columns = detailed_analysis.columns.str.strip()
        detailed_analysis['Ticket Count'] = pd.to_numeric(detailed_analysis['Ticket Count'], errors='coerce').fillna(0)
        detailed_analysis['Date'] = pd.to_datetime(detailed_analysis['Date'], errors='coerce').dt.strftime('%m/%d/%Y')

        detailed_existing_dates = set(detailed_tracker['Date'].unique())
        new_rows_detailed = detailed_analysis[~detailed_analysis['Date'].isin(detailed_existing_dates)]

        if not new_rows_detailed.empty:
            detailed_tracker = pd.concat(
                [detailed_tracker, pd.DataFrame([["", "", "", ""]], columns=detailed_tracker.columns), new_rows_detailed],
                ignore_index=True
            )
            logging.info(f"Appended {len(new_rows_detailed)} new rows to detailed_daily_ticket_tracker.")
    else:
        logging.warning("detailed_analysis.xlsx not found. Skipping updates to detailed_daily_ticket_tracker.")

    updated_dfs = {'detailed_daily_ticket_tracker': detailed_tracker, sheet_name_daily: daily_tracker}

    # Attempt to save the main file
    try:
        save_dataframe_to_sharepoint(ctx, folder_relative_path, sharepoint_file_name, updated_dfs)
        logging.info(f"{sharepoint_file_name} updated successfully.")
    except Exception as e:
        logging.error(f"Failed to update main file {sharepoint_file_name}: {e}")

    # Ensure the backup file is saved regardless of the main file update status
    try:
        save_dataframe_to_sharepoint(ctx, folder_relative_path, backup_file_name, updated_dfs)
        logging.info(f"{backup_file_name} updated successfully as backup.")
    except Exception as e:
        logging.error(f"Failed to update backup file {backup_file_name}: {e}")

    logging.info("Synchronization and update process completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_and_update_excel()
