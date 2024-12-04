import pandas as pd
import re
import sys
import io
import os

# Adjust the module search path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import tmp_dir

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Access the paths from the project_config
    input_csv_file_path = f'{tmp_dir}/filtered_groups.csv'  # Adjusted for temp storage
    output_csv_file_path = f'{tmp_dir}/filtered_subjects.csv' 


    # Define keyword rules for specific Subject Groups using regex
    keyword_rules = {
        'ADUC': [
            r'.*\bactive directory\b.*', r'.*\baduc\b.*', 
            r'.*\bDisable Accounts\b.*', r'.*\bAD\b.*'
        ],
        'Azure Virtual Desktop (AVD)': [
            r'.*\bavd\b.*', r'.*\bremote desktop\b.*', r'.*\bazure virtual desktop\b.*', 
            r'.*\bpennant desktop\b.*', r'.*\bpennant desk top\b.*', r'.*\bremote desk top\b.*', r'.*\bAzure Access\b.*', 
            r'.*\baccess to azure\b.*', r'.*\bazure\b.*', r'.*\bADV\b.*', r'.*\bdesk top\b.*'
        ],
        'Workday': [
            r'.*\bworker profile update\b.*', r'.*\bprofile update\b.*', r'.*\bupdated withholding\b.*', r'.*\bworkday\b.*'
        ],
        'HCHB': [
            r'.*\bhchb\b.*', r'.*\bpointcare training\b.*', r'.*\bpointcare\b.*', 
            r'.*\bpoint care\b.*', r'.*\bPoint Care\b.*', r'.*\bPointCare\b.*',
            r'.*\bhome care home base\b.*', r'.*\bhomecarehomebase\b.*', 
            r'.*\bworkflow\b.*', r'.*\bHCHB\b.*', r'.*\bhomecare homebase\b.*', 
            r'.*\bPennant Guide\b.*', r'.*\bPennantGuide\b.*', r'.*\bOLH\b.*', r'.*\bolh\b.*', r'.*\bHBHC\b.*'
        ],
        'Printer/Scanner/Copier': [
            r'.*\bprinter\b.*', r'.*\bscanner\b.*', r'.*\bcopier\b.*', 
            r'.*\badd printer\b.*', r'.*\bprinterlogic\b.*', 
            r'.*\badd new printer\b.*', r'.*\bremove printer\b.*', r'.*\bprinting\b.*', r'.*\bprint\b.*', r'.*\bprinters\b.*'
        ],
        'Drive Access': [
            r'.*\bj-drive\b.*', r'.*\bg-drive\b.*', r'.*\bg drive\b.*', 
            r'.*\bshared drive\b.*', r'.*\bh-drive\b.*', r'.*\bH Drive\b.*', r'.*\bH drive\b.*',
            r'.*\bh drive\b.*', r'.*\bj drive\b.*', r'.*\bJ drive\b.*', r'.*\baccess to drive\b.*', r'.*\bnetwork drive\b.*', 
            r'.*\bunable to access drive\b.*', r'.*\bdrive connection issue\b.*', 
            r'.*\bsyncing\b.*', r'.*\bSyncing\b.*', r'.*\bsync\b.*', r'.*\bSync\b.*', r'.*\bdrive access\b.*', r'.*\bJ Drive\b.*', r'.*\bdrive\b.*', r'.*\bDrive\b.*', r'.*\bone drive\b.*', r'.*\bonedrive\b.*',  
        ],
        'Exchange': [
            r'.*\bemail\b.*', r'.*\bemails\b.*', r'.*\bmail\b.*', r'.*\bmailbox\b.*', 
            r'.*\bemail inbox\b.*', r'.*\binbox\b.*', r'.*\bInbox\b.*'
            r'.*\bdistribution list\b.*', r'.*\bdl\b.*', 
            r'.*\bshared mailbox\b.*', r'.*\boutlook\b.*', r'.*\bGroup List\b.*'
        ],
        'Faxage': [
            r'.*\bfax\b.*', r'.*\bfaxage\b.*', r'.*\bfaxes\b.*', 
            r'.*\bfaxs\b.*', r'.*\bfaxages\b.*', r'.*\bfax age\b.*'  
        ],
        'MOBI': [
            r'.*\bmobi\b.*', r'.*\bmobile\b.*', r'.*\bcellphone\b.*', 
            r'.*\bcell\b.*', r'.*\bphone\b.*', r'.*\bphone number\b.*', 
            r'.*\bsamsung\b.*', r'.*\bandroid\b.*', r'.*\bverizon\b.*', 
            r'.*\bactivate\b.*', r'.*\bphones\b.*', r'.*\bHotspot\b.*', 
            r'.*\bBluetooth\b.*', r'.*\btiger\b.*', r'.*\bTiger\b.*', 
            r'.*\bhotspot\b.*', r'.*\bhot spot\b.*', r'.*\bText Message\b.*', 
            r'.*\btext message\b.*', r'.*\btextmessage\b.*', r'.*\bTigertext\b.*'
        ],
        'PCC': [
            r'.*\bpcc\b.*', r'.*\bpointclickcare\b.*', r'.*\bpoint click care\b.*', 
            r'.*\bPCC\b.*', r'.*\bpointclick care\b.*'
        ],
        'Fuze': [
            r'.*\bfuze\b.*'
        ],
        'Equipment': [
            r'.*\bshipping label\b.*', r'.*\bequipment order\b.*', 
            r'.*\border equipment\b.*', r'.*\bFedEx\b.*', r'.*\blaptops\b.*', 
            r'.*\blaptop\b.*', r'.*\bcomputer\b.*', r'.*\bchromebook\b.*', 
            r'.*\bchrome book\b.*', r'.*\bntd\b.*', r'.*\bstratodesk\b.*', r'.*\bkeyboard\b.*', r'.*\bmouse\b.*', r'.*\bbluetooth\b.*', r'.*\bblue tooth\b.*'
            r'.*\bstrato desk\b.*', r'.*\btablet\b.*', r'.*\breturn label\b.*', 
            r'.*\bHP\b.*', r'.*\bMonitor\b.*', r'.*\bDevice\b.*', 
            r'.*\bdevice\b.*', r'.*\bHeadphone\b.*', r'.*\bheadphone\b.*', 
            r'.*\bMicrophone\b.*', r'.*\bmicrophone\b.*', r'.*\bmonitor\b.*', r'.*\bequipment\b.*', r'.*\bEquipment\b.*', r'.*\bscreen\b.*', r'.*\bScreen\b.*', r'.*\baudio\b.*'
        ],
        'UAP': [
            r'.*\bUAP\b.*', r'.*\buser account provisioning\b.*', 
            r'.*\btermination\b.*', r'.*\btermination-\b.*', r'.*\btermed\b.*', 
            r'.*\bTerminations\b.*', r'.*\bname change\b.*', r'.*\bName Change\b.*', 
            r'.*\bName change\b.*', r'.*\bUPN\b.*', r'.*\bupn\b.*', r'.*\bvolunteer\b.*', r'.*\bVolunteer\b.*', r'.*\bcontractor\b.*', r'.*\bdeactivate\b.*',
        ],
        'Microsoft 365 Products': [
            r'.*\bExcel\b.*', r'.*\bTeams\b.*', r'.*\bteams\b.*', 
            r'.*\bexcel\b.*', r'.*\bintune\b.*', r'.*\bIntune\b.*', r'.*\bentra\b.*', r'.*\bEntra\b.*', r'.*\bsharepoint\b.*', r'.*\bshare point\b.*'
        ],
        'Adobe': [
            r'.*\badobe\b.*', r'.*\bAdobe\b.*', r'.*\badobe pdf\b.*'
        ],
        'Forcura': [
            r'.*\bforcura\b.*', r'.*\bForcura\b.*'
        ],
        'Network': [
            r'.*\bservice alert\b.*', r'.*\bnetwork\b.*', r'.*\binternet\b.*', 
            r'.*\bfirewall\b.*', r'.*\bISP\b.*', r'.*\byour service is restored\b.*'  
        ],
        'Smartsheet': [
            r'.*\bsmartsheet\b.*', r'.*\bsmartsheets\b.*', 
            r'.*\bsmart sheet\b.*', r'.*\bsmart sheets\b.*'
        ],
        'Pennant Guide': [
            r'.*\bPennU\b.*', r'.*\bPenn U\b.*', r'.*\bPennant U\b.*', r'.*\bpennant U\b.*' 
            r'.*\bPennant University\b.*', r'.*\bPennantUniversity\b.*', 
            r'.*\bPennant Guide\b.*', r'.*\bPennantGuide\b.*', r'.*\bPennant Guide:\b.*', 
            r'.*\bPenn Guide\b.*', r'.*\bhartfordguide\b.*', r'.*\bhartford guide\b.*',  r'.*\bpennant U\b.*', r'.*\bPenn U:\b.*'
        ],
        'No Action Taken': [
            r'.*\bMissed Call Follow Up\b.*',
            r'.*\bCall Back Request\b.*', r'.*\bCallback\b.*',
            r'.*\bNo vm left\b.*', r'.*\bno vm\b.*', 
            r'.*\bUnknown caller\b.*', r'.*\bConversation with\b.*',  
            r'.*\bfollow up\b.*', r'.*\bVoicemail\b.*', 
            r'.*\bvoicemail\b.*', r'.*\bNo answer on call back\b.*', r'.*\bself resolve\b.*'
        ],
        'End User Training': [
            r'.*\bbenefits\b.*', r'.*\bDocuSign\b.*', r'.*\burgent\b.*', r'.*\bhelp please\b.*',  r'.*\bhelp\b.*', r'.*\bBenefits\b.*', r'.*\bdocusign\b.*', r'.*\bphishing\b.*', r'.*\bPhishing\b.*'
        ],
        'Zendesk': [
            r'.*\bZenDesk\b.*', r'.*\bZendesk\b.*', r'.*\bzendesk\b.*', 
            r'.*\bZen Desk\b.*'
        ],
        'aduc_new': [
            r'.*\bsso\b.*', r'.*\bsingle sign-on\b.*', r'.*\blogin\b.*', 
            r'.*\bcannot login\b.*', r'.*\blogin issue\b.*', 
            r'.*\blogins\b.*', r'.*\blog ins\b.*', r'.*\bcreds check\b.*', 
            r'.*\bpassword reset\b.*', r'.*\bpw reset\b.*', r'.*\bpw\b.*', 
            r'.*\bcredential\b.*', r'.*\bcredentials\b.*', r'.*\bSSO\b.*', 
            r'.*\breset\b.*', r'.*\breset password\b.*', r'.*\bWorkday login\b.*',
            r'.*\bworkday login\b.*', r'.*\bWorkday Login\b.*', r'.*\bpassword\b.*'
        ],
    }


    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_csv_file_path)

    # Ensure relevant columns are treated as strings
    df['Ticket subject'] = df['Ticket subject'].astype(str)
    df['Product - Service Desk Tool'] = df['Product - Service Desk Tool'].astype(str)

    df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: f"'{x}" if not str(x).startswith("'") else str(x))
    df.iloc[:, 0] = df.iloc[:, 0].replace(r"^'|\.0$", "", regex=True)

    # Filter DataFrame to exclude 'No Action Taken' subjects
    def no_action_taken(ticket_subject):
        for pattern in keyword_rules.get('No Action Taken', []):
            if re.search(pattern, ticket_subject, re.IGNORECASE):
                return True
        return False

    df = df[~df['Ticket subject'].apply(no_action_taken)]

    # Define the logic for assigning the "Product - Service Desk Tool"
    def assign_product(ticket_subject, product_tool, action_taken):
        try:
            # Check if Action Taken is 'sso self_service' and return 'SSO Self Service'
            if action_taken == 'sso_self_service':
                return 'SSO Self Service'

            # Check if Action Taken is 'password_reset' and if keywords match
            if action_taken == 'password_reset':
                if re.search(r'\bSSO\b|\bADUC\b|\bAVD\b', ticket_subject, re.IGNORECASE):
                    return 'aduc_new'
            
            # Use the existing product_tool if it is valid
            if pd.notna(product_tool) and product_tool.strip() != 'nan' and product_tool.strip():
                return product_tool

            # Custom rules based on the subject of the ticket
            if re.search(r'\bConversation with\b', ticket_subject, re.IGNORECASE):
                return 'End User Training'
            
            if re.search(r'.*\bSSO Self-Service-Password Reset\b.*', ticket_subject, re.IGNORECASE):
                return 'SSO Self Service'
            
            if re.search(r'.*\bSSO Self-Service\b.*', ticket_subject, re.IGNORECASE):
                return 'SSO Self Service'
            
            ticket_subject_lower = ticket_subject.lower()
            for product, patterns in keyword_rules.items():
                if any(re.search(pattern, ticket_subject_lower) for pattern in patterns):
                    print(f"Matched '{ticket_subject}' to product '{product}'")
                    return product

            return 'Other'  # Default to 'Other' if no match is found
        except Exception as e:
            print(f"Error processing row with subject '{ticket_subject}': {e}")
            return 'Other'  # Return 'Other' in case of any error

    # Apply the product assignment function with error handling
    df['Product - Service Desk Tool'] = df.apply(
        lambda row: assign_product(row['Ticket subject'], row['Product - Service Desk Tool'], row['Action Taken']), axis=1
    )

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_file_path, index=False)

if __name__ == '__main__':
    main()