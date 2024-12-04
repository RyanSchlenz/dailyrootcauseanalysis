import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Define the Azure temporary directory for files created during execution
tmp_dir = '/tmp'

# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
logging.info(f"Script Directory: {script_directory}")

# Move up two levels to find the HelpDeskTimer directory
helpdesk_timer_dir = os.path.abspath(os.path.join(script_directory, 'HelpDeskTimer'))
logging.info(f"HelpDeskTimer Directory: {helpdesk_timer_dir}")

# Ensure the tmp directory exists
os.makedirs(tmp_dir, exist_ok=True)

# Add the parent directory to sys.path to allow imports from project_config
parent_dir = os.path.abspath(os.path.join(script_directory, '..', '..'))
sys.path.append(parent_dir)

# Configuration dictionary
config = {
    'tmp_dir': tmp_dir,
    'scripts': [
        os.path.join(helpdesk_timer_dir, 'extract.py'),
        os.path.join(helpdesk_timer_dir, 'filter_groups.py'),
        os.path.join(helpdesk_timer_dir, 'filter_subjects.py'),
        os.path.join(helpdesk_timer_dir, 'map_products.py'),
        os.path.join(helpdesk_timer_dir, 'aggregate.py'),
        os.path.join(helpdesk_timer_dir, 'convert.py'),
        os.path.join(helpdesk_timer_dir, 'sharepoint_upload.py')
    ],
    'csv_files': [
        os.path.join(tmp_dir, 'extracted_data.csv'),
        os.path.join(tmp_dir, 'filtered_groups.csv'),
        os.path.join(tmp_dir, 'filtered_subjects.csv'),
        os.path.join(tmp_dir, 'mapped_filtered_subjects.csv'),
        os.path.join(tmp_dir, 'aggregated_data.csv'),
        os.path.join(tmp_dir, 'aggregated_data.xlsx'),
        os.path.join(tmp_dir, 'detailed_analysis.csv'),
        os.path.join(tmp_dir, 'detailed_analysis.xlsx')
    ],
    # SharePoint configuration embedded directly into the main config
    'sharepoint': {
        'site_url': os.getenv('SHAREPOINT_SITE_URL'),
        'remote_path': os.getenv('SHAREPOINT_REMOTE_PATH'),
        'target_file_name': os.getenv('SHAREPOINT_TARGET_FILE_NAME'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'tenant_id': os.getenv('TENANT_ID'),
        'tenant_name': os.getenv('TENANT_NAME'),
        'function_key': os.getenv('FUNCTION_KEY'),
        'access_token': os.getenv('access_token'),
        'sharepoint_file_name': "zendesk_ticket_analysis.xlsx",
        'scope': "api://ddf1fb9c-9247-487d-8fcc-4da0dd8e0f40/.default",
        'grant_type': "client_credentials",
        'tenant_domain': "pennantservices.com",
        'folder_url': "/sites/ITOperations/Shared%20Documents",
        'parent_folder_id': "01ZSE3CYV6Y2GOVW7725BZO354PWSELRRZ",
        'sheet_name_daily': "daily_ticket_tracker",
        'sheet_name_detailed': "detailed_daily_ticket_tracker",
        'documents_library': "/Shared Documents",
        'api_url': "https://graph.microsoft.com/v1.0/sites/{site_url_formatted}",
        'site_id': "pennantservicesinc.sharepoint.com,a6f51605-0051-49f5-b257-07a722122fbc,7411702e-5a64-4517-9a0d-35cde9ab6d59",
        'list_id': "f481df67-bd4c-4b33-91a2-63fca68156f8",
        'file_id': "01ZSE3CYSXU47NUEK2JVD2CJFWPMVG6GYK", 
        'site_location': "sites/ITOperations/Shared Documents/Solutions Engineering",
        'my_date_folder': "Solutions Engineering",
        'drive_id': "b!BRb1plEA9UmyVwenIhIvvC5wEXRkWhdFmg01zemrbVln34H0TL0zS5GiY_ymgVb4",
        'relative_path': "drives/b!BRb1plEA9UmyVwenIhIvvC5wEXRkWhdFmg01zemrbVln34H0TL0zS5GiY_ymgVb4/root:/Solutions%20Engineering/zendesk_ticket_analysis.xlsx",
        'download_url': "https://graph.microsoft.com/v1.0/drives/b!BRb1plEA9UmyVwenIhIvvC5wEXRkWhdFmg01zemrbVln34H0TL0zS5GiY_ymgVb4/items/01ZSE3CYSXU47NUEK2JVD2CJFWPMVG6GYK",
        'file_relative_url': "EVenPtoRWk1HoSS2eypvGwoByg976h2KgUXd7E-OtGya8Q",
           }
}

# Zendesk configuration
zendesk_subdomain = 'cornerstoneguide'
zendesk_email = 'Ryan.schlenz@pennantservices.com'
zendesk_api_token = os.getenv('ZENDESK_API_TOKEN')  # Load from env
zendesk_api_url = f'https://{zendesk_subdomain}.zendesk.com/api/v2'
product_service_desk_tool_id = 14419377944851
action_taken_id = 14420345771795