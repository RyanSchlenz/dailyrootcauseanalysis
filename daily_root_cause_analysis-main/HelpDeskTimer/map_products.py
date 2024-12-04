import pandas as pd
from io import StringIO
import sys
import io
import os

# Adjust the module search path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import tmp_dir

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Sample CSV data for mapping (Replace with your actual mapping CSV)
csv_data = """value,tag,default
3rd Party ERM,account_change,false
Accounting Close,accounting_close,false
aduc_new,aduc_new,false
App::Account Lookup Tool,app__account_lookup_tool,false
App::ADR & Appeals Claim Tracking,app__adr___appeals_claim_tracking,false
App::ADR/Denials,app__adr/denials,false
App::Equity,app__equity,false
App::Equity Nomination,app__equity_nomination,false
App::Financial Approvals,app__financial_approvals,false
App::Financial Emailer,app__financial_emailer,false
App::Interviews,app__interviews,false
App::Journal Entry Deletion,app__journal_entry_deletion,false
App::MEC Packet,app__mec_packet,false
App::Monitive Health,app__monitive_health,false
App::Nominations,app__nominations,false
App::pennant directory,app__pennant_directory,false
App::Photoshoot Tracker,app__photoshoot_tracker,false
App::QI Tracker,app__qi_tracker,false
App::Refunds & writeoffs app,app__refunds___writeoffs_app,false
App::State Survey,app__state_survey,false
App::Vehicle & Mileage Tracking,app__vehicle___mileage_tracking,false
Aruba Wireless,aruba_wireless_new,false
AT&T,at_t_mobiledevice,false
Automation,automation_uap,false
Automation Mobile Device Hire,automation_mobile_device_hire,false
Automation Mobile Device Term,automation_mobile_device_term,false
Azure,azure_new,false
Azure Virtual Desktop (AVD),azure_virtual_desktop__avd_,false
BitLocker,bitlocker,false
Black Line,black_line,false
Blank Voicemail,blank_voicemail,false
Cabeling,cabeling,false
Citrix,citrix_new,false
Concur,concur_new,false
Contract Room,contact_room,false
Contractor/Volunteer Set-Up,contractor/volunteer_set-up,false
Day 1 Concierge,day_1_concierge,false
DocLink,doclink_accounting,false
DocuSign,docusign_admin,false
Doxy,doxy_new,false
End User Training,end_user_training,false
Entra,entra_m365_admin_tools,false
Equipment Order,equipment_order,false
Exchange,exchange_m365,false
Fax,fax_new,false
Faxage,faxage_new,false
FedEx,fedex_shipping,false
File Explorer,file_explorer,false
Forcura,forcura_admin,false
Fuze,fuze,false
G-Drive,g-drive_new,false
"Google Authenticator ",google_authenticator_,false
Google Chrome,google_chrome,false
GP,gp,false
Great Plains,great_plains,false
H-Drive,h-drive_file_manager,false
Hardware,hardware,false
HCHB,hchb_new,false
Hexagon Call Audit,hexagon_call_audit,false
HFS,hfs,false
Hometrack,hometrack,false
Infrastructure,infrastructure_admin,false
Internet Account,internet_account_admin,false
Intune,intune_m365_admin_tools,false
IP Phones,ip_phones_admin,false
J-Drive,j-drive,false
Knowledge Link,knowledge_link,false
Laptop Troubleshooting,laptop_troubleshooting,false
Leave of Absence (LOA),leave_of_absence__loa_benefits,false
Legacy Excel Reports,legacy_excel_reports,false
Lippincott,lippincott,false
Location Change,location_change,false
Maleware/Spyware,maleware/spyware,false
Manual Census,manual_census,false
MECM (SCCM),mecm__sccm_,false
Medalogix,medalogix_admin,false
Medical Records Request,medical_records_request_admin,false
Microsoft Edge,microsoft_edge,false
Microsoft Office 365 Tools,microsoft_office_365_tools,false
MOBI,mobi_mobiledevice,false
Mobile Device,mobile_device_new,false
Mobile Device Order,mobile_device_order,false
Monitor Troubleshooting,monitor_troubleshooting_support,false
Move/Startup,move/startup_uap_product,false
Network,network_new,false
No Response - Requester,no_response_-_requester,false
No Touch Device (NTD),no_touch_device__ntd_,false
Nurse Call,nurse_call,false
Other (please list below),other__please_list_below_,false
Out of Country,out_of_country,false
Outlook,outlook_new,false
PAN Firewall,pan_firewall,false
PCC,pcc_new,false
PDF Xchange Editor,pdf_xchange_editor,false
Pennant Guide,pennant_guide_user_error_help,false
Pennant University,pennant_university_admin,false
PointCare,pointcare_new,false
Printer/Scanner/Copier,printer/scanner/copier,false
ProofPoint,provider_link,false
Router,router_new,false
Ruckus Wireless,ruckus_wireless,false
Sage,sage_accounting,false
Security,security,false
Service Provider,service_provider_new,false
SharePoint,sharepoint_m365,false
SHP,shp_new,false
Smartconnect,smartconnect,false
Smartsheets,smartsheets,false
Sophos,sophos,false
SPAM,spam_new,false
SSRS,ssrs,false
Stratodesk,stratodesk_admin,false
System Administrator,system_administrator,false
System Audit,system_audit,false
Tableau,tableau,false
Teams,teams_new,false
Telco,telco,false
Tiger Connect,tiger_connect_admin,false
Time Clock,time_clock_admin,false
Tipalti,tipalti,false
Trella Health,trella_health,false
Ultimus,ultimus,false
Unknown End User,unknown_end_user,false
UPS,ups,false
Veeam,veeam_admin,false
Verizon,verizon_admin,false
Voicemail,voicemail,false
Vulnerability Management,vulnerability_management,false
Waystar,waystar,false
Webex,webex_admin,false
Welcome Home,welcome_home_admin,false
Wells Fargo,wells_fargo_product_action,false
WiFi Connection,wifi_connection,false
Windows,windows_new,false
Workday,workday_new,false
Zendesk,zendesk_new,false
Zoom,zoom_new,false
"""

# Read the mapping CSV data into a DataFrame
mapping_df = pd.read_csv(StringIO(csv_data))

# Create a mapping dictionary
mapping_dict = dict(zip(mapping_df['tag'], mapping_df['value']))

# Read the filtered_subjects.csv into a DataFrame (update with your actual file path)
filtered_subjects_df = pd.read_csv(f'{tmp_dir}/filtered_subjects.csv')

# Replace the 'Product - Service Desk Tool' column with mapped values only if they exist in the mapping_dict
filtered_subjects_df['Product - Service Desk Tool'] = filtered_subjects_df['Product - Service Desk Tool'].replace(mapping_dict)

# Save the updated DataFrame to a new CSV file
mapped_filtered_subjects_path = f'{tmp_dir}/mapped_filtered_subjects.csv'
print(f"Saving file to: {mapped_filtered_subjects_path}")
filtered_subjects_df.to_csv(mapped_filtered_subjects_path, index=False)

