import sys
import os

# Add current function directory to sys.path so main_app, generator, cloud_uploader & site-packages resolve cleanly
func_dir = os.path.dirname(os.path.abspath(__file__))
if func_dir not in sys.path:
    sys.path.insert(0, func_dir)

root_dir = os.path.abspath(os.path.join(func_dir, '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import serverless_wsgi
from main_app import app

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
