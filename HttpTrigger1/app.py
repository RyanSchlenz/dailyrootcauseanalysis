from flask import Flask, render_template, jsonify, request
import threading
import os
import asyncio
from main import run_script  # Import run_script which will perform SharePoint and Excel update

app = Flask(__name__)

# File to track sync status
SYNC_STATUS_FILE = "status.txt"

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
    asyncio.run(run_script("main.py"))  # Replace with the actual script you want to run for SharePoint integration

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
    
    # Start the sync task in a background thread using asyncio
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
