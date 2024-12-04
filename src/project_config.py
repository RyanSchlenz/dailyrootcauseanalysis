import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Script Directory: {script_directory}")

# Configuration dictionary
config = {
    'scripts': [
        os.path.join(script_directory, 'extract.py'),
        os.path.join(script_directory, 'filter_groups.py'),
        os.path.join(script_directory, 'filter_subjects.py'),
        os.path.join(script_directory, 'map_products.py'),
        os.path.join(script_directory, 'aggregate.py'),
        os.path.join(script_directory, 'convert.py'),
        os.path.join(script_directory, 'sharepoint_upload.py'),
    ],
    'csv_files': [
        os.path.join(script_directory, 'extracted_data.csv'),
        os.path.join(script_directory, 'filtered_groups.csv'),
        os.path.join(script_directory, 'filtered_subjects.csv'),
        os.path.join(script_directory, 'mapped_filtered_subjects.csv'),
        os.path.join(script_directory, 'aggregated_data.csv'),
        os.path.join(script_directory, 'aggregated_data.xlsx'),
        os.path.join(script_directory, 'detailed_analysis.csv'),
        os.path.join(script_directory, 'detailed_analysis.xlsx'),
    ],
    'sharepoint': {
        'site_url': os.getenv('SHAREPOINT_SITE_URL'),
        'remote_path': os.getenv('SHAREPOINT_REMOTE_PATH'),
        'target_file_name': os.getenv('SHAREPOINT_TARGET_FILE_NAME'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'tenant_id': os.getenv('TENANT_ID'),
        'tenant_name': os.getenv('TENANT_NAME'),
        'access_token': os.getenv('ACCESS_TOKEN'),
        'sharepoint_file_name': "zendesk_ticket_analysis.xlsx",
        'scope': "api://ddf1fb9c-9247-487d-8fcc-4da0dd8e0f40/.default",
        'grant_type': "client_credentials",
        'tenant_domain': "pennantservices.com",
        'folder_url': "/sites/ITOperations/Shared%20Documents",
        'sheet_name_daily': "daily_ticket_tracker",
        'sheet_name_detailed': "detailed_daily_ticket_tracker",
        'documents_library': "/Shared Documents",
        'api_url': "https://graph.microsoft.com/v1.0/sites/{site_url_formatted}",
    }
}

# Zendesk configuration
zendesk_subdomain = 'cornerstoneguide'
zendesk_email = 'Ryan.schlenz@pennantservices.com'
zendesk_api_token = os.getenv('ZENDESK_API_TOKEN') # Load from environment variables
zendesk_api_url = f'https://{zendesk_subdomain}.zendesk.com/api/v2'
product_service_desk_tool_id = 14419377944851
action_taken_id = 14420345771795

# Helper functions
def get_script_path(script_name):
    """Returns the full path of a script in the current directory."""
    return os.path.join(script_directory, script_name)

def get_csv_path(filename):
    """Returns the full path of a CSV file in the current directory."""
    return os.path.join(script_directory, filename)

logging.info("Configuration and paths have been set up.")
