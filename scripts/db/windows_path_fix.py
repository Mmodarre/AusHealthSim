"""
Windows-specific path fix for the Health Insurance AU simulation.
This file should be placed in the same directory as add_initial_data.py.
"""
import os
import sys

# Get the absolute path of the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

# Add project root to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(project_root, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Set environment variables
os.environ['HEALTH_INSURANCE_LOG_DIR'] = logs_dir

# Print debug information
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")
print(f"Logs directory: {logs_dir}")