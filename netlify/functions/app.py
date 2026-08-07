import sys
import os

# Add root directory to sys.path so app.py and generator.py imports resolve cleanly
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import serverless_wsgi
from app import app

def handler(event, context):
    if isinstance(event, dict):
        if 'path' in event and isinstance(event['path'], str):
            if event['path'].startswith('/.netlify/functions/app'):
                clean_path = event['path'][len('/.netlify/functions/app'):]
                event['path'] = clean_path if clean_path else '/'
        if 'rawPath' in event and isinstance(event['rawPath'], str):
            if event['rawPath'].startswith('/.netlify/functions/app'):
                clean_path = event['rawPath'][len('/.netlify/functions/app'):]
                event['rawPath'] = clean_path if clean_path else '/'

    return serverless_wsgi.handle_request(app, event, context)

