import os
import asyncio
import logging
import sys
import io

# Adjust the module search path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_config import config
from project_config import tmp_dir

# Set the standard output to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Use Azure's built-in logger
logger = logging.getLogger(__name__)

# Load configuration from project_config
scripts = config['scripts']
csv_files = config['csv_files']

# Function to get the full path of a script in the HelpDeskTimer directory
def get_script_path(script):
    return script  # No changes needed if paths are already correct in project_config.py

# Function to get the full path of a file in the temporary directory
def get_tmp_file_path(filename):
    return os.path.join(tmp_dir, filename)

# Function to create required directories
async def create_directories(directories):
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")

# Function to run a script asynchronously
async def run_script(script):
    script_path = get_script_path(script)  # Path to script in HelpDeskTimer
    try:
        logger.info(f"Running {script_path}...")
        process = await asyncio.create_subprocess_exec(
            'python3', script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"Successfully ran {script_path}")
            logger.info(f"Output: {stdout.decode()}")
            return True
        else:
            logger.error(f"Failed to run {script_path}: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Exception occurred while running {script_path}: {e}")
        return False

# Function to check if required CSV files exist
async def check_csv_files(files, retries=3, delay=2):
    for attempt in range(retries):
        missing_files = [get_tmp_file_path(file) for file in files if not os.path.isfile(get_tmp_file_path(file))]
        if not missing_files:
            return True
        logger.warning(f"Attempt {attempt + 1}: Missing files: {', '.join(missing_files)}")
        await asyncio.sleep(delay)
    return False

# Function to delete all created CSV and XLSX files except zendesk_ticket_analysis.xlsx
async def delete_files(files):
    # Delete specific CSV files provided in the list
    for file in files:
        file_path = get_tmp_file_path(file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f"Deleted {file_path}")

    # Delete any other CSV or XLSX files in the temporary directory, excluding specific file
    for file in os.listdir(tmp_dir):
        if (file.endswith('.csv') or file.endswith('.xlsx')) and file != 'zendesk_ticket_analysis.xlsx':
            file_to_delete = os.path.join(tmp_dir, file)
            os.remove(file_to_delete)
            logger.info(f"Deleted {file_to_delete}")

# Function to run all scripts and check CSV and XLSX file existence
async def main_function():
    success = True

    for script in scripts:
        if not await run_script(script):
            success = False
            break

    await asyncio.sleep(2)  # Give a little delay before checking files

    if success and await check_csv_files(csv_files):
        logger.info("All scripts ran successfully and all required CSV files are present.")
    else:
        logger.warning("One or more files are missing. Not retrying the scripts.")
        success = False  # Ensure success is marked as False if files are missing

    # Delete files regardless of success
    await delete_files(csv_files)
    return success  # Indicate overall success or failure
