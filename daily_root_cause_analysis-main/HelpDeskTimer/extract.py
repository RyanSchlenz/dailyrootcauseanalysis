import sys 
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import tmp_dir
from project_config import zendesk_email, zendesk_subdomain, product_service_desk_tool_id, action_taken_id, zendesk_api_token 

# Get Zendesk API token from environment variable (Assuming it's set in the Azure environment)
api_token = zendesk_api_token

if api_token is None:
    raise ValueError("Zendesk API Token is not set in the project config variables.")

# Zendesk credentials and details
subdomain = zendesk_subdomain
email = f'{zendesk_email}/token'

# List of allowed group names
allowed_group_names = {
    'IT', 'Equipment', 'Fuze', 'Light Agents', 'Network', 'Mobile Reconciliation',
    'Outbound', 'Tier 1', 'Tier 2', 'UAP', 'Tier 1 - OB', 'Trainee',
    'Equipment Waiting', 'Email', 'Inbound', 'QA'
}

# List of subject patterns to exclude
excluded_subject_patterns = [
    r'\bTermination-\b.*',
    r'\bCreate HCHB\b.*',
    r'\bCreate desktop\b.*',
    r'\bCreate Forcura\b.*',
    r'\bVerify System\b.*',
    r'\bCompleted: Complete with DocuSign\b.*',
    r'\bBackground Check\b.*',
    r'\bCompleted With Errors\b.*',
    r'\bAlert: Network\b.*',
    r'\bReset: Facility\b.*',
    r'\bFax Status for Job\b.*',
    r'\bAssign Online Learning Hub\b.*',
    r'\bCall with Caller\b.*',
    r'\bSUPPORT EXPIRED\b.*',
    r'\bADP\b.*',
    r'\bA Rehire Has Been Processed\b.*',
    r'\bMissed call with Caller\b.*',
    r'\bHartford Inbound\b.*',
    r'\bMissed call from\b.*',
    r'\bwithholding\b.*',
    r'\bCall Back Request\b.*',
    r'\bCall on\b.*',
    r'\bCall with\b.*',
    r'\bUnknown caller\b.*',
    r'\bVoicemail\b.*',
    r'\bvoicemail\b.*',
    r'\bConversation with\b.*',
    r'\b"Conversation with\b.*',
    r'\bConversation with \b.*',
    r'\bCall Back - No Answer\b.*',
    r'\bCall back follow-up\b.*',
    r'\bCall back request\b.*',
    r'\bCall back\b.*'    
]

tickets = []
batch_size = 500  # Fetch 500 tickets at a time
pause_duration = 15  # Pause for 15 seconds after each batch

# Function to fetch groups from Zendesk
def fetch_groups():
    url = f'https://{subdomain}.zendesk.com/api/v2/groups.json'
    response = requests.get(url, auth=(email, api_token))
    
    if response.status_code != 200:
        print(f"Error fetching groups: {response.status_code}")
        return {}

    group_data = response.json()
    group_map = {group['id']: group['name'] for group in group_data['groups']}
    return group_map

# Function to fetch tickets within a date range
def fetch_tickets_for_date_range(start_date, end_date, group_map):
    url = f'https://{subdomain}.zendesk.com/api/v2/search.json?query=type:ticket created>{start_date} created<{end_date}&per_page={batch_size}'
    tickets_fetched = []
    
    while url:
        response = requests.get(url, auth=(email, api_token))
        
        if response.status_code == 429:  # Rate limit hit
            print("Rate limit exceeded. Pausing for longer duration...")
            time.sleep(pause_duration)
            continue  # Retry the request after the pause

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.json())
            return tickets_fetched  # Return whatever we have fetched so far

        data = response.json()
        tickets_data = data.get('results', [])
        tickets_fetched.extend(process_tickets(tickets_data, group_map))
        url = data.get('next_page')  # Get the next page URL

        if len(tickets_fetched) >= 500:
            save_tickets_to_csv(tickets_fetched)
            tickets_fetched.clear()
            time.sleep(pause_duration)  # Pause after every 500 tickets

    return tickets_fetched

def save_tickets_to_csv(tickets_batch):
    if tickets_batch:
        df = pd.DataFrame(tickets_batch)
        # Define the path to save the extracted data in the /tmp directory
        output_path = f'{tmp_dir}/extracted_data.csv'
        # Ensure the schema has header in the first write
        df.to_csv(output_path, mode='a', index=False, header=not pd.io.common.file_exists(output_path))
        print(f"Saved {len(tickets_batch)} tickets to {output_path}")
            
def filter_ticket(ticket, group_map):
    group_id = ticket.get('group_id')
    group_name = group_map.get(group_id, 'Unknown')

    if group_name not in allowed_group_names:
        return False

    ticket_subject = ticket.get('subject', '')
    for pattern in excluded_subject_patterns:
        if re.match(pattern, ticket_subject):
            return False

    return True

def process_tickets(tickets_data, group_map):
    filtered_tickets = []

    for ticket in tickets_data:
        # Print the entire ticket object for inspection
        print("\nFull Ticket Data:")
        print(ticket)  # Print the full ticket to see all fields
        
        if filter_ticket(ticket, group_map):
            created_at = ticket.get('created_at', ' ')
            group_id = ticket.get('group_id', ' ')
            group_name = group_map.get(group_id, 'Unknown')
            subject = ticket.get('subject', '')

            # Retrieve the product name and action taken from custom fields
            product_name = None  # Initialize to None if not found
            action_taken = None  # Initialize to None if not found
            
            for custom_field in ticket.get('custom_fields', []):
                if custom_field['id'] == product_service_desk_tool_id:  # Use the imported variable
                    product_name = custom_field.get('value', 'No Value')  # Use 'No Value' if field is empty
                elif custom_field['id'] == action_taken_id:  # Use the imported variable
                    action_taken = custom_field.get('value', 'No Action')  # Use 'No Action' if field is empty

            # Extract day, month, and year from created_at
            try:
                created_datetime = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                created_day = created_datetime.day
                created_month = created_datetime.month
                created_year = created_datetime.year  # Extract the year
                
                # Debug prints
                print(f"Created Date: {created_datetime}, Day: {created_day}, Month: {created_month}, Year: {created_year}")
                
            except Exception as e:
                print(f"Error parsing created_at: {created_at}. Error: {e}")
                continue  # Skip to the next ticket if there's an error

            # Append the filtered ticket data
            filtered_tickets.append({
                'Product - Service Desk Tool': product_name or 'No Product',  # Default to 'No Product' if None
                'Action Taken': action_taken or 'No Action',  # Default to 'No Action' if None
                'Ticket group': group_name,
                'Ticket subject': subject,
                'Ticket created - Day of month': created_day,
                'Ticket created - Month': created_month,
                'Ticket created - Year': created_year,  # Include the year in the output
                'Tickets': 1
            })

    # Print the schema and the first ticket for verification
    if filtered_tickets:
        print("Schema of pulled tickets:")
        print(", ".join(filtered_tickets[0].keys()))  # Print column names (schema)
        print("\nSample Ticket Data:")
        print(filtered_tickets[0])  # Print the first ticket for inspection

    return filtered_tickets

# Main function to fetch tickets for the previous day
def main():
    # Set end_date to midnight of the current day (start of today)
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # Set start_date to midnight of the previous day (start of yesterday)
    start_date = end_date - timedelta(days=1)

    group_map = fetch_groups()
    
    # Debugging: Print start and end dates to ensure they're correct
    print(f"Fetching tickets from {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
     # Fetch tickets for the specified date range
    tickets_fetched = fetch_tickets_for_date_range(start_date.strftime('%Y-%m-%dT%H:%M:%SZ'), 
                                                     end_date.strftime('%Y-%m-%dT%H:%M:%SZ'), 
                                                     group_map)
    
    # Save any remaining tickets after the last batch
    save_tickets_to_csv(tickets_fetched)

if __name__ == '__main__':
    main()
