import os
import subprocess
import time
import logging
import datetime
import azure.functions as func
from HttpTrigger1.project_config import config  # Note the dot before 


logger = logging.getLogger(__name__)

# Load configuration from project_config
scripts = config['scripts']
csv_files = config['csv_files']

# Define the base directory for this function
BASE_DIR = os.path.dirname(__file__)  # This points to the HttpTrigger1 directory

# Function to get the full path of a file in the HttpTrigger1 directory
def get_file_path(filename):
    return os.path.join(BASE_DIR, filename)

# Function to run a script
def run_script(script):
    script_path = get_file_path(script)
    try:
        logger.info(f"Running {script_path}...")
        subprocess.check_call(['python3', script_path])
        logger.info(f"Successfully ran {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run {script_path}: {e}")
        return False

# Function to check if required CSV files exist
def check_csv_files(files, retries=3, delay=2):
    for attempt in range(retries):
        missing_files = [get_file_path(file) for file in files if not os.path.isfile(get_file_path(file))]
        if not missing_files:
            return True
        logger.warning(f"Attempt {attempt + 1}: Missing files: {', '.join(missing_files)}")
        time.sleep(delay)
    return False

# Function to delete all created CSV and XLSX files except certain ones
def delete_files(files):
    dir_path = BASE_DIR  # Use BASE_DIR for deletion

    for file in files:
        file_path = get_file_path(file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"Deleted {file_path}")
    
    for file in os.listdir(dir_path):
        if file.endswith('.csv') or file.endswith('.xlsx'):
            file_to_delete = os.path.join(dir_path, file)
            os.remove(file_to_delete)
            logger.info(f"Deleted {file_to_delete}")

# Function to run all scripts and check CSV and XLSX file existence
def run_all_scripts():
    success = True
    
    for script in scripts:
        if not run_script(script):
            success = False
            break
    
    time.sleep(2)  # Give a little delay before checking files
    
    if success and check_csv_files(csv_files):
        logger.info("All scripts ran successfully and all required CSV files are present.")
    else:
        logger.warning("One or more files are missing. Not retrying the scripts.")
        success = False  # Ensure success is marked as False if files are missing
    
    # Delete files regardless of success
    delete_files(csv_files)
    return success  # Indicate overall success or failure

# Azure Function entry point for HTTP Trigger
def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('HTTP trigger function executed at %s', datetime.datetime.utcnow())
    
    # Log request information
    logger.info("Request method: %s", req.method)
    logger.info("Request URL: %s", req.url)

    # Optional: Log query parameters if any
    if req.params:
        logger.info("Query parameters: %s", req.params)

    # Run all scripts and check for CSV files
    try:
        success = run_all_scripts()
        
        if success:
            return func.HttpResponse("All scripts executed successfully and all required CSV files are present.", status_code=200)
        else:
            return func.HttpResponse("One or more files are missing. Scripts did not execute as expected.", status_code=400)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return func.HttpResponse("An internal server error occurred.", status_code=500)

# Allow manual testing when running as a standalone script
if __name__ == "__main__":
    logger.info("Running as standalone script.")
    run_all_scripts()
