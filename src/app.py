from flask import Flask, render_template, jsonify, request
import threading
import os
import asyncio
import requests  # To call Azure Function
from .main import run_script

app = Flask(__name__)

# File to track sync status
SYNC_STATUS_FILE = "status.txt"

# Azure Function Configuration
AZURE_FUNCTION_URL = os.getenv("AZURE_FUNCTION_URL")
AZURE_FUNCTION_KEY = os.getenv("AZURE_FUNCTION_KEY")

def call_azure_function(payload):
    """Function to call Azure Function."""
    try:
        headers = {"Content-Type": "application/json"}
        if AZURE_FUNCTION_KEY:
            function_url_with_key = f"{AZURE_FUNCTION_URL}?code={AZURE_FUNCTION_KEY}"
        else:
            function_url_with_key = AZURE_FUNCTION_URL
        
        response = requests.post(function_url_with_key, json=payload, headers=headers)
        response.raise_for_status()
        print("Azure Function Response:", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Azure Function: {e}")
        return {"error": str(e)}

# Function to reset the sync status (can be triggered after each sync)
def reset_sync_state():
    with open(SYNC_STATUS_FILE, 'w') as file:
        file.write("Sync not started")  # Reset the state to "not started"

# Serve the homepage with the correct template
@app.route("/")
def home():
    return render_template("home.html")

# Function to run the async script within Flask
def run_async_script():
    """Runs the main SharePoint script and optionally triggers the Azure Function."""
    try:
        # Run your script
        asyncio.run(run_script("main.py"))
        
        # After script completes, trigger Azure Function
        payload = {"key": "value"}  # Replace with actual payload data
        azure_response = call_azure_function(payload)
        print(f"Azure Function response: {azure_response}")
        
        # Update the status to completed
        with open(SYNC_STATUS_FILE, 'w') as file:
            file.write("Sync completed")
    except Exception as e:
        print(f"Error in run_async_script: {e}")
        with open(SYNC_STATUS_FILE, 'w') as file:
            file.write("Sync failed")

# Endpoint to handle sync logic (triggering the task from main.py)
@app.route("/sync", methods=["POST"])
def sync():
    # Check if the sync is already running or completed
    if os.path.exists(SYNC_STATUS_FILE):
        with open(SYNC_STATUS_FILE, 'r') as file:
            status = file.read().strip()

        # If sync is already completed or running, reset it to start again
        if status == "Sync completed" or status == "Sync running":
            reset_sync_state()  # Reset sync state to allow a new sync

    # Update sync status to "Sync running"
    with open(SYNC_STATUS_FILE, 'w') as file:
        file.write("Sync running")
    
    # Start the sync task in a background thread
    thread = threading.Thread(target=run_async_script)
    thread.start()
    
    # Return an immediate response to the user indicating that the task has started
    return jsonify({"status": "success", "message": "Script task started", "link": "/path/to/sharepoint"})

# Endpoint to check sync status
@app.route("/status", methods=["GET"])
def status():
    try:
        with open(SYNC_STATUS_FILE, 'r') as file:
            status = file.read().strip()
    except FileNotFoundError:
        status = "Sync not started"
    
    return jsonify({"status": status})

# Serve static files (CSS, JS, etc.) if needed
@app.route('/static/<path:path>')
def static_files(path):
    return app.send_static_file(path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, use_reloader=False)
