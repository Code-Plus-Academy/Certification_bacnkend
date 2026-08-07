import sys
import os

# Add parent root directory to sys.path so app.py, generator.py, and cloud_uploader.py resolve cleanly
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
