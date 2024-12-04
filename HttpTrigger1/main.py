import os
import asyncio
import logging
import sys
import io
from HttpTrigger1.project_config import config  # Ensure `project_config.py` exists in the same directory

# Set up UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
scripts = config['scripts']
csv_files = config['csv_files']

# Function to run a script asynchronously
async def run_script(script):
    try:
        logger.info(f"Running script: {script}")
        process = await asyncio.create_subprocess_exec(
            'python3', script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f"Script {script} completed successfully.")
            logger.info(f"Output:\n{stdout.decode()}")
            return True
        else:
            logger.error(f"Script {script} failed with error:\n{stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Failed to execute script {script}: {e}")
        return False

# Function to verify the existence of required CSV files
async def check_csv_files(files):
    missing_files = [file for file in files if not os.path.isfile(file)]
    if missing_files:
        logger.warning(f"Missing files: {missing_files}")
        return False
    logger.info("All required CSV files are present.")
    return True

# Entry point for the script
if __name__ == "__main__":
    # This main entry point won't be used in Azure Functions, as the execution is triggered by HTTP.
    pass
