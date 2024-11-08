import sys
import os

# Insert the path to your project directory
sys.path.insert(0, r"F:\Dokkan Battle Damage Taken\Dokkan-Battle-Damage-Taken")

# Set the environment variable for the Flask app (only needed if FLASK_APP is required)
os.environ["FLASK_APP"] = "app.py"  # Replace "app.py" with the main file of your app

# Import the Flask app
from app import app as application  # Replace 'app' with the name of your main Flask file (without .py)
