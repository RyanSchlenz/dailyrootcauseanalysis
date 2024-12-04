import azure.functions as func
import logging
import sys
import os

# Ensure the current directory is in sys.path
sys.path.append(os.path.dirname(__file__))

from main import main_function


# Use Azure's built-in logger
logger = logging.getLogger(__name__)

# Azure Function entry point for Timer Trigger
async def main(myTimer: func.TimerRequest) -> None:
    logger.info('Azure Timer trigger function executed')

    # Run the main function from main.py
    try:
        await main_function()  # Call main_function from main.py
        logger.info("Completed execution of main_function from main.py")
    except Exception as e:
        logger.error(f"An error occurred while running main_function: {e}")
